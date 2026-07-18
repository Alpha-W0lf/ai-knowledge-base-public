# Context: Harder CE-discriminative eval (unpark Park C / Option B)

**Date:** 2026-07-18  
**Repos:** `ai-knowledge-base-public`  
**Status:** Draft Gather + Guide 08 written + **Ready-check Met** (8.7/10) — awaiting Tom authorize Implement  
**Mode last used:** spoke  
**Handoff (Gather):** `second_brain/docs/2026-07-18_spoke_aikb_gather_ce_eval_pass151_handoff.md`  
**Handoff (Write):** `second_brain/docs/2026-07-18_spoke_aikb_write_ce_eval_pass152_handoff.md`  
**Handoff (Ready):** `second_brain/docs/2026-07-18_spoke_aikb_ready_ce_eval_pass152_handoff.md`  
**Guide:** `docs/dev_guides/2026-07-18_dev_guide_08_harder_ce_discriminative_eval.md`  
**Ready-check:** `docs/2026-07-18_guide08_harder_ce_discriminative_ready_check.md`  
**Hub:** `second_brain/docs/2026-07-18_prioritize_hub_pass151.md` / pass 152  
**Tom locks (pass 152):** **B1** confusable +1–2 fixtures · **E3** no eval-complete on flat · **fold R1**  
**Prior inventory:** `docs/2026-07-17_post_guide07_next_slice_inventory_context_summary.md` (recommended **C park**; Tom later authorized **B**)  
**Role lens:** AI engineer (RAG eval honesty / discriminative goldens)

## Problem

Guides 01–07 closed the public portfolio surface through hard-negative harness + honesty. Recorded metrics (`docs/2026-07-12_ce_keep_note.md`):

| Arm | Easy hit@K | Hard-neg `neg_at_k` | Notes |
|-----|------------|--------------------|-------|
| Fusion | **1.0** (18/18) | **0.0** (0/6) | All six `hn*` still return a forbidden `source_id` in top-K |
| CE | **1.0** CE-success | **0.0** (0/6) | CE ran; **no** rejection lift vs fusion |
| Keep | — | — | `ce_keep=false` (hit@K-gated; **never** from `neg_at_k` alone) |

Hub pass 151 treats harder CE-discriminative eval as the **only remaining public quality gate** before any honest “eval-complete” language. Post–Guide 07 inventory (pass 121) had recommended **park**; Tom has **unparked Option B for this Gather only** — design the thinnest next guide without fake lift, private flip, or Implement.

**Why Guide 07 is not enough:** The six traps are **discriminative for fusion** (B2: 6/6 fusion-failing) but **not CE-discriminative** — CE fails the same traps. Mechanic Guide 08 already showed that paraphrase-only trap growth on a tiny synthetic corpus yields **flat** CE vs fusion metrics again. AI KB must not repeat that dead end with query-only rewrites of `hn1`–`hn6`.

## Acceptance criteria (for later Guide 08 — not checked this Gather)

- [ ] Human locks trap strategy (corpus growth vs query-only) before Write invents pins  
- [ ] Soft pins for case count, ids, anti-paraphrase, and honesty / `ce_keep` rules  
- [ ] Harness contract **unchanged** unless a named residual (e.g. R1 smoke) is explicitly in-guide  
- [ ] Success = **honest measurement**: either CE `neg_at_k` > fusion `neg_at_k` **or** documented flat with no lift ads  
- [ ] **No** auto “eval-complete” claim from a flat run; **no** `ce_keep` flip from `neg_at_k` alone  
- [ ] **No** private flip / `CE_ENABLED` flip / KB4 embedding change  
- [ ] Honesty docs (`ce_keep_note`, GETTING_STARTED, INTERVIEW, PORTFOLIO_VISION) updated only after a real eval re-run (Implement)

## In scope

- Context for **Guide 08 candidate**: harder CE-discriminative goldens (Option B)  
- Absorb Mechanic Guide 08 lessons (T1 confusable sections vs T2 paraphrase-only)  
- Soft pins for Write-dev-guide; open decisions with recommendation  
- Optional fold of Guide 07 soft residuals R1–R3 (polish, not a solo product slice)  
- Handoff Results update  

## Out of scope

- Write / Refine / Implement / Review Guide 08  
- Private tip scrub / remote visibility flip  
- `CE_ENABLED` default flip; embedding / KB4 change  
- Claiming eval-complete or portfolio v1 Done without evidence  
- Easy `g*` golden theater growth  
- Fake CE relevance ads; flipping `ce_keep` from `neg_at_k` alone  
- Mechanic / AlphaGuard / Vehicle Implement  

## Prior art (paths only)

**This repo**

- `docs/PORTFOLIO_VISION.md` — Guides 01–07 Done; not eval-complete  
- `docs/ARCHITECTURE.md` — KB1 ≈3–8 fixtures; KB5 CE seam + eval honesty  
- `docs/2026-07-12_ce_keep_note.md` — live metric SSOT  
- `docs/2026-07-17_post_guide07_next_slice_inventory_context_summary.md` — A/B/C; park lean  
- `docs/2026-07-17_guide07_hard_negative_neg_at_k_context_summary.md` — superseded Gather  
- `docs/2026-07-17_guide07_hard_negative_review.md` — R1–R3 soft residuals  
- `docs/dev_guides/2026-07-17_dev_guide_07_hard_negative_neg_at_k.md` — closed Align  
- `fixtures/eval/golden_cases.jsonl` — 18 easy + 6 hard-neg  
- `fixtures/manifest.json` — **6** `fixture:*` docs  
- `fixtures/transcripts/*.md` — short synthetic siblings (high lexical overlap themes)  
- `src/eval/__init__.py` — `neg_at_k`, hard-neg exclusion, `_decide_ce_keep` ignores `neg_at_k`  
- `tests/test_eval_neg_at_k.py`, `tests/test_eval_ce_honesty.py`

**Program / sibling lessons**

- `second_brain/docs/2026-07-18_prioritize_hub_pass151.md`  
- `second_brain/docs/2026-07-18_portfolio_doneness_pass151.md` (~84% AI KB; Park C)  
- `mechanic_rag/docs/2026-07-17_guide08_harder_discriminative_ce_traps_context_summary.md` — T1 confusable sections; T2 failed  
- `mechanic_rag` Guide 08 outcome: n=44 paired ask still delta **0** / helps=0 after +3 confusable sections  

## Locked starting contracts (do not reopen)

| Lock | Value |
|------|--------|
| Metric formula | Guide 06/07: `neg_ok` iff forbidden ∩ returned = ∅; `neg_at_k` per arm; hard-neg **excluded** from hit@K / CE-success / `_decide_ce_keep` |
| `ce_keep` | Hit@K / CE-success rules only — **never** from `neg_at_k` alone unless Tom later locks a new keep policy |
| Stack | KB5 hybrid → RRF → pluggable MiniLM CE; degrade `fusion_degraded` + `error` |
| Defaults | `CE_ENABLED=True`; `nomic-embed-text` @ 768 — no flip without authorize |
| Public surface | Fixture-first only for this guide; no BYO YouTube as eval DoD |
| Unpark | Tom authorized Option B **Gather** (pass 151); prior park recommendation superseded for this slice |

## Current harness / corpus facts (evidence)

| Fact | Evidence |
|------|----------|
| Easy goldens | `g1`–`g18`; fusion + CE-success hit@K **1.0** |
| Hard-neg goldens | `hn1`–`hn6`; each pairs expected sibling vs forbidden sibling |
| B2 | 6/6 fusion returned forbidden before ship; CE also 0/6 `neg_ok` |
| Corpus size | **6** docs — at KB1 soft mid; headroom to **≤8** before soft ceiling |
| Doc length | Very short (~5–8 lines each) — high sibling confusability already, but CE still matches fusion |
| Harness | Ready for more `hn*` rows; no new metric invention required for Option B |
| Soft residuals | R1 exclusion smoke; R2 `must_cite:false` validate; R3 easy-error counting — polish |

## Why query-only harder traps are likely to fail again

1. **Shared retrieve pool** — CE only reorders fused shortlist N→K; if forbidden and gold both sit high under fusion, CE often keeps both.  
2. **Guide 07 already used sibling temptation** — `hn*` queries mix gold keywords with forbidden-theme tokens; CE did not demote forbidden.  
3. **Mechanic lesson** — paraphrase / near-duplicate traps → flat asymmetry; **T1 synthetic confusable sections** were the only plausible path on a tiny corpus (and even T1 stayed flat on Mechanic).  
4. **Flat is a valid scientific outcome** — Guide 08 must be designed to **report** flat honestly, not to force CE wins via gold-probed theater.

## Trap design options (Guide 08 candidates)

| Option | Idea | CE-discriminative chance | Risk |
|--------|------|--------------------------|------|
| **B1 — Confusable corpus growth (preferred)** | Add **1–2** new synthetic fixture docs (stay ≤8 total) with overlapping lexical tokens but **distinct** facts; author new `hn7+` that tempt the confusable sibling | Best chance on this stack | Eval gaming if texts/CE-probed; must stay synthetic + provenance; KB1 ceiling |
| **B2 — Query-only anti-paraphrase** | No new docs; craft `hn*` that avoid near-paraphrase of `hn1`–`hn6` | Weak (Guide 07 + Mechanic T2) | Likely another flat report; wasted guide cycle |
| **B3 — Diagnostics-only** | Rank dumps / forbidden rank position before new goldens | Diagnostic | Scope creep; not a product DoD alone |
| **B4 — Keep-policy change** | Allow `ce_keep` from `neg_at_k` lift | N/A product policy | **Out** unless Tom locks; high honesty risk |
| **B5 — Re-park** | Stop after this Gather; leave eval-complete unchecked | N/A | Contradicts pass 151 unpark unless Tom re-parks |

**Gather lean:** Prefer **B1-primary** (minimal confusable fixtures + new hard-neg band + anti-paraphrase) over B2-only. Accept flat as shippable honesty if B1 still yields CE `neg_at_k` == fusion `neg_at_k`.

## Recommended approach (thinnest next guide)

**Guide 08 — Harder CE-discriminative traps (fixture growth + `neg_at_k` re-baseline)**

1. **No harness redesign** — reuse Guide 07 `kind: hard_negative` / `neg_at_k` / keep exclusion. Optionally fold **R1** thin exclusion smoke if cheap.  
2. **Corpus:** +1 or +2 confusable synthetic docs under `fixtures/transcripts/` + manifest/PROVENANCE (hard max total fixtures **8** per KB1).  
3. **Cases:** soft target **+4–6** new `hn*` (hard max total hard-neg **12** including existing six — prefer **≤10** total). Existing `hn1`–`hn6` stay as regression band.  
4. **Authoring rules (anti-fake-lift):**  
   - Ground queries in committed fixture text only.  
   - Forbidden id must be a real confusable sibling, not an unrelated distant doc.  
   - Do **not** CE-probe during authoring to cherry-pick only CE-win rows.  
   - Mandatory B2-style spot-check: prefer traps where **fusion currently returns** forbidden; if CE also clears some, record per-case asymmetry.  
5. **Success signal:** Stranger runs `uv run python -m src.eval`; sees updated per-arm `neg_at_k`; docs state CE lift **only if** CE `neg_at_k` > fusion; else flat honesty. **`ce_keep` unchanged** unless separate Tom lock.  
6. **Eval-complete language:** Recommend **not** checking “eval-complete” from one flat Guide 08 run. Prefer a human gate: either (a) measurable CE rejection lift on hard-neg **or** (b) explicit Tom lock that “eval-complete = honest ceiling + discriminative harness + documented flat.”  

**Why this is thinnest:** Harness already exists; work is fixtures + goldens + honesty re-run + optional R1 — not a ranking rewrite.

## Risks and blast radius

| Risk | Angle | Mitigation |
|------|-------|------------|
| Confusable docs authored to force CE wins | Portfolio honesty / fake lift | Anti-probe rule; ship flat; no keep flip |
| Exceed KB1 soft ceiling (>8 docs) | Maintainability / stranger smoke | Cap +1–2; hard stop at 8 |
| Query-only Band 2 | Wasted cycle | Prefer B1; park B2 as sole strategy |
| Claiming eval-complete after flat | Docs trust | Explicit human gate (decision below) |
| Folding R1–R3 into mega-guide | Scope creep | R1 optional; R2/R3 park unless free |
| Parallel Mechanic freeze story confusion | Interview messaging | AI KB metric is `neg_at_k`, not Mechanic paired-ask delta |
| Private flip sneaks in via “hygiene” | Security / out of scope | Locked out |

## Edge cases

- B1 corpus growth but **no** fusion-failing new traps → ship best honest set + note (Guide 07 B2 precedent).  
- CE `neg_at_k` **improves** but easy hit@K still flat → report rejection lift; **still** do not auto-flip `ce_keep` without lock.  
- CE `neg_at_k` **worsens** → keep seam; document; do not disable CE without authorize.  
- New fixture breaks easy `g*` hit@K < 1.0 → investigate before claiming growth success; easy band is regression.  
- HF/Ollama unavailable on Implement machine → unit tests Hub-free; live eval still required for honesty note (Guide 06/07 pattern).  
- Total hard-neg >8 with weak traps → prefer quality ≤ quantity; Guide 07 hard max 8 was for *first* band — new band soft-capped in Write.

## Unknowns (must resolve or escalate)

| Unknown | How to resolve | Blocking? |
|---------|----------------|-----------|
| Allow +1–2 confusable fixtures (B1) vs query-only (B2)? | Human lock below | **Yes** for Write pins |
| What closes “eval-complete” after Guide 08? | Human lock below | **Yes** for PORTFOLIO_VISION honesty |
| Exact confusable theme pair (e.g. fusion vs CE twin facts)? | Write invent within soft pins; optional short Refine | Soft |
| Fold R1 smoke into Guide 08 DoD? | Human lean / Write default | Soft — recommend yes if ≤1 file |
| Will flat B1 still raise portfolio %? | Hub after Review | Soft — honesty > percentage theater |

## Open decisions (human)

> **Pass 152 locks:** Decision 1 → **B1**; Decision 2 → **E3**; Decision 3 → **fold R1**. Historical recommendations below retained for audit.

### 1. Trap strategy: confusable corpus growth vs query-only — **LOCKED B1**

- **Plain title:** How should Guide 08 try to make CE look different from fusion on hard negatives?
- **In plain terms:** Add 1–2 new synthetic fixture docs that are easy to confuse, or only rewrite queries against the existing six docs.
- **Options:** **B1** confusable corpus growth (+1–2 docs) · **B2** query-only · **B5** re-park
- **Recommendation:** **B1**
- **Lock:** **B1** (Tom pass 152)
- **Reasoning:** Guide 07 already exhausted sibling-temptation queries on 6 docs with CE `neg_at_k=0.0`. Mechanic proved paraphrase-only growth stays flat; their only plausible path was confusable sections. KB1 still allows up to ~8 fixtures.
- **Tradeoffs:** Slightly larger stranger corpus and authoring risk of eval gaming; gives up the “zero corpus change” path that is likely to re-prove flat without new information.

### 2. When may we say “eval-complete”? — **LOCKED E3**

- **Plain title:** After Guide 08, what evidence is enough to check eval-complete on the portfolio vision?
- **In plain terms:** Does a careful flat report count, or only a real CE hard-neg win (or a separate Tom override)?
- **Options:** **E1** CE `neg_at_k` > fusion required · **E2** honest discriminative harness + documented flat counts · **E3** leave unchecked until a later gate
- **Recommendation:** **E3**
- **Lock:** **E3** (Tom pass 152) — do not auto-check eval-complete on flat
- **Reasoning:** Pass 151 calls this the gate *before* eval-complete claims — not automatic completion. Mechanic kept freeze unchecked after flat Guide 08; same honesty pattern fits AI KB.
- **Tradeoffs:** E1 may leave the box open after another flat run; E2 closes the story faster but weakens the word “complete”; E3 keeps ~84% narrative until an explicit later lock.

### 3. Optional R1 exclusion smoke in Guide 08? — **LOCKED fold R1**

- **Plain title:** Should Guide 08 include the thin hard-neg hit@K exclusion unit smoke (Review residual R1)?
- **In plain terms:** Add a small Hub-free test that hard-neg rows do not inflate easy hit@K.
- **Options:** **Yes fold R1** · **No — park R1**
- **Recommendation:** **Yes fold R1**
- **Lock:** **fold R1** (Tom pass 152)
- **Reasoning:** Strengthens regression without expanding product scope; R2/R3 stay parked.
- **Tradeoffs:** Slightly longer DoD; residual polish could wait forever otherwise.

## Evidence opened this pass

- Handoff pass 151; hub Prioritize + doneness pass 151  
- `PORTFOLIO_VISION.md`; ARCHITECTURE KB1/KB5 + §9 gate notes  
- `ce_keep_note`; post–Guide 07 inventory; Guide 07 review residuals  
- Guide 07 dev guide soft pins; `src/eval/__init__.py` keep/neg math  
- `golden_cases.jsonl` (24 lines); `manifest.json` (6 fixtures); sample transcripts  
- Mechanic Guide 08 harder-trap context + flat outcome (T1 lessons)  

## Honest readiness

- Ready for **Write dev guide**? **Done** (pass 152).  
- Ready for **Ready-check**? **Done** — **8.7 / 10**; artifact `docs/2026-07-18_guide08_harder_ce_discriminative_ready_check.md`.  
- Ready for **Implement**? **Yes after Tom authorize** — no self-start. Prefer +4 new `hn*` (total hard-neg 10); fixture prose + queries remain Implement invent.  
- Further Refine-dev-guide? **No**.  
- Next human stage name (recommended): `Stage: Implement` · Repo: `ai-knowledge-base-public` · Work item: Guide 08 harder CE-discriminative eval — **after authorize**.

## Learning notes (interview-portable)

1. **Hard negative** — success is *not* retrieving a forbidden document in top-K, not merely retrieving the gold.  
2. **Ceiling effect** — when easy hit@K is already 1.0, only a separate metric (`neg_at_k`) can compare rankers.  
3. **Confusable corpus** — on tiny fixture sets, paraphrase queries rarely create cross-encoder vs fusion asymmetry; overlapping-but-distinct docs are the usual next lever.  
4. **Proxy vs task honesty** — shipping more goldens is not the same as proving CE relevance lift; flat metrics after a harder attempt are still evidence.
