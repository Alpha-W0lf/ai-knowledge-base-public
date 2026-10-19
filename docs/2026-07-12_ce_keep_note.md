# Cross-encoder decision note

**Started:** 2026-07-12 · **Updated:** 2026-10-19

The cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) runs after RRF fusion and reorders the fused shortlist. It is the default whenever the `ce` extra is installed. With `nomic-embed-text`, it lifts nDCG@10 over fusion alone by +0.047 on the development queries (0.933 to 0.980, 95% CI +0.011 to +0.088) and by +0.011 on the blind held-out queries (0.952 to 0.962, 95% CI −0.016 to +0.040), where the gain is within the interval ([results](../evals/results/2026-10-18_b8ea769.json)). `AI_KB_CE=0` turns it off and `AI_KB_CE=1` forces it on. A light install without the extra runs fusion.

If the reranker fails at query time, search returns the fused order with `ranking_stage=fusion_degraded` and the error message, so callers always know which stage ran. The held-out evaluation of the shipped pipeline is defined in [`evals/PREREGISTRATION_v2.md`](../evals/PREREGISTRATION_v2.md).
