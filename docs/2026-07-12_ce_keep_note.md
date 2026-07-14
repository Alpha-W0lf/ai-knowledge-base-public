# CE keep / disable note (Guide 01 F1)

**Date:** 2026-07-12  
**Repo:** `ai_knowledge_base`

## Decision

On the committed 6-doc fixture golden set, **hit@K lift from local CE vs fusion-only was not shown** (`ce_keep=false` from `uv run python -m src.eval`). Lift is **not required** to keep the CE *seam*. The adapter + `ranking_stage` provenance + degrade path are the DoD for Guide 01.

- Keep **pluggable CE** wired after fusion (KB5).
- Default `CE_ENABLED=True` remains for demo of the full spine when `sentence-transformers` + model load succeed.
- **Honesty rule:** do **not** advertise “CE improves relevance” in README/VISION/portfolio claims; say CE is optional rerank with measured timings and fusion degrade (`ranking_stage=fusion_degraded` on failure).
- Revisit keep/disable default after a larger eval baseline (numeric p95 still TBD).
- Unrelated: embeddings stay **`nomic-embed-text`** — CE model ≠ embedding model ≠ portfolio chat Gemma (D1).

Run: `uv run python -m src.eval` (temp LanceDB; needs Ollama + fixtures).
