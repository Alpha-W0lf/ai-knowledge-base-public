# Dev Guide 09 — Build-MV packaging (docs only)

**Date:** 2026-07-18  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 09 — mark portfolio **build MV Met**; keep **eval-complete unchecked (E3)**; no CE lift; no private flip  
**Stage that authored this:** Write-dev-guide (pass 153)  
**Status:** Draft — Ready-check Met (9.2/10); awaiting Tom authorize Implement  

**Context SSOT:** `ai-knowledge-base-public/docs/2026-07-18_post_guide08_build_doneness_closeout_context_summary.md`  
**Handoff:** `second_brain/docs/2026-07-18_spoke_aikb_ready_guide09_pass153_handoff.md`  
**Prerequisite:** Guide 08 Align Met — 8 fixtures; 18 easy + 10 hard-neg; flat `neg_at_k`; E3 held.

**Tom / hub locks (do not reopen — pass 153):**

| Lock | Value |
|------|--------|
| Path | **A** — docs-only build-MV packaging |
| Build MV | May declare **portfolio public success / build MV Met** (§4 Done + §9(a) Met + Guides 01–08) |
| Eval-complete | Remains **unchecked** — explicit **Parked (E3)** honesty; **no invent tick** |
| CE lift | No relevance / hard-neg lift ads; `ce_keep` stays hit@K-gated honesty |
| Private flip | **Out of scope** — not required for public sibling build % |
| Code | **None** — no fixtures, eval harness, `CE_ENABLED` flip, embedding change |

---

## Objective

1. Reconcile PORTFOLIO_VISION / ARCHITECTURE / README / GETTING_STARTED / INTERVIEW so **Done checklists** and **prose** agree.  
2. State clearly: **build MV / portfolio public success = Met**; **eval-complete claim = parked (E3)**; **private flip = not this repo’s build gate**.  
3. Do **not** check eval-complete; do **not** claim CE improves relevance; do **not** flip private archive.  
4. Optional: thin Align-style note recording Guide 09 closeout (same delivery or Align stage).

**Success signal:** A stranger (or later agent) reading VISION cannot confuse “build MV Met” with “eval-complete claimed” or “private-flip ready,” and hub build-100% can treat AI KB public delivery as closed under pass-151 definition without inventing an eval-complete tick.

---

## Learning notes (interview-portable)

1. **Definition of Done vs claim** — checklist Met ≠ permission to claim “eval-complete” when the honesty bar forbids it.  
2. **Doc drift** — Done tables with “not complete” prose create false open work.  
3. **Three lanes** — (a) build MV delivery, (b) parked scientific claims, (c) out-of-repo private flip.  
4. **Preferred phrasing** — “portfolio public success / build MV Met” over ambiguous “v1 complete” when eval-complete and private flip remain separate.

---

## References (paths only)

- `ai-knowledge-base-public/docs/2026-07-18_post_guide08_build_doneness_closeout_context_summary.md`
- `ai-knowledge-base-public/docs/PORTFOLIO_VISION.md`
- `ai-knowledge-base-public/docs/ARCHITECTURE.md` (§9)
- `ai-knowledge-base-public/docs/2026-07-12_ce_keep_note.md`
- `ai-knowledge-base-public/docs/2026-07-18_guide08_harder_ce_discriminative_align.md`
- `ai-knowledge-base-public/GETTING_STARTED.md`
- `ai-knowledge-base-public/INTERVIEW.md`
- `ai-knowledge-base-public/README.md`
- `second_brain/docs/2026-07-18_prioritize_hub_pass151.md` (build 100% definition)
- `second_brain/docs/2026-07-18_spoke_aikb_write_build_closeout_pass153_handoff.md`
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`

---

## Architecture constraints (binding)

1. **Docs only** — no `src/` / `fixtures/` / `tests/` changes unless a typo in a docs path requires none (default: zero code).  
2. **E3:** never check eval-complete; never imply Guide 08 flat metrics earned that claim.  
3. **KB5 / CE honesty:** keep seam + degrade; no “CE improves relevance” language.  
4. **Private flip / tip scrub:** remain optional private-archive hygiene — not a public-sibling build blocker.  
5. **G08-R2/R3:** stay parked (not Guide 09 DoD).  
6. Prefer phrase **“portfolio public success / build MV Met”**; if “v1” appears, disambiguate vs eval-complete claim and private flip.

---

## Soft pins

| Pin | Locked default |
|-----|----------------|
| Files to edit | `docs/PORTFOLIO_VISION.md`, `docs/ARCHITECTURE.md` (§9 header / gate-5 note as needed), `README.md`, `GETTING_STARTED.md`, `INTERVIEW.md` |
| Optional | `docs/2026-07-12_ce_keep_note.md` one-line pointer that build MV packaging ≠ eval-complete; thin `docs/2026-07-18_guide09_build_mv_packaging_align.md` at Align |
| PORTFOLIO_VISION §4 | Keep existing Done rows; **add** explicit residual row or footnote: `Eval-complete claim \| Parked (E3) \| flat Guide 08; not a build MV blocker` — status must **not** read as Done/checked |
| PORTFOLIO_VISION §1 | Rewrite so Guides 01–08 + §4 Done ⇒ **build MV Met**; separately: eval-complete parked; private flip not required |
| ARCHITECTURE top banner | Refresh Guide 01–08 status; stop implying open public delivery when §9 1–7 + 8(a) are Met |
| ARCHITECTURE §9 gate 5 “Still needed” | Change “Larger baseline optional later” → note Guide 08 attempted confusable baseline; still flat; eval-complete claim parked (E3) — optional larger baseline is **not** an open build gate |
| README / GETTING_STARTED / INTERVIEW | Replace blanket “not v1 complete / not eval-complete” with three-lane honesty: build MV Met · eval-complete parked · private flip out of scope |
| Forbidden language | “eval-complete” as Done/checked; “CE improves relevance”; “private flip ready”; inventing new golden/fixture work |
| Verification | `rg` must find Parked/E3 for eval-complete; must **not** find a checked eval-complete checkbox; CE lift ads absent |

---

## Acceptance criteria

- [ ] PORTFOLIO_VISION states build MV / portfolio public success **Met** with Guides 01–08 evidence  
- [ ] Explicit **eval-complete = Parked (E3)** — unchecked; no invent tick  
- [ ] README / GETTING_STARTED / INTERVIEW / ARCHITECTURE prose no longer imply unfinished **public delivery** while listing open “not v1” without disambiguation  
- [ ] No CE lift ads; no private-flip readiness claim  
- [ ] No code / fixture / eval harness changes  
- [ ] G08-R2/R3 not expanded unless free one-liner (default: skip)  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Refine-dev-guide / Ready-check.**

### Phase A — Vision + architecture packaging

- [ ] **A1.** Update `docs/PORTFOLIO_VISION.md` §1 narrative: build MV Met; eval-complete parked (E3); private flip not a public build gate.  
- [ ] **A2.** Update §4 table: add Parked (E3) eval-complete residual row/footnote; keep Guide 08 Done; do **not** check eval-complete.  
- [ ] **A3.** Refresh §5 CE honesty to mention Guide 09 packaging closeout without lift claims.  
- [ ] **A4.** Update `docs/ARCHITECTURE.md` status/header + §9 gate-5 “Still needed” note per soft pins.

### Phase B — Operator / interview surfaces

- [ ] **B1.** `README.md` — three-lane honesty (build MV Met / eval-complete parked / private flip out of scope).  
- [ ] **B2.** `GETTING_STARTED.md` — same; eval section still points at `ce_keep_note`.  
- [ ] **B3.** `INTERVIEW.md` — FAQ “v1 / flip / eval-complete” answers match three lanes; no CE lift.

### Phase C — Optional keep-note pointer + stop

- [ ] **C1.** Optional one sentence in `ce_keep_note`: build MV packaging (Guide 09) ≠ eval-complete claim.  
- [ ] **C2.** Stop. No code. No CE/`CE_ENABLED` flip. No private flip. No eval-complete tick.  
- [ ] **C3.** Await Review / Align as hub directs (Align may add thin Guide 09 align note).

---

## Verification / Definition of Done

```bash
# From ai-knowledge-base-public/
rg -n 'build MV Met|portfolio public success|Parked \(E3\)|eval-complete' \
  docs/PORTFOLIO_VISION.md docs/ARCHITECTURE.md README.md GETTING_STARTED.md INTERVIEW.md

# Must NOT invent a checked eval-complete delivery row:
rg -n 'eval-complete.*Done|Done.*eval-complete|\[x\].*eval-complete|eval-complete.*\[x\]' \
  docs/PORTFOLIO_VISION.md docs/ARCHITECTURE.md || true

# No CE lift / private-flip-ready theater:
rg -n 'CE improves relevance|private flip ready|private-flip ready' \
  docs/PORTFOLIO_VISION.md README.md GETTING_STARTED.md INTERVIEW.md docs/2026-07-12_ce_keep_note.md || true

# No accidental code churn:
git diff --stat -- src/ fixtures/ tests/
# expect empty
```

**DoD:**

1. Build MV / portfolio public success stated **Met** with evidence pointers (Guides 01–08, §4, §9(a)).  
2. Eval-complete explicitly **Parked (E3)** — unchecked.  
3. Operator/interview docs use three-lane honesty; no CE lift; no private-flip readiness.  
4. Zero product code / fixture / test changes.  
5. Soft polish G08-R2/R3 not required for DoD.

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| Accidental eval-complete tick | Soft pin + DoD `rg`; Review rejects |
| “v1 complete” overclaim | Prefer “build MV Met”; disambiguate lanes |
| Scope into CE traps / code | Hard non-goals; empty `git diff` on src/fixtures/tests |
| Leaving ARCHITECTURE “Still needed” implying open build gate | A4 pin closes gate-5 wording |

### Rollback

Revert Guide 09 doc commits only.

---

## Edge-case handling

| Case | Behavior |
|------|----------|
| Tom later unlocks eval-complete claim | Separate authorize — not this guide |
| Conflict between “Met” and `ce_keep_note` flat metrics | Keep both: Met = delivery; flat = honesty; E3 parks claim |
| Temptation to “fix” CE keep | Out of scope — stop |
| Private flip requested mid-guide | Wrong repo — stop / escalate |

---

## Stop conditions

- Phases A–C docs landed per DoD  
- **No** eval-complete tick  
- **No** CE lift ads  
- **No** private flip / code  
- Stop for human if asked to check eval-complete or claim CE lift  

---

## Ready-check / Implement / Review / Align

### Ready-check result (2026-07-18)

| Track | Implement ready? | Score (0–10) | Why not 10 |
|-------|------------------|--------------|------------|
| Guide 09 build-MV packaging | **Yes** (await Tom authorize Implement) | **9.2** | Three-lane prose invent; v1-phrasing craft risk; optional C1; multi-file banner consistency |

**Artifact:** `docs/2026-07-18_guide09_build_mv_packaging_ready_check.md`  
**Further Refine-dev-guide:** **Not required.**  
**Implement now:** **No** until Tom authorizes Implement Stage.
