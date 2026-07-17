# Ready-check — Guide 06 CE-effectiveness eval

**Date:** 2026-07-17  
**Repo:** `ai-knowledge-base-public`  
**Stage:** Ready check before code  
**Mode:** spoke  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`  
**Authorize:** `second_brain/docs/2026-07-17_hub_authorize_wave5_ready_check.md`  
**Guide:** `docs/dev_guides/2026-07-17_dev_guide_06_ce_effectiveness_eval.md`  
**Context:** `docs/2026-07-17_ce_effectiveness_eval_context_summary.md`

## Verdict

| Question | Answer |
|----------|--------|
| Ready for Implement? | **Yes** — after Tom authorizes Implement Stage |
| Implement readiness score | **8.9 / 10** |
| Further Refine-dev-guide required? | **No** |
| Implementation started this stage? | **No** |

## Alignment check

| Check | Result | Evidence |
|-------|--------|----------|
| Context ↔ Guide | **Aligned** | Both CE load-first; `RetrievalResult.error`; stage-gated CE-success metrics; N=18 no golden growth; no CE flip / private flip / KB4 change |
| Guide ↔ code seams | **Aligned (pre-change)** | Bare `except Exception` in `src/search.py` ~190–195 (no `error` set yet); `RetrievalResult.error` already on `src/models.py`; eval keep logic still uses attempt `hit_at_k` in `src/eval/__init__.py` — exactly what Guide 06 Phases A–B change |
| Guide ↔ `ce_keep_note` | **Aligned intent** | Note already records 18/18 `fusion_degraded` / not measured; Guide 06 Phase C refreshes fields after harness fix |
| Tom / hub locks | **Honored** | Soft locks in wave-5 authorize match Guide 06 header locks |
| `neg_at_k` | **Soft-pin only** | Formula in guide; no cases this Implement — coherent |

## Blast radius / rollback

- **Code:** `search.py`, `eval/__init__.py`, retrieval + eval tests — fail-open semantics unchanged; add `error` + metrics fields.  
- **Docs:** `ce_keep_note`, GETTING_STARTED, optionally INTERVIEW / PORTFOLIO_VISION.  
- **MCP:** `error` already in `to_public_dict` when set — truncate 500 pinned.  
- **Goldens:** untouched → rollback = revert code+docs commits only.  
- **Clear:** Yes.

## Edge cases

Planned in guide table: Hub/proxy fail, partial degrade, fusion ceiling 1.0, Ollama down, forced failure tests, hard-negative temptation refused. **Sufficient for Implement.**

## Soft residuals (why not 10)

1. Exact `ce_justify` sentence templates are Implement craft (rules pinned; wording not verbatim).  
2. Optional `logging.warning` / Phase D one-liner — non-DoD.  
3. Phase C live `uv run python -m src.eval` needs Ollama + HF MiniLM on the Implement machine — documented footgun, not a missing design pin.  
4. Stub vs `IdentityReranker` for A4 — both allowed; Implement picks one.

**Recommendation:** Park residuals; do **not** another Refine pass.

## QUALITY_STANDARD §5

Assumptions eliminated with path evidence; spoke stayed in slice; no scope creep; no Implement; findings written to this note + handoff; numeric score reported; open decisions surfaced in chat reply.
