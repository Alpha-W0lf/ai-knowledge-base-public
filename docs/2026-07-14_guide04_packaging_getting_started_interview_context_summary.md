# Context: Guide 04 — GETTING_STARTED + INTERVIEW packaging (public AI KB)

**Date:** 2026-07-14  
**Repos:** `ai-knowledge-base-public`  
**Status:** Refined (pass 42)  
**Mode last used:** hub  
**Stage:** Refine context (pass 42 — second human-gated pass)  
**Role lens:** AI engineer (portfolio packaging / interview FAQ)  
**Prioritize SSOT:** `second_brain/docs/2026-07-14_prioritize_next_work_guide04_pass40_fan_in.md`

## Problem

Guides 01–03 shipped retrieval spine, packaging DoD, and public-sibling honesty. Public still lacks root **`GETTING_STARTED.md`** / **`INTERVIEW.md`**. README already has a fixture-first Quick Start + MCP section — Guide 04 **extracts and deepens** that into peer-style GS + INTERVIEW (not a new operator path).

## Soft pins (Refine) — eight INTERVIEW themes

| # | Theme (must cover) | Evidence anchors |
|---|--------------------|------------------|
| 1 | Fixtures vs BYO live path | README Quick Start vs Optional BYO; `BACKFILL_DAYS=7` |
| 2 | Public sibling vs private archive | PORTFOLIO_VISION §1–2; private README already points at public |
| 3 | KB2 RO MCP | README MCP allowlist; mutations behind `AI_KB_MCP_PRIVATE=1` |
| 4 | KB4 embeddings | `nomic-embed-text` @ 768 — not Gemma / not mxbai |
| 5 | Hybrid → fusion → CE + degrade | ARCHITECTURE ranking; `fusion_degraded` honesty |
| 6 | CE no-lift | `docs/2026-07-12_ce_keep_note.md` — forbid “CE improves relevance” |
| 7 | Identity / citations | `source_id` / `source_url` — never owner filepaths |
| 8 | Packaging honesty banners | Packaging ≠ v1 complete ≠ private flip ≠ eval-complete |

**Tone / length:** Concise staff FAQ; **~1 Q per theme** (≈8–10 Qs). Ceiling = peer Mechanic INTERVIEW length (~9 sections), not AlphaGuard’s 15+.

**GETTING_STARTED content ceiling (pinned):**

1. `uv sync`  
2. `ollama pull nomic-embed-text`  
3. Fixture ingest  
4. Search smoke  
5. `src.eval` (or documented eval entry)  
6. Footguns: Ollama missing; BYO needs `channels.local.json`  
7. Honesty banner  

BYO YouTube path = **advanced / optional section**, not core DoD steps.

**Private README:** Already has public sibling pointer — **out of DoD** (do not require private edits).

**README after guide:** Link both new root docs; do not delete Quick Start (may thin-duplicate or point to GS).

## Acceptance criteria

- [ ] Root `GETTING_STARTED.md` matching pinned ceiling  
- [ ] Root `INTERVIEW.md` covering all **eight** themes  
- [ ] README links both  
- [ ] Same-delivery `PORTFOLIO_VISION` / `ARCHITECTURE` status honesty (GS/INTERVIEW present; still not claiming eval-complete / private flip)  
- [ ] No CE lift ads; no “scrub private required for public KB” claim  
- [ ] No eval golden growth; no tip scrub; no BACKFILL change  

## In scope

Docs + links packaging on public sibling.

## Out of scope

Private tip scrub; CE default flip; eval harness growth; auto-sync on clone; January rewrite; BACKFILL change; private README edits.

## Prior art (paths only)

- Root `README.md` (Quick Start already present — extract/align)  
- `docs/PORTFOLIO_VISION.md`, `docs/ARCHITECTURE.md`, `docs/2026-07-12_ce_keep_note.md`  
- Guide 03 context/guide  
- Peers: `mechanic_rag/{GETTING_STARTED,INTERVIEW}.md`, `alphaguard/{GETTING_STARTED,INTERVIEW}.md`  
- Private `ai_knowledge_base/README.md` (sibling pointer already present)  
- Pass 40–41 fan-ins  

## Risks and blast radius

| Risk | Mitigation |
|------|------------|
| CE lift theater | Theme 6 + `ce_keep_note` |
| BYO as default | GS ceiling = fixtures |
| Eval growth creep | Hard out |
| README / GS drift | GS must match README fixture commands |
| Overlong INTERVIEW (AG-sized) | Soft ceiling ≈ Mechanic |

## Edge cases

- Ollama missing / wrong model name  
- Missing `channels.local.json` for BYO  
- Portable MCP `cwd` placeholder  
- Stranger clones without network for BYO  

## Unknowns (post–pass 42)

| Unknown | How to resolve | Blocking for Write? |
|---------|----------------|---------------------|
| Exact FAQ prose | Implement craft under eight themes | No |
| Whether README Quick Start remains full copy vs link-only | Write: prefer short README + “see GETTING_STARTED” | No |

## Recommended approach

Extract README Quick Start → `GETTING_STARTED.md`; author `INTERVIEW.md` from eight themes + peer tone; link from README; honesty status lines in VISION/ARCHITECTURE.

## Open decisions (human)

- None material — packaging Guide 04 locked  

## Evidence opened this pass (42)

- Confirmed **no** root GS/INTERVIEW on public sibling  
- README already has fixture-first Quick Start + BYO + MCP sections  
- Private README already points at public sibling  
- Peer INTERVIEW lengths: Mechanic ~9 Qs; AG ~15+ — pin Mechanic-scale  
- `ce_keep_note.md` present on public  

## Honest readiness

- Ready for Write-dev-guide? **Yes**  
- Ready for Implement? **No**  
- Still weak: prose quality only (non-blocking for Write)  
