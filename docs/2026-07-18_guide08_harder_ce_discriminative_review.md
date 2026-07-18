# Review — Guide 08 harder CE-discriminative eval Implement

**Date:** 2026-07-18  
**Repo:** `ai-knowledge-base-public`  
**Stage:** Review implementation  
**Mode:** spoke  
**Implement commit:** `ec6d8fe`  
**Guide:** `docs/dev_guides/2026-07-18_dev_guide_08_harder_ce_discriminative_eval.md`  
**Handoff:** `second_brain/docs/2026-07-18_spoke_aikb_review_ce_eval_pass152_handoff.md`  
**Locks verified:** B1 · E3 · fold R1  

## Verdict

| Call | Value |
|------|--------|
| Shippable as-is? | **Yes** |
| Fix-first required? | **No** |
| Must-fix patches this Review? | **None** |
| Ready for Align docs? | **Yes** (optional — Gather/Ready-check superseded banners; not a ship blocker) |

## Guide DoD mapping

| Guide requirement | Evidence | Pass? |
|-------------------|----------|-------|
| B1: +1–2 confusable fixtures; total ≤8 | `combsum-fusion-07` + `bi-encoder-rerank-08`; manifest **8**; PROVENANCE rows | Yes |
| +4 new `hn*` (total hard-neg ≤10); prior goldens preserved | `hn7`–`hn10`; **10** hard-neg; **28** JSONL lines; `g1`–`g18` + `hn1`–`hn6` intact | Yes |
| B2 spot-check documented (prefer fusion-failing) | `ce_keep_note`: **4/4** new traps fusion returned forbidden; 10/10 on re-eval | Yes |
| R1 Hub-free exclusion smoke | `test_run_fixture_eval_excludes_hard_neg_from_hit_at_k` in `tests/test_eval_neg_at_k.py` | Yes |
| Live eval + honesty; flat shippable under E3 | Note: fusion/CE `neg_at_k` **0.0** (0/10); easy hit@K **1.0**; `ce_keep=false`; **not** eval-complete | Yes |
| No CE lift ads; `ce_keep` not from `neg_at_k` | INTERVIEW / GETTING_STARTED / PORTFOLIO_VISION / README / `ce_keep_note` | Yes |
| No `CE_ENABLED` / embedding / private flip | `CE_ENABLED=True`; `EMBEDDING_MODEL=nomic-embed-text`; no flip work in commit | Yes |
| Harness formula unchanged | `src/eval/__init__.py` **not** in Implement diff (275 lines); metric contract preserved | Yes |

## Re-verification this Review

```text
HEAD: ec6d8fe (matches Implement)
uv run pytest tests/test_eval_ce_honesty.py tests/test_eval_neg_at_k.py -q
→ 16 passed
fixtures/manifest.json → 8 source_ids (includes combsum-fusion-07, bi-encoder-rerank-08)
wc -l fixtures/eval/golden_cases.jsonl → 28
hard_negative count → 10 (hn1–hn10)
CE_ENABLED=True; EMBEDDING_MODEL=nomic-embed-text
```

Live Ollama+HF eval **not** re-run this Review — Implement recorded metrics match honesty docs (`ce_keep_note`); Hub-free unit coverage re-confirmed. Flat `neg_at_k` is an **expected shippable** outcome under E3 — not a defect.

## Findings (severity)

### None — must-fix

No DoD violations. No false CE-lift claims. No eval-complete auto-check. No private flip. No keep-policy regression. Confusable twins + new traps match B1 soft pins.

### Soft residuals (park / later Align — not blocking ship)

| ID | Finding | Why not blocking | Smallest later fix |
|----|---------|------------------|--------------------|
| G08-R1 | Gather / Ready-check artifacts still speak pre-Implement readiness in places | Implement + Review + `ce_keep_note` are SSOT for metrics | Align: superseded banners on Gather/Ready-check |
| G08-R2 | Guide 07 residuals R2 (`must_cite` validate) / R3 (easy RetrievalError counting) still parked | Explicitly out of Guide 08; not regressions | Leave parked unless Tom unlocks |
| G08-R3 | Live eval not re-run in Review | Same Guide 07 Review pattern; metrics already in `ce_keep_note` | Optional re-run at Align if Tom wants |

### Architectural drift

**None.** KB5 stack unchanged; KB1 at soft ceiling (8); Guide 06/07 keep math preserved; fixture-first only; no ranking rewrite.

### Weak tests?

**Adequate.** Guide 07 R1 gap is **closed** by folded exclusion smoke. Existing neg_ok / validate / keep tests remain green (16 passed with honesty suite).

### Doc honesty (delivery path)

Operator-facing docs match Implement metrics (8 fixtures; 28 goldens; flat `neg_at_k` both arms; `ce_keep=false`; eval-complete unchecked). No delivery honesty bug requiring a fix-first patch.

## Smallest refinement set

**Ship as-is.** No code patches this Review.

Optional later Align: superseded banners on Gather/Ready-check; tick guide Review section when authorized.

## QUALITY_STANDARD §5

Assumptions checked against `ec6d8fe` + re-run pytest + fixture/golden counts + honesty grep; spoke stayed in Guide 08 Review slice; no scope creep into CE flip / eval-complete theater / private flip / Align; findings written here + handoff; shippable call honest — flat CE is not treated as failure under E3.

## Stop

Review complete. **Await Tom authorize Align** (optional polish) or close slice — do not self-start Align/Implement.
