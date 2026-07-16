# CE keep / disable note (Guide 01 F1 → Guide 05 growth)

**Date:** 2026-07-16 (Guide 05 eval golden growth)  
**Repo:** `ai-knowledge-base-public`  
**Prior:** 2026-07-12 Guide 01 F1 (N=6)

## Decision

On the committed fixture golden set (**N=18**, `g1`–`g18`), **hit@K lift from local CE vs fusion-only was not shown** (`ce_keep=false` from `uv run python -m src.eval`).

| Metric | Value (2026-07-16) |
|--------|---------------------|
| `cases` | 18 |
| `fusion.hit_at_k` | **1.0** (18/18) |
| `ce.hit_at_k` | **1.0** (18/18) |
| `ce_keep` | **false** |
| CE path `ranking_stage` | predominantly `fusion_degraded` on this run (CE load/score failed open to fusion order — not an ablation “win”) |

Lift is **not required** to keep the CE *seam*. The adapter + `ranking_stage` provenance + degrade path remain the architecture DoD. Larger N improves measurement confidence; it does **not** equal “eval-complete” or “CE improves relevance.”

- Keep **pluggable CE** wired after fusion (KB5).
- Default `CE_ENABLED=True` remains for demo of the full spine when `sentence-transformers` + model load succeed — **do not flip default without human authorize**.
- **Honesty rule:** do **not** advertise “CE improves relevance” in README/VISION/portfolio claims; say CE is optional rerank with measured timings and fusion degrade (`ranking_stage=fusion_degraded` on failure).
- Unrelated: embeddings stay **`nomic-embed-text`** — CE model ≠ embedding model ≠ portfolio chat Gemma (D1).

Run: `uv run python -m src.eval` (temp LanceDB; needs Ollama + fixtures).
