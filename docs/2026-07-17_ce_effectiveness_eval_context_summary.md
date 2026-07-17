# Context: CE-effectiveness eval (post Guide 05 N=18)

**Date:** 2026-07-17  
**Repos:** `ai-knowledge-base-public` (+ `ai_knowledge_base` read-only sibling at most; not SSOT)  
**Status:** Draft (Gather context)  
**Mode last used:** spoke  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`  
**Prior guide:** Guide 05 eval golden growth — **done** (N=18); this slice is CE *measurement*, not golden-count theater  

## Problem

Guide 05 grew fixture goldens to **N=18** and re-ran eval. Recorded honesty (`docs/2026-07-12_ce_keep_note.md`):

| Pin | Value |
|-----|--------|
| `cases` | **18** |
| Fusion-only `hit_at_k` | **1.0** (18/18) |
| CE-attempt arm | **18/18** `ranking_stage=fusion_degraded` |
| Successful `ranking_stage=ce` cases | **0** |
| Reported `ce.hit_at_k` | **1.0** — equals fusion fallback order, **not** successful CE rerank |
| `ce_keep` | **false** |

**CE effectiveness was not measured.** The pluggable CE seam exists (KB5), but the CE-attempt eval arm never produced `ranking_stage=ce`. Marketing “CE improves relevance” or shorthand “CE hit@K=1.0” would be false. PORTFOLIO_VISION / INTERVIEW already state this; the next eng gap is making CE *run* under eval so ablation is real, then measuring lift (or documenting honest no-lift) without inventing wins.

## Acceptance criteria

- [ ] Root cause of `fusion_degraded` on the CE-attempt arm is documented with code evidence (this Gather) and addressed in a later Write-dev-guide / Implement (not this stage)
- [ ] Eval can produce counts of `ranking_stage=ce` vs `fusion_degraded` (and vs intentional `fusion`)
- [ ] Hit@K for “CE effectiveness” is reported **only** on cases where `ranking_stage=ce` (or an explicit “CE-success subset”); degraded cases are not scored as CE wins
- [ ] At least one honest ablation run where CE load succeeds end-to-end on the fixture path (so `ranking_stage=ce` appears)
- [ ] If fusion remains hit@K=1.0 on easy goldens, document that CE **cannot show lift** without harder / discriminative cases — no fake lift
- [ ] Docs honesty (`ce_keep_note`, GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION as needed) match metrics; still **not** eval-complete / portfolio v1 Done
- [ ] No `CE_ENABLED` default flip without human authorize; no private tip scrub / remote flip; no KB4 embedding change

## In scope

- Diagnose why CE-attempt → `fusion_degraded` (deps, HF cold start / Hub fetch, model id, silent exception swallowing, env)
- Define what a real CE ablation requires (stage counts + conditional hit@K)
- Fixture-first ideas for discriminative / hard-negative cases **without** silently breaking hit@K math (empty `expected_source_ids` currently always miss)
- Keep sophisticated stack: vector + FTS → RRF → pluggable local CE + honest degrade
- Context summary artifact only this stage

## Out of scope

- Fake CE lift / marketing claims
- Claiming eval-complete or portfolio v1 Done
- Private tip scrub / private remote flip; treating private tip as SSOT
- Changing KB4 embedding (`nomic-embed-text` @ 768)
- Flipping `CE_ENABLED` without human authorize
- Write-dev-guide / Implement (unless Tom re-authorizes Stage)
- Mechanic / Vehicle / AlphaGuard slices
- Full harness redesign beyond what CE measurement needs

## Prior art (paths only)

- `docs/2026-07-12_ce_keep_note.md` — honesty SSOT (N=18 pins)
- `docs/2026-07-15_guide05_eval_growth_context_summary.md` — prior Gather for golden growth
- `docs/dev_guides/2026-07-16_dev_guide_05_eval_golden_growth.md` — Guide 05 done; hard negatives deferred
- `docs/PORTFOLIO_VISION.md` §4–5 — Guide 05 done; CE no-lift honesty
- `docs/ARCHITECTURE.md` §0 KB5, §4 ranking_stage / degrade contract
- `GETTING_STARTED.md` / `INTERVIEW.md` Theme / FAQ on fusion_degraded
- `fixtures/eval/golden_cases.jsonl` (18 lines), `fixtures/transcripts/`
- `src/search.py` — shared retrieve; CE try/except → `fusion_degraded`
- `src/rerank.py` — `LocalCrossEncoder` + `get_default_ce_adapter`
- `src/eval/__init__.py` — fusion vs CE arms; `ce_keep` gate
- `src/config.py` — `CE_ENABLED=True`, `CE_MODEL_ID=cross-encoder/ms-marco-MiniLM-L-6-v2`
- `tests/tests_retrieval_spine.py` — forced CE failure → `fusion_degraded`
- Hub locks: `second_brain/docs/2026-07-16_human_locks_pass60_fan_in.md` (eval growth authorized; CE measurement is follow-on)
- Handoff: `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`

## Root-cause diagnosis (Gather evidence — no fix shipped)

### What the code does

1. **Eval CE arm** (`src/eval/__init__.py`): `retrieve(..., ce_enabled=True, ce_adapter=None)` → default `LocalCrossEncoder` via `get_default_ce_adapter()`.
2. **Fusion-only arm**: `ce_enabled=False` → `ranking_stage=fusion` (IdentityReranker is passed but unused when CE is off).
3. **Degrade path** (`src/search.py` ~179–195): on **any** `Exception` during `adapter.rerank(...)`, return fused top-K with `ranking_stage=fusion_degraded`. **Bare `except Exception:` — no log, no exception type/message in result/timings.**
4. **CE load** (`src/rerank.py`): lazy `from sentence_transformers import CrossEncoder` then `CrossEncoder(config.CE_MODEL_ID)` on first `rerank`. Model id matches lock: `cross-encoder/ms-marco-MiniLM-L-6-v2`. Dep declared in `pyproject.toml` (`sentence-transformers>=3.0.0`).

### Why Guide 05 saw 18/18 `fusion_degraded`

| Hypothesis | Evidence | Verdict |
|------------|----------|---------|
| Missing `sentence-transformers` | Import succeeds in `.venv`; listed in `pyproject.toml` / `uv.lock` | **Not** the steady-state cause |
| Wrong model id | `CE_MODEL_ID` matches Hub + ARCHITECTURE default | **Ruled out** |
| CE never attempted (`CE_ENABLED` false) | Eval passes `ce_enabled=True` on CE arm; config default `True` | **Ruled out** |
| Hub / cache / first-load failure | HF cache dir `~/.cache/huggingface/hub/models--cross-encoder--ms-marco-MiniLM-L-6-v2` exists. Sandboxed probe: Hub HEAD via proxy → `httpx.ProxyError: 403 Forbidden` → load fails → degrade. Unrestricted probe: load OK from cache. | **Primary mechanism:** first `_load()` raised (network/proxy/Hub/cache miss or incomplete fetch); every case retries `_load()` and fails the same way → **18/18 degrade**. Exact Guide 05 exception string was **not recorded** (silent swallow). |
| Predict/runtime error after load | Unrestricted probe after cache warm: `ranking_stage=ce` on hybrid retrieve | Unlikely as sole Guide 05 cause once load works |
| Intentional IdentityReranker on CE arm | Only when `ce=False` | **Ruled out** |

### Reproduce notes (2026-07-17 spoke)

| Probe | Result |
|-------|--------|
| `CrossEncoder(...)` under sandbox network | Fail: `ProxyError: 403 Forbidden` during `hf_hub_download` metadata |
| Same load with unrestricted network + existing HF cache | **OK** — weights load; `predict` works |
| `retrieve(..., ce_enabled=True)` after fixture ingest (unrestricted) | **`ranking_stage=ce`**; first call `ce_ms` ≈ 8.7s (model load); hits carry `rerank_score` |

**Implication:** The seam works when the local MiniLM CE can load. Guide 05’s “CE hit@K=1.0” was fusion order under degrade. CE effectiveness eval is blocked until eval runs in an environment where CE load succeeds **and** the harness distinguishes CE-success from degrade.

### Secondary honesty / harness gaps (not root of degrade, but block “real ablation”)

1. **Auto `ce_justify` when flat** (`src/eval/__init__.py`) claims “identity/adapter path validated; lift TBD” even when **0** cases have `ranking_stage=ce`. `ce_keep_note` manually corrected this; harness text can still mislead.
2. **No stage aggregate** in printed summary — operators must scan `details[].ranking_stage`.
3. **Fusion hit@K=1.0** on current easy goldens → even successful CE cannot demonstrate lift without harder / discriminative cases (Guide 05 deferred hard negatives because empty `expected_source_ids` always miss).

## Risks and blast radius

| Risk | Angle | Mitigation |
|------|-------|------------|
| Claiming CE lift from degraded arm | Docs / interview honesty | Stage-gated metrics; never equate `ce.hit_at_k` with CE success if all `fusion_degraded` |
| Silent CE failures in demos | Operability | Log/record exception class + message on degrade (Implement later) |
| HF Hub dependency on cold machines | Stranger clone / CI / sandboxed agents | Document pre-download / cache warm; optional `local_files_only` after warm; fail-open remains correct |
| First CE call latency (~seconds) | Demo UX | Document warm-up; singleton already caches model after first load |
| Hard negatives distort hit@K | Eval math | Design harness support before empty expected sets; do not dump empty expected into current formula |
| Flipping `CE_ENABLED` to hide failures | Product honesty | Human gate; keep default on + degrade |
| Scope into golden-count theater | Portfolio time | N=18 already done; this slice is CE *load + measure* |
| Doc drift vs private sibling | Public SSOT | Public repo only; private read-only at most |

## Edge cases

- HF cold start / proxy / offline → all `fusion_degraded` (observed pattern)
- Incomplete HF cache → Hub fetch required → same degrade
- `sentence-transformers` / torch import error → degrade (fail-open)
- CE OOM / predict error mid-batch → degrade for that query (adapter is process-singleton; next query may retry load)
- Fusion already hit@K=1.0 → CE cannot show positive lift without harder cases
- Empty `expected_source_ids` → always miss under current hit@K; forbidden until harness redesign
- Ollama down → embed/retrieve fails before CE; document fail vs skip
- `force_ce_failure=True` (tests) → intentional `fusion_degraded` (DoD for degrade path — keep)
- Misquoting “CE hit@K=1.0” when arm was degraded — INTERVIEW already warns; keep

## Unknowns (must resolve or escalate)

| Unknown | How to resolve | Blocking? |
|---------|----------------|-----------|
| Exact exception string from the Guide 05 eval run | Not in git; swallowed by bare except. Next Implement: log on degrade; re-run eval and capture | No for Gather; Yes for durable ops |
| Whether stranger/CI must pre-warm HF cache | Soft-pin in Write-dev-guide (GETTING_STARTED footgun + optional offline flag) | Soft |
| Hard-negative schema (separate metric vs empty expected) | Design in Gather; soft-pin only if harness plan clear in Write-dev-guide | Soft for first CE-success ablation |
| Target N for discriminative set after CE works | After CE-success baseline; may stay N=18 for first ablation | No for first “CE ran” proof |

## Recommended approach

1. **Diagnose + plan CE load path** so `ranking_stage=ce` can appear under `uv run python -m src.eval` (observability on degrade; document HF cache warm / Hub access; confirm model id — already correct).
2. **Harness honesty:** aggregate stage counts; compute CE hit@K on `ranking_stage=ce` subset (or report both “CE-attempt” and “CE-success”); fix justify text when CE-success count is 0.
3. **Re-run ablation** once CE loads: record fusion vs CE-success metrics; update `ce_keep_note`. Expect possible flat hit@K on easy goldens — that is honest, not a bug.
4. **Only then** design discriminative / hard-negative cases (separate metric or harness support) if lift measurement is the goal — do not pretend N=18 easy goldens can show CE lift.
5. **Do not** flip `CE_ENABLED`; **do not** advertise lift without CE-success evidence.

## Open decisions (human)

- **Plain title:** Fix CE load path first vs expand goldens first?
  - In plain terms: Guide 05 already has 18 easy questions. The cross-encoder never successfully reranked on that run (all fell back to fusion). Growing more easy questions without fixing load still cannot measure the reranker.
  - Options: (A) diagnose/plan CE load + eval honesty so `ranking_stage=ce` appears, then measure; (B) grow goldens first while CE still degrades; (C) park CE measurement.
  - Recommendation: **(A)**
  - Reasoning: Ablation requires the treatment arm to run. Expanding goldens under 100% degrade is fusion-only theater. Fusion is already hit@K=1.0 — more easy cases will not create CE lift.
  - Tradeoffs: Delays “bigger N” optics; requires env/cache/ops attention. Residual risk: after CE works, lift may still be zero until harder cases exist — that must be stated honestly.

- **Plain title:** Hard negatives in this guide or later?
  - In plain terms: Should this work item invent “trap” questions / negative expectations now, or only after CE successfully runs and the harness can score them without breaking hit@K?
  - Options: (A) design now, soft-pin in Write-dev-guide if harness plan is clear; (B) defer until after first CE-success ablation on current N=18; (C) never — fusion-ceiling is enough.
  - Recommendation: **(A) design in Gather / soft-pin later only if clear; default sequence = CE-success baseline first, hard negatives as follow-on pin** — aligned with handoff lean: design here, soft-pin in Write-dev-guide only if harness plan is clear.
  - Reasoning: Empty `expected_source_ids` currently always miss. Shipping them without a metric contract corrupts hit@K. First proof is “CE ran.” Discriminative set is how you *then* look for lift.
  - Tradeoffs: Two-step delivery vs one mega-guide. Skipping hard negatives forever leaves CE keep forever unprovable on easy fixtures.

- **Plain title:** Write-dev-guide next after this Gather?
  - In plain terms: Is context enough to author an eng guide for CE load observability + eval stage-gated metrics (+ optional hard-negative design)?
  - Options: (A) Refine context first; (B) Write-dev-guide next; (C) park.
  - Recommendation: **(A) Refine context once if Tom wants tighter soft pins; else (B) Write-dev-guide is justified** — root cause and acceptance criteria are evidence-backed; soft pins (log shape, stage-count fields, cache warm steps) belong in the guide.
  - Reasoning: Gather DoD met with code probes. Remaining unknowns are guide-level soft pins, not missing problem framing.
  - Tradeoffs: Skipping Refine risks loose Implement; an extra Refine pass costs calendar time.

## Evidence opened this pass

- Workflow OS: `SESSION.md`, `QUALITY_STANDARD.md`, `ALWAYS.md`, `LEARNING_MODE.md`, `stages/gather-context.md`, `templates/context-summary.md`
- Handoff: `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`
- Locks: `second_brain/docs/2026-07-16_human_locks_pass60_fan_in.md`
- `docs/2026-07-12_ce_keep_note.md`, Guide 05 context + guide, `PORTFOLIO_VISION.md`, `ARCHITECTURE.md` (§0/§4), `GETTING_STARTED.md` eval section
- Code: `src/search.py`, `src/rerank.py`, `src/eval/__init__.py`, `src/config.py`, `pyproject.toml`, `tests/tests_retrieval_spine.py` (D4), `fixtures/eval/golden_cases.jsonl` (wc = 18)
- Commands: HF cache listing; sandboxed vs unrestricted `CrossEncoder` load; unrestricted `retrieve` → `ranking_stage=ce`

## Honest readiness

- Ready for Write-dev-guide? **Conditionally yes** after human locks on the three open decisions (especially “CE load first”). Prefer a short **Refine context** if Tom wants numeric readiness scores + tighter soft pins before guide authoring.
- Ready for Implement? **No** — no approved guide yet; Gather only.
- Context quality: sufficient to explain why CE was unmeasured and what “real ablation” requires. Residual: Guide 05’s exact exception text is unknowable without re-run + logging.
