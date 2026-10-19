"""
Ranking metrics and paired bootstrap, as defined in evals/PREREGISTRATION_v2.md.

Pure functions over a ranked list of source ids and a {source_id: grade} map.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

K = 10


def hit_at_1(ranked: Sequence[str], relevance: dict[str, int]) -> float:
    return 1.0 if ranked and relevance.get(ranked[0], 0) == 2 else 0.0


def mrr_at_k(ranked: Sequence[str], relevance: dict[str, int], k: int = K) -> float:
    for rank, sid in enumerate(ranked[:k], start=1):
        if relevance.get(sid, 0) == 2:
            return 1.0 / rank
    return 0.0


def _dcg(grades: Sequence[int]) -> float:
    return sum((2**g - 1) / math.log2(rank + 1) for rank, g in enumerate(grades, start=1))


def ndcg_at_k(ranked: Sequence[str], relevance: dict[str, int], k: int = K) -> float:
    ideal = _dcg(sorted(relevance.values(), reverse=True)[:k])
    if ideal == 0:
        return 0.0
    return _dcg([relevance.get(sid, 0) for sid in ranked[:k]]) / ideal


METRICS = {"mrr@10": mrr_at_k, "ndcg@10": ndcg_at_k, "hit@1": hit_at_1}


def score(ranked: Sequence[str], relevance: dict[str, int]) -> dict[str, float]:
    return {name: fn(ranked, relevance) for name, fn in METRICS.items()}


def random_baseline(
    all_ids: Sequence[str], relevance: dict[str, int], *, shuffles: int = 1000, seed: int = 0
) -> dict[str, float]:
    """Expected metrics of a uniformly random order of the whole corpus."""
    rng = random.Random(seed)
    ids = list(all_ids)
    totals = dict.fromkeys(METRICS, 0.0)
    for _ in range(shuffles):
        rng.shuffle(ids)
        for name, value in score(ids, relevance).items():
            totals[name] += value
    return {name: total / shuffles for name, total in totals.items()}


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percentile(sorted_values: Sequence[float], q: float) -> float:
    """Linear-interpolated percentile of an already sorted list, q in [0, 100]."""
    if not sorted_values:
        return 0.0
    pos = (len(sorted_values) - 1) * q / 100.0
    lo = math.floor(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def paired_bootstrap(
    a: Sequence[float], b: Sequence[float], *, resamples: int = 10_000, seed: int = 0
) -> dict[str, float]:
    """Mean of a - b with a 95% percentile CI from resampling queries (pairs kept)."""
    if len(a) != len(b) or not a:
        raise ValueError("paired_bootstrap needs two equal-length, non-empty lists")
    diffs = [x - y for x, y in zip(a, b)]
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples))
    return {
        "diff": mean(diffs),
        "ci_low": percentile(means, 2.5),
        "ci_high": percentile(means, 97.5),
    }
