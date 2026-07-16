# CE keep / disable note (Guide 01 F1 → Guide 05 growth)

**Date:** 2026-07-16 (Guide 05 eval golden growth; Review honesty fix)  
**Repo:** `ai-knowledge-base-public`  
**Prior:** 2026-07-12 Guide 01 F1 (N=6)

## Decision

On the committed fixture golden set (**N=18**, `g1`–`g18`), **hit@K lift from local CE vs fusion-only was not shown** (`ce_keep=false`).

| Metric | Value (2026-07-16) |
|--------|---------------------|
| `cases` | 18 |
| `fusion.hit_at_k` | **1.0** (18/18) — fusion-only arm |
| CE-attempt arm | **18/18** `ranking_stage=fusion_degraded` (CE load/score failed open to fusion order) |
| Successful CE-ranked cases | **0** — CE effectiveness was **not measured** on this run |
| Reported `ce.hit_at_k` | 1.0 equals fusion fallback, **not** successful CE rerank |
| `ce_keep` | **false** |
| `ce_justify` (verbatim) | `No hit@K lift vs fusion-only on this tiny fixture set; keep CE seam + default-on for portfolio demos only with this note (identity/adapter path validated; lift TBD on larger eval).` |

Lift is **not required** to keep the CE *seam*. The adapter + `ranking_stage` provenance + degrade path remain the architecture DoD. Larger N improves measurement confidence; it does **not** equal “eval-complete” or “CE improves relevance.”

- Keep **pluggable CE** wired after fusion (KB5).
- Default `CE_ENABLED=True` remains for demo of the full spine when `sentence-transformers` + model load succeed — **do not flip default without human authorize**.
- **Honesty rule:** do **not** advertise “CE improves relevance”; do **not** shorthand “CE hit@K=1.0” without stating the arm degraded to fusion.
- Unrelated: embeddings stay **`nomic-embed-text`**.

Run: `uv run python -m src.eval` (temp LanceDB; needs Ollama + fixtures).
