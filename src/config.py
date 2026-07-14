"""
AI Knowledge Base Configuration
"""

from __future__ import annotations

import json
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
TRANSCRIPTS_DIR = RAW_DIR / "youtube_transcripts"
LANCEDB_DIR = DATA_DIR / "lancedb"
FIXTURES_DIR = ROOT_DIR / "fixtures"
FIXTURES_TRANSCRIPTS_DIR = FIXTURES_DIR / "transcripts"

# Personal channel overlay (ignored by git) — see channels.local.example.json
CHANNELS_LOCAL_PATH = ROOT_DIR / "channels.local.json"

# Embedding settings
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIMENSIONS = 768
EMBEDDING_VERSION = f"{EMBEDDING_MODEL}@{EMBEDDING_DIMENSIONS}"
OLLAMA_BASE_URL = "http://localhost:11434"

# Chunking settings
CHUNK_SIZE = 1500  # characters per chunk
CHUNK_OVERLAP = 200  # overlap between chunks

# Search / retrieval settings (KB5 N→K)
DEFAULT_LIMIT = 10
RETRIEVAL_N = 30  # fused shortlist size into CE (clamp 20–50)
RETRIEVAL_K = 8  # return size (clamp 5–10)
CE_ENABLED = True  # default on when local CE loads; off path must work
CE_MODEL_ID = "cross-encoder/ms-marco-MiniLM-L-6-v2"
# Deprecated as fusion API — not wired to a weighted combiner. Prefer RRF / LanceDB hybrid.
HYBRID_VECTOR_WEIGHT = 0.7

# YouTube sync settings
SYNC_INTERVAL_DAYS = 1  # Minimum days between syncs per channel
BACKFILL_DAYS = 7  # Public demo default; raise locally for deeper BYO backfill
MAX_RETRY_ATTEMPTS = 2  # Retry failed downloads
RETRY_DELAY_SECONDS = 30  # Delay between retries
PARALLEL_WORKERS = 8  # Concurrent channel listings (8-10 is safe, higher may rate-limit)

def load_youtube_channels(
    overlay_path: Path | None = None,
) -> list[tuple[str, str]]:
    """
    Load effective YouTube channels.

    Missing overlay → []. Present + valid → mapped tuples (dedupe by handle,
    case-insensitive, first wins). Present + invalid → fail closed with path.
    """
    path = CHANNELS_LOCAL_PATH if overlay_path is None else Path(overlay_path)
    if not path.is_file():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in channel overlay {path}: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})"
        ) from exc
    except OSError as exc:
        raise ValueError(f"Cannot read channel overlay {path}: {exc}") from exc

    if not isinstance(raw, list):
        raise ValueError(
            f"Channel overlay {path} must be a JSON array of "
            '{"handle": "...", "description": "..."} objects, '
            f"got {type(raw).__name__}"
        )

    channels: list[tuple[str, str]] = []
    seen: set[str] = set()
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(
                f"Channel overlay {path}: entry [{i}] must be an object, "
                f"got {type(item).__name__}"
            )
        handle = item.get("handle")
        description = item.get("description", "")
        if not isinstance(handle, str) or not handle.strip():
            raise ValueError(
                f"Channel overlay {path}: entry [{i}] requires non-empty "
                f'string "handle"'
            )
        if description is None:
            description = ""
        if not isinstance(description, str):
            raise ValueError(
                f"Channel overlay {path}: entry [{i}] \"description\" must be "
                f"a string, got {type(description).__name__}"
            )
        key = handle.strip().casefold()
        if key in seen:
            continue
        seen.add(key)
        channels.append((handle.strip(), description))
    return channels


# Public committed default: empty (KB1). Personal list → ignored channels.local.json.
# Format: list of (handle, description) tuples after overlay load.
YOUTUBE_CHANNELS: list[tuple[str, str]] = load_youtube_channels()


def clamp_retrieval_n(n: int | None = None) -> int:
    value = RETRIEVAL_N if n is None else n
    return max(20, min(50, int(value)))


def clamp_retrieval_k(k: int | None = None) -> int:
    value = RETRIEVAL_K if k is None else k
    return max(5, min(10, int(value)))
