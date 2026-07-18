# CE keep / disable note (Guide 01 F1 → … → Guide 08 confusable hard-neg)

**Date:** 2026-07-18 (Guide 08 harder CE-discriminative / confusable fixtures Implement)  
**Repo:** `ai-knowledge-base-public`  
**Prior:** 2026-07-17 Guide 07 (6 hard-neg; fusion/CE `neg_at_k` 0.0; `ce_keep=false`)

## Decision

On the committed fixture golden set (**18 easy** `g1`–`g18` + **10 hard-negative** `hn1`–`hn10`), **CE ran successfully** on easy cases (`ranking_stage=ce` on all 18) but **hit@K lift vs fusion-only was not shown** (`ce_keep=false`). Easy goldens already ceiling fusion at 1.0. Guide 08 added **2** confusable twin fixtures + **4** new hard-neg traps; hard-neg `neg_at_k` remains **flat on both arms** — **no** CE rejection lift. `neg_at_k` is reported **per arm** and does **not** drive `ce_keep`. **Still not eval-complete** (E3 — flat Guide 08 does not auto-check that box).

| Metric | Value (2026-07-18 Guide 08) |
|--------|------------------------------|
| Fixture docs | **8** (KB1 ceiling; +2 confusable twins) |
| `cases` (total goldens) | **28** (18 easy + 10 hard-neg) |
| `easy_cases` | **18** |
| `hard_negative_cases` | **10** |
| `fusion.hit_at_k` | **1.0** (18/18 easy) — fusion-only arm |
| `fusion.neg_at_k` | **0.0** (0/10 `neg_ok`) |
| CE-attempt easy `stage_counts` | **`{"ce": 18}`** |
| `ce_success_cases` | **18** (easy + `ranking_stage=ce` only) |
| `ce_success_hits` | **18** |
| `ce_success_hit_at_k` | **1.0** (CE-success subset only) |
| Attempt/fallback `ce.hit_at_k` | 1.0 over easy (same order possible; **not** used for `ce_keep`) |
| `ce.neg_at_k` | **0.0** (0/10 `neg_ok`) — **no** hard-neg rejection lift vs fusion |
| `ce_keep` | **false** |
| `ce_justify` (verbatim) | `No CE-success hit@K lift vs fusion-only on this fixture set; keep CE seam + default-on with honesty (easy goldens / ceiling may apply; not eval-complete).` |

**New fixtures (Guide 08 B1):** `fixture:combsum-fusion-07` (CombSUM twin of RRF) · `fixture:bi-encoder-rerank-08` (bi-encoder twin of CE).

**B2 spot-check (mandatory — new `hn7`–`hn10`):** All **4/4** new hard-neg queries returned at least one forbidden `source_id` under hybrid fusion (`ce_enabled=False`) before shipping. Prior `hn1`–`hn6` remain fusion-failing on re-eval (10/10 total). CE also left forbidden ids in top-K on all ten (`neg_at_k` flat at 0.0). That is honest: **do not** advertise CE hard-neg lift from this run; **do not** check eval-complete from a flat Guide 08.

**Vs Guide 07:** Easy hit@K / CE-success / `ce_keep` math unchanged. Guide 08 grows confusable corpus + hard-neg band only; harness formula unchanged; R1 Hub-free exclusion smoke added in tests.

- Keep **pluggable CE** wired after fusion (KB5).
- Default `CE_ENABLED=True` remains — **do not flip default without human authorize**.
- On CE failure: `ranking_stage=fusion_degraded` and `RetrievalResult.error` carries `ExcType: message` (≤500 chars).
- **Honesty rule:** do **not** advertise “CE improves relevance”; report **CE-success** hit@K and separately report `neg_at_k`. **`ce_keep` is never flipped by `neg_at_k` alone.**
- Unrelated: embeddings stay **`nomic-embed-text`**.

Run: `uv run python -m src.eval` (temp LanceDB; needs Ollama + HF MiniLM for CE).
