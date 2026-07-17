# Ready-check — Guide 07 hard-negative / `neg_at_k`

> **Superseded (Align 2026-07-17):** Pre-Implement Ready-check only. Guide 07 **shipped** — Implement `ff9ad33`, Review shippable as-is (`docs/2026-07-17_guide07_hard_negative_review.md`). “Ready for Implement?” / pre-change code-seam notes below are **historical**. Current metrics: [`docs/2026-07-12_ce_keep_note.md`](./2026-07-12_ce_keep_note.md).

**Date:** 2026-07-17  
**Repo:** `ai-knowledge-base-public`  
**Stage:** Ready check before code  
**Mode:** spoke  
**Guide:** `docs/dev_guides/2026-07-17_dev_guide_07_hard_negative_neg_at_k.md`  
**Context:** `docs/2026-07-17_guide07_hard_negative_neg_at_k_context_summary.md`  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_guide07_ready_check_pass105_handoff.md`  
**Align status:** **Superseded** by Implement + Review (was: Ready for Implement after authorize)

## Verdict

| Question | Answer |
|----------|--------|
| Ready for Implement? | **Yes** — after Tom authorizes Implement Stage |
| Implement readiness score | **8.8 / 10** |
| Further Refine-dev-guide required? | **No** |
| Implementation started this stage? | **No** |

## Alignment check

| Check | Result | Evidence |
|-------|--------|----------|
| Context ↔ Guide | **Aligned** | Same Guide 06 `neg_at_k` formula; exclude hard-neg from hit@K; 4–6 cases; `ce_keep` not from neg alone; no fake lift / CE flip / private flip / KB4 change |
| Guide ↔ code seams (pre-change) | **Aligned** | `src/eval/__init__.py` still scores hit@K over **all** cases and has no `forbidden_source_ids` / `neg_at_k` — exactly Phases A–C change |
| Guide ↔ Guide 06 keep | **Aligned** | Soft pin: `_decide_ce_keep` prefers `easy_cases`; never keep from `neg_at_k` alone |
| Locks | **Honored** | Case count 4–6 (max 8); B2 mandatory; per-arm `neg_at_k`; validate → `ValueError` |

## Blast radius / rollback

- **Code:** `src/eval/__init__.py` + new `tests/test_eval_neg_at_k.py`  
- **Data:** append `hn*` to `golden_cases.jsonl` only (`g1`–`g18` preserved)  
- **Docs:** `ce_keep_note`, GETTING_STARTED, INTERVIEW, PORTFOLIO_VISION  
- **Rollback:** revert those commits or delete `hn*` + harness fields  
- **Clear:** Yes

## Edge cases

Planned: empty/unknown forbidden → raise; multi-forbidden; CE degrade still scores neg_ok; RetrievalError; zero hard-neg → `neg_at_k: null`; B2 ship-with-note if <4 fusion-failing traps. **Sufficient.**

## Soft residuals (why not 10)

1. Exact `hn*` query wording is Implement craft.  
2. B2 may yield fewer than 4 fusion-currently-failing traps (guide allows ship + note).  
3. Phase C live eval needs Ollama + HF MiniLM (documented Guide 06 footgun — runtime proof, not missing design).  
4. Minor: whether docs tables echo total `cases` vs `easy_cases` labels — craft only.

**Recommendation:** Park residuals; **no** further Refine.

## QUALITY_STANDARD §5

Assumptions checked against guide + current eval code; spoke stayed in slice; no Implement; findings in this note + handoff; numeric score reported; open decisions in chat reply.
