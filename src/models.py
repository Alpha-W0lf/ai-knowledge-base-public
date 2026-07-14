"""
Typed retrieval contracts shared by CLI and MCP.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RankingStage = Literal["vector", "fusion", "ce", "fusion_degraded"]


@dataclass
class RetrievalHit:
    """One ranked chunk returned by the shared retrieval spine."""

    chunk_id: str
    source_id: str
    title: str
    channel: str
    date: str
    text: str
    source_url: str  # durable citation — never absolute owner filepath for public MCP
    fusion_rank: int | None = None
    ranking_stage: RankingStage = "vector"
    retriever_scores: dict[str, float] = field(default_factory=dict)
    rerank_score: float | None = None
    source_type: str = ""
    doc_id: str = ""
    snippet: str = ""

    def __post_init__(self) -> None:
        if not self.snippet and self.text:
            self.snippet = self.text[:500] + ("..." if len(self.text) > 500 else "")

    def to_public_dict(self) -> dict[str, Any]:
        """Serialize for public MCP — never includes filepath."""
        return {
            "chunk_id": self.chunk_id,
            "source_id": self.source_id,
            "title": self.title,
            "channel": self.channel,
            "date": self.date,
            "text": self.text,
            "snippet": self.snippet,
            "source_url": self.source_url,
            "fusion_rank": self.fusion_rank,
            "ranking_stage": self.ranking_stage,
            "retriever_scores": self.retriever_scores,
            "rerank_score": self.rerank_score,
            "source_type": self.source_type,
            "doc_id": self.doc_id,
        }


@dataclass
class RetrievalResult:
    """Envelope around ranked hits plus stage timings."""

    query: str
    mode: str
    ranking_stage: RankingStage
    hits: list[RetrievalHit]
    timings_ms: dict[str, float] = field(default_factory=dict)
    error: str | None = None

    def to_public_dict(self) -> dict[str, Any]:
        payload = {
            "query": self.query,
            "mode": self.mode,
            "ranking_stage": self.ranking_stage,
            "results": [h.to_public_dict() for h in self.hits],
            "count": len(self.hits),
            "timings_ms": self.timings_ms,
        }
        if self.error:
            payload["error"] = self.error
        return payload

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class RetrievalError(Exception):
    """Typed retrieval failure (fail-closed hybrid, version mismatch, etc.)."""

    def __init__(self, message: str, *, code: str = "retrieval_error") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
