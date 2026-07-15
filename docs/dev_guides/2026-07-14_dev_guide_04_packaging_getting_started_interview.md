# Dev Guide 04 — GETTING_STARTED + INTERVIEW packaging (public AI KB)

**Date:** 2026-07-14  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 04 — root GETTING_STARTED + INTERVIEW packaging  
**Stage that authored this:** Write-dev-guide (pass 43); Refine-dev-guide (pass 44)  
**Status:** **Implemented** (Guide 04 — 2026-07-14)

**Context SSOT:** `ai-knowledge-base-public/docs/2026-07-14_guide04_packaging_getting_started_interview_context_summary.md`  
**Prerequisite:** Guides 01–03 shippable on public sibling (retrieval spine, packaging DoD, sibling honesty + BYO). This guide is **docs + links only**.

---

## Objective

Land the **defendable interview + stranger-clone shell** on the public sibling:

1. Root `GETTING_STARTED.md` — extract/align README fixture-first path (`uv sync` → nomic pull → fixture ingest → search → `src.eval`).  
2. Root `INTERVIEW.md` — FAQ covering **eight pinned themes** (≈Mechanic length, not AlphaGuard 15+).  
3. README links both; thin Quick Start or point to GS.  
4. Same-delivery PORTFOLIO_VISION / ARCHITECTURE honesty.

**Success signal:** Reviewer opens GS + INTERVIEW, runs fixture Quick Start, hears honest KB1–KB5 / CE no-lift / sibling vs private answers without tip scrub or eval growth.

---

## Learning notes (new for this guide)

1. **Extract vs invent** — README already has Quick Start. Guide 04 promotes that path into GETTING_STARTED; do not invent a second operator story.

2. **CE no-lift** — Point at `docs/2026-07-12_ce_keep_note.md`. Never advertise “CE improves relevance.”

3. **Sibling vs scrub** — Public KB exists via this repo. Private tip scrub is optional hygiene, not a blocker.

4. **Packaging ≠ complete** — GS/INTERVIEW ≠ v1 complete ≠ private flip ≠ eval-complete.

---

## References (paths only)

- `ai-knowledge-base-public/docs/2026-07-14_guide04_packaging_getting_started_interview_context_summary.md`
- `ai-knowledge-base-public/README.md`
- `ai-knowledge-base-public/docs/PORTFOLIO_VISION.md`
- `ai-knowledge-base-public/docs/ARCHITECTURE.md`
- `ai-knowledge-base-public/docs/2026-07-12_ce_keep_note.md`
- `ai-knowledge-base-public/docs/dev_guides/2026-07-14_dev_guide_03_public_sibling_optional_live_path.md`
- Peer: `mechanic_rag/{GETTING_STARTED,INTERVIEW}.md`, `alphaguard/{GETTING_STARTED,INTERVIEW}.md` (shape only)
- `second_brain/docs/2026-07-14_prioritize_next_work_guide04_pass40_fan_in.md`
- `second_brain/docs/2026-07-14_refine_context_guide04_pass42_fan_in.md`
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`

**Out of DoD:** private README edits (sibling pointer already present); tip scrub; eval growth; BACKFILL change.

---

## Architecture constraints (binding)

1. **Docs + links only.** No CE default flip; no eval harness growth; no tip scrub; no BACKFILL change; no auto-sync on clone; no January rewrite.  
2. **Placement:** `GETTING_STARTED.md` + `INTERVIEW.md` at **repo root**.  
3. **GS ceiling:** fixtures default; BYO optional advanced only.  
4. **Eight INTERVIEW themes** required (table below).  
5. **Tone ceiling:** ≈Mechanic (~8–10 Qs), not AG 15+.  
6. Same-delivery VISION/ARCHITECTURE status honesty.

---

## Soft pins (locked defaults)

### INTERVIEW themes (must cover) — frozen example Q titles

| # | Theme | Example Q title (wording flexible ± minor) |
|---|-------|-----------------------------------------------|
| 1 | Fixtures vs BYO | Why are fixtures the default path, and when is BYO YouTube sync optional? |
| 2 | Sibling vs private | Why is private tip-history scrub not required to “have a public AI KB”? |
| 3 | KB2 RO MCP | Which MCP tools are public vs private-gated? |
| 4 | KB4 embeddings | Why `nomic-embed-text` @ 768 — not Gemma / not mxbai? |
| 5 | Hybrid → fusion → CE + degrade | What is the ranking order, and what does `fusion_degraded` mean? |
| 6 | CE no-lift | Does CE improve relevance here? Where is the keep note? |
| 7 | Identity / citations | What do citations use instead of owner filepaths? |
| 8 | Packaging honesty banners | Does packaging mean v1 complete / private flip / eval-complete? |

**README soft pin:** Keep a **thin** Quick Start (≤ ~15 lines) that points to `GETTING_STARTED.md` for full clone depth — do not triplicate the long path.

### GETTING_STARTED ceiling

1. `uv sync`  
2. `ollama pull nomic-embed-text`  
3. `uv run python -m src.ingest --fixtures`  
4. Search smoke (`src.search` hybrid example)  
5. `uv run python -m src.eval`  
6. Footguns: Ollama missing; BYO needs `channels.local.json`  
7. Honesty banner  

BYO section = optional advanced (not core steps).

---

## Acceptance criteria (unchecked)

- [x] Root `GETTING_STARTED.md` matching ceiling  
- [x] Root `INTERVIEW.md` covering all eight themes  
- [x] README links both  
- [x] PORTFOLIO_VISION / ARCHITECTURE honesty updated same delivery  
- [x] No CE lift ads; no scrub-required claim; no eval growth; no tip scrub; no private README DoD  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Ready-check.**

### Phase A — INTERVIEW.md

- [x] **A1.** Create root `INTERVIEW.md`.  
- [x] **A2.** Cover all eight themes (~1 Q each).  
- [x] **A3.** Theme 6: explicit pointer to `docs/2026-07-12_ce_keep_note.md`; forbid lift language.  
- [x] **A4.** Theme 2/8: sibling is public surface; scrub optional; packaging ≠ complete.  
- [x] **A5.** Link ARCHITECTURE / PORTFOLIO_VISION / ce_keep_note.

### Phase B — GETTING_STARTED.md

- [x] **B1.** Create root `GETTING_STARTED.md` from README fixture path (teach why).  
- [x] **B2.** Ordered ceiling steps above.  
- [x] **B3.** Optional BYO subsection (7-day; not default; never commit `channels.local.json`).  
- [x] **B4.** Honesty banner.

### Phase C — README + VISION/ARCHITECTURE

- [x] **C1.** README: thin Quick Start + links to GS + INTERVIEW (Soft pin — no triplicate).  
- [x] **C2.** PORTFOLIO_VISION: note GS/INTERVIEW present; still not eval-complete / v1 complete.  
- [x] **C3.** ARCHITECTURE status honesty for packaging docs.  
- [x] **C4.** Grep CE lift / scrub-required / v1 Done claims — fix.

### Phase D — Stop

- [x] **D1.** Verify commands below.  
- [x] **D2.** Stop. No eval growth; no tip scrub; no private force-edit.

---

## Verification / Definition of Done

**Done when:**

1. Root GS + INTERVIEW exist; eight themes covered.  
2. README links both.  
3. VISION/ARCHITECTURE honesty updated.  
4. Doc-only diffs; no CE/eval/scrub code DoD.

**Suggested verification:**

```bash
# From ai-knowledge-base-public/
test -f GETTING_STARTED.md && test -f INTERVIEW.md
rg -n 'GETTING_STARTED|INTERVIEW' README.md
rg -n 'nomic-embed-text|ce_keep_note|fixtures|MCP|source_id|sibling|fusion_degraded|BACKFILL' INTERVIEW.md
rg -n 'improves relevance|scrub.*required|v1 complete|eval-complete' GETTING_STARTED.md INTERVIEW.md && exit 1 || true
# Optional stranger smoke:
# uv sync && ollama pull nomic-embed-text
# uv run python -m src.ingest --fixtures
# uv run python -m src.search "reciprocal rank fusion RRF" --hybrid --db data/lancedb
# uv run python -m src.eval
```

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| CE lift theater | Theme 6 + ce_keep_note |
| BYO as default | GS ceiling |
| AG-length FAQ | Soft ceiling ≈ Mechanic |
| README/GS drift | Extract README path |
| Eval/scrub creep | Hard out |
| Private README churn | Out of DoD |

### Rollback

Delete root GS/INTERVIEW; restore README links; revert VISION/ARCHITECTURE lines.

---

## Edge-case handling

| Edge case | Behavior |
|-----------|----------|
| Ollama missing | Document pull / fail message |
| Missing channels.local for BYO | Document copy from example |
| Portable MCP cwd | Keep placeholder; no owner abs paths |
| Stranger without network for BYO | Fixtures still work |

---

## Stop conditions / non-goals

**Stop when** packaging DoD met. **Do not:** tip scrub; CE flip; eval growth; BACKFILL change; January rewrite; private remote flip.

---

## Honest readiness (after Refine pass 44)

- FAQ titles + README thin-Quick-Start pin closed. Remaining = answer prose craft.  
- Next: **Ready check before code**. Implement only after Ready + human approve.  
