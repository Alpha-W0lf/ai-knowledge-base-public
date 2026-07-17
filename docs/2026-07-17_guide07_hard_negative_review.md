# Review — Guide 07 hard-negative / `neg_at_k` Implement

**Date:** 2026-07-17  
**Repo:** `ai-knowledge-base-public`  
**Stage:** Review implementation  
**Mode:** spoke  
**Implement commit:** `ff9ad33`  
**Guide:** `docs/dev_guides/2026-07-17_dev_guide_07_hard_negative_neg_at_k.md`  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_guide07_review_pass110_handoff.md`

## Verdict

| Call | Value |
|------|--------|
| Shippable as-is? | **Yes** |
| Fix-first required? | **No** |
| Must-fix patches this Review? | **None** |
| Ready for Align docs? | Optional only — operator honesty already aligned; Gather/Ready-check meta notes can wait |

## Guide DoD mapping

| Guide requirement | Evidence | Pass? |
|-------------------|----------|-------|
| Per-arm `neg_at_k` / `neg_ok_count` / `hard_negative_cases` / `easy_cases` | `src/eval/__init__.py` `_run` arm dict | Yes |
| Hard-neg excluded from hit@K + CE-success / keep coverage | Easy-only loop + `easy_details` filter + `_decide_ce_keep` prefers `easy_cases` | Yes |
| Invalid hard-neg schema → `ValueError` | `validate_hard_negatives` + tests | Yes |
| 4–6 `hn*`; `g1`–`g18` preserved | JSONL = **24** (18+6); ids unique; themes match guide table | Yes |
| B2 spot-check documented | `ce_keep_note`: **6/6** fusion returned forbidden | Yes |
| `tests/test_eval_neg_at_k.py` | neg_ok, validate, keep/`easy_cases`, ignore `neg_at_k` for keep | Yes |
| Eval + honesty docs; no fake lift; `ce_keep` not from neg | Note + GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION: fusion/CE `neg_at_k` **0.0**, `ce_keep=false` | Yes |
| No CE / embedding / private flip | `CE_ENABLED=True`; `EMBEDDING_MODEL=nomic-embed-text` unchanged | Yes |
| No top-level `neg_at_k` | Return dict only `fusion` / `ce` / `ce_keep` / `ce_justify` | Yes |

## Re-verification this Review

```text
uv run pytest tests/test_eval_ce_honesty.py tests/test_eval_neg_at_k.py -q
→ 15 passed
wc -l fixtures/eval/golden_cases.jsonl → 24
CE_ENABLED=True; EMBEDDING_MODEL=nomic-embed-text
Implement HEAD: ff9ad33 (clean working tree)
```

Live Ollama+HF eval not re-run this Review — Implement recorded metrics match honesty docs; Hub-free unit coverage re-confirmed.

## Findings (severity)

### None — must-fix

No DoD violations, no false CE-lift claims, no keep-policy regression from hard-neg inflation.

### Soft residuals (park / later Align — not blocking ship)

| ID | Finding | Why not blocking | Smallest later fix |
|----|---------|------------------|--------------------|
| R1 | No monkeypatched `run_fixture_eval` test that asserts hard-neg excluded from `hits` / `hit_at_k` | Pure helpers + keep/`easy_cases` tests + live Implement eval cover the contract | Thin smoke with stubbed `retrieve` |
| R2 | `validate_hard_negatives` does not enforce `must_cite: false` | All six shipped rows already set it; fail-closed on forbidden ids is the load-bearing check | Optional assert in validate |
| R3 | Easy-case `RetrievalError` omits row from `easy_cases` count (pre-Guide-07 pattern) | Keep/partial logic still fail-closed via CE-success coverage; hard-neg errors counted as `neg_ok=false` | Optional `retrieval_error` stage key |
| R4 | Gather / Ready-check notes still speak pre-Implement readiness language | Historical process artifacts; operator path (`ce_keep_note`, GETTING_STARTED, INTERVIEW, PORTFOLIO_VISION) is current | Align: superseded banners |
| R5 | README still thin on Guide 07 `neg_at_k` (points at `ce_keep_note`) | Soft pins did not require README; stranger path is GETTING_STARTED | Optional one-line README |

### Architectural drift

**None.** KB5 stack unchanged; Guide 06 keep math preserved (ignores `neg_at_k`); fixture-first only; file ≤300 lines (`src/eval/__init__.py` = 275).

### Weak tests?

Adequate for Guide 07 DoD. Strongest gap is R1 (integration exclusion smoke) — not a ship blocker given live eval evidence in `ce_keep_note`.

### Doc honesty (delivery path)

Operator-facing docs match Implement metrics (flat `neg_at_k` both arms; `ce_keep=false`; not eval-complete). No delivery honesty bug requiring Align in this Review.

## Smallest refinement set

**Ship as-is.** No code patches this Review.

Optional later (only if Tom wants Align): R1 smoke test; R4 superseded banners on Gather/Ready-check.

## QUALITY_STANDARD §5

Assumptions checked against `ff9ad33` + re-run pytest; spoke stayed in Guide 07 slice; no scope creep into CE flip / easy golden growth / Align; findings written here + handoff; shippable call honest; no silent rubber-stamp.

## Stop

Review complete. **Do not** self-start Align. Await Tom for Align or close slice.
