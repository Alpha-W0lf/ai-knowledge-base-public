"""
Retrieval eval over the 48-doc corpus, as pre-registered in evals/PREREGISTRATION_v2.md.

python -m src.eval            run dev + held-out, print the table
python -m src.eval --write             also write evals/results/<date>_<sha>.json (full report)
python -m src.eval --write-baseline    write the CI baseline, evals/baseline/<embedder>.json
python -m src.eval --check             CI gate: fail on a fusion regression vs that baseline
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from .. import config
from ..ingest import ingest_fixtures
from ..models import RetrievalError
from ..rerank import is_ce_available
from ..search import retrieve
from .metrics import METRICS, mean, paired_bootstrap, percentile, random_baseline, score

EVALS_DIR = config.ROOT_DIR / "evals"
CORPUS_DIR = EVALS_DIR / "corpus"
RESULTS_DIR = EVALS_DIR / "results"
BASELINE_DIR = EVALS_DIR / "baseline"
SETS = ("dev", "heldout_v2")
HELDOUT = "heldout_v2"
SHIPPED = "fusion+ce"  # the default pipeline when the ce extra is installed
ARMS = ("random", "vector", "keyword", "fusion", "fusion+ce")
GATE_TOLERANCE = 0.02


def load_queries(name: str) -> list[dict]:
    path = EVALS_DIR / f"{name}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def corpus_ids() -> list[str]:
    manifest = json.loads((CORPUS_DIR / "manifest.json").read_text(encoding="utf-8"))
    return [entry["source_id"] for entry in manifest["fixtures"]]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dataset_hashes() -> dict[str, str]:
    """Hashes exactly as listed in PREREGISTRATION_v2.md (docs = hash of the shasum listing)."""
    listing = "".join(
        f"{_sha256(p.read_bytes())}  {p.relative_to(config.ROOT_DIR).as_posix()}\n"
        for p in sorted((CORPUS_DIR / "docs").glob("*.md"))
    )
    return {
        "corpus_manifest": _sha256((CORPUS_DIR / "manifest.json").read_bytes()),
        "corpus_docs": _sha256(listing.encode()),
        **{name: _sha256((EVALS_DIR / f"{name}.jsonl").read_bytes()) for name in SETS},
    }


def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=config.ROOT_DIR, capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _arm_call(arm: str) -> dict:
    if arm == "vector":
        return {"mode": "vector"}
    if arm == "keyword":
        return {"mode": "keyword"}
    return {"mode": "hybrid", "ce_enabled": arm == "fusion+ce"}


def run_arm(arm: str, queries: list[dict], db_path: Path) -> dict:
    """Per-query metrics for one retrieval arm. Errors score 0 and are listed."""
    rows = []
    for q in queries:
        row: dict = {"id": q["id"], "kind": q["kind"]}
        try:
            result = retrieve(q["query"], k=10, db_path=db_path, **_arm_call(arm))
            ranked = [h.source_id for h in result.hits]
            row.update(stage=result.ranking_stage, top3=ranked[:3])
            row["total_ms"] = result.timings_ms.get("total_ms", 0.0)
        except RetrievalError as e:
            ranked = []
            row.update(stage="error", error=f"{e.code}: {e.message}")
        row["metrics"] = score(ranked, q["relevance"])
        rows.append(row)
    return {"queries": rows}


def summarise(rows: list[dict]) -> dict:
    out = {name: mean([r["metrics"][name] for r in rows]) for name in METRICS}
    times = sorted(r["total_ms"] for r in rows if "total_ms" in r)
    if times:
        out["latency_ms"] = {"p50": percentile(times, 50), "p95": percentile(times, 95)}
    return out


def _per_query(arm: dict, name: str) -> list[float]:
    return [r["metrics"][name] for r in arm["queries"]]


def evaluate_set(name: str, db_path: Path, *, run_ce: bool) -> dict:
    queries = load_queries(name)
    ids = corpus_ids()
    arms: dict[str, dict] = {
        "random": {
            "queries": [
                {"id": q["id"], "kind": q["kind"], "metrics": random_baseline(ids, q["relevance"])}
                for q in queries
            ]
        }
    }
    for arm in ("vector", "keyword", "fusion"):
        arms[arm] = run_arm(arm, queries, db_path)
    ce_status = (
        "not run: sentence-transformers not installed (uv sync --extra ce)"
        if not is_ce_available()
        else "not run: skipped with --no-ce"
    )
    if run_ce:
        arms["fusion+ce"] = run_arm("fusion+ce", queries, db_path)
        stages = {r["stage"] for r in arms["fusion+ce"]["queries"]}
        ce_status = "measured" if stages == {"ce"} else f"not measured: stages {sorted(stages)}"

    summary = {arm: summarise(data["queries"]) for arm, data in arms.items()}
    by_kind = {
        kind: {
            arm: summarise([r for r in data["queries"] if r["kind"] == kind])
            for arm, data in arms.items()
        }
        for kind in ("lexical", "intent")
    }
    pairs = [("fusion", "random"), ("fusion", "vector"), ("fusion", "keyword")]
    if ce_status == "measured":
        pairs += [(SHIPPED, other) for other in ("random", "vector", "keyword", "fusion")]
    comparisons = {
        f"{a} - {b}": {
            metric: paired_bootstrap(_per_query(arms[a], metric), _per_query(arms[b], metric))
            for metric in METRICS
        }
        for a, b in pairs
    }
    return {
        "n": len(queries),
        "summary": summary,
        "by_kind": by_kind,
        "comparisons": comparisons,
        "cross_encoder": ce_status,
        "per_query": {arm: data["queries"] for arm, data in arms.items() if arm != "random"},
    }


def judge_criteria(held: dict) -> dict:
    """H1-H3 from PREREGISTRATION_v2.md, on the held-out set, for the shipped pipeline."""
    if held["cross_encoder"] != "measured":
        status = f"Not measured ({held['cross_encoder']})"
        return {
            "H1 well above chance": status,
            "H2 quality floor": status,
            "H3 beats each leg": status,
        }
    s, c = held["summary"][SHIPPED], held["comparisons"]
    vs_random = c[f"{SHIPPED} - random"]
    h1 = all(
        vs_random[m]["diff"] >= 0.30 and vs_random[m]["ci_low"] > 0 for m in ("ndcg@10", "hit@1")
    )
    h2 = s["mrr@10"] >= 0.70 and s["ndcg@10"] >= 0.70 and s["hit@1"] >= 0.60
    legs = [c[f"{SHIPPED} - {leg}"]["ndcg@10"] for leg in ("vector", "keyword")]
    word = {True: "Pass", False: "Fail"}
    return {
        "H1 well above chance": word[h1],
        "H2 quality floor": word[h2],
        "H3 beats each leg": word[all(leg["diff"] >= 0 for leg in legs)],
        "H3 beats each leg (CI above 0)": "Yes" if all(leg["ci_low"] > 0 for leg in legs) else "No",
    }


def _ollama_digest() -> str:
    if config.EMBEDDINGS != "ollama":
        return "n/a (offline stub)"
    try:
        import httpx

        tags = httpx.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5.0).json()["models"]
        return next(m["digest"] for m in tags if m["name"].split(":")[0] == config.EMBEDDING_MODEL)
    except Exception as e:  # recorded, never silently dropped
        return f"unknown ({type(e).__name__})"


def _ce_revision() -> str:
    from ..rerank import get_default_ce_adapter

    model = getattr(get_default_ce_adapter(), "_model", None)
    inner = getattr(model, "model", None)
    return str(getattr(getattr(inner, "config", None), "_commit_hash", None) or "unknown")


def run_eval(*, run_ce: bool | None = None) -> dict:
    run_ce = is_ce_available() if run_ce is None else run_ce
    with tempfile.TemporaryDirectory(prefix="aikb_eval_") as tmp:
        db_path = Path(tmp) / "lancedb"
        ingest_fixtures(CORPUS_DIR, db_path=db_path, ensure_fts=True)
        sets = {name: evaluate_set(name, db_path, run_ce=run_ce) for name in SETS}
    import lancedb

    return {
        "schema": 1,
        "date": date.today().isoformat(),
        "git_sha": _git("rev-parse", "HEAD"),
        "git_dirty": _git("status", "--porcelain") not in ("", "unknown"),
        "preregistration": "evals/PREREGISTRATION_v2.md",
        "embedder": config.EMBEDDING_VERSION,
        "embedder_digest": _ollama_digest(),
        "cross_encoder_model": config.CE_MODEL_ID,
        "cross_encoder_revision": _ce_revision() if run_ce else "not run",
        "runtime": {"python": platform.python_version(), "lancedb": lancedb.__version__},
        "datasets": dataset_hashes(),
        "criteria": judge_criteria(sets[HELDOUT]),
        "sets": sets,
    }


def baseline_path(embedder: str) -> Path:
    return BASELINE_DIR / f"{embedder}.json"


def baseline_of(report: dict) -> dict:
    """The fields the regression gate compares: dataset hashes and fusion metrics."""
    return {
        "embedder": report["embedder"],
        "git_sha": report["git_sha"],
        "date": report["date"],
        "datasets": report["datasets"],
        "sets": {
            name: {"n": data["n"], "summary": {"fusion": data["summary"]["fusion"]}}
            for name, data in report["sets"].items()
        },
    }


def gate(report: dict, baseline: dict) -> list[str]:
    """Regression gate from PREREGISTRATION_v2.md. Returns failure messages (empty = pass)."""
    failures = [
        f"dataset {key} changed ({baseline['datasets'].get(key)} -> {value}); "
        "register a new version before changing eval data"
        for key, value in report["datasets"].items()
        if baseline["datasets"].get(key) != value
    ]
    for name in SETS:
        now = report["sets"][name]["summary"]["fusion"]
        was = baseline["sets"][name]["summary"]["fusion"]
        for metric in METRICS:
            if now[metric] < was[metric] - GATE_TOLERANCE:
                failures.append(
                    f"{name} fusion {metric} {now[metric]:.3f} is more than "
                    f"{GATE_TOLERANCE} below the committed {was[metric]:.3f}"
                )
    return failures


def gate_table(report: dict, baseline: dict | None) -> str:
    """Fusion metrics now vs the committed baseline (what CI prints)."""
    lines = [
        f"embedder {report['embedder']} | commit {report['git_sha'][:7]}",
        "",
        "| Set | Metric | Now | Baseline |",
        "|---|---|---|---|",
    ]
    for name in SETS:
        now = report["sets"][name]["summary"]["fusion"]
        was = baseline["sets"][name]["summary"]["fusion"] if baseline else {}
        for metric in METRICS:
            ref = f"{was[metric]:.3f}" if metric in was else "-"
            lines.append(f"| {name} | fusion {metric} | {now[metric]:.3f} | {ref} |")
    return "\n".join(lines)


def format_table(report: dict) -> str:
    lines = [
        f"embedder {report['embedder']} | commit {report['git_sha'][:7]}",
        "",
        "| Set | Arm | MRR@10 | nDCG@10 | hit@1 | p50 ms |",
        "|---|---|---|---|---|---|",
    ]
    for name in SETS:
        data = report["sets"][name]
        for arm in ARMS:
            if arm not in data["summary"]:
                continue
            s = data["summary"][arm]
            p50 = f"{s['latency_ms']['p50']:.0f}" if "latency_ms" in s else "-"
            lines.append(
                f"| {name} (n={data['n']}) | {arm} | {s['mrr@10']:.3f} | "
                f"{s['ndcg@10']:.3f} | {s['hit@1']:.3f} | {p50} |"
            )
    lines.append("")
    lines += [f"- {k}: {v}" for k, v in report["criteria"].items()]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="python -m src.eval", description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the full report JSON")
    parser.add_argument("--write-baseline", action="store_true", help="write the CI baseline")
    parser.add_argument("--check", action="store_true", help="fail on regression vs the baseline")
    parser.add_argument("--no-ce", action="store_true", help="skip the cross-encoder arm")
    args = parser.parse_args(argv)

    report = run_eval(run_ce=False if args.no_ce else None)
    base_file = baseline_path(report["embedder"])
    previous = json.loads(base_file.read_text(encoding="utf-8")) if base_file.exists() else None
    print(gate_table(report, previous) if args.check else format_table(report))

    if args.write:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out = RESULTS_DIR / f"{report['date']}_{report['git_sha'][:7]}.json"
        out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        print(f"\nwrote {out.relative_to(config.ROOT_DIR)}")
    if args.write_baseline:
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        base_file.write_text(json.dumps(baseline_of(report), indent=1) + "\n", encoding="utf-8")
        print(f"\nwrote {base_file.relative_to(config.ROOT_DIR)}")

    if args.check:
        rel = base_file.relative_to(config.ROOT_DIR)
        if previous is None:
            print(f"\nGATE FAIL: no committed baseline {rel}")
            return 1
        failures = gate(report, previous)
        for failure in failures:
            print(f"GATE FAIL: {failure}")
        print(f"\ngate vs {rel}: {'FAIL' if failures else 'pass'}")
        return 1 if failures else 0
    return 0
