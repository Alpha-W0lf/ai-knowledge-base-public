"""Hub-free unit tests for CE keep / justify honesty (Guide 06)."""

from __future__ import annotations

from src.eval import _decide_ce_keep


def _arms(
    *,
    cases: int,
    fusion_hit: float,
    ce_success_cases: int,
    ce_success_hit_at_k: float | None,
) -> tuple[dict, dict]:
    fusion = {"cases": cases, "hit_at_k": fusion_hit}
    ce = {
        "cases": cases,
        "hit_at_k": 1.0,  # attempt/fallback — must be ignored by _decide_ce_keep
        "ce_success_cases": ce_success_cases,
        "ce_success_hit_at_k": ce_success_hit_at_k,
    }
    return fusion, ce


def test_decide_ce_keep_not_measured_when_zero_success():
    fusion, ce = _arms(cases=18, fusion_hit=1.0, ce_success_cases=0, ce_success_hit_at_k=None)
    keep, justify = _decide_ce_keep(fusion, ce)
    assert keep is False
    assert "not measured" in justify.lower()
    assert "0 ranking_stage=ce" in justify


def test_decide_ce_keep_partial_degrade():
    fusion, ce = _arms(cases=18, fusion_hit=1.0, ce_success_cases=10, ce_success_hit_at_k=1.0)
    keep, justify = _decide_ce_keep(fusion, ce)
    assert keep is False
    assert "partial" in justify.lower()


def test_decide_ce_keep_flat_full_ce():
    fusion, ce = _arms(cases=18, fusion_hit=1.0, ce_success_cases=18, ce_success_hit_at_k=1.0)
    keep, justify = _decide_ce_keep(fusion, ce)
    assert keep is False
    assert "lift" in justify.lower() or "no ce-success" in justify.lower()


def test_decide_ce_keep_lift():
    fusion, ce = _arms(cases=18, fusion_hit=0.5, ce_success_cases=18, ce_success_hit_at_k=0.8)
    keep, justify = _decide_ce_keep(fusion, ce)
    assert keep is True
    assert "improved" in justify.lower()


def test_decide_ce_keep_worse():
    fusion, ce = _arms(cases=18, fusion_hit=0.9, ce_success_cases=18, ce_success_hit_at_k=0.5)
    keep, justify = _decide_ce_keep(fusion, ce)
    assert keep is False
    assert "reduced" in justify.lower()


def test_decide_ce_keep_ignores_attempt_hit_at_k():
    """Attempt hit@K=1.0 must not create a keep=true when CE-success is worse."""
    fusion = {"cases": 18, "hit_at_k": 0.5}
    ce = {
        "cases": 18,
        "hit_at_k": 1.0,  # misleading attempt/fallback
        "ce_success_cases": 18,
        "ce_success_hit_at_k": 0.4,
    }
    keep, justify = _decide_ce_keep(fusion, ce)
    assert keep is False
    assert "reduced" in justify.lower()
