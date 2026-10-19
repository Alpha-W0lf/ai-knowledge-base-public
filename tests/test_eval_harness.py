"""
Eval harness on the real 48-doc corpus (dev set only), with the offline stub embedder.

Covers: registered data hashes, the cross-encoder "not measured" rule, the CI
regression gate, and a deliberate ranking regression that the gate must catch.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

import src.search as search_mod
from src import eval as ev
from src.ingest import ingest_fixtures
from src.rerank import IdentityReranker


@pytest.fixture(scope="module")
def corpus_db(tmp_path_factory) -> Path:
    db_path = tmp_path_factory.mktemp("eval") / "lancedb"
    ingest_fixtures(ev.CORPUS_DIR, db_path=db_path, ensure_fts=True)
    return db_path


def test_eval_data_matches_the_preregistered_hashes():
    registered = set(
        re.findall(r"`([0-9a-f]{64})`", (ev.EVALS_DIR / "PREREGISTRATION_v2.md").read_text())
    )
    assert set(ev.dataset_hashes().values()) == registered


def test_dev_and_heldout_are_disjoint_and_balanced():
    dev, held = ev.load_queries("dev"), ev.load_queries(ev.HELDOUT)
    assert {q["id"] for q in dev}.isdisjoint({q["id"] for q in held})
    for queries in (dev, held):
        assert len(queries) == 48
        assert sum(q["kind"] == "intent" for q in queries) == 24
    ids = set(ev.corpus_ids())
    assert all(set(q["relevance"]) <= ids for q in dev + held)


def test_fusion_is_far_above_random_on_dev(corpus_db: Path):
    report = ev.evaluate_set("dev", corpus_db, run_ce=False)
    s = report["summary"]
    assert s["fusion"]["ndcg@10"] > s["random"]["ndcg@10"] + 0.5
    assert report["cross_encoder"].startswith("not run")
    assert "fusion+ce" not in s


def _ce_set(corpus_db: Path, monkeypatch, adapter) -> dict:
    monkeypatch.setattr(search_mod, "get_default_ce_adapter", lambda: adapter)
    return ev.evaluate_set("dev", corpus_db, run_ce=True)


def test_ce_that_degrades_is_reported_not_measured(corpus_db: Path, monkeypatch):
    class Broken:
        def rerank(self, query, candidates):
            raise RuntimeError("model missing")

    report = _ce_set(corpus_db, monkeypatch, Broken())
    assert report["cross_encoder"] == "not measured: stages ['fusion_degraded']"
    assert "fusion+ce - fusion" not in report["comparisons"]
    assert set(ev.judge_criteria(report).values()) == {
        "Not measured (not measured: stages ['fusion_degraded'])"
    }


def test_criteria_are_judged_on_the_shipped_pipeline(corpus_db: Path, monkeypatch):
    held = _ce_set(corpus_db, monkeypatch, IdentityReranker())  # dev data as stand-in
    assert held["cross_encoder"] == "measured"
    assert "fusion+ce - keyword" in held["comparisons"]
    criteria = ev.judge_criteria(held)
    assert criteria["H1 well above chance"] == "Pass"
    assert criteria["H2 quality floor"] == "Pass"


def test_gate_passes_on_identical_results_and_flags_drops():
    base = {
        "datasets": ev.dataset_hashes(),
        "sets": {
            name: {"summary": {"fusion": {"mrr@10": 0.9, "ndcg@10": 0.9, "hit@1": 0.9}}}
            for name in ev.SETS
        },
    }
    assert ev.gate(copy.deepcopy(base), base) == []

    dropped = copy.deepcopy(base)
    dropped["sets"][ev.HELDOUT]["summary"]["fusion"]["hit@1"] = 0.87
    assert ev.gate(dropped, base) == [
        f"{ev.HELDOUT} fusion hit@1 0.870 is more than 0.02 below the committed 0.900"
    ]

    changed = copy.deepcopy(base)
    changed["datasets"][ev.HELDOUT] = "0" * 64
    assert "register a new version" in ev.gate(changed, base)[0]


def test_committed_baseline_catches_a_reversed_rrf(corpus_db: Path, monkeypatch):
    """A deliberate ranking regression (RRF sorted worst-first) must fail the committed gate."""
    baseline = json.loads(ev.baseline_path("stub-hash@768").read_text())
    real_fuse = search_mod.rrf_fuse
    monkeypatch.setattr(search_mod, "rrf_fuse", lambda v, f: list(reversed(real_fuse(v, f))))
    broken = ev.evaluate_set("dev", corpus_db, run_ce=False)
    report = {"datasets": ev.dataset_hashes(), "sets": {"dev": broken, ev.HELDOUT: broken}}
    failures = ev.gate(report, baseline)
    assert any(f.startswith("dev fusion ndcg@10") for f in failures)
