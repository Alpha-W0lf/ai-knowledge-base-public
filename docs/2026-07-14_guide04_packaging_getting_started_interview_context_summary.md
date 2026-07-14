# Context: Guide 04 — GETTING_STARTED + INTERVIEW packaging (public AI KB)

**Date:** 2026-07-14  
**Repos:** `ai-knowledge-base-public`  
**Status:** Refined  
**Mode last used:** hub  
**Stage:** Refine context (pass 41)  
**Prioritize SSOT:** `second_brain/docs/2026-07-14_prioritize_next_work_guide04_pass40_fan_in.md`

## Problem

Guides 01–03 shipped retrieval spine, packaging DoD, and public-sibling honesty. Public still lacks root `GETTING_STARTED.md` / `INTERVIEW.md`. Interview FAQ for KB1–5, CE no-lift, sibling vs private, RO MCP is the remaining packaging gap.

## Soft pins (Refine) — eight INTERVIEW themes

| # | Theme (must cover) | Example Q intent |
|---|--------------------|------------------|
| 1 | Fixtures vs BYO live path | Why fixtures are default; when BYO 7-day sync is optional |
| 2 | Public sibling vs private archive | Why scrub is not required for “having a public AI KB” |
| 3 | KB2 RO MCP | Public allowlist; mutation tools private-gated |
| 4 | KB4 embeddings | Why `nomic-embed-text` @ 768 — not Gemma / not mxbai |
| 5 | Hybrid → fusion → CE + degrade | Ranking order; `fusion_degraded` honesty |
| 6 | CE no-lift | Point at `ce_keep_note`; forbid “CE improves relevance” ads |
| 7 | Identity / citations | `source_id` / durable citation — not owner filepaths |
| 8 | Packaging honesty banners | Packaging ≠ v1 complete ≠ private flip ≠ eval-complete |

**Tone:** Concise staff FAQ; ~1–2 Qs per theme; peer AG/Mechanic length is ceiling.

**Private README:** Optional one-line sibling pointer only if still missing — not core DoD (private already has pointer commit `2172f20`).

## Acceptance criteria

- [ ] Root `GETTING_STARTED.md` — `uv sync` → `ollama pull nomic-embed-text` → fixture ingest → search → `src.eval`; BYO advanced section not DoD  
- [ ] Root `INTERVIEW.md` covers all **eight** themes above  
- [ ] README links both  
- [ ] Same-delivery PORTFOLIO_VISION / ARCHITECTURE status honesty  
- [ ] No CE lift ads; no private scrub required claim  
- [ ] No eval golden growth; no tip scrub  

## In scope

Docs + links packaging on public sibling.

## Out of scope

Private tip scrub; CE default flip; eval harness growth; auto-sync on clone; January rewrite; BACKFILL change.

## Prior art (paths only)

- `ai-knowledge-base-public/README.md`  
- `docs/PORTFOLIO_VISION.md`, `docs/ARCHITECTURE.md`, `docs/2026-07-12_ce_keep_note.md`  
- Guide 03 public sibling  
- Peer Mechanic/AG GETTING_STARTED + INTERVIEW  
- Pass 40 fan-in  

## Risks and blast radius

| Risk | Mitigation |
|------|------------|
| CE lift theater | Theme 6 + `ce_keep_note` |
| BYO as default | GETTING_STARTED ceiling = fixtures |
| Eval growth creep | Hard out |

## Edge cases

- Ollama missing  
- Missing `channels.local.json` for BYO  
- Portable MCP cwd  

## Unknowns (post-Refine)

| Unknown | Status |
|---------|--------|
| Exact FAQ prose | Implement craft under eight themes |

## Open decisions (human)

- None material — packaging Guide 04 locked  

## Evidence opened this Refine

- No root GS/INTERVIEW; Guide 03 IMPLEMENTED; private sibling pointer already present  

## Honest readiness

- Ready for Write-dev-guide? **Yes**  
- Not Implement  
