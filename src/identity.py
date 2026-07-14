"""
Identity, content hash, and embedding-version helpers.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from . import config


def normalize_text(text: str) -> str:
    """Normalize text before hashing/chunking (stable fingerprint)."""
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def content_hash(text: str) -> str:
    """SHA-256 of normalized text used for chunking."""
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_doc_id(source_type: str, source_id: str) -> str:
    """
    Deterministic document id from (source_type, source_id).

    Path moves must not change identity. Never hash absolute filepath.
    """
    payload = f"{source_type}:{source_id}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def extract_youtube_video_id(filepath: Path) -> str | None:
    """Extract YouTube video id from filename pattern ..._[VIDEOID]_..."""
    match = re.search(r"\[([A-Za-z0-9_-]{11})\]", filepath.name)
    if match:
        return match.group(1)
    return None


def fixture_source_id_from_path(filepath: Path) -> str:
    """Stable fixture source_id from stem, e.g. rag-hooks-01 → fixture:rag-hooks-01."""
    stem = filepath.stem
    if stem.startswith("fixture:"):
        return stem
    return f"fixture:{stem}"


def resolve_source_identity(
    filepath: Path,
    *,
    source_type: str | None = None,
    source_id: str | None = None,
    title: str | None = None,
    channel: str | None = None,
    date: str | None = None,
    source_url: str | None = None,
) -> dict:
    """
    Resolve stable identity fields for a markdown file.

    For fixtures: source_id = fixture:<slug> (from filename or override).
    For youtube: source_id = 11-char video id from filename; refuse path-hash fallback.
    """
    if source_type is None:
        # Heuristic: under fixtures/ → fixture; else youtube
        parts = {p.lower() for p in filepath.parts}
        source_type = "fixture" if "fixtures" in parts else "youtube"

    if source_type == "fixture":
        sid = source_id or fixture_source_id_from_path(filepath)
        return {
            "source_type": "fixture",
            "source_id": sid,
            "doc_id": compute_doc_id("fixture", sid),
            "channel": channel or "fixtures",
            "title": title or filepath.stem.replace("-", " "),
            "date": date or "",
            "source_url": source_url or sid,
            "filepath": str(filepath),
            "source": "fixture",
        }

    # youtube
    sid = source_id or extract_youtube_video_id(filepath)
    if not sid:
        raise ValueError(
            f"Cannot derive YouTube source_id from filename {filepath.name}. "
            "Expected pattern with [VIDEO_ID]. Path-hash identity is retired."
        )
    return {
        "source_type": "youtube",
        "source_id": sid,
        "doc_id": compute_doc_id("youtube", sid),
        "channel": channel or filepath.parent.name,
        "title": title or filepath.stem,
        "date": date or "",
        "source_url": source_url or f"https://www.youtube.com/watch?v={sid}",
        "filepath": str(filepath),
        "source": "youtube",
    }


def load_fixture_manifest(fixtures_dir: Path | None = None) -> list[dict]:
    """Load fixture provenance entries from PROVENANCE.md JSON block or manifest.json."""
    fixtures_dir = fixtures_dir or config.FIXTURES_DIR
    manifest_path = fixtures_dir / "manifest.json"
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return data["fixtures"] if isinstance(data, dict) and "fixtures" in data else data

    provenance = fixtures_dir / "PROVENANCE.md"
    if not provenance.exists():
        raise FileNotFoundError(
            f"Missing fixture provenance: {manifest_path} or {provenance}"
        )
    # Prefer companion JSON if present; else parse simple table is optional —
    # Implement ships manifest.json for machine use.
    raise FileNotFoundError(
        f"Found {provenance} but no machine-readable {manifest_path}. "
        "Add fixtures/manifest.json listing source_id entries."
    )


def check_embedding_version(stored: str, expected: str | None = None) -> None:
    """Fail closed if stored embedding_version mismatches current config."""
    expected = expected or config.EMBEDDING_VERSION
    if stored != expected:
        raise ValueError(
            f"embedding_version mismatch: index has {stored!r}, "
            f"runtime expects {expected!r}. Rebuild the LanceDB index from files "
            f"(delete derived lancedb dir and re-ingest)."
        )
