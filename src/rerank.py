"""
Pluggable cross-encoder (CE) rerank adapter.

Owns query–document scoring on a fused shortlist only.
Must NOT open LanceDB or reimplement hybrid/fusion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from . import config
from .models import RetrievalHit


class CrossEncoderAdapter(Protocol):
    def rerank(self, query: str, candidates: list[RetrievalHit]) -> list[RetrievalHit]:
        """Score (query, passage) pairs; return candidates in new order with rerank_score."""


@dataclass
class IdentityReranker:
    """No-op adapter — preserves fusion order (useful for tests / CE off)."""

    def rerank(self, query: str, candidates: list[RetrievalHit]) -> list[RetrievalHit]:
        return list(candidates)


class LocalCrossEncoder:
    """
    Local sentence-transformers CrossEncoder.

    Default model: cross-encoder/ms-marco-MiniLM-L-6-v2 (config.CE_MODEL_ID).
    """

    def __init__(self, model_id: str | None = None) -> None:
        self.model_id = model_id or config.CE_MODEL_ID
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.model_id)
        return self._model

    def rerank(self, query: str, candidates: list[RetrievalHit]) -> list[RetrievalHit]:
        if not candidates:
            return []
        model = self._load()
        pairs = [(query, c.text) for c in candidates]
        scores = model.predict(pairs)
        ranked = list(candidates)
        for hit, score in zip(ranked, scores):
            hit.rerank_score = float(score)
        ranked.sort(key=lambda h: h.rerank_score if h.rerank_score is not None else 0.0, reverse=True)
        return ranked


_default_adapter: CrossEncoderAdapter | None = None


def get_default_ce_adapter() -> CrossEncoderAdapter:
    """Lazy singleton for the default local CE."""
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = LocalCrossEncoder()
    return _default_adapter


def reset_ce_adapter_for_tests() -> None:
    global _default_adapter
    _default_adapter = None
