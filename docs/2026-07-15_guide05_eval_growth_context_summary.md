# Context: Guide 05 — Eval golden growth / CE de-theater

**Date:** 2026-07-15  
**Repos:** `ai-knowledge-base-public`  
**Status:** Refined (pass 59); **authorized 2026-07-16** — eval growth next; keep sophisticated stack + honest eval  
**Locks:** `second_brain/docs/2026-07-16_human_locks_pass60_fan_in.md`

## Problem

Guides 01–04 shipped retrieval spine + packaging (`GETTING_STARTED` / `INTERVIEW`). Eval remains a **fixture golden stub**. `docs/2026-07-12_ce_keep_note.md` records **no hit@K lift** on the tiny set (`ce_keep=false`). PORTFOLIO_VISION forbids marketing CE as proven relevance lift until a **larger eval baseline** exists. Packaging ≠ eval-complete.

## Acceptance criteria

- [ ] Grow fixture golden set to a documented **N** (soft pin in Write-dev-guide; propose ≥15–20 distinct cases unless evidence says otherwise)  
- [ ] Cases cite real fixture text only (no invented corpus facts)  
- [ ] Re-run `uv run python -m src.eval`; refresh honesty for hit@K / CE vs fusion  
- [ ] Update `ce_keep_note` + INTERVIEW / GETTING_STARTED / PORTFOLIO_VISION — still not v1-complete  
- [ ] No CE lift ads unless metrics show lift; flat/negative → keep seam honesty  
- [ ] Doc-only or eval-JSON + docs; no tip scrub; no January rewrite  

## In scope

- Golden growth on **committed fixtures**  
- Eval harness output honesty + ce_keep revisit note  

## Out of scope

- Private archive tip scrub / private remote flip  
- Changing KB4 embedding model  
- Public MCP mutation defaults  
- Claiming eval-complete / portfolio v1 Done  

## Prior art (paths only)

- `docs/2026-07-12_ce_keep_note.md`  
- `docs/PORTFOLIO_VISION.md`  
- `docs/ARCHITECTURE.md` (eval gates)  
- `GETTING_STARTED.md` / `INTERVIEW.md` Theme 6  
- `fixtures/` + `src.eval`  
- Guide 04 packaging guide  

## Risks and blast radius

| Risk | Mitigation |
|------|------------|
| Invented fixture facts | Quote only committed fixture markdown |
| Tiny N still overclaimed as “eval-complete” | Explicit band + honesty banners |
| Flipping CE default without evidence | Require metrics + human if changing default |
| Scope into BYO YouTube eval | Fixtures-first only for this guide |

## Edge cases

- Duplicate questions → unique ids  
- Hard-miss / negative cases if fixture text supports them  
- `fusion_degraded` observation ≠ ablation  
- Ollama missing → document skip vs fail  

## Unknowns

| Unknown | How to resolve | Blocking? |
|---------|----------------|-----------|
| Exact target N and theme mix | Soft-pin in Write-dev-guide from fixture inventory | No for Gather |
| Whether to change CE default after growth | Human after metrics | Yes for default flip only |

## Recommended approach

1. Inventory current goldens + fixture docs.  
2. Write-dev-guide: soft-pin N (propose **≥15–20**), themes, metrics, honesty updates.  
3. Implement eval JSON + docs; stop.  

## Open decisions (human)

- **Plain title:** Should we grow the AI Knowledge Base eval question set next? (id: H-AIKB)
  - In plain terms: Packaging docs are done. The eval set is still a small stub. Growing it means adding more real test questions grounded in the committed fixture docs, then re-running eval so we stay honest about whether the reranker helps.
  - Options: (A) start the next eng guide for eval growth now; (B) park this while AlphaGuard / Vehicle take focus; (C) allow it as a lower-priority parallel track.
  - Recommendation: **(A) or (C)** — allow as a small parallel win; if you can only do one eng track, prefer AlphaGuard’s training-dataset work after the news-source lock.
  - Reasoning: This track has few blockers (no news-source license gate). Packaging is already shipped. The next honesty gap on this repo is “eval is still tiny.”
  - Tradeoffs: Splits attention if you only want AlphaGuard Option B. A larger question count still does **not** let us advertise reranker “lift” unless the metrics show lift.
- Soft target: about **15–20** distinct fixture-grounded cases unless the write-guide inventory says otherwise.

## Evidence opened this pass

- ce_keep_note, PORTFOLIO_VISION, INTERVIEW Theme 6  
- Pass 58; Refine pass 59  

## Honest readiness

- Ready for Write-dev-guide? **Yes.** Soft-pin ~15–20 fixture-grounded cases; keep hybrid + fusion + rerank seam; do not advertise lift without metrics.  
- Context quality: sufficient.  
