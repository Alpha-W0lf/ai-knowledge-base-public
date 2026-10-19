"""
AI Knowledge Base Configuration
"""

from __future__ import annotations

import importlib.util
import json
import os
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

# Embedding settings. AI_KB_EMBEDDINGS picks the embedder:
#   "ollama" (default): nomic-embed-text through a local Ollama server.
#   "stub": a deterministic offline hashing embedder (src/embed.py) for CI and tests.
# The version stamp differs per embedder, so an index built by one is refused by the other.
EMBEDDINGS = os.environ.get("AI_KB_EMBEDDINGS", "ollama").strip().lower() or "ollama"
if EMBEDDINGS not in {"ollama", "stub"}:
    raise ValueError(f"AI_KB_EMBEDDINGS must be 'ollama' or 'stub', got {EMBEDDINGS!r}")
EMBEDDING_MODEL = "nomic-embed-text" if EMBEDDINGS == "ollama" else "stub-hash"
EMBEDDING_DIMENSIONS = 768
EMBEDDING_VERSION = f"{EMBEDDING_MODEL}@{EMBEDDING_DIMENSIONS}"
OLLAMA_BASE_URL = "http://localhost:11434"

# Chunking settings
CHUNK_SIZE = 1500  # characters per chunk
CHUNK_OVERLAP = 200  # overlap between chunks

# Search settings: fused shortlist N into the cross-encoder, K results returned
RETRIEVAL_N = 30  # fused shortlist size into CE (clamp 20–50)
RETRIEVAL_K = 8  # return size (clamp 5–10)
# Cross-encoder rerank after fusion: on by default when the `ce` extra is installed.
# AI_KB_CE=0 turns it off, AI_KB_CE=1 forces it on. Without the extra, search runs fusion.
_CE_ENV = os.environ.get("AI_KB_CE", "").strip().lower()
if _CE_ENV:
    CE_ENABLED = _CE_ENV in {"1", "true", "yes", "on"}
else:
    CE_ENABLED = importlib.util.find_spec("sentence_transformers") is not None
CE_MODEL_ID = "cross-encoder/ms-marco-MiniLM-L-6-v2"
# Pinned Hugging Face commit, so later loads need no network check.
CE_MODEL_REVISION = "233902d25c440f23af6f7d6e94d2946bac0bee0a"

# YouTube sync settings
SYNC_INTERVAL_DAYS = 1  # Minimum days between syncs per channel
BACKFILL_DAYS = 7  # Days of history per channel on first sync; raise for a deeper backfill
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
                f"Channel overlay {path}: entry [{i}] must be an object, got {type(item).__name__}"
            )
        handle = item.get("handle")
        description = item.get("description", "")
        if not isinstance(handle, str) or not handle.strip():
            raise ValueError(
                f'Channel overlay {path}: entry [{i}] requires non-empty string "handle"'
            )
        if description is None:
            description = ""
        if not isinstance(description, str):
            raise ValueError(
                f'Channel overlay {path}: entry [{i}] "description" must be '
                f"a string, got {type(description).__name__}"
            )
        key = handle.strip().casefold()
        if key in seen:
            continue
        seen.add(key)
        channels.append((handle.strip(), description))
    return channels


# Public committed default: empty. Personal list → git-ignored channels.local.json.
# Format: list of (handle, description) tuples after overlay load.
YOUTUBE_CHANNELS: list[tuple[str, str]] = load_youtube_channels()


def clamp_retrieval_n(n: int | None = None) -> int:
    value = RETRIEVAL_N if n is None else n
    return max(20, min(50, int(value)))


def clamp_retrieval_k(k: int | None = None) -> int:
    value = RETRIEVAL_K if k is None else k
    return max(5, min(10, int(value)))
