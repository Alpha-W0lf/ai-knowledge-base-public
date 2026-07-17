# CE keep / disable note (Guide 01 F1 → Guide 05 growth → Guide 06 measure → Guide 07 hard-neg)

**Date:** 2026-07-17 (Guide 07 hard-negative / `neg_at_k` Implement)  
**Repo:** `ai-knowledge-base-public`  
**Prior:** 2026-07-17 Guide 06 (CE-success measured; flat hit@K; no hard-neg cases)

## Decision

On the committed fixture golden set (**18 easy** `g1`–`g18` + **6 hard-negative** `hn1`–`hn6`), **CE ran successfully** on easy cases (`ranking_stage=ce` on all 18) but **hit@K lift vs fusion-only was not shown** (`ce_keep=false`). Easy goldens already ceiling fusion at 1.0. Hard-neg `neg_at_k` is reported **per arm** and does **not** drive `ce_keep`.

| Metric | Value (2026-07-17 Guide 07) |
|--------|------------------------------|
| `cases` (total goldens) | **24** (18 easy + 6 hard-neg) |
| `easy_cases` | **18** |
| `hard_negative_cases` | **6** |
| `fusion.hit_at_k` | **1.0** (18/18 easy) — fusion-only arm |
| `fusion.neg_at_k` | **0.0** (0/6 `neg_ok`) |
| CE-attempt easy `stage_counts` | **`{"ce": 18}`** |
| `ce_success_cases` | **18** (easy + `ranking_stage=ce` only) |
| `ce_success_hits` | **18** |
| `ce_success_hit_at_k` | **1.0** (CE-success subset only) |
| Attempt/fallback `ce.hit_at_k` | 1.0 over easy (same order possible; **not** used for `ce_keep`) |
| `ce.neg_at_k` | **0.0** (0/6 `neg_ok`) — **no** hard-neg rejection lift vs fusion |
| `ce_keep` | **false** |
| `ce_justify` (verbatim) | `No CE-success hit@K lift vs fusion-only on this fixture set; keep CE seam + default-on with honesty (easy goldens / ceiling may apply; not eval-complete).` |

**B2 spot-check (mandatory):** All **6/6** hard-neg queries returned at least one forbidden `source_id` under hybrid fusion (`ce_enabled=False`) before shipping — traps are discriminative, not trivial “already clean” rows. CE also left forbidden ids in top-K on all six (`neg_at_k` flat at 0.0). That is honest: **do not** advertise CE hard-neg lift from this run.

**Vs Guide 06:** Easy hit@K / CE-success / `ce_keep` math unchanged in meaning. Guide 07 adds `kind: hard_negative` + `forbidden_source_ids`, excludes hard-neg from hit@K **and** CE-success/`_decide_ce_keep` denominators, and reports per-arm `neg_at_k`.

- Keep **pluggable CE** wired after fusion (KB5).
- Default `CE_ENABLED=True` remains — **do not flip default without human authorize**.
- On CE failure: `ranking_stage=fusion_degraded` and `RetrievalResult.error` carries `ExcType: message` (≤500 chars).
- **Honesty rule:** do **not** advertise “CE improves relevance”; report **CE-success** hit@K and separately report `neg_at_k`. **`ce_keep` is never flipped by `neg_at_k` alone.**
- Unrelated: embeddings stay **`nomic-embed-text`**.

Run: `uv run python -m src.eval` (temp LanceDB; needs Ollama + HF MiniLM for CE).
