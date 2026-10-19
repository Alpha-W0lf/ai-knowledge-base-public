"""Ranking metrics and the paired bootstrap (definitions in evals/PREREGISTRATION_v2.md)."""

from __future__ import annotations

import math

import pytest

from src.eval.metrics import (
    hit_at_1,
    mrr_at_k,
    ndcg_at_k,
    paired_bootstrap,
    percentile,
    random_baseline,
)

REL = {"a": 2, "b": 1}


def test_hit_at_1_needs_a_grade_2_document_first():
    assert hit_at_1(["a", "x"], REL) == 1.0
    assert hit_at_1(["b", "a"], REL) == 0.0  # grade 1 is related, not an answer
    assert hit_at_1([], REL) == 0.0


def test_mrr_uses_first_grade_2_rank_within_10():
    assert mrr_at_k(["x", "b", "a"], REL) == pytest.approx(1 / 3)
    assert mrr_at_k(["x"] * 10 + ["a"], REL) == 0.0


def test_ndcg_is_1_for_the_ideal_order_and_rewards_grades():
    assert ndcg_at_k(["a", "b", "x"], REL) == pytest.approx(1.0)
    swapped = ndcg_at_k(["b", "a"], REL)
    ideal_dcg = 3 / math.log2(2) + 1 / math.log2(3)
    assert swapped == pytest.approx((1 / math.log2(2) + 3 / math.log2(3)) / ideal_dcg)
    assert ndcg_at_k(["x", "y"], REL) == 0.0


def test_random_baseline_matches_chance():
    ids = [f"d{i}" for i in range(48)]
    base = random_baseline(ids, {"d0": 2}, shuffles=4000, seed=1)
    assert base["hit@1"] == pytest.approx(1 / 48, abs=0.01)
    assert random_baseline(ids, {"d0": 2}) == random_baseline(ids, {"d0": 2})  # seeded


def test_paired_bootstrap_is_seeded_and_brackets_the_mean():
    a = [1.0, 0.5, 1.0, 0.0, 1.0, 1.0]
    b = [0.5, 0.5, 0.0, 0.0, 1.0, 0.5]
    r = paired_bootstrap(a, b, resamples=2000)
    assert r == paired_bootstrap(a, b, resamples=2000)
    assert r["ci_low"] <= r["diff"] <= r["ci_high"]
    assert r["diff"] == pytest.approx(2.0 / 6)
    same = paired_bootstrap(a, a, resamples=200)
    assert same == {"diff": 0.0, "ci_low": 0.0, "ci_high": 0.0}


def test_paired_bootstrap_rejects_unpaired_input():
    with pytest.raises(ValueError):
        paired_bootstrap([1.0], [1.0, 0.0])


def test_percentile_interpolates():
    assert percentile([0.0, 1.0], 50) == 0.5
    assert percentile([2.0], 97.5) == 2.0
