# Retrieval eval: pre-registration v2 (2026-10-18)

Written before any run on the v2 held-out set. The dataset hashes below fix the data; every results file records the same hashes, so anyone can check a result against this registration. Results produced before the public snapshot label their `git_sha` as pre-release history. This version supersedes an earlier internal version. A later change to the data or criteria gets a new version file.

## Data

| File | What it is | SHA-256 |
|---|---|---|
| `evals/corpus/manifest.json` | 48 synthetic docs in 12 look-alike clusters of 4 (for example RRF, CombSUM, Borda and weighted fusion), 1.9-2.4k characters each, 2 chunks per doc | `c7027c2e8dfabbdac8db56e52df846b9b904ff14c80f7aa8b999ac41eafd413e` |
| `evals/corpus/docs/*.md` | The 48 docs (hash of the sorted `shasum -a 256` listing) | `ae0d95f54a25b3845d6e0e066f511de39622ffc9dd6fd57d6850e13d8655baff` |
| `evals/dev.jsonl` | 48 queries for development and tuning | `5fb4b85b0041c2e6ff2b258ab1e37a8bdb779b9b74864daafddc912db71607c3` |
| `evals/heldout_v2.jsonl` | 48 queries for reporting only | `b5a3887fe0618b7074d69e0565ca86fee373f56740a23a0e463b8a70f26dd0f0` |

The held-out queries were written blind: a separate agent saw only the 48 docs and these rules, never the dev queries, any results or any code. One query per doc. In each cluster, a seeded shuffle (`random.Random(20261019)`, manifest order) picked 2 docs for a lexical query (a practitioner's keyword query using some of the doc's terms) and 2 for an intent query (the need in plain language, without the doc's method names or distinctive terms). That gives 24 of each. Labels are graded: 2 answers the query, 1 is related (4 labels), anything unlabelled is 0.

Tuning happens on `dev.jsonl` only. Held-out queries never go into code, prompts, thresholds or models.

## Systems (arms)

All arms call `retrieve()` in `src/search.py` with `k=10`, which returns up to 10 distinct documents. Embeddings: `nomic-embed-text` at 768 dimensions through Ollama (digest recorded in the results). Cross-encoder: `cross-encoder/ms-marco-MiniLM-L-6-v2` (revision recorded).

| Arm | How |
|---|---|
| random | Expected metrics over 1,000 seeded shuffles of all 48 docs per query |
| vector | `mode="vector"` |
| keyword | `mode="keyword"` (full-text index) |
| fusion | `mode="hybrid"`, cross-encoder off: vector + keyword merged with RRF (k = 60) |
| **shipped** | `mode="hybrid"`, cross-encoder on: the default pipeline when the `ce` extra is installed. Counted only if every query ran at `ranking_stage="ce"` |

## Metrics

Per query, over the ranked list of distinct documents:

- **hit@1**: the top document has grade 2.
- **MRR@10**: 1 / rank of the first grade-2 document in the top 10, else 0.
- **nDCG@10**: gain 2^grade - 1, discount log2(rank + 1), ideal DCG from all labelled grades for that query.

Means over queries. Confidence intervals for differences between arms: paired bootstrap over queries, 10,000 resamples, seed 0, 95% percentile interval. Latency p50 and p95 of `timings_ms.total_ms` are recorded per arm.

## Criteria (held-out set, shipped pipeline)

| # | Criterion | Pass if |
|---|---|---|
| H1 | Far above chance | shipped minus random is at least 0.30 on nDCG@10 and on hit@1, and the 95% CI lower bound of both differences is above 0 |
| H2 | Quality floor | MRR@10 ≥ 0.70 and nDCG@10 ≥ 0.70 and hit@1 ≥ 0.60 |
| H3 | Beats each single leg | shipped nDCG@10 ≥ both vector-only and keyword-only nDCG@10 (point estimates). "Beats each leg" with statistical support is claimed only if both paired CI lower bounds are above 0 |

Each criterion is computed exactly as defined here by `python -m src.eval` and recorded in the results file with the commit, model IDs and dataset hashes.

## Regression gate (CI)

CI has no Ollama and installs no cross-encoder, so it runs the offline stub embedder (`stub-hash@768`) and the fusion arm on both query files. On pull requests that touch ranking code, the corpus or the eval, it fails if any dataset hash differs from `evals/baseline/stub-hash@768.json`, or if any fusion metric (MRR@10, nDCG@10, hit@1) on either file is more than 0.02 below that baseline.
