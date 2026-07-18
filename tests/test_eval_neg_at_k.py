"""Hub-free unit tests for hard-negative / neg_at_k (Guide 07 + Guide 08 R1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.eval import (
    _decide_ce_keep,
    is_hard_negative,
    neg_ok,
    run_fixture_eval,
    validate_hard_negatives,
)
from src.models import RetrievalHit, RetrievalResult


def test_is_hard_negative():
    assert is_hard_negative({"kind": "hard_negative"}) is True
    assert is_hard_negative({"kind": "lexical"}) is False


def test_neg_ok_true_when_forbidden_absent():
    assert neg_ok(["fixture:cross-encoder-05"], ["fixture:fusion-rrf-04"]) is True


def test_neg_ok_false_when_forbidden_present():
    assert (
        neg_ok(
            ["fixture:cross-encoder-05"],
            ["fixture:fusion-rrf-04", "fixture:cross-encoder-05"],
        )
        is False
    )


def test_neg_ok_multiple_forbidden_none_allowed():
    assert (
        neg_ok(
            ["fixture:a", "fixture:b"],
            ["fixture:c"],
        )
        is True
    )
    assert (
        neg_ok(
            ["fixture:a", "fixture:b"],
            ["fixture:b"],
        )
        is False
    )


def test_validate_rejects_empty_forbidden():
    with pytest.raises(ValueError, match="non-empty"):
        validate_hard_negatives(
            [
                {
                    "id": "hn_bad",
                    "kind": "hard_negative",
                    "forbidden_source_ids": [],
                }
            ],
            {"fixture:fusion-rrf-04"},
        )


def test_validate_rejects_unknown_forbidden():
    with pytest.raises(ValueError, match="not in fixture manifest"):
        validate_hard_negatives(
            [
                {
                    "id": "hn_bad",
                    "kind": "hard_negative",
                    "forbidden_source_ids": ["fixture:nope"],
                }
            ],
            {"fixture:fusion-rrf-04"},
        )


def test_validate_accepts_good_hard_neg():
    validate_hard_negatives(
        [
            {
                "id": "hn1",
                "kind": "hard_negative",
                "forbidden_source_ids": ["fixture:fusion-rrf-04"],
            },
            {"id": "g1", "kind": "lexical"},
        ],
        {"fixture:fusion-rrf-04"},
    )


def test_decide_ce_keep_uses_easy_cases_not_total():
    """Hard-neg inflated total cases must not force partial-degrade keep false wrongly."""
    fusion = {"easy_cases": 18, "cases": 24, "hit_at_k": 1.0}
    ce = {
        "easy_cases": 18,
        "cases": 24,
        "ce_success_cases": 18,
        "ce_success_hit_at_k": 1.0,
        "hit_at_k": 1.0,
        "neg_at_k": 0.9,  # must be ignored for keep
    }
    keep, justify = _decide_ce_keep(fusion, ce)
    assert keep is False
    assert "lift" in justify.lower() or "no ce-success" in justify.lower()
    assert "partial" not in justify.lower()


def test_decide_ce_keep_ignores_neg_at_k_for_lift():
    fusion = {"easy_cases": 18, "hit_at_k": 1.0}
    ce = {
        "easy_cases": 18,
        "ce_success_cases": 18,
        "ce_success_hit_at_k": 1.0,
        "neg_at_k": 1.0,  # better neg would not matter — hit@K flat
    }
    keep, _ = _decide_ce_keep(fusion, ce)
    assert keep is False


def test_run_fixture_eval_excludes_hard_neg_from_hit_at_k(monkeypatch, tmp_path: Path):
    """Guide 08 R1: hard-neg must not inflate easy hits / hit_at_k (Hub-free)."""
    import src.eval as eval_mod

    cases = [
        {
            "id": "g_easy",
            "query": "easy gold query",
            "expected_source_ids": ["fixture:gold"],
            "must_cite": False,
            "kind": "lexical",
        },
        {
            "id": "hn_trap",
            "query": "hard neg trap",
            "forbidden_source_ids": ["fixture:bad"],
            "must_cite": False,
            "kind": "hard_negative",
        },
    ]

    monkeypatch.setattr(eval_mod, "ingest_fixtures", lambda **_kwargs: {"files": 0})
    monkeypatch.setattr(eval_mod, "load_golden_cases", lambda path=None: cases)
    monkeypatch.setattr(
        eval_mod,
        "load_manifest_source_ids",
        lambda path=None: {"fixture:gold", "fixture:bad"},
    )

    def fake_retrieve(query: str, **_kwargs):
        # Easy: gold hit. Hard-neg: returns forbidden (would corrupt hit@K if counted).
        sid = "fixture:gold" if query.startswith("easy") else "fixture:bad"
        hit = RetrievalHit(
            chunk_id="c1",
            source_id=sid,
            title="t",
            channel="fixtures",
            date="",
            text="x",
            source_url=sid,
        )
        return RetrievalResult(
            query=query,
            mode="hybrid",
            ranking_stage="fusion",
            hits=[hit],
            timings_ms={"total": 1.0},
        )

    monkeypatch.setattr(eval_mod, "retrieve", fake_retrieve)

    report = run_fixture_eval(tmp_path / "db", use_ce=False)
    fusion = report["fusion"]
    assert fusion["easy_cases"] == 1
    assert fusion["hard_negative_cases"] == 1
    assert fusion["hits"] == 1
    assert fusion["hit_at_k"] == 1.0
    assert fusion["neg_ok_count"] == 0
    assert fusion["neg_at_k"] == 0.0
    assert report["ce"] is None
