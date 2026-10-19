"""
LanceDB schema for transcript chunks.

Ingest computes every vector itself through src/embed.py (the same embedder search
uses for queries), so the schema carries no embedding function and importing or
using it never contacts Ollama.
"""

from __future__ import annotations

from typing import Type

from lancedb.pydantic import LanceModel, Vector

from . import config


def get_transcript_schema() -> Type[LanceModel]:
    """TranscriptChunk schema sized to the configured embedding dimensions."""

    class TranscriptChunk(LanceModel):
        """One chunk of a source document plus its precomputed vector."""

        text: str
        vector: Vector(config.EMBEDDING_DIMENSIONS)

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
        source: str  # same value as source_type
        filepath: str  # local path for private ops only — never public citation
        source_url: str  # durable citation (YouTube URL or fixture id)

    return TranscriptChunk
