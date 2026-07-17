"""
Shared retrieval spine: hybrid → fusion → pluggable CE (N→K).

CLI and MCP must call retrieve() — this module owns ranking policy.

Dedupe policy (named once): dedupe by source_id BEFORE CE for shortlist hygiene,
keeping the best (lowest fusion_rank) chunk per source_id, then take top K after CE/fusion.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Literal

import click
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import config
from .embed import get_embedding
from .ingest import (
    FTSIndexError,
    assert_table_embedding_version,
    ensure_fts_index,
    get_db,
    table_exists,
)
from .models import RankingStage, RetrievalError, RetrievalResult
from .rerank import CrossEncoderAdapter, get_default_ce_adapter
from .retrieval_helpers import apply_filters, dedupe_by_source_id, row_to_hit, rrf_fuse

console = Console()

Mode = Literal["vector", "hybrid"]


def retrieve(
    query: str,
    *,
    mode: Mode = "hybrid",
    limit: int | None = None,
    n: int | None = None,
    k: int | None = None,
    channel: str | None = None,
    since: str | None = None,
    ce_enabled: bool | None = None,
    ce_adapter: CrossEncoderAdapter | None = None,
    db_path: Path | None = None,
    force_ce_failure: bool = False,
) -> RetrievalResult:
    """
    Shared retrieval: vector | hybrid→fusion→optional CE.

    Hybrid fails closed if FTS cannot be ensured.
    CE failure degrades to fused ranks with ranking_stage=fusion_degraded.
    """
    query = (query or "").strip()
    if not query:
        raise RetrievalError("Empty query — provide a non-empty search string.", code="empty_query")

    n_val = config.clamp_retrieval_n(n)
    k_val = config.clamp_retrieval_k(k if k is not None else limit)
    if n_val < k_val:
        raise RetrievalError(
            f"N ({n_val}) must be >= K ({k_val}). Adjust RETRIEVAL_N / RETRIEVAL_K.",
            code="n_lt_k",
        )

    use_ce = config.CE_ENABLED if ce_enabled is None else ce_enabled
    timings: dict[str, float] = {}
    t0 = time.perf_counter()

    db = get_db(db_path)
    if not table_exists(db, "transcripts"):
        raise RetrievalError(
            "No documents in knowledge base. Run fixture or personal ingest first.",
            code="empty_index",
        )

    try:
        assert_table_embedding_version(db)
    except ValueError as e:
        raise RetrievalError(str(e), code="embedding_version_mismatch") from e
    table = db.open_table("transcripts")

    if mode == "vector":
        t_embed = time.perf_counter()
        query_vector = get_embedding(query)
        timings["embed_ms"] = (time.perf_counter() - t_embed) * 1000
        t_ret = time.perf_counter()
        results = table.search(query_vector).limit(max(n_val * 2, k_val * 2)).to_pandas()
        timings["retrieve_ms"] = (time.perf_counter() - t_ret) * 1000
        results = apply_filters(results, channel=channel, since=since)
        hits = [
            row_to_hit(row, fusion_rank=None, ranking_stage="vector")
            for _, row in results.iterrows()
        ]
        hits = dedupe_by_source_id(hits)[:k_val]
        for i, h in enumerate(hits, start=1):
            h.fusion_rank = i
            h.ranking_stage = "vector"
        timings["total_ms"] = (time.perf_counter() - t0) * 1000
        return RetrievalResult(
            query=query,
            mode="vector",
            ranking_stage="vector",
            hits=hits,
            timings_ms=timings,
        )

    # --- hybrid ---
    t_fts = time.perf_counter()
    try:
        ensure_fts_index(db)
    except FTSIndexError as e:
        raise RetrievalError(str(e), code="fts_unavailable") from e
    timings["fts_ensure_ms"] = (time.perf_counter() - t_fts) * 1000

    t_embed = time.perf_counter()
    query_vector = get_embedding(query)
    timings["embed_ms"] = (time.perf_counter() - t_embed) * 1000

    fetch = max(n_val * 2, k_val * 2)
    t_ret = time.perf_counter()
    vector_df = table.search(query_vector).limit(fetch).to_pandas()
    try:
        fts_df = table.search(query, query_type="fts").limit(fetch).to_pandas()
    except Exception as e:
        raise RetrievalError(
            f"FTS query failed after ensure — hybrid fail closed: {e}",
            code="fts_query_failed",
        ) from e
    timings["retrieve_ms"] = (time.perf_counter() - t_ret) * 1000

    vector_df = apply_filters(vector_df, channel=channel, since=since)
    fts_df = apply_filters(fts_df, channel=channel, since=since)

    vector_ids = [str(x) for x in vector_df["id"].tolist()] if not vector_df.empty else []
    fts_ids = [str(x) for x in fts_df["id"].tolist()] if not fts_df.empty else []

    t_fuse = time.perf_counter()
    fused_ids = rrf_fuse(vector_ids, fts_ids)[:n_val]
    timings["fuse_ms"] = (time.perf_counter() - t_fuse) * 1000

    by_id: dict[str, pd.Series] = {}
    for df in (vector_df, fts_df):
        for _, row in df.iterrows():
            by_id[str(row["id"])] = row

    fused_hits = []
    for rank, cid in enumerate(fused_ids, start=1):
        row = by_id.get(cid)
        if row is None:
            continue
        v_score = {}
        if cid in vector_ids:
            v_score["vector_rank"] = float(vector_ids.index(cid) + 1)
        if cid in fts_ids:
            v_score["fts_rank"] = float(fts_ids.index(cid) + 1)
        fused_hits.append(
            row_to_hit(
                row,
                fusion_rank=rank,
                ranking_stage="fusion",
                retriever_scores=v_score,
            )
        )

    fused_hits = dedupe_by_source_id(fused_hits)[:n_val]
    for i, h in enumerate(fused_hits, start=1):
        h.fusion_rank = i

    stage: RankingStage = "fusion"
    final_hits = fused_hits[:k_val]
    error: str | None = None

    if use_ce:
        adapter = ce_adapter if ce_adapter is not None else get_default_ce_adapter()
        t_ce = time.perf_counter()
        try:
            if force_ce_failure:
                raise RuntimeError("forced CE failure for tests")
            reranked = adapter.rerank(query, list(fused_hits))
            final_hits = reranked[:k_val]
            for h in final_hits:
                h.ranking_stage = "ce"
            stage = "ce"
            error = None
        except Exception as e:
            final_hits = fused_hits[:k_val]
            for h in final_hits:
                h.ranking_stage = "fusion_degraded"
                h.rerank_score = None
            stage = "fusion_degraded"
            msg = f"{type(e).__name__}: {e}"
            error = msg if len(msg) <= 500 else msg[:497] + "..."
        timings["ce_ms"] = (time.perf_counter() - t_ce) * 1000
    else:
        for h in final_hits:
            h.ranking_stage = "fusion"
        stage = "fusion"
        error = None

    timings["total_ms"] = (time.perf_counter() - t0) * 1000
    return RetrievalResult(
        query=query,
        mode="hybrid",
        ranking_stage=stage,
        hits=final_hits,
        timings_ms=timings,
        error=error,
    )


def search(
    query: str,
    limit: int = None,
    hybrid: bool = False,
    channel: str = None,
    since: str = None,
    db_path: Path | None = None,
    ce_enabled: bool | None = None,
) -> pd.DataFrame:
    """
    Backward-compatible DataFrame wrapper over shared retrieve().

    `--hybrid` is real hybrid+fusion(+CE per config), not a no-op.
    """
    mode: Mode = "hybrid" if hybrid else "vector"
    try:
        result = retrieve(
            query,
            mode=mode,
            limit=limit,
            channel=channel,
            since=since,
            db_path=db_path,
            ce_enabled=ce_enabled if hybrid else False,
        )
    except RetrievalError as e:
        console.print(f"[red]{e.message}[/red]")
        return pd.DataFrame()

    if not result.hits:
        return pd.DataFrame()

    rows = []
    for h in result.hits:
        rows.append(
            {
                "id": h.chunk_id,
                "doc_id": h.doc_id,
                "source_id": h.source_id,
                "title": h.title,
                "channel": h.channel,
                "date": h.date,
                "text": h.text,
                "source_url": h.source_url,
                "source_type": h.source_type,
                "fusion_rank": h.fusion_rank,
                "ranking_stage": h.ranking_stage,
                "rerank_score": h.rerank_score,
            }
        )
    return pd.DataFrame(rows)


def format_results(results: pd.DataFrame, show_text: bool = True) -> None:
    """Pretty print search results."""
    if results.empty:
        console.print("[yellow]No results found.[/yellow]")
        return

    for _, row in results.iterrows():
        title = str(row.get("title", "Unknown"))[:60]
        channel = row.get("channel", "Unknown")
        date = str(row.get("date", "") or "")[:10]
        stage = row.get("ranking_stage", "")
        source_id = row.get("source_id", "")
        header = f"[bold cyan]{channel}[/bold cyan] | {date} | {source_id} | {stage}"
        console.print()
        console.print(Panel(Text(title, style="bold"), subtitle=header, border_style="dim"))
        if show_text:
            text = str(row.get("text", ""))
            if len(text) > 500:
                text = text[:500] + "..."
            console.print(f"[dim]{text}[/dim]")


@click.command()
@click.argument("query")
@click.option("--limit", "-n", default=None, type=int, help="Number of results (K)")
@click.option("--hybrid", "-h", is_flag=True, help="Use hybrid search (vector+FTS+fusion+CE)")
@click.option("--channel", "-c", help="Filter by channel")
@click.option("--since", "-s", help="Filter by date (YYYY-MM-DD)")
@click.option("--brief", "-b", is_flag=True, help="Show titles only")
@click.option("--no-ce", is_flag=True, help="Disable cross-encoder even on hybrid")
@click.option("--db", "db_path", default=None, type=click.Path(), help="Override LanceDB path")
def main(
    query: str,
    limit: int | None,
    hybrid: bool,
    channel: str,
    since: str,
    brief: bool,
    no_ce: bool,
    db_path: str | None,
):
    """Search the AI knowledge base via the shared retrieval spine."""
    console.print(f"[dim]Searching for: {query} (hybrid={hybrid})[/dim]")
    results = search(
        query=query,
        limit=limit,
        hybrid=hybrid,
        channel=channel,
        since=since,
        db_path=Path(db_path) if db_path else None,
        ce_enabled=False if no_ce else None,
    )
    format_results(results, show_text=not brief)
    console.print()
    console.print(f"[dim]Found {len(results)} results[/dim]")


if __name__ == "__main__":
    main()
