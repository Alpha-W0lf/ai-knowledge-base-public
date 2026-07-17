# Dev Guide 06 — CE-effectiveness eval (load-first honesty)

**Date:** 2026-07-17  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 06 — make `ranking_stage=ce` measurable; surface CE degrade errors; stage-gated eval metrics; re-run N=18 ablation; refresh honesty docs  
**Stage that authored this:** Write-dev-guide; **Refine-dev-guide** (pass 1, 2026-07-17)  
**Status:** Ready-check **PASSED** 2026-07-17 (Implement readiness **8.9/10**) — **do not Implement until Tom authorizes Implement Stage**

**Context SSOT:** `ai-knowledge-base-public/docs/2026-07-17_ce_effectiveness_eval_context_summary.md`  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`  
**Prerequisite:** Guide 05 done (N=18 goldens). Public corpus = committed `fixtures/` only.

**Tom locks (do not reopen):** CE load-first; `RetrievalResult.error` on degrade; stage-gated CE-success metrics; `neg_at_k` soft-pin with **no hard-negative cases** this Implement; no fake lift; no `CE_ENABLED` flip; no private flip; no KB4 embedding change.

---

## Objective

1. Stop silently swallowing CE failures: on degrade, set `RetrievalResult.error` so operators see *why* `ranking_stage=fusion_degraded`.  
2. Fix eval honesty: report **stage counts** and **CE-success hit@K** (only cases with `ranking_stage=ce`); never treat degrade as a CE win.  
3. Fix `ce_keep` / `ce_justify` when CE-success count is 0 (“not measured,” not adapter-theater); never use attempt/fallback hit@K for keep decisions.  
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
| Degrade error | On CE `except Exception as e:` in `retrieve` (`src/search.py` ~190): set envelope `error = f"{type(e).__name__}: {e}"` truncated to **500** chars; keep fail-open fused ranks; **optional** one-line `logging.warning` (not required for DoD) |
| Eval details | Each CE-attempt detail row includes `error` when `result.error` is set (so `ce_keep_note` can quote a real string) |
| Eval stage counts | On **CE-attempt arm only**: `stage_counts: {"ce": int, "fusion_degraded": int, ...}` from `details[].ranking_stage` (only keys that appear). Fusion-only arm need not add stage_counts |
| Attempt hit@K | Keep existing `hit_at_k` / `hits` on CE-attempt arm as **attempt/fallback** (may include degraded). **Never** use attempt `hit_at_k` for `ce_keep` |
| CE-success metrics | `ce_success_cases` = count `ranking_stage=="ce"`; `ce_success_hits` = hits among those; `ce_success_hit_at_k` = `ce_success_hits / ce_success_cases` if `ce_success_cases > 0` else JSON **`null`** (do not omit key — always present on CE arm) |
| `ce_keep` / `ce_justify` | Decide **only** from fusion arm + CE-success fields via helper `_decide_ce_keep(fusion: dict, ce: dict) -> tuple[bool, str]` (see Phase B). Rules below |
| Keep decision rules | (1) `ce_success_cases == 0` → keep=false, justify contains **“not measured”** and cites 0 `ranking_stage=ce`. (2) `0 < ce_success_cases < cases` → keep=false, justify notes **partial degrade** (not lift). (3) `ce_success_cases == cases` and `ce_success_hit_at_k > fusion["hit_at_k"]` → keep=true, lift justify. (4) equal → keep=false, no-lift honesty (seam may stay on). (5) less → keep=false, CE reduced hit@K |
| Model / flags | Do not change `CE_ENABLED` or `CE_MODEL_ID` |
| Operator footgun | GETTING_STARTED: HF cache warm for MiniLM (hybrid search with CE, or Hub download of `cross-encoder/ms-marco-MiniLM-L-6-v2`); Ollama required for embeds |
| Tests — degrade | Extend D4: `force_ce_failure=True` → `fusion_degraded` **and** `result.error` non-empty containing `"forced CE failure"` |
| Tests — CE stage without Hub | Stub `CrossEncoderAdapter` that sets `rerank_score` and returns candidates (or `IdentityReranker` is enough for stage=`ce`); assert `ranking_stage=ce` and `error is None` |
| Tests — keep/justify | Unit-test `_decide_ce_keep` with synthetic arm dicts: all-degraded; partial; flat full-CE; lift; worse — **no** LanceDB/Ollama/Hub |
| Golden file | **Do not modify** `golden_cases.jsonl` |
| Files likely touched | `src/search.py`, `src/eval/__init__.py`, `tests/tests_retrieval_spine.py`, new thin `tests/test_eval_ce_honesty.py` (or equivalent), `docs/2026-07-12_ce_keep_note.md`, `GETTING_STARTED.md`, `INTERVIEW.md`, `docs/PORTFOLIO_VISION.md` as needed |
| Non-goals | Golden N growth; hard-negative cases/harness; `CE_ENABLED` flip; private scrub; embedding change; marketing lift |

### Hard-negative metric (soft-pin — later guide only; no cases this Implement)

Cases with `kind: "hard_negative"` carry non-empty `forbidden_source_ids`. A case is **neg_ok** iff none of those ids appear in the top-K returned `source_id`s. Report `neg_at_k = (# hard_negative cases with neg_ok) / (# hard_negative cases)`. **Exclude** `kind=hard_negative` rows from the hit@K denominator entirely. Never use empty `expected_source_ids` as a hard-negative stand-in. **This guide does not add such cases or harness code.**

---

## Acceptance criteria

- [ ] Degrade path sets `RetrievalResult.error` (type + message, ≤500 chars); fused order preserved; `ranking_stage=fusion_degraded`  
- [ ] Eval CE-arm JSON includes `stage_counts`, `ce_success_cases`, `ce_success_hits`, `ce_success_hit_at_k` (`null` when 0 successes)  
- [ ] Detail rows include `error` when envelope has one  
- [ ] `ce_keep` decided only via `_decide_ce_keep` rules above; zero-success justify includes “not measured”  
- [ ] Tests: forced-failure `error`; CE stage via stub/identity without Hub; `_decide_ce_keep` table cases  
- [ ] `uv run python -m src.eval` re-run recorded; `ce_keep_note` matches printed metrics (including stage_counts / ce_success_* / sample error if degraded)  
- [ ] GETTING_STARTED documents HF MiniLM warm footgun; INTERVIEW / PORTFOLIO_VISION honesty aligned if metrics changed  
- [ ] Still not eval-complete / v1 Done; no fake lift; no CE default flip; no golden growth; no hard-negative cases shipped  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Refine-dev-guide / Ready-check.**

### Phase A — Observability (CE load path)

- [ ] **A1.** In `src/search.py` CE `try/except`: `except Exception as e:`; on degrade set `error` per soft pin; fail-open unchanged.  
- [ ] **A2.** Pass `error=None` on CE success / fusion-only; pass `error=...` on degrade in `RetrievalResult(...)`.  
- [ ] **A3.** Extend `test_ce_forced_failure_degrades_to_fusion` to assert `result.error` contains `"forced CE failure"`.  
- [ ] **A4.** Add stub/identity CE-on test: `ranking_stage=ce`, `error is None` (no Hub).  

### Phase B — Eval harness honesty

- [ ] **B1.** In `_run` details: include `"error": result.error` when set.  
- [ ] **B2.** After details: compute `stage_counts`; `ce_success_cases` / `ce_success_hits` / `ce_success_hit_at_k` (`null` if 0). Attach to returned arm dict (CE path always; fusion arm may skip success fields).  
- [ ] **B3.** Extract `_decide_ce_keep(fusion, ce) -> tuple[bool, str]` implementing the five rules; call it from `run_fixture_eval` instead of inline attempt-`hit_at_k` compare.  
- [ ] **B4.** Keep backward-compatible keys (`hit_at_k`, `hits`, `details`, …); add new fields alongside.  
- [ ] **B5.** Add `tests/test_eval_ce_honesty.py` (or equivalent) covering `_decide_ce_keep` for: all-degraded; partial; flat; lift; worse.  

### Phase C — Re-run + honesty docs

- [ ] **C1.** Warm HF MiniLM if needed; ensure Ollama; run `uv run python -m src.eval`.  
- [ ] **C2.** If `ce_success_cases == 0`: quote `error` from a detail row into `ce_keep_note`; no lift; prefer env fix + re-run until `ce_success_cases > 0` when feasible on this machine.  
- [ ] **C3.** Update `docs/2026-07-12_ce_keep_note.md` with N, fusion hit@K, `stage_counts`, `ce_success_*`, `ce_keep`, justify verbatim.  
- [ ] **C4.** Update GETTING_STARTED (HF footgun + eval honesty); INTERVIEW / PORTFOLIO_VISION if wording would contradict the new run.  
- [ ] **C5.** Stop. No golden growth. No hard-negative cases. No `CE_ENABLED` flip.

### Phase D — Hard-negative (docs only, optional)

- [ ] **D1.** Optional one sentence in INTERVIEW or `ce_keep_note` pointing at Guide 06 `neg_at_k` soft-pin — **no** `golden_cases.jsonl` edits. Skipping D1 does **not** fail DoD.

---

## Verification / Definition of Done

```bash
# From ai-knowledge-base-public/
wc -l fixtures/eval/golden_cases.jsonl   # expect exactly 18 (unchanged)
uv run pytest tests/tests_retrieval_spine.py tests/test_eval_ce_honesty.py -q
uv run python -m src.eval                # needs Ollama + CE model load
# Inspect printed JSON for: stage_counts, ce_success_cases, ce_success_hit_at_k, ce_keep, ce_justify
rg -n 'not measured|stage_counts|ce_success|fusion_degraded|HF|MiniLM|ce_keep' \
  docs/2026-07-12_ce_keep_note.md GETTING_STARTED.md INTERVIEW.md docs/PORTFOLIO_VISION.md
```

**DoD:**

1. Forced CE failure test asserts `fusion_degraded` **and** non-empty `error` mentioning forced failure.  
2. Stub/identity CE-on test asserts `ranking_stage=ce` without Hub.  
3. `_decide_ce_keep` unit tests cover not-measured / partial / flat / lift / worse.  
4. Eval JSON has attempt vs CE-success fields; `ce_success_hit_at_k` is `null` when zero successes.  
5. `ce_keep_note` matches the latest eval run; no unearned lift ads.  
6. GETTING_STARTED lists HF MiniLM warm as footgun.  
7. N=18 goldens unchanged; `CE_ENABLED` unchanged; no private/embedding scope; no hard-negative cases.

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| MCP/CLI expose `error` strings | Already on `to_public_dict`; truncate 500; no secrets/paths |
| Breaking consumers of eval JSON | Keep old keys; add fields; document attempt ≠ CE-success |
| Claiming lift from attempt hit@K | `_decide_ce_keep` ignores attempt `hit_at_k` |
| Claiming lift under partial degrade | Rule (2): keep=false until all cases `ce` |
| Env still cannot load CE | Record `error` in details + note; operator footgun; do not flip CE off as “fix” |
| Scope into hard-negative Implement | Soft-pin only; D1 optional; no golden edits |
| Helper extract churn | Keep `_decide_ce_keep` small and local to `src/eval/__init__.py` |

### Rollback

Revert `search.py` / `eval` / tests / honesty doc commits; goldens untouched so rollback is code+docs only.

---

## Edge-case handling

| Case | Behavior |
|------|----------|
| Hub/proxy/cache fail | `fusion_degraded` + `error`; stage_counts all degraded; justify not measured |
| Mixed `ce` + `fusion_degraded` in one run | Partial rule: keep=false; report both attempt and CE-success metrics |
| Fusion hit@K=1.0 and CE-success=1.0 | keep=false; document ceiling / later discriminative set |
| Ollama down | Retrieve fails before CE; document fail; not a CE keep flip |
| Empty query / FTS fail | Unchanged RetrievalError paths |
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

## Refine pass notes (2026-07-17)

- Locked keep decisions to CE-success fields only (never attempt `hit_at_k`).  
- Added partial-degrade rule; pinned `ce_success_hit_at_k: null` when zero successes.  
- Details must carry `error`; Hub-free tests via stub + pure `_decide_ce_keep`.  
- Phase D optional and non-blocking for DoD.

---

## Ready-check result (2026-07-17)

| Track | Implement ready? | Score (0–10) | Why not 10 |
|-------|------------------|--------------|------------|
| Guide 06 CE-effectiveness eval | **Yes** (await Tom authorize Implement) | **8.9** | Justify sentence craft; optional logging/D1; Phase C needs Ollama+HF at runtime; A4 stub vs IdentityReranker choice. No pin conflicts found vs context/code seams. |

**Artifact:** `docs/2026-07-17_guide06_ce_effectiveness_ready_check.md`  
**Implement now:** **No** until Tom authorizes Implement Stage.  
**Further Refine-dev-guide:** **Not required.**
