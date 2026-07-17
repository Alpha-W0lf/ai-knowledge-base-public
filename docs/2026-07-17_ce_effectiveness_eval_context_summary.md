# Context: CE-effectiveness eval (post Guide 05 N=18)

**Date:** 2026-07-17  
**Repos:** `ai-knowledge-base-public` (+ `ai_knowledge_base` read-only sibling at most; not SSOT)  
**Status:** Refined (Refine context pass 1)  
**Mode last used:** spoke  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`  
**Prior guide:** Guide 05 eval golden growth — **done** (N=18); this slice is CE *measurement*, not golden-count theater  

## Locked (Tom — 2026-07-17 Refine)

| Decision | Lock |
|----------|------|
| Order of work | **CE load-first** so `ranking_stage=ce` can appear before any golden-expansion theater |
| Honesty | No fake lift; do not advertise CE relevance wins without CE-success evidence |
| `CE_ENABLED` | **No flip** without separate human authorize (default stays `True`) |
| Private sibling | No tip scrub / remote flip; public repo is SSOT for this slice |
| Embeddings (KB4) | No change — `nomic-embed-text` @ 768 |
| Hard negatives | **Design only** in this work item; soft-pin in Write-dev-guide **only if** harness plan is clear; do not ship empty `expected_source_ids` into current hit@K |

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

**CE effectiveness was not measured.** The KB5 pluggable CE seam exists, but the CE-attempt eval arm never produced `ranking_stage=ce`. Next eng gap: make CE *load and score* under eval with observable failures, gate metrics on CE-success, re-run ablation on N=18, update honesty docs — without inventing lift or growing easy goldens first.

## Acceptance criteria

- [ ] CE degrade path records a durable failure reason (exception type + message) when `ranking_stage=fusion_degraded` (prefer existing `RetrievalResult.error`; do not silently swallow)
- [ ] Eval printed JSON includes **stage counts** on the CE-attempt arm: at least `ce` / `fusion_degraded` (and intentional `fusion` if present)
- [ ] Eval reports **CE-success hit@K** only over cases with `ranking_stage=ce`; degraded cases are counted separately and **never** treated as CE wins
- [ ] `ce_justify` / `ce_keep` logic: if CE-success count is **0**, justify must say effectiveness **not measured** (not “adapter path validated / lift TBD” theater)
- [ ] At least one full `uv run python -m src.eval` run where CE-success count **> 0** (ideally 18/18 `ce`) **or** documented operator blocker (HF cache / Hub / Ollama) with exact error string captured
- [ ] Honesty docs updated to match that run (`ce_keep_note` required; GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION as needed) — still **not** eval-complete / v1 Done; no fake lift
- [ ] GETTING_STARTED (or equivalent) documents HF MiniLM cache warm / Hub access as an eval footgun
- [ ] Hard-negative **design** written in the guide (metric contract sketch); **no** empty-expected goldens shipped unless soft-pin locks a harness plan
- [ ] No `CE_ENABLED` flip; no private flip; no KB4 embedding change; no golden-N expansion theater in this guide

## In scope

- CE load reliability + observability so `ranking_stage=ce` can appear under fixture eval
- Harness honesty: stage aggregates + CE-success-gated hit@K + justify fix
- Re-run ablation on existing **N=18**; refresh honesty docs
- Hard-negative **design only** (optional soft-pin if harness plan clear)
- Keep stack: vector + FTS → RRF → pluggable local CE + honest degrade

## Out of scope

- Fake CE lift / marketing
- Claiming eval-complete or portfolio v1 Done
- Growing golden N “for optics” while CE still degrades (or as a substitute for CE load)
- Shipping hard-negative cases that break current hit@K without a locked metric contract
- Private tip scrub / remote flip; private tip as SSOT
- Changing KB4 embedding
- Flipping `CE_ENABLED` without human authorize
- Mechanic / Vehicle / AlphaGuard slices
- Full harness redesign beyond CE measurement needs

## Prior art (paths only)

- `docs/2026-07-12_ce_keep_note.md` — honesty SSOT (N=18 pins)
- `docs/2026-07-15_guide05_eval_growth_context_summary.md` — Guide 05 Gather
- `docs/dev_guides/2026-07-16_dev_guide_05_eval_golden_growth.md` — Guide 05 done; hard negatives deferred
- `docs/PORTFOLIO_VISION.md` §4–5; `docs/ARCHITECTURE.md` §0 KB5, §4 ranking_stage
- `GETTING_STARTED.md` / `INTERVIEW.md`
- `fixtures/eval/golden_cases.jsonl` (N=18), `fixtures/transcripts/`
- `src/search.py` (bare `except Exception` → `fusion_degraded`); `src/rerank.py`; `src/eval/__init__.py`; `src/config.py`; `src/models.py` (`RetrievalResult.error` already exists, unused on degrade)
- `tests/tests_retrieval_spine.py` (D4 forced degrade)
- Handoff: `second_brain/docs/2026-07-17_spoke_ai_kb_ce_eval_gather_handoff.md`

## Root-cause diagnosis (tightened)

### Mechanism (code)

1. Eval CE arm: `retrieve(..., ce_enabled=True, ce_adapter=None)` → `LocalCrossEncoder` (`src/eval/__init__.py`, `src/rerank.py`).
2. First `rerank` calls `_load()` → `sentence_transformers.CrossEncoder(CE_MODEL_ID)` with `CE_MODEL_ID=cross-encoder/ms-marco-MiniLM-L-6-v2` (correct; dep present).
3. Any exception in that path → `src/search.py` sets `ranking_stage=fusion_degraded` and **discards the exception** (bare `except Exception:`). `RetrievalResult.error` is never set.
4. Same failure repeats per case → Guide 05 **18/18** degrade. Reported `ce.hit_at_k=1.0` is fusion order under fail-open, **not** CE scoring.

### Primary cause class

**CE model load / Hub-or-cache access failed at eval time**, not a wrong model id and not `CE_ENABLED=False`. Spoke probes (2026-07-17):

| Probe | Result |
|-------|--------|
| Sandboxed Hub download | `httpx.ProxyError: 403 Forbidden` → load fails → would degrade |
| Unrestricted + existing HF cache | Load OK; `predict` OK |
| `retrieve(..., ce_enabled=True)` unrestricted | **`ranking_stage=ce`**; first `ce_ms` ≈ 8.7s (cold load) |

Exact Guide 05 exception string is **unknowable from git** (swallowed). Treat as: env/network/cache prevented `_load()`; fix is observability + documented warm path + re-run where Hub/cache works — not golden expansion.

### Secondary gaps (block honest ablation even after CE loads)

1. Harness `ce_justify` on flat hit@K claims adapter validated even when CE-success count is 0.
2. No stage-count aggregate in eval JSON.
3. Fusion hit@K already **1.0** on easy N=18 → CE **cannot show lift** without harder/discriminative cases later; flat CE-success hit@K is an honest outcome, not a bug.

## Soft pins (for Write-dev-guide)

| Pin | Default |
|-----|---------|
| Guide focus | **CE load + eval honesty + re-run N=18** — not golden growth |
| Degrade observability | On CE exception: set `RetrievalResult.error` to `"{ExcType}: {message}"` (truncate if huge); keep fail-open fused ranks; optional stderr/`logging` one-liner |
| Eval stage counts | Add e.g. `ce.stage_counts = {"ce": n, "fusion_degraded": n, ...}` from `details[].ranking_stage` |
| CE-success metric | `ce_success_cases`, `ce_success_hit_at_k` over `ranking_stage=="ce"` only; keep attempt-level hit@K labeled as attempt/fallback if retained |
| `ce_keep` / justify | Lift only if CE-success count covers the eval set (soft: all cases `ce`, or document threshold) **and** CE-success hit@K > fusion hit@K; if CE-success count == 0 → `ce_keep=false` + “not measured” justify |
| Model / enablement | Keep `CE_MODEL_ID` and `CE_ENABLED=True`; no flip |
| Operator docs | GETTING_STARTED footgun: warm HF cache for MiniLM (e.g. one successful hybrid search or Hub download); Ollama still required for embeds |
| Tests | Extend D4-style test: forced failure populates `error`; happy-path mock/adapter still `ce` |
| Hard negatives | **Design subsection only** — sketch options: (1) separate `kind` + metric excluded from hit@K denominator; (2) `forbidden_source_ids` / neg@K. **Do not implement cases** unless soft-pin locks option + formula |
| Files likely touched | `src/search.py`, `src/eval/__init__.py`, tests, `docs/2026-07-12_ce_keep_note.md`, GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION as needed |
| Non-goals in Implement | Golden N expansion; `CE_ENABLED` flip; private scrub; embedding change; marketing lift |

### Hard-negative design sketch (not Implement)

Current hit@K: `hit = bool(expected_source_ids ∩ returned_source_ids)`; empty expected → always miss → corrupts mean hit@K.  
**Design lean for later:** add a separate metric (e.g. neg@K / “must not retrieve”) or exclude hard-negative ids from the hit@K denominator — never dump empty expected into today’s formula. Soft-pin the chosen contract in Write-dev-guide only if the formula is one paragraph clear; else defer to a follow-on guide after CE-success baseline.

## Risks and blast radius

| Risk | Angle | Mitigation |
|------|-------|------------|
| CE lift claimed from degraded arm | Honesty | Stage counts + CE-success-gated metrics |
| Silent CE failures | Ops / interview | Populate `RetrievalResult.error` on degrade |
| HF Hub cold / proxy / sandbox | Stranger + agents | Document cache warm; fail-open stays correct |
| First CE latency ~seconds | Demo | Document warm-up; singleton caches after first load |
| Hard negatives break hit@K | Eval math | Design-only until contract locked |
| Scope creep into golden theater | Time | Locked: CE load-first; N=18 sufficient for first ablation |
| Touching MCP public payload | Blast | `error` already in `to_public_dict` when set — acceptable; keep messages free of secrets/paths |

## Edge cases

- HF cold start / proxy / offline → all `fusion_degraded` + now with `error` string
- Incomplete HF cache → Hub fetch required → same
- Import / OOM / predict errors → per-query degrade; singleton may retry `_load`
- Fusion hit@K=1.0 → no positive lift possible on current goldens
- Empty `expected_source_ids` → forbidden until metric contract
- Ollama down → fail before CE; document
- `force_ce_failure` tests → still `fusion_degraded`, assert `error` set
- Misquoting “CE hit@K=1.0” under degrade — keep INTERVIEW warning

## Unknowns

| Unknown | How to resolve | Blocking Write-dev-guide? |
|---------|----------------|---------------------------|
| Exact Guide 05 exception text | Unknowable; Implement logs + re-run captures new string | **No** |
| Stranger must pre-warm vs auto-download | Soft-pin: document warm; allow Hub download when network works | **No** |
| Hard-negative metric choice | Design in guide; soft-pin only if one clear formula | **No** (design-only) |
| Will CE-success hit@K beat fusion on N=18? | Probably not (ceiling 1.0); honesty = flat OK | **No** |

## Recommended approach

1. Write-dev-guide: soft pins above — observability + harness honesty + docs + re-run; hard-negative design subsection; **no** golden growth.
2. Implement that guide; stop.
3. If CE-success hit@K is flat at 1.0 (expected), keep seam + `ce_keep=false` (or justify-keep without lift claim); schedule discriminative cases as a **later** guide only after hard-negative contract is locked.

## Open decisions (human)

**None blocking Write-dev-guide.** Tom locked CE load-first, no fake lift / no CE flip / no private flip / no KB4 change, hard negatives design-only.

Residual soft choice (guide author may pick without new hub gate):

- **Plain title:** Soft-pin a hard-negative metric in Write-dev-guide now, or design-only prose with “defer Implement”?
  - In plain terms: Should the next eng guide name a concrete scoring formula for trap questions, or only describe the problem and wait?
  - Options: (A) soft-pin one formula if it fits in one clear paragraph; (B) design prose only, no soft-pin, no cases.
  - Recommendation: **(A) if clear in ≤1 paragraph, else (B)** — matches Tom’s “soft-pin later if harness plan clear.”
  - Reasoning: Avoids corrupting hit@K; still captures the design so the next discriminative guide is not blank.
  - Tradeoffs: Soft-pin too early may churn; prose-only may delay lift measurement.

## Evidence opened this pass (Refine)

- `stages/refine-context.md`; prior Gather context; handoff Results
- Reconfirmed: `RetrievalResult.error` exists unused on degrade (`src/models.py`); eval justify gap (`src/eval/__init__.py`); search bare except (`src/search.py`)
- Tom locks from Refine authorization message (CE load-first; hard negatives design-only)

## Honest readiness

| Track | Write-dev-guide ready? | Score (0–10) | Why not 10 |
|-------|------------------------|--------------|------------|
| CE-effectiveness eval context | **Yes** | **8.5** | Soft pins are guide-ready but Implement still must choose exact JSON field names / truncate rules; Guide 05’s original exception string will never be recovered; hard-negative metric remains intentionally unpinned until guide author tests clarity; first CE-success eval still depends on operator HF/Ollama env (documented, not eliminated). |

- Ready for Write-dev-guide? **Yes** (score **8.5 / 10**).  
- Ready for Implement? **No** — needs approved Write-dev-guide.  
- Do **not** start Write-dev-guide until Tom authorizes that Stage.
