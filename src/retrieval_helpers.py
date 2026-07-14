"""Small helpers for shared retrieval (fusion + hit mapping)."""

from __future__ import annotations

import pandas as pd

from .models import RankingStage, RetrievalHit


def rrf_fuse(vector_ids: list[str], fts_ids: list[str], *, k: int = 60) -> list[str]:
    """Reciprocal Rank Fusion over stable chunk ids."""
    scores: dict[str, float] = {}
    for rank, cid in enumerate(vector_ids, start=1):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    for rank, cid in enumerate(fts_ids, start=1):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    return sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)


def row_to_hit(
    row: pd.Series,
    *,
    fusion_rank: int | None,
    ranking_stage: RankingStage,
    retriever_scores: dict[str, float] | None = None,
    rerank_score: float | None = None,
) -> RetrievalHit:
    source_id = str(row.get("source_id") or row.get("doc_id") or "")
    source_url = str(row.get("source_url") or source_id)
    if source_url.startswith("/") or (len(source_url) > 1 and source_url[1] == ":"):
        source_url = source_id
    return RetrievalHit(
        chunk_id=str(row.get("id", "")),
        source_id=source_id,
        title=str(row.get("title", "")),
        channel=str(row.get("channel", "")),
        date=str(row.get("date", "") or ""),
        text=str(row.get("text", "")),
        source_url=source_url,
        fusion_rank=fusion_rank,
        ranking_stage=ranking_stage,
        retriever_scores=retriever_scores or {},
        rerank_score=rerank_score,
        source_type=str(row.get("source_type") or row.get("source") or ""),
        doc_id=str(row.get("doc_id", "")),
    )


def dedupe_by_source_id(hits: list[RetrievalHit]) -> list[RetrievalHit]:
    """Keep best chunk per source_id (first wins — callers order best-first)."""
    seen: set[str] = set()
    out: list[RetrievalHit] = []
    for hit in hits:
        key = hit.source_id or hit.doc_id or hit.chunk_id
        if key in seen:
            continue
        seen.add(key)
        out.append(hit)
    return out


def apply_filters(
    df: pd.DataFrame,
    *,
    channel: str | None,
    since: str | None,
) -> pd.DataFrame:
    if df.empty:
        return df
    out = df
    if channel:
        channel_filter = channel if channel.startswith("@") else f"@{channel}"
        out = out[(out["channel"] == channel_filter) | (out["channel"] == channel)]
    if since and "date" in out.columns:
        out = out[out["date"] >= since]
    return out
