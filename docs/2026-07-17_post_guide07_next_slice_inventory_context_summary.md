# Context: Post–Guide 07 next-slice inventory (private hygiene vs harder CE vs park)

> **Outcome (Align 2026-07-18):** Option **B** was later unparked (pass 151–152) and **Guide 08 closed** — Implement `ec6d8fe`, Review shippable, Align Met. Current public honesty: [`docs/2026-07-12_ce_keep_note.md`](./2026-07-12_ce_keep_note.md) (8 fixtures; 10 hard-neg; flat `neg_at_k`; E3 eval-complete unchecked). A/B/C comparison and park recommendation below are **historical** Gather inventory — not open work.

**Date:** 2026-07-17  
**Repos:** `ai-knowledge-base-public` (+ `ai_knowledge_base` read-only for tip inventory evidence; **not** SSOT for public story)  
**Status:** **Superseded** by Guide 08 close (was: Draft Gather; lean park)  
**Mode last used:** spoke  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_next_gather_pass121_handoff.md`  
**Prior:** Guide 07 hard-negative / `neg_at_k` **Align Met** (pass 117 fan-in); Implement `ff9ad33`; Review shippable; Align `b243f2d`  
**Role lens:** AI engineer (RAG eval honesty) + light DE (private tip inventory / flip hygiene)

## Problem

Guide 07 closed the hard-negative harness and shipped **6** discriminative traps. Live honesty (`docs/2026-07-12_ce_keep_note.md`):

| Arm | Easy hit@K | Hard-neg `neg_at_k` | Notes |
|-----|------------|--------------------|-------|
| Fusion | **1.0** (18/18) | **0.0** (0/6) | All six traps still surface a forbidden id |
| CE | **1.0** CE-success | **0.0** (0/6) | CE ran; **no** rejection lift vs fusion |
| Keep | — | — | `ce_keep=false` (hit@K-gated; **not** from `neg_at_k`) |

The public portfolio surface (sibling + fixtures + packaging + measured CE honesty) is strong. Hub Prioritize pass 121 asks what **agent-movable** slice comes next:

- **Option A** — Private tip / hygiene **inventory** (no flip execution)  
- **Option B** — Harder cross-encoder (CE)–discriminative follow-up (new guide candidate)  
- **Option C** — **Park** AI KB agent work until a clearer gate appears  

This Gather inventories evidence and recommends one — **no** Implement, **no** private flip, **no** `CE_ENABLED` flip, **no** KB4 embedding change.

## Acceptance criteria

- [x] Compare Options A / B / C with evidence from VISION / ARCHITECTURE / Guide 07 / private tip paths  
- [x] Recommend one option with reasoning + tradeoffs (chat + this file)  
- [x] Dated context summary under `ai-knowledge-base-public/docs/`  
- [x] Handoff Results filled  
- [ ] Human locks A vs B vs C (recommendation is **not** a lock)  
- [x] No private flip / CE default flip / embedding change / Implement in this stage  

## In scope

- Evidence-backed next-slice inventory for `ai-knowledge-base-public` after Guide 07 Align  
- Read-only peek at private archive tip paths / KB3 runbook existence (inventory only)  
- Soft Review residuals R1–R3 called out as polish (not a guide by themselves)  
- Honest readiness: Write-dev-guide next? only if human picks B (or rare A design)

## Out of scope

- Private GitHub visibility flip  
- Tip-delete / `git filter-repo` / KB3-exec Implement  
- `CE_ENABLED` flip; embedding / KB4 change  
- Guide 08 Write / Implement / Review  
- Fake CE lift ads; growing easy `g*` goldens for theater  
- Mechanic / AlphaGuard / Vehicle work (other spokes)

## Prior art (paths only)

- `ai-knowledge-base-public/docs/PORTFOLIO_VISION.md` (no root `VISION.md` — portfolio SSOT is this file)  
- `ai-knowledge-base-public/docs/ARCHITECTURE.md` (§9 gate 8 sibling vs private flip; §10 tip table)  
- `ai-knowledge-base-public/docs/2026-07-12_ce_keep_note.md`  
- `ai-knowledge-base-public/docs/archive/2026-08_sprawl_c3b_aikb_public_stage_notes/2026-07-17_guide07_hard_negative_review.md` (R1–R5)  
- `ai-knowledge-base-public/docs/dev_guides/2026-07-17_dev_guide_07_hard_negative_neg_at_k.md`  
- `ai-knowledge-base-public/fixtures/` (6 transcripts; 24 golden lines)  
- `second_brain/docs/2026-07-17_hub_fanin_ai_kb_align_pass117.md`  
- `second_brain/docs/2026-07-17_prioritize_hub_pass121.md`  
- Private (read-only): `ai_knowledge_base/docs/ARCHITECTURE.md` §9–10; `docs/dev_guides/2026-07-14_dev_guide_03_kb3_exec_scrub.md`; tip markdowns still tracked  

## Option comparison

### Option A — Private tip / hygiene inventory (no flip)

**What it is:** Document live private-archive tip status (disk + `git ls-files` + §10), confirm scrub runbook still valid, write an inventory note — **stop before any delete/rewrite/visibility flip**.

**Evidence now:**

- Public sibling: tip transcripts **absent** (ARCHITECTURE §10); gate 8(a) portfolio public surface **met** by sibling + fixtures.  
- PORTFOLIO_VISION: scrub is **optional hygiene**, **not** a blocker for “having a public AI KB.”  
- Private archive: **three tip transcripts + research** still tracked; private Guide 03 KB3-exec scrub runbook exists; private §9 still treats KB3-exec as flip blocker for **that** remote.

| Pros | Cons |
|------|------|
| Cheap; unblocks future flip prep | Does **not** improve stranger-runnable public demo |
| Clarifies private vs public gate stories | Easy to overclaim “flip-ready” from inventory alone |
| Matches KB3 “inventory before flip” spirit | Wrong repo for public portfolio %; irreversible work still later |

### Option B — Harder CE-discriminative follow-up

**What it is:** New guide (Guide 08 candidate) to craft traps where CE might **reject** a forbidden sibling that fusion keeps — or honestly show CE still cannot — without flipping keep from `neg_at_k` alone unless Tom later locks that policy.

**Evidence now:**

- Guide 07: fusion **and** CE `neg_at_k` = **0.0** on 6/6 fusion-failing traps — discriminative set works; CE adds **no** rejection lift.  
- Corpus = **6** fixture docs — headroom for “harder” traps without new docs is thin; corpus growth risks theater if authored to force CE wins.  
- Soft residuals R1–R3 = test/validate polish, not a product slice.  
- Mechanic spoke is also Gathering harder discriminative traps (hub #2) — learn-before-duplicate.

| Pros | Cons |
|------|------|
| Continues the honest RAG eval story | High craft risk of fake lift / corpus theater |
| Could show CE value *or* confirm “seam only” | May burn a guide cycle to re-prove flat metrics |
| Interview-relevant (discriminative eval) | Overlaps Mechanic Guide 08 timing |

### Option C — Park agent work

**What it is:** Leave `ai-knowledge-base-public` idle until Tom locks a new guide or a flip intent appears. Soft residuals stay parked.

| Pros | Cons |
|------|------|
| Public Guides 01–07 + Align already closed | Eval still “not complete” in honesty banners |
| Frees agent capacity for Vehicle / Mechanic / AG | Private tip debt remains (acceptable per VISION) |
| Avoids low-yield CE trap craft or flip theater | Requires hub to re-authorize later |

## Risks and blast radius

| Risk | Angle | Mitigation |
|------|-------|------------|
| Inventory → silent scrub | Security / irreversible | Out of scope; stop at inventory if A ever chosen |
| Harder traps → fake CE ads | Portfolio honesty | Keep `ce_keep` hit@K-gated; no lift without evidence |
| Corpus growth for CE theater | Maintainability | Prefer park or wait Mechanic lessons; KB1 ≈3–8 docs soft ceiling |
| Claiming eval-complete | Docs trust | Still not eval-complete after A/B/C |
| Parallel trap guides (Mechanic + AI KB) | Cost / duplication | Park AI KB until Mechanic Gather fans in |

## Edge cases

- Inventory finds tip paths already gone on private → still no flip; update private docs only if a later private slice is authorized.  
- Harder traps still flat on both arms → valid scientific outcome; must not flip `CE_ENABLED` off without human authorize.  
- Park then Tom wants flip → start private KB3-exec with authorize stamp (separate work item, not this public spoke).  
- R1 smoke test alone is **not** enough for a full guide — fold into B if B is chosen, or leave parked.

## Unknowns (must resolve or escalate)

| Unknown | How to resolve | Blocking? |
|---------|----------------|-----------|
| Does Tom want private-remote flip **this quarter**? | Human say yes/no | Blocks A urgency only |
| Can CE ever beat fusion on hard-neg with only 6 fixtures? | Spot-check probes in Write if B locked; else Unknown | Blocks B DoD craft, not this Gather |
| Will Mechanic harder-trap Gather yield reusable patterns? | Hub fan-in after Mechanic Gather | Soft — favors C short-term |

## Recommended approach

**Recommend Option C — park AI KB agent work** for the next portfolio cycle.

**Why (evidence):**

1. Public “having an AI KB” story is already met (sibling + packaging + fixture eval through Guide 07 Align). Private scrub is explicitly **optional** for that story.  
2. Option A inventory does not move public stranger proof and risks flip-theater if misread.  
3. Option B is scientifically interesting but Guide 07 already showed CE fails the same six fusion traps; without corpus expansion or a new keep policy, expected outcome is another flat report — better to absorb Mechanic’s harder-trap Gather first.  
4. Soft R1–R3 are polish; not worth a solo guide.

**If Tom rejects park and wants AI KB work next:** prefer **Option B** (harder CE-discriminative design → Write-dev-guide) over **Option A**. Only pick **A** if the human goal is specifically “prepare private remote for a future visibility flip” — still **no flip** in that slice.

## Open decisions (human)

- **Plain title:** What should AI KB do next after Guide 07? (A / B / C)
  - In plain terms: Inventory private tip hygiene (no flip), try harder CE traps on the public fixtures, or park the spoke.
  - Options: **A** private hygiene inventory · **B** harder CE-discriminative follow-up · **C** park
  - Recommendation: **C — park**
  - Reasoning: Public surface + honesty closed; private scrub optional for portfolio; CE already flat on all Guide 07 traps; Mechanic is already exploring harder traps; avoid fake-lift and flip theater.
  - Tradeoffs: Gives up near-term AI KB guide progress; eval stays “not complete”; private tip debt remains until an explicit flip program.
  - Needs from you: Say `lock C` / `lock B` / `lock A` (or park with a revisit date).

## Evidence opened this pass

- `PORTFOLIO_VISION.md`, `ARCHITECTURE.md` §9–10 (public)  
- `ce_keep_note`, Guide 07 review, Guide 07 guide header/status  
- Hub fan-in pass 117; Prioritize pass 121  
- Private read-only: `git ls-files` tip transcripts present; KB3 scrub guide exists; private ARCHITECTURE still lists KB3-exec as flip blocker  
- Confirmed: no `docs/VISION.md` on public sibling (use `PORTFOLIO_VISION.md`)  
- Fixture counts: 6 transcripts; 24 golden lines  

## Honest readiness

- Ready for Write-dev-guide? **No** while recommendation is park (**C**).  
- Ready for Write-dev-guide if human **locks B**? **Yes** (after optional short Refine if trap strategy needs corpus-growth pins).  
- Ready for Write-dev-guide if human **locks A**? **Thin inventory guide only** — prefer a private-archive spoke; this public repo can only host a pointer note.  
- Ready for Implement? **No** — Gather only; locks forbid flip / CE / embedding / Implement.
