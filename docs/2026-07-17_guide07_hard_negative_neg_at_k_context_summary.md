# Context: Guide 07 — Hard-negative goldens / `neg_at_k`

> **Superseded (Align 2026-07-17):** Historical Gather artifact. Guide 07 **Implement** `ff9ad33` + **Review** shippable (`e7f59d2` / `docs/2026-07-17_guide07_hard_negative_review.md`). Current honesty SSOT: [`docs/2026-07-12_ce_keep_note.md`](./2026-07-12_ce_keep_note.md) — 18 easy + 6 hard-neg; fusion/CE `neg_at_k` **0.0**; `ce_keep=false`; **not** eval-complete. Do not treat unchecked boxes below as open work.

**Date:** 2026-07-17  
**Repos:** `ai-knowledge-base-public` (+ `ai_knowledge_base` read-only at most; not SSOT)  
**Status:** **Superseded** by Implement + Review (was: Draft Gather)  
**Mode last used:** spoke  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_guide07_gather_pass101_handoff.md`  
**Prior:** Guide 06 CE-effectiveness **closed** (Review shippable) — CE-success 18/18 `ce`; fusion + CE-success hit@K **1.0**; `ce_keep=false`

## Problem

Guide 06 made CE *measurable*, but the N=18 fixture goldens are **easy**: fusion-only hit@K already **1.0**, so CE-success hit@K cannot show lift (ceiling effect). PORTFOLIO_VISION and `ce_keep_note` correctly refuse to advertise CE relevance wins.

To discriminate rankers (fusion vs CE), the eval set needs **hard negatives**: queries where a *wrong* fixture `source_id` is temptingly similar, and success means that forbidden id does **not** appear in top-K. Guide 06 already soft-pinned the metric contract — this work item **implements** that contract (harness + cases), without using empty `expected_source_ids` as a fake negative (that always misses today’s hit@K and corrupts the mean).

## Acceptance criteria

- [ ] Harness supports `kind: "hard_negative"` with non-empty `forbidden_source_ids`  
- [ ] **neg_ok** iff none of `forbidden_source_ids` appear in top-K returned `source_id`s  
- [ ] Report `neg_at_k = (# hard_negative cases with neg_ok) / (# hard_negative cases)` (JSON `null` if zero hard-neg cases)  
- [ ] **Exclude** `kind=hard_negative` rows from the hit@K denominator (and from CE-success hit@K denominator used by `_decide_ce_keep`)  
- [ ] Never use empty `expected_source_ids` alone as a hard-negative stand-in  
- [ ] Add a small documented set of fixture-grounded hard-negative cases (soft target in Write-dev-guide)  
- [ ] Report fusion vs CE **neg_at_k** (and stage honesty) without claiming CE lift unless metrics show it  
- [ ] Update `ce_keep_note` / GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION honesty — still **not** eval-complete / v1 Done  
- [ ] No `CE_ENABLED` flip; no private flip; no KB4 embedding change; no fake lift ads  

## In scope

- Eval harness: hard-negative schema + `neg_at_k` + hit@K denominator exclusion  
- Fixture-first hard-negative golden authoring (committed `fixtures/` text only)  
- Fusion vs CE reporting for `neg_at_k` (ablation-shaped)  
- Honesty doc refresh  
- Keep sophisticated stack: hybrid → RRF → pluggable CE + degrade  

## Out of scope

- Implement this Gather stage (Write-dev-guide / Implement later)  
- Fake CE lift / marketing  
- Claiming eval-complete or portfolio v1 Done  
- Private tip scrub / remote flip  
- `CE_ENABLED` flip; KB4 embedding change  
- Vehicle / Mechanic / AlphaGuard  
- Expanding easy lexical/semantic goldens “for optics” without discriminative value  

## Prior art (paths only)

- Guide 06 soft-pin (binding starting contract): `docs/dev_guides/2026-07-17_dev_guide_06_ce_effectiveness_eval.md` § Hard-negative metric  
- `docs/2026-07-12_ce_keep_note.md` — Guide 06 metrics; points at later hard-neg guide  
- `docs/PORTFOLIO_VISION.md` §5 — hard negatives / `neg_at_k` remain later guide  
- `docs/2026-07-17_ce_effectiveness_eval_context_summary.md` — CE load-first prior slice  
- `docs/dev_guides/2026-07-16_dev_guide_05_eval_golden_growth.md` — deferred empty-expected negatives  
- `src/eval/__init__.py` — current hit@K = `expected ∩ returned`; kinds `lexical`\|`semantic` only in practice  
- `fixtures/eval/golden_cases.jsonl` (N=18); `fixtures/manifest.json` (6 `fixture:*` source ids)  
- `GETTING_STARTED.md` / `INTERVIEW.md` — hard negatives deferred wording  

## Locked starting contract (from Guide 06 — do not invent a second formula)

> Cases with `kind: "hard_negative"` carry non-empty `forbidden_source_ids`. A case is **neg_ok** iff none of those ids appear in the top-K returned `source_id`s. Report `neg_at_k = (# hard_negative cases with neg_ok) / (# hard_negative cases)`. **Exclude** `kind=hard_negative` rows from the hit@K denominator entirely. Never use empty `expected_source_ids` as a hard-negative stand-in.

## Current harness facts (evidence)

| Fact | Evidence |
|------|----------|
| Golden fields today | `id`, `query`, `expected_source_ids`, `must_cite`, `kind` ∈ {`lexical`,`semantic`} |
| hit@K | `bool(expected ∩ returned_sources)`; mean over **all** cases |
| Empty expected | Always miss → corrupts mean (Guide 05/06 correctly forbade) |
| CE keep | `_decide_ce_keep` uses CE-success hit@K only — must **not** count hard-neg rows in that denominator once they exist |
| Fixture ids available | `fixture:rag-hooks-01`, `mcp-allowlist-02`, `embedding-version-03`, `fusion-rrf-04`, `cross-encoder-05`, `fixture-ingest-06` |

## Recommended approach

1. **Harness first:** extend `src/eval` to parse `forbidden_source_ids`, compute `neg_at_k` per arm (fusion / CE), exclude `hard_negative` from hit@K and CE-success hit@K denominators; unit-test neg_ok / exclusion math Hub-free.  
2. **Then cases:** author a small N of fixture-grounded hard negatives (query wording must tempt a *wrong* sibling fixture; `forbidden_source_ids` = that wrong id; optional positive `expected_source_ids` for documentation only — still excluded from hit@K).  
3. **Re-run** `uv run python -m src.eval`; record fusion/CE `neg_at_k` + existing hit@K / CE-success metrics.  
4. **Honesty:** update `ce_keep_note` — `ce_keep` remains hit@K-gated per Guide 06 unless Tom later locks a neg_at_k keep rule; do not advertise CE wins from `neg_at_k` without clear improvement.  
5. Soft target for Write-dev-guide: propose **≥4 and ≤8** hard-negative cases (enough to discriminate, not a second golden theater).

### Case authoring lean (implementer aid)

| Pattern | Idea |
|---------|------|
| Cross-topic temptation | Query mixes CE vocabulary but forbids `fixture:cross-encoder-05` when the grounded answer is another doc (or vice versa) |
| Allowlist vs ingest | Query about “public tools / no sync” must not return `fixture:fixture-ingest-06` if forbidden |
| Fusion vs embedding | RRF wording must not surface embedding-version doc when forbidden |

All queries must be answerable / checkable from committed fixture text — no invented corpus facts.

## Risks and blast radius

| Risk | Angle | Mitigation |
|------|-------|------------|
| Empty expected used as “negative” | Corrupts hit@K | Forbidden; require `forbidden_source_ids` |
| Hard-neg counted in hit@K / CE-success denom | Fake drops or fake CE keep | Explicit exclusion in harness |
| Claiming CE lift from noisy tiny neg set | Honesty | Report both arms; no ads without clear delta; keep `ce_keep` on hit@K unless Tom locks otherwise |
| Trivial forbidden ids never retrieved | Metric always 1.0 | Author temptations that fusion currently retrieves (spot-check before freeze) |
| Scope into easy golden growth | Time | Cap hard-neg N; do not re-litigate Guide 05/06 |
| Doc drift | Operators | Same-delivery honesty updates |

## Edge cases

- Zero hard-neg cases → `neg_at_k: null` (or omit with documented key always-null policy — soft-pin in Write-dev-guide; prefer **always present, null when 0** to match Guide 06 `ce_success_hit_at_k` style)  
- Empty or missing `forbidden_source_ids` on `hard_negative` → fail closed at load / skip with error in details  
- Forbidden id not in corpus → invalid case; reject at authoring  
- Multiple forbidden ids → neg_ok only if **none** appear  
- CE `fusion_degraded` on hard-neg arm → still score neg_ok on returned fused order; stage_counts honesty unchanged  
- `must_cite` on hard-neg → prefer `false` or ignore for hit@K (excluded anyway)  
- Ollama / HF down → same as Guide 06 footguns  

## Unknowns (must resolve or escalate)

| Unknown | How to resolve | Blocking Gather? |
|---------|----------------|------------------|
| Exact hard-neg N (4–8?) | Soft-pin in Write-dev-guide | No |
| Whether `expected_source_ids` required on hard-neg rows | Soft-pin: optional; if present, informational only (excluded from hit@K) | No |
| Whether `ce_keep` may later use `neg_at_k` lift | Default **No** this guide; human gate to reopen | Soft |
| Which temptations fusion currently fails | Spot-check retrieve during Implement / Write | No for Gather |

## Open decisions (human)

- **Plain title:** Soft-target how many hard-negative cases?
  - In plain terms: Enough trap questions to stress fusion vs CE without building a second huge golden set.
  - Options: (A) 4–6; (B) 8–12; (C) harness-only first, cases in Guide 08.
  - Recommendation: **(A) 4–6** (Write-dev-guide soft-pin ≥4 ≤8).
  - Reasoning: Ceiling problem is proven; small discriminative set is enough for a first `neg_at_k` baseline.
  - Tradeoffs: Tiny N is noisy; large N burns authoring time and may still not prove CE lift.

- **Plain title:** Keep `ce_keep` on hit@K only, or allow keep-true from `neg_at_k` lift?
  - In plain terms: Should “keep the reranker default-on” flip if CE only wins on hard negatives?
  - Options: (A) hit@K only (Guide 06 rules unchanged); (B) allow keep if CE `neg_at_k` > fusion `neg_at_k` with full CE-success coverage; (C) report both, never auto-keep from neg.
  - Recommendation: **(A)** for Guide 07; report `neg_at_k` honestly; reopen keep rule only with explicit Tom lock.
  - Reasoning: Avoid moving the keep goalposts mid-portfolio; ceiling hit@K already documented.
  - Tradeoffs: May leave `ce_keep=false` even if CE helps on traps — more honest for interviews.

- **Plain title:** Write-dev-guide next after this Gather?
  - In plain terms: Is context enough to author an executable Guide 07?
  - Options: (A) Refine context first; (B) Write-dev-guide next; (C) park.
  - Recommendation: **(B)** after Tom locks soft-target N (or accepts 4–6 default); Refine optional if you want numeric readiness scores.
  - Reasoning: Metric contract already soft-pinned in Guide 06; Gather only needs case-count + keep-policy soft pins.
  - Tradeoffs: Skipping Refine risks loose N; extra Refine costs calendar time.

## Evidence opened this pass

- Handoff pass 101; `stages/gather-context.md`; template context-summary  
- Guide 06 soft-pin §; `ce_keep_note`; PORTFOLIO_VISION §5  
- `src/eval/__init__.py` hit@K path; `golden_cases.jsonl` fields; `fixtures/manifest.json` source ids  
- QUALITY / ALWAYS / LEARNING (Workflow OS rails — spoke load)

## Honest readiness

- Ready for Write-dev-guide? **Yes**, once soft-target N is accepted (recommend 4–6) and `ce_keep` stays hit@K-only unless Tom locks otherwise.  
- Ready for Implement? **No** — needs approved Guide 07.  
- Context quality: sufficient — problem, locked formula, harness gaps, and case authoring lean are evidence-backed. Residual: which exact temptations fusion fails today is Implement craft / spot-check.
