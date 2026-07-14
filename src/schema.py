"""
LanceDB schema definitions with lazy embedding wiring.

Importing this module must NOT contact Ollama. Embedding SourceField/VectorField
are attached only when get_transcript_schema() is first called (ingest path).
"""

from __future__ import annotations

from typing import Any, Type

from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

from . import config

_embedding_func = None
_transcript_schema: Type[LanceModel] | None = None


def get_embedding_function():
    """Get the Ollama embedding function from LanceDB registry (contacts Ollama)."""
    return get_registry().get("ollama").create(name=config.EMBEDDING_MODEL)


def _get_func():
    """Lazy initialization of embedding function — not called at import time."""
    global _embedding_func
    if _embedding_func is None:
        _embedding_func = get_embedding_function()
    return _embedding_func


def get_transcript_schema() -> Type[LanceModel]:
    """
    Build TranscriptChunk schema with SourceField/VectorField.

    Call only on ingest / table-create paths that need auto-embedding.
    Status/help/MCP tools that do not embed must not call this.
    """
    global _transcript_schema
    if _transcript_schema is not None:
        return _transcript_schema

    func = _get_func()

    class TranscriptChunk(LanceModel):
        """Schema for transcript chunks with automatic embedding."""

        text: str = func.SourceField()
        vector: Vector(func.ndims()) = func.VectorField()

        # Identifiers
        id: str  # Unique chunk ID: {doc_id}_{chunk_idx}
        doc_id: str  # Deterministic id from (source_type, source_id) — not filepath hash
        chunk_index: int
        source_id: str  # YouTube video ID or fixture:<slug>
        source_type: str  # youtube | fixture
        content_hash: str  # hash of normalized text used for chunking
        embedding_version: str  # e.g. nomic-embed-text@768

        # Metadata
        channel: str
        title: str
        date: str
        source: str  # legacy alias of source_type
        filepath: str  # local path for private ops only — never public citation
        source_url: str  # durable citation (YouTube URL or fixture id)

    _transcript_schema = TranscriptChunk
    return TranscriptChunk


# Back-compat name for callers that historically imported TranscriptChunk.
# Resolving it still contacts Ollama — prefer get_transcript_schema() explicitly.
def __getattr__(name: str) -> Any:
    if name == "TranscriptChunk":
        return get_transcript_schema()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
