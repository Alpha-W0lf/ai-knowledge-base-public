# CE keep / disable note (Guide 01 F1 → Guide 05 growth → Guide 06 measure)

**Date:** 2026-07-17 (Guide 06 CE-effectiveness eval Implement)  
**Repo:** `ai-knowledge-base-public`  
**Prior:** 2026-07-16 Guide 05 (N=18; CE-attempt was 18/18 `fusion_degraded` — not measured)

## Decision

On the committed fixture golden set (**N=18**, `g1`–`g18`), **CE ran successfully** (`ranking_stage=ce` on all cases) but **hit@K lift vs fusion-only was not shown** (`ce_keep=false`). Easy goldens already ceiling fusion at 1.0.

| Metric | Value (2026-07-17 Guide 06) |
|--------|------------------------------|
| `cases` | 18 |
| `fusion.hit_at_k` | **1.0** (18/18) — fusion-only arm |
| CE-attempt `stage_counts` | **`{"ce": 18}`** |
| `ce_success_cases` | **18** |
| `ce_success_hits` | **18** |
| `ce_success_hit_at_k` | **1.0** (CE-success subset only) |
| Attempt/fallback `ce.hit_at_k` | 1.0 (same order possible; **not** used for `ce_keep`) |
| `ce_keep` | **false** |
| `ce_justify` (verbatim) | `No CE-success hit@K lift vs fusion-only on this fixture set; keep CE seam + default-on with honesty (easy goldens / ceiling may apply; not eval-complete).` |

**Vs Guide 05:** That run was **18/18 `fusion_degraded`** (CE load failed; effectiveness not measured). Guide 06 fixed degrade observability + CE-success-gated metrics; with HF MiniLM cache warm, CE load succeeded. Flat CE-success hit@K at the fusion ceiling is honest — **not** a claim of relevance lift.

Lift is **not required** to keep the CE *seam*. Discriminative / hard-negative cases (`neg_at_k` with `forbidden_source_ids`) are soft-pinned in Guide 06 for a **later** guide — **not** shipped here.

- Keep **pluggable CE** wired after fusion (KB5).
- Default `CE_ENABLED=True` remains — **do not flip default without human authorize**.
- On CE failure: `ranking_stage=fusion_degraded` and `RetrievalResult.error` carries `ExcType: message` (≤500 chars).
- **Honesty rule:** do **not** advertise “CE improves relevance”; report **CE-success** metrics, not attempt/fallback alone.
- Unrelated: embeddings stay **`nomic-embed-text`**.

Run: `uv run python -m src.eval` (temp LanceDB; needs Ollama + HF MiniLM for CE).
