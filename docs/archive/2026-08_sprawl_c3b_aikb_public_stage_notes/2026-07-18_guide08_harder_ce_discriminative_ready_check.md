> **ARCHIVED** — moved under Workflow OS documentation sprawl reform.
> Do not treat this file as living SSOT.
> Living successor: `docs/PORTFOLIO_VISION.md` · `docs/ARCHITECTURE.md` · `docs/LIVING_DOCS_INDEX.md` · matching living guide under `docs/dev_guides/`
> Batch: `2026-08_sprawl_c3b_aikb_public_stage_notes`
> Date: 2026-08-14
# Ready-check — Guide 08 harder CE-discriminative eval

> **Superseded (Align 2026-07-18):** Pre-Implement Ready-check only. Guide 08 **shipped** — Implement `ec6d8fe`, Review shippable as-is (`docs/archive/2026-08_sprawl_c3b_aikb_public_stage_notes/2026-07-18_guide08_harder_ce_discriminative_review.md`). “Ready for Implement?” / pre-change invent notes below are **historical**. Current metrics: [`docs/2026-07-12_ce_keep_note.md`](./2026-07-12_ce_keep_note.md).

**Date:** 2026-07-18  
**Repo:** `ai-knowledge-base-public`  
**Stage:** Ready check before code  
**Mode:** spoke  
**Guide:** `docs/dev_guides/2026-07-18_dev_guide_08_harder_ce_discriminative_eval.md`  
**Context:** `docs/2026-07-18_harder_ce_discriminative_eval_context_summary.md`  
**Handoff:** `second_brain/docs/2026-07-18_spoke_aikb_ready_ce_eval_pass152_handoff.md`  
**Locks:** B1 (+1–2 confusable fixtures) · E3 (no eval-complete on flat) · fold R1  
**Align status:** **Superseded** by Implement + Review + Align (was: Ready for Implement after authorize)

## Verdict

| Question | Answer |
|----------|--------|
| Ready for Implement? | **Yes** — after Tom authorizes Implement Stage |
| Implement readiness score | **8.7 / 10** |
| Further Refine-dev-guide required? | **No** |
| Implementation started this stage? | **No** |

## Score — why not 10

| Gap | Severity | Notes |
|-----|----------|-------|
| Exact fixture slug + body prose (fusion twin / optional CE twin) | Soft invent | Soft pins constrain themes; Implement still authors text |
| `hn7+` query craft + B2 fusion-failing yield | Soft invent | Guide allows ship-with-note if &lt;4 new fusion-failing traps |
| Easy `g1`–`g18` hit@K regression after corpus growth | Runtime risk | D3 gate plans investigate-before-honesty; not a design hole |
| Live eval needs Ollama + HF MiniLM | Runtime | Same Guide 06/07 footgun; Hub-free R1 still DoD |
| Soft count tension (+4–6 new vs total hard-neg ≤10) | Soft pin clarity | Prefer **+4** new (`hn7`–`hn10`) to honor total ≤10 without unlock |

**Not blockers:** metric formula locked; harness already ships `neg_at_k` / keep exclusion; B1/E3/R1 human locks present; blast radius + rollback clear; flat CE outcome is an explicit shippable path.

## Alignment check

| Check | Result | Evidence |
|-------|--------|----------|
| Context ↔ Guide | **Aligned** | B1 confusable growth; E3 no eval-complete on flat; fold R1; no keep-from-neg; no fake lift / private / CE / KB4 flip |
| Guide ↔ code seams (pre-change) | **Aligned** | `src/eval/__init__.py` already has hard-neg/`neg_at_k`/`_decide_ce_keep`; Implement is fixtures + goldens + R1 test + honesty — **usually not** harness rewrite |
| Guide ↔ ingest | **Aligned** | `ingest_fixtures` reads `manifest.json` and loads `fixtures/transcripts/{slug}.md` where `slug = source_id` without `fixture:` prefix |
| Corpus baseline | **Confirmed** | 6 fixtures; 24 goldens (18 easy + 6 hard-neg) |
| Locks | **Honored** | B1 ≤8 total fixtures; E3; R1 in `test_eval_neg_at_k.py`; `ce_keep` hit@K-gated |

## Blast radius / rollback

- **Code (thin):** `tests/test_eval_neg_at_k.py` (R1 monkeypatch smoke); rarely `src/eval`  
- **Data:** +1–2 transcripts; `manifest.json`; `PROVENANCE.md`; append `hn7+` to `golden_cases.jsonl`  
- **Docs:** `ce_keep_note`, GETTING_STARTED, INTERVIEW, PORTFOLIO_VISION (eval-complete **unchecked**)  
- **Rollback:** revert those commits; or delete new transcripts/`hn*` and restore manifest to 6  
- **Clear:** Yes

## Edge cases

Planned in guide: ship 1 fixture if only one authors; &lt;4 fusion-failing → note; CE flat / lift / worse paths; easy hit@K drop blocks honesty success; missing forbidden → `ValueError`; HF/Ollama down → units green, live eval still required for note. **Sufficient.**

## Soft residuals (park — no Refine)

1. Prefer shipping **2** confusable fixtures when both pairs author cleanly; **1** OK.  
2. Prefer **+4** new hard-negs (`total hard-neg = 10`) unless Tom unlocks total &gt;10.  
3. R2/R3 remain parked.  
4. Exact CombSUM / bi-encoder wording = Implement craft within theme pins.

**Recommendation:** Park residuals; **no** further Refine-dev-guide.

## QUALITY_STANDARD §5

Assumptions checked against guide + context + ingest/eval seams + fixture counts; spoke stayed in Ready-check slice; no Implement; findings in this note + handoff; numeric score + why-not-10 reported; locks not reopened.

## Stop

Ready-check complete. **Historical** — Implement authorized and shipped; see Align / `ce_keep_note`.
