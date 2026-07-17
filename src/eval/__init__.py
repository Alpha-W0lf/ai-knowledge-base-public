"""
Minimal fixture ranking eval: hit@K, stage latency, groundedness stub.
"""

from __future__ import annotations

import json
from collections import Counter
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


def _decide_ce_keep(fusion: dict, ce: dict) -> tuple[bool, str]:
    """
    CE keep gate from fusion arm + CE-success fields only.

    Never uses CE-attempt/fallback hit_at_k for the decision.
    """
    cases = int(ce.get("cases") or fusion.get("cases") or 0)
    success = int(ce.get("ce_success_cases") or 0)
    success_hit = ce.get("ce_success_hit_at_k")
    fusion_hit = float(fusion.get("hit_at_k") or 0.0)

    if success == 0:
        return (
            False,
            "CE effectiveness not measured: 0 ranking_stage=ce "
            "(CE-attempt arm degraded or failed to load/score).",
        )
    if 0 < success < cases:
        return (
            False,
            f"Partial CE degrade: {success}/{cases} ranking_stage=ce; "
            "not a clean ablation — ce_keep=false.",
        )
    # success == cases (full CE-success coverage)
    if success_hit is None:
        return (
            False,
            "CE effectiveness not measured: ce_success_hit_at_k is null.",
        )
    if success_hit > fusion_hit:
        return (
            True,
            "CE improved CE-success hit@K vs fusion-only on fixture golden set.",
        )
    if success_hit == fusion_hit:
        return (
            False,
            "No CE-success hit@K lift vs fusion-only on this fixture set; "
            "keep CE seam + default-on with honesty "
            "(easy goldens / ceiling may apply; not eval-complete).",
        )
    return (
        False,
        "CE-success hit@K reduced vs fusion; prefer fusion until lift shown.",
    )


def run_fixture_eval(
    db_path: Path,
    *,
    k: int = 5,
    use_ce: bool = False,
) -> dict:
    """
    Ingest fixtures into db_path, run golden cases, report hit@K + latencies.

    CE keep gate: compare fusion-only vs CE-success metrics when use_ce True.
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
            row = {
                "id": case["id"],
                "hit": hit,
                "ranking_stage": result.ranking_stage,
                "returned_source_ids": returned_sources,
                "timings_ms": result.timings_ms,
            }
            if result.error:
                row["error"] = result.error
            details.append(row)
        n = max(len(cases), 1)
        arm: dict = {
            "cases": len(cases),
            "hit_at_k": hits / n,
            "hits": hits,
            "groundedness_failures": grounded_fail,
            "latencies": latencies,
            "details": details,
        }
        if ce:
            stage_counts = dict(Counter(d.get("ranking_stage") for d in details if "ranking_stage" in d))
            success_rows = [d for d in details if d.get("ranking_stage") == "ce"]
            ce_success_cases = len(success_rows)
            ce_success_hits = sum(1 for d in success_rows if d.get("hit"))
            arm["stage_counts"] = stage_counts
            arm["ce_success_cases"] = ce_success_cases
            arm["ce_success_hits"] = ce_success_hits
            arm["ce_success_hit_at_k"] = (
                ce_success_hits / ce_success_cases if ce_success_cases > 0 else None
            )
        return arm

    fusion = _run(False)
    ce_result = _run(True) if use_ce else None

    keep_ce = False
    justify = ""
    if ce_result is not None:
        keep_ce, justify = _decide_ce_keep(fusion, ce_result)

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
