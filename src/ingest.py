"""
Document ingestion pipeline for the knowledge base.

Owns chunking, identity, content_hash, table writes, and FTS ensure.
Uses LanceDB's built-in Ollama integration for automatic embedding (lazy schema).
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import lancedb
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import config
from .identity import (
    check_embedding_version,
    content_hash,
    load_fixture_manifest,
    normalize_text,
    resolve_source_identity,
)

console = Console()


def get_db(db_path: Path | None = None) -> lancedb.DBConnection:
    """Get or create the LanceDB connection."""
    path = Path(db_path) if db_path else config.LANCEDB_DIR
    path.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(str(path))


def table_exists(db: lancedb.DBConnection, table_name: str) -> bool:
    """Check if a table exists in the database."""
    tables = db.list_tables()
    return table_name in tables.tables


class FTSIndexError(RuntimeError):
    """Raised when FTS cannot be ensured — hybrid must fail closed."""


def ensure_fts_index(db: lancedb.DBConnection, table_name: str = "transcripts") -> None:
    """
    Create/ensure FTS index on text column.

    Raises FTSIndexError if table missing or FTS cannot be ensured.
    Hybrid search must call this and fail closed on error.
    """
    if not table_exists(db, table_name):
        raise FTSIndexError(
            f"Table {table_name!r} missing — cannot ensure FTS. Ingest fixtures/docs first."
        )

    table = db.open_table(table_name)
    try:
        table.create_fts_index("text", replace=True)
    except Exception as e:
        msg = str(e).lower()
        if "already exists" in msg:
            return
        raise FTSIndexError(
            f"Failed to ensure FTS index on {table_name}.text: {e}. "
            "Rebuild the index or re-ingest, then retry hybrid search."
        ) from e


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    """
    Split text into overlapping chunks.

    Handles both paragraph-based text (double newlines) and
    transcript-style text (single newlines between lines).
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    text = normalize_text(text)

    if "\n\n" in text:
        segments = re.split(r"\n\s*\n", text)
    else:
        lines = text.split("\n")
        segments = []
        for i in range(0, len(lines), 5):
            segment = "\n".join(lines[i : i + 5])
            if segment.strip():
                segments.append(segment.strip())

    chunks: list[str] = []
    current_chunk = ""

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        if len(segment) > chunk_size:
            words = segment.split()
            sub_chunk = ""
            for word in words:
                if len(sub_chunk) + len(word) + 1 > chunk_size and sub_chunk:
                    chunks.append(sub_chunk.strip())
                    if overlap > 0 and len(sub_chunk) > overlap:
                        sub_chunk = sub_chunk[-overlap:] + " " + word
                    else:
                        sub_chunk = word
                else:
                    sub_chunk = sub_chunk + " " + word if sub_chunk else word
            if sub_chunk.strip():
                segment = sub_chunk.strip()
            else:
                continue

        if len(current_chunk) + len(segment) + 2 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + "\n\n" + segment
            else:
                current_chunk = segment
        else:
            if current_chunk:
                current_chunk += "\n\n" + segment
            else:
                current_chunk = segment

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def parse_transcript_metadata(filepath: Path) -> dict:
    """
    Extract metadata from transcript filename and path.

    Expected format: @channel/YYYYMMDD_[video_id]_title.md
    """
    filename = filepath.stem
    channel = filepath.parent.name

    date_match = re.match(r"^(\d{8})_(.+)$", filename)
    if date_match:
        date_str = date_match.group(1)
        title = date_match.group(2)
        try:
            date = datetime.strptime(date_str, "%Y%m%d").isoformat()
        except ValueError:
            date = None
    else:
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})_(.+)$", filename)
        if date_match:
            date_str = date_match.group(1)
            title = date_match.group(2)
            date = date_str
        else:
            date = None
            title = filename

    # Strip [video_id] from title display if present
    title = re.sub(r"\[[A-Za-z0-9_-]{11}\]_?", "", title).strip("_ ").strip()

    return {
        "channel": channel,
        "title": title,
        "date": date or "",
        "source": "youtube",
        "filepath": str(filepath),
    }


def delete_chunks_for_source(
    db: lancedb.DBConnection,
    source_id: str,
    table_name: str = "transcripts",
) -> int:
    """Delete all chunks for a source_id. Returns rows removed (best-effort count)."""
    if not table_exists(db, table_name):
        return 0
    table = db.open_table(table_name)
    try:
        before = table.count_rows()
    except Exception:
        before = None
    # LanceDB delete uses SQL-like filter; source_id is controlled id (fixture:/video id)
    safe_id = source_id.replace("'", "''")
    table.delete(f"source_id = '{safe_id}'")
    if before is None:
        return 0
    try:
        return max(0, before - table.count_rows())
    except Exception:
        return 0


def source_content_hash(
    db: lancedb.DBConnection,
    source_id: str,
    table_name: str = "transcripts",
) -> str | None:
    """Return stored content_hash for source_id, or None if absent."""
    if not table_exists(db, table_name):
        return None
    table = db.open_table(table_name)
    df = table.to_pandas()
    if "source_id" not in df.columns or df.empty:
        return None
    rows = df[df["source_id"] == source_id]
    if rows.empty:
        return None
    return str(rows.iloc[0].get("content_hash", "")) or None


def assert_table_embedding_version(
    db: lancedb.DBConnection,
    table_name: str = "transcripts",
) -> None:
    """Fail closed if any chunk has mismatched embedding_version."""
    if not table_exists(db, table_name):
        return
    table = db.open_table(table_name)
    df = table.to_pandas()
    # Empty after replace-delete is fine — caller is about to add new chunks.
    if df.empty:
        return
    if "embedding_version" not in df.columns:
        raise ValueError(
            "Index missing embedding_version column. Rebuild LanceDB from files "
            f"(expected {config.EMBEDDING_VERSION})."
        )
    versions = set(df["embedding_version"].dropna().unique().tolist())
    for v in versions:
        check_embedding_version(str(v))


def ingest_file(
    filepath: Path,
    db: lancedb.DBConnection,
    skip_existing: bool = True,
    *,
    source_type: str | None = None,
    source_id: str | None = None,
    title: str | None = None,
    channel: str | None = None,
    date: str | None = None,
    source_url: str | None = None,
) -> int:
    """
    Ingest a single markdown file into the knowledge base.

    Idempotent via source_id + content_hash:
    - same source_id + same hash → skip (if skip_existing)
    - same source_id + different hash → replace chunks
    """
    text = filepath.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return 0

    # Prefer explicit identity; fall back to youtube path metadata for title/date/channel
    meta = {}
    if source_type != "fixture":
        try:
            meta = parse_transcript_metadata(filepath)
        except Exception:
            meta = {}

    identity = resolve_source_identity(
        filepath,
        source_type=source_type,
        source_id=source_id,
        title=title or meta.get("title"),
        channel=channel or meta.get("channel"),
        date=date or meta.get("date"),
        source_url=source_url,
    )

    file_hash = content_hash(text)
    existing_hash = source_content_hash(db, identity["source_id"])

    if existing_hash is not None:
        if skip_existing and existing_hash == file_hash:
            return 0
        # Content changed (or force) → replace chunks for this source_id
        delete_chunks_for_source(db, identity["source_id"])

    chunks = chunk_text(text)
    if not chunks:
        return 0

    records = []
    for i, chunk in enumerate(chunks):
        records.append(
            {
                "id": f"{identity['doc_id']}_{i}",
                "doc_id": identity["doc_id"],
                "chunk_index": i,
                "source_id": identity["source_id"],
                "source_type": identity["source_type"],
                "content_hash": file_hash,
                "embedding_version": config.EMBEDDING_VERSION,
                "text": chunk,
                "channel": identity["channel"],
                "title": identity["title"],
                "date": identity["date"],
                "source": identity["source"],
                "filepath": identity["filepath"],
                "source_url": identity["source_url"],
            }
        )

    table_name = "transcripts"
    from .schema import get_transcript_schema

    schema = get_transcript_schema()

    if table_exists(db, table_name):
        assert_table_embedding_version(db, table_name)
        table = db.open_table(table_name)
        table.add(records)
    else:
        db.create_table(table_name, records, schema=schema)

    return len(records)


def ingest_directory(
    directory: Path,
    incremental: bool = True,
    pattern: str = "**/*.md",
    db_path: Path | None = None,
) -> dict:
    """Ingest all markdown files from a directory (personal / youtube path)."""
    db = get_db(db_path)

    files = list(directory.glob(pattern))
    console.print(f"Found [bold]{len(files)}[/bold] markdown files")

    stats = {"files": 0, "chunks": 0, "skipped": 0}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Ingesting...", total=len(files))

        for filepath in files:
            try:
                chunks = ingest_file(filepath, db, skip_existing=incremental)
                if chunks == 0:
                    stats["skipped"] += 1
                else:
                    stats["files"] += 1
                    stats["chunks"] += chunks
                    progress.update(task, description=f"Ingested: {filepath.name[:40]}...")
            except Exception as e:
                console.print(f"[red]Error ingesting {filepath}: {e}[/red]")

            progress.advance(task)

    if stats["files"] > 0:
        try:
            ensure_fts_index(db)
            console.print("[green]Created/ensured FTS index for hybrid search[/green]")
        except FTSIndexError as e:
            console.print(f"[yellow]FTS ensure failed: {e}[/yellow]")

    return stats


def ingest_fixtures(
    fixtures_dir: Path | None = None,
    db_path: Path | None = None,
    *,
    ensure_fts: bool = True,
) -> dict:
    """
    Ingest allowlisted fixture markdown into a LanceDB (often temp/gitignored).

    Reads only files listed in fixtures/manifest.json under fixtures/transcripts/.
    Does not require personal data/raw/.
    """
    fixtures_dir = Path(fixtures_dir) if fixtures_dir else config.FIXTURES_DIR
    transcripts_dir = fixtures_dir / "transcripts"
    manifest = load_fixture_manifest(fixtures_dir)

    missing = []
    entries = []
    for entry in manifest:
        sid = entry["source_id"]
        # filename: fixture:rag-hooks-01 → rag-hooks-01.md
        slug = sid.removeprefix("fixture:")
        path = transcripts_dir / f"{slug}.md"
        if not path.exists():
            missing.append(str(path))
        else:
            entries.append((path, entry))

    if missing:
        raise FileNotFoundError(
            "Fixture provenance lists files that are missing:\n  - " + "\n  - ".join(missing)
        )

    db = get_db(db_path)
    stats = {"files": 0, "chunks": 0, "skipped": 0}

    for path, entry in entries:
        chunks = ingest_file(
            path,
            db,
            skip_existing=True,
            source_type="fixture",
            source_id=entry["source_id"],
            title=entry.get("title"),
            channel=entry.get("channel", "fixtures"),
            date=entry.get("date", ""),
            source_url=entry.get("url") or entry["source_id"],
        )
        if chunks == 0:
            stats["skipped"] += 1
        else:
            stats["files"] += 1
            stats["chunks"] += chunks

    if ensure_fts and (stats["files"] > 0 or table_exists(db, "transcripts")):
        ensure_fts_index(db)

    return stats


def get_stats(db_path: Path | None = None) -> dict:
    """Get statistics about the knowledge base."""
    db = get_db(db_path)

    if not table_exists(db, "transcripts"):
        return {"documents": 0, "chunks": 0, "channels": []}

    table = db.open_table("transcripts")
    df = table.to_pandas()

    return {
        "documents": df["doc_id"].nunique() if "doc_id" in df.columns else 0,
        "chunks": len(df),
        "channels": df["channel"].unique().tolist() if "channel" in df.columns else [],
        "source_ids": (
            df["source_id"].nunique() if "source_id" in df.columns else 0
        ),
    }


# CLI entry point
if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    if args and args[0] in {"--fixtures", "fixtures"}:
        out = Path(args[1]) if len(args) > 1 else None
        stats = ingest_fixtures(db_path=out)
        console.print()
        console.print("[bold green]Fixture ingestion complete![/bold green]")
        console.print(f"  Files: {stats['files']}")
        console.print(f"  Chunks: {stats['chunks']}")
        console.print(f"  Skipped: {stats['skipped']}")
        sys.exit(0)

    if not args:
        directory = config.TRANSCRIPTS_DIR
    else:
        directory = Path(args[0])

    if not directory.exists():
        console.print(f"[red]Directory not found: {directory}[/red]")
        sys.exit(1)

    stats = ingest_directory(directory)

    console.print()
    console.print("[bold green]Ingestion complete![/bold green]")
    console.print(f"  Files: {stats['files']}")
    console.print(f"  Chunks: {stats['chunks']}")
    console.print(f"  Skipped: {stats['skipped']}")
