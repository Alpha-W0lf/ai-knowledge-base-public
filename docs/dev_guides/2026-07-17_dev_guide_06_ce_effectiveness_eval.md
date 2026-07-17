# Dev Guide 06 — CE-effectiveness eval (load-first honesty)

**Date:** 2026-07-17  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 06 — make `ranking_stage=ce` measurable; surface CE degrade errors; stage-gated eval metrics; re-run N=18 ablation; refresh honesty docs  
**Stage that authored this:** Write-dev-guide  
**Status:** Draft (await Refine-dev-guide / Ready-check before Implement)

**Context SSOT:** `ai-knowledge-base-public/docs/2026-07-17_ce_effectiveness_eval_context_summary.md`  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`  
**Prerequisite:** Guide 05 done (N=18 goldens). Public corpus = committed `fixtures/` only.

---

## Objective

1. Stop silently swallowing CE failures: on degrade, set `RetrievalResult.error` so operators see *why* `ranking_stage=fusion_degraded`.  
2. Fix eval honesty: report **stage counts** and **CE-success hit@K** (only cases with `ranking_stage=ce`); never treat degrade as a CE win.  
3. Fix `ce_keep` / `ce_justify` when CE-success count is 0 (“not measured,” not adapter-theater).  
4. Re-run `uv run python -m src.eval` on existing **N=18**; update `ce_keep_note` + related docs to match.  
5. Document HF MiniLM cache warm as an eval footgun in GETTING_STARTED.  
6. Soft-pin a hard-negative metric formula for a **later** guide — **do not** add hard-negative cases in this Implement.

**Success signal:** A stranger (or agent) can run fixture eval, see either mostly `ranking_stage=ce` with clear metrics, or `fusion_degraded` **with an error string**, and docs never claim unearned CE lift.

---

## Learning notes (interview-portable)

1. **Ablation requires the treatment arm** — Comparing fusion vs “CE-attempt” is meaningless if every attempt degrades to fusion.  
2. **Fail-open ≠ silent failure** — Returning fused ranks on CE error is correct; omitting the exception type is an observability bug.  
3. **Ceiling metrics** — Fusion hit@K already 1.0 on easy goldens; flat CE-success hit@K is honest, not a bug. Lift needs discriminative cases later.

---

## References (paths only)

- `ai-knowledge-base-public/docs/2026-07-17_ce_effectiveness_eval_context_summary.md`
- `ai-knowledge-base-public/docs/2026-07-12_ce_keep_note.md`
- `ai-knowledge-base-public/docs/dev_guides/2026-07-16_dev_guide_05_eval_golden_growth.md`
- `ai-knowledge-base-public/docs/PORTFOLIO_VISION.md`
- `ai-knowledge-base-public/docs/ARCHITECTURE.md`
- `ai-knowledge-base-public/GETTING_STARTED.md`
- `ai-knowledge-base-public/INTERVIEW.md`
- `ai-knowledge-base-public/fixtures/eval/golden_cases.jsonl`
- `ai-knowledge-base-public/src/search.py`
- `ai-knowledge-base-public/src/rerank.py`
- `ai-knowledge-base-public/src/eval/__init__.py`
- `ai-knowledge-base-public/src/models.py`
- `ai-knowledge-base-public/src/config.py`
- `ai-knowledge-base-public/tests/tests_retrieval_spine.py`
- `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`

---

## Architecture constraints (binding)

1. **KB5 stack unchanged:** hybrid (vector + FTS) → RRF fusion → pluggable local CE; on CE failure → fused ranks + `ranking_stage=fusion_degraded` (never silent vector-only under hybrid+CE claim).  
2. **CE model / enablement:** keep `CE_MODEL_ID=cross-encoder/ms-marco-MiniLM-L-6-v2` and `CE_ENABLED=True` — **no flip** without human authorize.  
3. **KB4 embeddings:** `nomic-embed-text` @ 768 — no change.  
4. **No private tip scrub / remote flip**; public sibling is SSOT.  
5. **No golden-N expansion theater** in this guide (stay at N=18).  
6. **No fake lift** — do not advertise CE relevance wins without CE-success evidence.  
7. **Hard negatives:** soft-pin formula below; **do not** ship cases or empty `expected_source_ids` into today’s hit@K.

---

## Soft pins

| Pin | Locked default |
|-----|----------------|
| Guide focus | CE load observability + eval honesty + re-run N=18 — **not** golden growth |
| Degrade error | On CE `except Exception as e:` in `retrieve`: set `RetrievalResult.error = f"{type(e).__name__}: {e}"` truncated to **500** chars; keep fail-open fused ranks; optional one-line `logging.warning` / stderr |
| Eval stage counts | On CE-attempt arm dict: `stage_counts: {"ce": int, "fusion_degraded": int, "fusion": int, ...}` from `details[].ranking_stage` (only keys that appear) |
| Attempt hit@K | Keep existing `hit_at_k` / `hits` on the CE-attempt arm as **attempt/fallback** (may include degraded cases) — document in justify/docs that it is **not** CE-success |
| CE-success metrics | Add `ce_success_cases` (count where `ranking_stage=="ce"`) and `ce_success_hit_at_k` = hits among those cases / `ce_success_cases` (define as `null` or omit if `ce_success_cases==0`) |
| `ce_keep` / `ce_justify` | If `ce_success_cases == 0` → `ce_keep=false`, justify must say **CE effectiveness not measured** (cite 0 `ranking_stage=ce`). Lift (`ce_keep=true`) only if `ce_success_cases == cases` **and** `ce_success_hit_at_k > fusion.hit_at_k`. Flat CE-success vs fusion → `ce_keep=false` + no-lift honesty (seam may stay on; no marketing) |
| Model / flags | Do not change `CE_ENABLED` or `CE_MODEL_ID` |
| Operator footgun | GETTING_STARTED: HF cache warm for MiniLM (successful hybrid search with CE, or Hub download of `cross-encoder/ms-marco-MiniLM-L-6-v2`); Ollama still required for embeds |
| Tests | Extend D4: `force_ce_failure=True` → `ranking_stage=fusion_degraded` **and** `result.error` non-empty containing forced failure text. Add or extend: Identity/mock adapter with CE on → `ranking_stage=ce` and `error is None` |
| Golden file | **Do not modify** `golden_cases.jsonl` in this guide |
| Files likely touched | `src/search.py`, `src/eval/__init__.py`, `tests/tests_retrieval_spine.py`, `docs/2026-07-12_ce_keep_note.md`, `GETTING_STARTED.md`, `INTERVIEW.md`, `docs/PORTFOLIO_VISION.md` as needed |
| Non-goals | Golden N growth; hard-negative cases; `CE_ENABLED` flip; private scrub; embedding change; marketing lift |

### Hard-negative metric (soft-pin — later guide only; no cases this Implement)

Cases with `kind: "hard_negative"` carry non-empty `forbidden_source_ids`. A case is **neg_ok** iff none of those ids appear in the top-K returned `source_id`s. Report `neg_at_k = (# hard_negative cases with neg_ok) / (# hard_negative cases)`. **Exclude** `kind=hard_negative` rows from the hit@K denominator entirely. Never use empty `expected_source_ids` as a hard-negative stand-in. **This guide does not add such cases or harness code** — soft-pin only for the follow-on discriminative guide.

---

## Acceptance criteria

- [ ] Degrade path sets `RetrievalResult.error` (type + message, ≤500 chars); fused order preserved; `ranking_stage=fusion_degraded`  
- [ ] Eval JSON includes `stage_counts` on CE-attempt arm  
- [ ] Eval JSON includes `ce_success_cases` + `ce_success_hit_at_k` (or null/omit when 0 successes)  
- [ ] `ce_justify` says “not measured” when `ce_success_cases == 0`  
- [ ] Tests cover forced-failure `error` + CE-success path with mock/identity that returns scores without Hub (or real CE if env allows)  
- [ ] `uv run python -m src.eval` re-run recorded; `ce_keep_note` matches printed metrics  
- [ ] GETTING_STARTED documents HF MiniLM warm footgun; INTERVIEW / PORTFOLIO_VISION honesty aligned if metrics changed  
- [ ] Still not eval-complete / v1 Done; no fake lift; no CE default flip; no golden growth; no hard-negative cases shipped  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Refine-dev-guide / Ready-check.**

### Phase A — Observability (CE load path)

- [ ] **A1.** In `src/search.py` CE `try/except`: capture `Exception as e`; on degrade set envelope `error` per soft pin; do not change fail-open semantics.  
- [ ] **A2.** Ensure `RetrievalResult(..., error=...)` is passed on both success (`error=None`) and degrade paths for hybrid+CE.  
- [ ] **A3.** Extend `test_ce_forced_failure_degrades_to_fusion` to assert `result.error` is set and mentions forced failure.  

### Phase B — Eval harness honesty

- [ ] **B1.** In `src/eval/__init__.py` `_run`: after details, compute `stage_counts` from `ranking_stage`.  
- [ ] **B2.** Compute `ce_success_cases` / `ce_success_hit_at_k` only over `ranking_stage == "ce"`.  
- [ ] **B3.** Rewrite `ce_keep` / `ce_justify` per soft pin (not measured / lift / no-lift / worse).  
- [ ] **B4.** Include new fields in returned CE-arm dict and top-level print (keep backward-compatible keys where practical).  
- [ ] **B5.** Add/adjust unit coverage for justify when all degraded (can drive via mock adapter raising, or inject details — prefer calling `_run` path with a raising adapter if easy).  

### Phase C — Re-run + honesty docs

- [ ] **C1.** Ensure Ollama + HF MiniLM available (warm cache if needed); run `uv run python -m src.eval`.  
- [ ] **C2.** If CE-success count is 0: capture `error` from details/timings path into `ce_keep_note`; do **not** invent lift; document blocker. Prefer fixing env and re-running until `ce_success_cases > 0` when feasible on this machine.  
- [ ] **C3.** Update `docs/2026-07-12_ce_keep_note.md` with N, fusion hit@K, stage_counts, ce_success_*, `ce_keep`, justify verbatim.  
- [ ] **C4.** Update GETTING_STARTED (HF footgun + eval honesty bullets); INTERVIEW / PORTFOLIO_VISION if wording would otherwise contradict the new run.  
- [ ] **C5.** Stop. No golden growth. No hard-negative cases. No `CE_ENABLED` flip.

### Phase D — Hard-negative (docs only)

- [ ] **D1.** Optionally add one sentence to INTERVIEW or `ce_keep_note` pointing at Guide 06 soft-pin for future `neg_at_k` — **no** `golden_cases.jsonl` edits.

---

## Verification / Definition of Done

```bash
# From ai-knowledge-base-public/
wc -l fixtures/eval/golden_cases.jsonl   # expect exactly 18 (unchanged)
uv run pytest tests/tests_retrieval_spine.py -q -k 'ce_forced_failure or ce_disabled'
uv run python -m src.eval                # needs Ollama + CE model load
# Inspect printed JSON for: stage_counts, ce_success_cases, ce_success_hit_at_k, ce_keep, ce_justify
rg -n 'not measured|stage_counts|ce_success|fusion_degraded|HF|MiniLM|ce_keep' \
  docs/2026-07-12_ce_keep_note.md GETTING_STARTED.md INTERVIEW.md docs/PORTFOLIO_VISION.md
```

**DoD:**

1. Forced CE failure test asserts `fusion_degraded` **and** non-empty `error`.  
2. Eval output distinguishes attempt vs CE-success; zero-success justify = not measured.  
3. `ce_keep_note` matches the latest eval run; no unearned lift ads.  
4. GETTING_STARTED lists HF MiniLM warm as footgun.  
5. N=18 goldens unchanged; `CE_ENABLED` unchanged; no private/embedding scope.  
6. Hard-negative formula soft-pinned in this guide only — no cases shipped.

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| MCP/CLI expose `error` strings | Already supported on `to_public_dict`; truncate; no secrets/paths |
| Breaking consumers of eval JSON | Keep old keys; add fields; document attempt vs success |
| Claiming lift from flat ceiling | `ce_keep` requires strict inequality on CE-success subset |
| Env still cannot load CE | Record `error`; honesty “not measured”; operator footgun — do not flip CE off as “fix” |
| Scope into hard-negative Implement | Soft-pin only; Phase D docs optional; no golden edits |
| Over-logging | Truncate to 500 chars; one warning line max |

### Rollback

Revert `search.py` / `eval` / tests / honesty doc commits; goldens untouched so rollback is code+docs only.

---

## Edge-case handling

| Case | Behavior |
|------|----------|
| Hub/proxy/cache fail | `fusion_degraded` + `error` populated; eval stage_counts show all degraded; justify not measured |
| CE loads mid-run after first fail | Per-query stage may mix; success metrics only count `ce` rows |
| Fusion hit@K=1.0 and CE-success=1.0 | `ce_keep=false`; document ceiling / need discriminative set later |
| Ollama down | Retrieve fails before CE; document fail (existing); not a CE keep flip |
| Empty query / FTS fail | Unchanged fail-closed / RetrievalError paths |
| `force_ce_failure` | Degrade + error for tests |
| Hard-negative temptation | Refuse empty expected; follow soft-pin in a later guide |

---

## Stop conditions

- Observability + harness honesty + eval re-run + docs landed  
- **No** golden-N growth  
- **No** hard-negative cases  
- **No** `CE_ENABLED` / embedding / private flip  
- **No** marketing CE lift without CE-success evidence  
- Stop for human if asked to fake lift or flip CE default without gate  

---

## Ready for Refine-dev-guide / Ready-check?

**Yes** after this Write. Soft pins and ordered steps are executable. Residual craft for Refine: field naming nitpicks, test strategy for justify-without-Hub, whether to keep attempt `hit_at_k` renamed in prose only.

**Do not Implement until Ready-check passes and Tom authorizes Implement.**
