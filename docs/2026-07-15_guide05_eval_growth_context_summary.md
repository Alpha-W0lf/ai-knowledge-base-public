# Context: Guide 05 — Eval golden growth / CE de-theater

**Date:** 2026-07-15  
**Repos:** `ai-knowledge-base-public`  
**Status:** Refined (pass 59)  
**Mode last used:** hub  
**Prioritize SSOT:** `second_brain/docs/2026-07-15_prioritize_next_work_pass58_fan_in.md`  
**Refine fan-in:** `second_brain/docs/2026-07-15_refine_context_pass59_fan_in.md`  
**Role lens:** AI engineer (RAG evals)

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

- **H-AIKB**
  - Options: (A) authorize Write-dev-guide now; (B) park until AG U4/05a or Vehicle S9; (C) authorize but lower priority than AG after U4.
  - Recommendation: **(A) or (C)** — authorize as **parallel quick win**; if serial capacity is one track, prefer AG 05a after U4 for interview ROI, then AI KB.
  - Reasoning: Fewest blockers (no U4-class source lock); packaging already shipped; eval stub is the honesty gap interviewers will probe next on this repo.
  - Tradeoffs: Dilutes focus if Tom only wants AG Option B; growing N without theme discipline still won’t justify CE lift ads.
- Target N: soft-pin **≥15–20** distinct fixture-grounded cases unless Write-dev-guide inventory says otherwise.

## Evidence opened this pass

- ce_keep_note, PORTFOLIO_VISION, INTERVIEW Theme 6  
- Pass 58; Refine pass 59  

## Honest readiness

- Ready for Write-dev-guide? **Yes** (no hard source lock) — unless human parks H-AIKB.  
- Context quality: sufficient; soft-pin N in Write-dev-guide from fixture inventory.  
