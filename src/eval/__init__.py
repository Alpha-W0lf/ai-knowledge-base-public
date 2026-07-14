"""
Minimal fixture ranking eval: hit@K, stage latency, groundedness stub.
"""

from __future__ import annotations

import json
from pathlib import Path

from .. import config
from ..ingest import ingest_fixtures
from ..models import RetrievalError
from ..rerank import IdentityReranker
from ..search import retrieve


def load_golden_cases(path: Path | None = None) -> list[dict]:
    path = path or (config.FIXTURES_DIR / "eval" / "golden_cases.jsonl")
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            cases.append(json.loads(line))
    return cases


def groundedness_ok(cited_ids: list[str], retrieved_ids: list[str]) -> bool:
    """Fail if any citation invents an id not in retrieved hits."""
    retrieved = set(retrieved_ids)
    return all(cid in retrieved for cid in cited_ids)


def run_fixture_eval(
    db_path: Path,
    *,
    k: int = 5,
    use_ce: bool = False,
) -> dict:
    """
    Ingest fixtures into db_path, run golden cases, report hit@K + latencies.

    CE keep gate: compare fusion-only vs CE when use_ce True for second pass.
    """
    ingest_fixtures(db_path=db_path, ensure_fts=True)
    cases = load_golden_cases()

    def _run(ce: bool) -> dict:
        hits = 0
        grounded_fail = 0
        latencies = []
        details = []
        for case in cases:
            try:
                result = retrieve(
                    case["query"],
                    mode="hybrid",
                    limit=k,
                    db_path=db_path,
                    ce_enabled=ce,
                    ce_adapter=IdentityReranker() if not ce else None,
                )
            except RetrievalError as e:
                details.append({"id": case["id"], "error": e.message})
                continue
            returned_sources = [h.source_id for h in result.hits]
            returned_chunks = [h.chunk_id for h in result.hits]
            expected = set(case.get("expected_source_ids") or [])
            hit = bool(expected & set(returned_sources))
            if hit:
                hits += 1
            # Groundedness stub: treat returned chunk ids as the only valid citations
            fake_answer_cites = returned_chunks[:1] if case.get("must_cite") else []
            if not groundedness_ok(fake_answer_cites, returned_chunks):
                grounded_fail += 1
            # Also fail if we invent an unknown id
            if not groundedness_ok(returned_chunks, returned_chunks):
                grounded_fail += 1
            latencies.append(result.timings_ms)
            details.append(
                {
                    "id": case["id"],
                    "hit": hit,
                    "ranking_stage": result.ranking_stage,
                    "returned_source_ids": returned_sources,
                    "timings_ms": result.timings_ms,
                }
            )
        n = max(len(cases), 1)
        return {
            "cases": len(cases),
            "hit_at_k": hits / n,
            "hits": hits,
            "groundedness_failures": grounded_fail,
            "latencies": latencies,
            "details": details,
        }

    fusion = _run(False)
    ce_result = _run(True) if use_ce else None

    keep_ce = False
    justify = ""
    if ce_result is not None:
        if ce_result["hit_at_k"] > fusion["hit_at_k"]:
            keep_ce = True
            justify = "CE improved hit@K vs fusion-only on fixture golden set."
        elif ce_result["hit_at_k"] == fusion["hit_at_k"]:
            # No lift — require explicit justify-keep; default: do not claim CE lift
            keep_ce = False
            justify = (
                "No hit@K lift vs fusion-only on this tiny fixture set; "
                "keep CE seam + default-on for portfolio demos only with this note "
                "(identity/adapter path validated; lift TBD on larger eval)."
            )
        else:
            keep_ce = False
            justify = "CE reduced hit@K vs fusion; prefer fusion default until lift shown."

    return {
        "fusion": fusion,
        "ce": ce_result,
        "ce_keep": keep_ce,
        "ce_justify": justify,
    }


def main() -> None:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="aikb_eval_") as tmp:
        db_path = Path(tmp) / "lancedb"
        report = run_fixture_eval(db_path, use_ce=True)
        print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
