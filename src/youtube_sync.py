"""
YouTube channel synchronization - automatically download new transcripts.

Features:
- Incremental sync (only new videos)
- New channel backfill (100 videos)
- Retry logic for failed downloads
- Network connectivity check
- Tracks videos without subtitles to avoid re-trying
"""

import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import config
from .ingest import get_db, ingest_file

console = Console()


def check_network() -> bool:
    """Check if we have network connectivity."""
    try:
        import httpx
        response = httpx.head("https://www.youtube.com", timeout=5.0)
        return response.status_code < 500
    except Exception:
        return False


class SyncState:
    """
    Track sync state for channels.
    
    Simplified design:
    - no_subs: Videos with no subtitles (don't retry downloading)
    - last_sync: Rate limiting (don't sync same channel multiple times per day)
    
    Note: We no longer track "known" videos. The filesystem (MD files exist)
    and database (doc_id exists) are the source of truth for what's ingested.
    This makes the pipeline idempotent and self-healing.
    """
    
    def __init__(self):
        self.state_file = config.DATA_DIR / "sync_state.json"
        self.state = self._load()
    
    def _load(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except (json.JSONDecodeError, OSError):
                # Corrupted state file - start fresh
                return {}
        return {}
    
    def save(self):
        """Atomically save state to disk using temp file pattern."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write: write to temp file, then rename
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.state_file.parent,
            prefix="sync_state_",
            suffix=".tmp"
        )
        try:
            with os.fdopen(temp_fd, "w") as f:
                json.dump(self.state, f, indent=2)
            Path(temp_path).replace(self.state_file)
        except Exception:
            # Clean up temp file on failure
            Path(temp_path).unlink(missing_ok=True)
            raise
    
    def get_last_sync(self, channel: str) -> datetime | None:
        """Get last sync time for rate limiting."""
        if channel in self.state and "last_sync" in self.state[channel]:
            return datetime.fromisoformat(self.state[channel]["last_sync"])
        return None
    
    def get_no_subs_videos(self, channel: str) -> set:
        """Videos confirmed to have no subtitles - skip these."""
        if channel in self.state:
            return set(self.state[channel].get("no_subs", []))
        return set()
    
    def update(self, channel: str, no_subs_ids: list[str] | None = None):
        """Update channel state after sync."""
        if channel not in self.state:
            self.state[channel] = {"no_subs": []}
        
        if no_subs_ids:
            existing_no_subs = set(self.state[channel].get("no_subs", []))
            existing_no_subs.update(no_subs_ids)
            self.state[channel]["no_subs"] = list(existing_no_subs)
        
        self.state[channel]["last_sync"] = datetime.now().isoformat()
        self.save()


def run_ytdlp(args: list[str], capture: bool = True, retry: bool = True) -> str | None:
    """
    Run yt-dlp with arguments and optional retry logic.
    
    Returns stdout if capture=True, "success" if capture=False, None on failure.
    
    Note: yt-dlp returns non-zero exit codes for many non-error conditions
    (e.g., --break-on-reject returns 101). We check for actual output or
    specific error patterns rather than relying on return codes.
    """
    cmd = ["yt-dlp"] + args
    attempts = config.MAX_RETRY_ATTEMPTS if retry else 1
    
    for attempt in range(attempts):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,  # Always capture to check output
                text=True,
                timeout=120,
            )
            
            # Check for output - if we got data, it worked
            if capture and result.stdout and result.stdout.strip():
                return result.stdout
            
            # If not capturing, check for catastrophic errors only
            if not capture:
                stderr = result.stderr or ""
                # Real errors (not just warnings)
                if "ERROR:" in stderr or "HTTP Error 4" in stderr:
                    if attempt < attempts - 1:
                        console.print(f"[yellow]yt-dlp error, retrying...[/yellow]")
                        time.sleep(config.RETRY_DELAY_SECONDS)
                        continue
                    return None
                return "success"
            
            # No output - might be expected (no videos in range) or an error
            # Don't retry, just return None
            return None
            
        except subprocess.TimeoutExpired:
            if attempt < attempts - 1:
                console.print(f"[yellow]yt-dlp timeout, retrying in {config.RETRY_DELAY_SECONDS}s...[/yellow]")
                time.sleep(config.RETRY_DELAY_SECONDS)
            else:
                console.print("[yellow]yt-dlp timed out after retries[/yellow]")
                return None
        except FileNotFoundError:
            console.print("[red]yt-dlp not found. Install with: brew install yt-dlp[/red]")
            return None
        except Exception as e:
            if attempt < attempts - 1:
                console.print(f"[yellow]yt-dlp error: {e}, retrying...[/yellow]")
                time.sleep(config.RETRY_DELAY_SECONDS)
            else:
                console.print(f"[red]yt-dlp failed: {e}[/red]")
                return None
    return None


def list_channel_videos(channel: str, since_date: str | None = None) -> list[dict]:
    """
    List videos from a YouTube channel since a given date.
    
    Uses --break-on-reject to stop as soon as it hits a video older than cutoff.
    Videos are returned newest-first, so this is efficient.
    
    Args:
        channel: YouTube channel handle (@name)
        since_date: Cutoff date in YYYYMMDD format. If None, uses BACKFILL_DAYS.
    
    Returns list of {id, title, date} dicts.
    """
    if since_date is None:
        # Default: go back BACKFILL_DAYS
        cutoff = (datetime.now() - timedelta(days=config.BACKFILL_DAYS)).strftime("%Y%m%d")
    else:
        cutoff = since_date
    
    url = f"https://www.youtube.com/{channel}/videos"
    
    output = run_ytdlp([
        "--skip-download",
        "--match-filter", f"upload_date >= {cutoff}",
        "--break-on-reject",
        "--print", "%(id)s|%(title)s|%(upload_date)s",
        url,
    ], retry=False)
    
    if not output:
        return []
    
    videos = []
    for line in output.strip().split("\n"):
        if not line or "|" not in line:
            continue
        parts = line.split("|", 2)
        if len(parts) >= 2:
            videos.append({
                "id": parts[0],
                "title": parts[1] if len(parts) > 1 else "",
                "date": parts[2] if len(parts) > 2 else "",
            })
    
    return videos


def convert_srt_to_md(srt_file: Path) -> Path | None:
    """
    Convert an SRT subtitle file to clean markdown.
    
    Strips timestamps, line numbers, and empty lines.
    Uses atomic write pattern for crash safety.
    
    Returns path to the MD file, or None if conversion failed.
    """
    if not srt_file.exists():
        return None
    
    try:
        srt_content = srt_file.read_text(encoding="utf-8", errors="replace")
        
        # Validate: SRT should have timestamps
        if not re.search(r'\d{2}:\d{2}:\d{2}', srt_content):
            console.print(f"[yellow]Warning: {srt_file.name} doesn't appear to be valid SRT[/yellow]")
            return None
        
        # Remove SRT formatting: line numbers, timestamps, empty lines
        lines = []
        for line in srt_content.split("\n"):
            line = line.strip()
            # Skip line numbers
            if re.match(r'^\d+$', line):
                continue
            # Skip timestamps
            if re.match(r'^\d{2}:\d{2}:\d{2}', line):
                continue
            # Skip empty lines
            if not line:
                continue
            lines.append(line)
        
        if not lines:
            console.print(f"[yellow]Warning: {srt_file.name} has no text content[/yellow]")
            return None
        
        md_content = "\n".join(lines)
        
        # Determine MD filename (strip .en.srt → .md)
        md_file = srt_file.with_suffix(".md")
        if md_file.name.endswith(".en.md"):
            md_file = md_file.with_name(md_file.name.replace(".en.md", ".md"))
        
        # Atomic write: temp file then rename
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(
            dir=srt_file.parent,
            prefix="transcript_",
            suffix=".tmp"
        )
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(md_content)
            Path(temp_path).replace(md_file)
        except Exception:
            Path(temp_path).unlink(missing_ok=True)
            raise
        
        return md_file
        
    except Exception as e:
        console.print(f"[red]Error converting {srt_file.name}: {e}[/red]")
        return None


def find_existing_files(video_id: str, output_dir: Path) -> tuple[Path | None, Path | None]:
    """
    Find existing SRT and MD files for a video.
    
    Returns (srt_file, md_file) - either may be None.
    Handles both old format (no video_id) and new format ([video_id]).
    """
    if not output_dir.exists():
        return None, None
    
    # New format: files contain [video_id] in name
    # Must escape brackets since glob treats [] as character class
    escaped_id = f"[[]{ video_id }[]]"
    srt_files = list(output_dir.glob(f"*{escaped_id}*.srt"))
    md_files = list(output_dir.glob(f"*{escaped_id}*.md"))
    
    # If found with new format, return those
    if srt_files or md_files:
        return (srt_files[0] if srt_files else None, md_files[0] if md_files else None)
    
    # Fallback: search by iterating files (handles old format without video_id)
    # This is slower but reliable for legacy files
    for f in output_dir.iterdir():
        if video_id in f.name:
            if f.suffix == ".srt" or f.name.endswith(".en.srt"):
                return f, f.with_suffix(".md") if f.with_suffix(".md").exists() else None
            if f.suffix == ".md":
                # Find corresponding SRT
                srt = f.with_suffix(".en.srt")
                if not srt.exists():
                    srt = f.with_suffix(".srt")
                return srt if srt.exists() else None, f
    
    return None, None


def download_transcript(video_id: str, output_dir: Path) -> Path | None:
    """
    Get transcript for a video - download if needed, convert SRT to markdown.
    
    Resilient behavior:
    1. If MD already exists → return it (idempotent)
    2. If SRT exists but no MD → convert it (recovery)
    3. If neither exists → download SRT and convert (normal flow)
    
    Returns path to the markdown file, or None if failed.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for existing files
    existing_srt, existing_md = find_existing_files(video_id, output_dir)
    
    # Case 1: MD already exists - we're done
    if existing_md and existing_md.exists():
        return existing_md
    
    # Case 2: SRT exists but no MD - convert it
    if existing_srt and existing_srt.exists():
        console.print(f"  [dim]Converting existing SRT: {existing_srt.name}[/dim]")
        return convert_srt_to_md(existing_srt)
    
    # Case 3: Neither exists - download SRT
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = str(output_dir / f"%(upload_date)s_[{video_id}]_%(title)s")
    
    run_ytdlp([
        "--write-auto-sub",
        "--sub-lang", "en",
        "--skip-download",
        "--sub-format", "srt",
        "-o", output_template,
        url,
    ], capture=False)
    
    # Find the newly downloaded SRT
    srt_file, _ = find_existing_files(video_id, output_dir)
    
    if not srt_file:
        return None
    
    return convert_srt_to_md(srt_file)


def sync_channel(
    channel: str,
    state: SyncState,
    force: bool = False,
) -> dict:
    """
    Sync a single channel - download new transcripts.
    
    Always checks full BACKFILL_DAYS window. Idempotency is achieved by:
    - Filesystem check: skip if MD already exists
    - DB check: skip if already ingested
    - State check: skip videos known to have no subtitles
    
    Returns stats dict.
    """
    stats = {"checked": 0, "new": 0, "skipped": 0, "failed": 0, "no_subs": 0}
    
    # Rate limiting: don't sync same channel multiple times per day
    last_sync = state.get_last_sync(channel)
    if last_sync and not force:
        age = datetime.now() - last_sync
        if age < timedelta(days=config.SYNC_INTERVAL_DAYS):
            console.print(f"[dim]{channel}: synced {age.days}d {age.seconds // 3600}h ago, skipping[/dim]")
            return stats
    
    # Always use full backfill window - idempotency handles duplicates
    since_date = (datetime.now() - timedelta(days=config.BACKFILL_DAYS)).strftime("%Y%m%d")
    console.print(f"[cyan]{channel}[/cyan]: checking {config.BACKFILL_DAYS} days...")
    
    # Get all videos in window
    videos = list_channel_videos(channel, since_date=since_date)
    stats["checked"] = len(videos)
    
    if not videos:
        console.print(f"[dim]{channel}: no videos in date range[/dim]")
        state.update(channel)  # Update last_sync time
        return stats
    
    # Filter out videos known to have no subtitles
    no_subs_known = state.get_no_subs_videos(channel)
    videos_to_process = [v for v in videos if v["id"] not in no_subs_known]
    
    if not videos_to_process:
        console.print(f"[dim]{channel}: {len(videos)} videos, all have no subtitles[/dim]")
        state.update(channel)
        return stats
    
    # Process videos - download_transcript handles idempotency (skips if MD exists)
    output_dir = config.TRANSCRIPTS_DIR / channel
    db = get_db()
    no_subs_ids = []  # Videos confirmed to have no subtitles
    
    for video in videos_to_process:
        try:
            # Check if MD already exists (fast filesystem check)
            _, existing_md = find_existing_files(video["id"], output_dir)
            if existing_md and existing_md.exists():
                stats["skipped"] += 1
                continue
            
            md_file = download_transcript(video["id"], output_dir)
            if md_file and md_file.exists():
                # Ingest into vector DB (idempotent - skips if already ingested)
                chunks = ingest_file(md_file, db)
                if chunks > 0:
                    console.print(f"  [green]✓[/green] {video['title'][:50]}... ({chunks} chunks)")
                    stats["new"] += 1
                else:
                    stats["skipped"] += 1  # Already in DB
            else:
                # No subtitles available for this video
                console.print(f"  [yellow]⚠[/yellow] No transcript: {video['title'][:50]}...")
                no_subs_ids.append(video["id"])
                stats["no_subs"] += 1
        except Exception as e:
            # Exception during processing - will retry next time
            console.print(f"  [red]✗[/red] Error: {video['title'][:30]}... - {e}")
            stats["failed"] += 1
    
    # Update state with newly discovered no-subtitle videos
    state.update(channel, no_subs_ids if no_subs_ids else None)
    
    # Print summary if we processed anything
    if stats["new"] > 0 or stats["skipped"] > 0:
        console.print(f"  → {stats['new']} new, {stats['skipped']} skipped")
    
    return stats


def sync_all(force: bool = False) -> dict:
    """
    Sync all configured channels with parallel listing.
    
    Pipeline:
    1. Repair orphan SRT files (idempotent recovery)
    2. List videos from all channels in parallel
    3. Download and ingest transcripts sequentially per channel
    
    Returns aggregate stats.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Check network connectivity
    if not check_network():
        console.print("[red]No network connectivity. Aborting sync.[/red]")
        return {"error": "no_network", "channels": 0, "checked": 0, "new": 0, "skipped": 0, "failed": 0, "no_subs": 0, "repaired": 0}
    
    # First, repair any orphan SRT files (idempotent recovery)
    repair_stats = repair_orphan_srts(quiet=True)
    if repair_stats["found"] > 0:
        console.print(f"[dim]Repaired {repair_stats['ingested']} orphan SRT files[/dim]")
        console.print()
    
    state = SyncState()
    channels = [(ch, desc) for ch, desc in config.YOUTUBE_CHANNELS]
    
    # Phase 1: Parallel channel listing
    console.print(f"[bold]Listing videos from {len(channels)} channels ({config.PARALLEL_WORKERS} workers)...[/bold]")
    since_date = (datetime.now() - timedelta(days=config.BACKFILL_DAYS)).strftime("%Y%m%d")
    
    channel_videos = {}  # channel -> list of videos
    
    def list_videos_for_channel(channel: str) -> tuple[str, list[dict]]:
        """Worker function for parallel listing."""
        try:
            videos = list_channel_videos(channel, since_date=since_date)
            return channel, videos
        except Exception as e:
            console.print(f"[red]Error listing {channel}: {e}[/red]")
            return channel, []
    
    with ThreadPoolExecutor(max_workers=config.PARALLEL_WORKERS) as executor:
        futures = {executor.submit(list_videos_for_channel, ch): ch for ch, _ in channels}
        for future in as_completed(futures):
            channel, videos = future.result()
            channel_videos[channel] = videos
    
    console.print(f"[dim]Found {sum(len(v) for v in channel_videos.values())} total videos[/dim]")
    console.print()
    
    # Phase 2: Sequential processing per channel (downloads, conversions, ingestion)
    total_stats = {
        "channels": len(channels),
        "checked": 0,
        "new": 0,
        "skipped": 0,
        "failed": 0,
        "no_subs": 0,
        "repaired": repair_stats["ingested"]
    }
    
    for channel, description in channels:
        videos = channel_videos.get(channel, [])
        total_stats["checked"] += len(videos)
        
        if not videos:
            continue
        
        # Rate limiting check
        last_sync = state.get_last_sync(channel)
        if last_sync and not force:
            age = datetime.now() - last_sync
            if age < timedelta(days=config.SYNC_INTERVAL_DAYS):
                console.print(f"[dim]{channel}: synced {age.days}d {age.seconds // 3600}h ago, skipping[/dim]")
                continue
        
        console.print(f"[cyan]{channel}[/cyan]: {len(videos)} videos in window")
        
        # Filter out videos known to have no subtitles
        no_subs_known = state.get_no_subs_videos(channel)
        videos_to_process = [v for v in videos if v["id"] not in no_subs_known]
        
        if not videos_to_process:
            console.print(f"  [dim]All have no subtitles[/dim]")
            state.update(channel)
            continue
        
        # Process videos
        output_dir = config.TRANSCRIPTS_DIR / channel
        db = get_db()
        no_subs_ids = []
        
        for video in videos_to_process:
            try:
                # Check if MD already exists
                _, existing_md = find_existing_files(video["id"], output_dir)
                if existing_md and existing_md.exists():
                    total_stats["skipped"] += 1
                    continue
                
                md_file = download_transcript(video["id"], output_dir)
                if md_file and md_file.exists():
                    chunks = ingest_file(md_file, db)
                    if chunks > 0:
                        console.print(f"  [green]✓[/green] {video['title'][:50]}... ({chunks} chunks)")
                        total_stats["new"] += 1
                    else:
                        total_stats["skipped"] += 1
                else:
                    console.print(f"  [yellow]⚠[/yellow] No transcript: {video['title'][:50]}...")
                    no_subs_ids.append(video["id"])
                    total_stats["no_subs"] += 1
            except Exception as e:
                console.print(f"  [red]✗[/red] Error: {video['title'][:30]}... - {e}")
                total_stats["failed"] += 1
        
        state.update(channel, no_subs_ids if no_subs_ids else None)
    
    return total_stats


def show_status():
    """Show sync status for all channels."""
    state = SyncState()
    
    table = Table(title="YouTube Channel Sync Status")
    table.add_column("Channel", style="cyan")
    table.add_column("Last Sync", style="dim")
    table.add_column("Transcripts", justify="right")
    table.add_column("No Subs", justify="right", style="yellow")
    
    for channel, description in config.YOUTUBE_CHANNELS:
        last_sync = state.get_last_sync(channel)
        no_subs = len(state.get_no_subs_videos(channel))
        
        # Count actual MD files on disk
        channel_dir = config.TRANSCRIPTS_DIR / channel
        md_count = len(list(channel_dir.glob("*.md"))) if channel_dir.exists() else 0
        
        if last_sync:
            age = datetime.now() - last_sync
            if age.days > 0:
                sync_str = f"{age.days}d ago"
            else:
                sync_str = f"{age.seconds // 3600}h ago"
        else:
            sync_str = "never"
        
        table.add_row(channel, sync_str, str(md_count), str(no_subs))
    
    console.print(table)


def repair_orphan_srts(quiet: bool = False) -> dict:
    """
    Find and convert orphan SRT files (SRT without corresponding MD).
    
    Also ingests the newly created MD files into the vector database.
    Called automatically at the start of every sync.
    
    Args:
        quiet: If True, suppress per-file output
    
    Returns stats dict.
    """
    from .ingest import get_db, ingest_file
    
    stats = {"found": 0, "converted": 0, "ingested": 0, "failed": 0}
    
    # Check if transcripts directory exists
    if not config.TRANSCRIPTS_DIR.exists():
        return stats
    
    db = get_db()
    
    if not quiet:
        console.print("[bold]Repairing orphan SRT files...[/bold]")
        console.print()
    
    # Scan all channel directories
    for channel_dir in config.TRANSCRIPTS_DIR.iterdir():
        if not channel_dir.is_dir() or not channel_dir.name.startswith("@"):
            continue
        
        srt_files = list(channel_dir.glob("*.srt"))
        
        for srt_file in srt_files:
            # Determine expected MD filename
            md_name = srt_file.name
            if md_name.endswith(".en.srt"):
                md_name = md_name.replace(".en.srt", ".md")
            else:
                md_name = md_name.replace(".srt", ".md")
            
            md_file = channel_dir / md_name
            
            # If MD doesn't exist, this is an orphan
            if not md_file.exists():
                stats["found"] += 1
                if not quiet:
                    console.print(f"  [cyan]{channel_dir.name}[/cyan]: {srt_file.name[:50]}...")
                
                # Convert SRT to MD
                result_md = convert_srt_to_md(srt_file)
                
                if result_md and result_md.exists():
                    stats["converted"] += 1
                    
                    # Ingest into vector DB
                    try:
                        chunks = ingest_file(result_md, db)
                        if chunks > 0:
                            if not quiet:
                                console.print(f"    [green]✓[/green] Converted and ingested ({chunks} chunks)")
                            stats["ingested"] += 1
                        else:
                            if not quiet:
                                console.print(f"    [yellow]⚠[/yellow] Converted but no chunks")
                    except Exception as e:
                        if not quiet:
                            console.print(f"    [red]✗[/red] Ingest error: {e}")
                        stats["failed"] += 1
                else:
                    if not quiet:
                        console.print(f"    [red]✗[/red] Conversion failed")
                    stats["failed"] += 1
    
    return stats


@click.command()
@click.option("--force", "-f", is_flag=True, help="Force sync all channels")
@click.option("--status", "-s", is_flag=True, help="Show sync status")
@click.option("--add", "-a", help="Add a new channel to track")
@click.option("--channel", "-c", help="Sync only this channel")
def main(force: bool, status: bool, add: str, channel: str):
    """
    Sync YouTube channels - download new transcripts and ingest.
    
    The sync is idempotent and resilient:
    - Automatically repairs orphan SRT files (converts to MD and ingests)
    - Retries failed videos on subsequent syncs
    - Skips videos already successfully ingested
    
    Examples:
    
        # Sync all channels (new videos only)
        python -m src.youtube_sync
        
        # Force re-check all
        python -m src.youtube_sync --force
        
        # Show status
        python -m src.youtube_sync --status
        
        # Sync single channel
        python -m src.youtube_sync --channel @indydevdan
    """
    if status:
        show_status()
        return
    
    if add:
        console.print(
            "[yellow]To add a channel, edit ignored channels.local.json "
            "(copy from channels.local.example.json if needed)[/yellow]"
        )
        console.print(
            f'Add: {{"handle": "{add}", "description": "description here"}}'
        )
        return
    
    if channel:
        state = SyncState()
        stats = sync_channel(channel, state, force)
        console.print()
        console.print(f"[bold]Results:[/bold] {stats['new']} new, {stats['failed']} failed")
        return
    
    # Sync all
    console.print("[bold]YouTube Channel Sync[/bold]")
    console.print()
    
    stats = sync_all(force)
    
    console.print()
    console.print("[bold green]Sync complete![/bold green]")
    console.print(f"  Channels: {stats['channels']}")
    console.print(f"  Videos checked: {stats['checked']}")
    console.print(f"  New transcripts: {stats['new']}")
    if stats.get('repaired', 0) > 0:
        console.print(f"  Repaired: {stats['repaired']}")
    console.print(f"  Failed: {stats['failed']}")


if __name__ == "__main__":
    main()
