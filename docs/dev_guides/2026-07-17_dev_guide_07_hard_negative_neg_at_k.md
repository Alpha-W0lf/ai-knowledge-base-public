# Dev Guide 07 — Hard-negative goldens / `neg_at_k`

**Date:** 2026-07-17  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 07 — discriminative hard-negative cases + `neg_at_k` harness; report fusion vs CE without corrupting hit@K  
**Stage that authored this:** Write-dev-guide (pass 102)  
**Status:** Draft (await Refine-dev-guide / Ready-check before Implement)

**Context SSOT:** `ai-knowledge-base-public/docs/2026-07-17_guide07_hard_negative_neg_at_k_context_summary.md`  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_guide07_write_pass102_handoff.md`  
**Prerequisite:** Guide 06 Review shippable (CE measurable; fusion+CE-success hit@K ceiling 1.0; `ce_keep=false`). Public corpus = committed `fixtures/` only.

**Tom / hub locks (do not reopen):**

| Lock | Value |
|------|--------|
| Metric formula | Guide 06 soft-pin (below) — do not invent a second formula |
| Case count | Soft target **4–6** hard-negative cases (`hn1`…); hard max **8** |
| `ce_keep` | **Not** flipped by `neg_at_k` alone — Guide 06 hit@K / CE-success rules unchanged |
| Honesty | No fake lift; no CE relevance ads without clear metric evidence |
| Stack | No `CE_ENABLED` flip; no private flip; no KB4 embedding change |

---

## Objective

1. Extend the fixture eval harness so `kind: "hard_negative"` cases with non-empty `forbidden_source_ids` produce **`neg_at_k`**.  
2. **Exclude** hard-negative rows from hit@K and from CE-success hit@K denominators used by `_decide_ce_keep`.  
3. Author **4–6** fixture-grounded hard-negative goldens (tempt a wrong sibling `source_id`).  
4. Re-run `uv run python -m src.eval`; record fusion vs CE `neg_at_k` + existing Guide 06 metrics.  
5. Refresh honesty docs — still **not** eval-complete / v1 Done; no CE lift ads from `neg_at_k` alone.

**Success signal:** Stranger runs eval; sees `neg_at_k` on both arms; easy-case hit@K math unchanged in meaning (hard-neg excluded); docs never claim unearned CE wins.

---

## Learning notes (interview-portable)

1. **Hard negative** — a trap document a weak ranker retrieves; success = *not* retrieving forbidden ids in top-K.  
2. **Ceiling effect** — when hit@K is already 1.0, compare rankers with a separate metric (`neg_at_k`).  
3. **Metric isolation** — mixing trap cases into the hit@K mean corrupts the score; exclude them from that denominator.  
4. **Keep vs report** — reporting `neg_at_k` improvement ≠ flipping product `ce_keep` without an explicit keep-policy lock.

---

## References (paths only)

- `ai-knowledge-base-public/docs/2026-07-17_guide07_hard_negative_neg_at_k_context_summary.md`
- `ai-knowledge-base-public/docs/dev_guides/2026-07-17_dev_guide_06_ce_effectiveness_eval.md` (§ Hard-negative metric soft-pin)
- `ai-knowledge-base-public/docs/2026-07-12_ce_keep_note.md`
- `ai-knowledge-base-public/docs/PORTFOLIO_VISION.md`
- `ai-knowledge-base-public/docs/ARCHITECTURE.md`
- `ai-knowledge-base-public/GETTING_STARTED.md`
- `ai-knowledge-base-public/INTERVIEW.md`
- `ai-knowledge-base-public/fixtures/eval/golden_cases.jsonl`
- `ai-knowledge-base-public/fixtures/manifest.json`
- `ai-knowledge-base-public/fixtures/transcripts/`
- `ai-knowledge-base-public/src/eval/__init__.py`
- `ai-knowledge-base-public/tests/test_eval_ce_honesty.py`
- `second_brain/docs/2026-07-17_spoke_ai_kb_guide07_write_pass102_handoff.md`
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`

---

## Architecture constraints (binding)

1. **KB5 stack unchanged:** hybrid → RRF → pluggable local CE; degrade to `fusion_degraded` + `error`.  
2. **Guide 06 keep math stays:** `_decide_ce_keep` uses CE-success hit@K vs fusion hit@K only — **never** set `ce_keep=true` solely because CE `neg_at_k` > fusion `neg_at_k`.  
3. **Fixture-first only** — queries grounded in committed fixture text; no invented corpus facts; no BYO YouTube eval.  
4. **No empty-`expected_source_ids` stand-in** for negatives.  
5. **No** `CE_ENABLED` / embedding / private flip; no easy-golden theater expansion beyond adding hard-neg rows.

---

## Soft pins

| Pin | Locked default |
|-----|----------------|
| Metric formula | See **Hard-negative metric** below (Guide 06 text, now Implement-bound) |
| Case count | **4–6** hard-negative cases (prefer 6 if authoring is easy; never >8) |
| Case ids | `hn1` … `hnN` (do not reuse `g1`–`g18`) |
| Case file | Append to `fixtures/eval/golden_cases.jsonl` (keep existing 18 easy cases) |
| Required hard-neg fields | `id`, `query`, `kind: "hard_negative"`, `forbidden_source_ids` (non-empty list of `fixture:*` ids), `must_cite` (prefer `false`) |
| Optional field | `expected_source_ids` — informational only if present; **still excluded** from hit@K |
| Load validation | On `kind=hard_negative`: fail closed (raise / skip with detail error) if `forbidden_source_ids` missing/empty or contains unknown ids not in manifest |
| `neg_ok` | `set(forbidden_source_ids) ∩ set(returned_source_ids) == ∅` |
| `neg_at_k` | `(# hard_neg with neg_ok) / (# hard_neg)` per arm; key **always present**; value **`null`** if `# hard_neg == 0` |
| hit@K denominator | Only cases with `kind` ∈ {`lexical`,`semantic`} (or equivalently: exclude `hard_negative`) |
| CE-success hit@K / `_decide_ce_keep` | Compute CE-success hit metrics **only** on non-hard-neg rows with `ranking_stage=="ce"`; `cases` for keep coverage = count of non-hard-neg goldens (still 18 unless easy set grows — it must not) |
| Arm reporting | Both fusion and CE arms expose `neg_at_k`, `hard_negative_cases`, `neg_ok_count` |
| Detail rows | Include `neg_ok` (bool) for hard-neg cases; include `forbidden_source_ids` echo optional |
| Spot-check | Before freezing cases: for each `hn*`, run hybrid retrieve once; prefer temptations where fusion **currently returns** a forbidden id (otherwise `neg_at_k` may trivially be 1.0) |
| Docs | Update `ce_keep_note`, GETTING_STARTED, INTERVIEW, PORTFOLIO_VISION — report `neg_at_k`; do not claim CE lift unless CE `neg_at_k` clearly exceeds fusion **and** prose says that is separate from `ce_keep` |
| Tests | Hub-free unit tests: `neg_ok` true/false; exclusion from hit@K denom; `_decide_ce_keep` unchanged when hard-neg present in file but excluded from denom; load reject empty forbidden |
| Files likely touched | `src/eval/__init__.py`, `tests/test_eval_ce_honesty.py` (or `tests/test_eval_neg_at_k.py`), `fixtures/eval/golden_cases.jsonl`, honesty docs |
| Non-goals | Fake lift; `ce_keep` from neg alone; easy `g*` growth; hard-neg >8; CE/embedding/private flips |

### Hard-negative metric (binding — from Guide 06)

Cases with `kind: "hard_negative"` carry non-empty `forbidden_source_ids`. A case is **neg_ok** iff none of those ids appear in the top-K returned `source_id`s. Report `neg_at_k = (# hard_negative cases with neg_ok) / (# hard_negative cases)`. **Exclude** `kind=hard_negative` rows from the hit@K denominator entirely. Never use empty `expected_source_ids` as a hard-negative stand-in.

### Suggested temptation themes (implementer aid — not exhaustive)

| Theme | Forbidden lean | Positive lean (optional expected) |
|-------|----------------|-----------------------------------|
| CE vocab vs fusion doc | Forbid `fixture:cross-encoder-05` when query is really about RRF | `fixture:fusion-rrf-04` |
| Allowlist vs ingest provenance | Forbid `fixture:fixture-ingest-06` when query is MCP public tools | `fixture:mcp-allowlist-02` |
| Embedding rebuild vs RRF | Forbid `fixture:embedding-version-03` when query is RRF ranks | `fixture:fusion-rrf-04` |
| Hooks vs CE | Forbid `fixture:cross-encoder-05` when query is hybrid hooks stages | `fixture:rag-hooks-01` |
| Ingest vs allowlist | Forbid `fixture:mcp-allowlist-02` when query is fixture-only smoke | `fixture:fixture-ingest-06` |
| CE degrade wording vs hooks | Forbid `fixture:rag-hooks-01` when query is CE fail-open `fusion_degraded` | `fixture:cross-encoder-05` |

---

## Acceptance criteria

- [ ] Harness: `hard_negative` + `forbidden_source_ids` → `neg_ok` / `neg_at_k` on fusion and CE arms  
- [ ] Hard-neg excluded from hit@K and CE-success hit@K / keep coverage denominators  
- [ ] Load fails closed on invalid hard-neg schema  
- [ ] **4–6** fixture-grounded `hn*` cases in `golden_cases.jsonl`; easy `g1`–`g18` preserved  
- [ ] Unit tests for neg math + exclusion + keep isolation  
- [ ] Eval re-run recorded; `ce_keep_note` includes fusion/CE `neg_at_k` + states `ce_keep` still hit@K-gated  
- [ ] GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION updated — not eval-complete; no fake lift  
- [ ] No `CE_ENABLED` flip; no private/embedding scope  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Refine-dev-guide / Ready-check.**

### Phase A — Harness

- [ ] **A1.** In `src/eval/__init__.py`, add helpers: `is_hard_negative(case)`, `neg_ok(forbidden, returned)`, validate hard-neg at load or first use.  
- [ ] **A2.** Split cases into easy vs hard-neg; compute hit@K **only** over easy cases (`n_easy = max(len(easy), 1)`).  
- [ ] **A3.** For each arm, compute `hard_negative_cases`, `neg_ok_count`, `neg_at_k` (`null` if zero hard-neg).  
- [ ] **A4.** CE-success metrics / `_decide_ce_keep` inputs: use easy-case counts only for `cases` coverage and CE-success hit@K (hard-neg never inflate/deflate keep).  
- [ ] **A5.** Detail rows: for hard-neg, set `neg_ok`; do not count hard-neg toward `hits` / hit@K.  
- [ ] **A6.** Unit tests (Hub-free): neg_ok; hit@K exclusion; keep decision ignores hard-neg rows; reject empty forbidden.

### Phase B — Author goldens

- [ ] **B1.** Read all six fixture transcripts; draft **4–6** trap queries with clear forbidden sibling ids.  
- [ ] **B2.** Spot-check each with hybrid retrieve (CE on or off); prefer cases where fusion currently surfaces the forbidden id.  
- [ ] **B3.** Append `hn1`… to `golden_cases.jsonl`; keep `g1`–`g18` intact.  
- [ ] **B4.** Confirm every `forbidden_source_ids` entry ∈ manifest `source_id`s.

### Phase C — Eval + honesty

- [ ] **C1.** `uv run python -m src.eval` (Ollama + HF MiniLM as Guide 06).  
- [ ] **C2.** Update `docs/2026-07-12_ce_keep_note.md`: easy N=18 metrics unchanged in meaning; add hard-neg N; fusion/CE `neg_at_k`; reaffirm `ce_keep` not driven by neg alone.  
- [ ] **C3.** Update GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION — hard-neg shipped; still not eval-complete; no CE lift ads unless evidence.  
- [ ] **C4.** Stop. No `CE_ENABLED` flip. No easy-golden growth. No fake lift.

---

## Verification / Definition of Done

```bash
# From ai-knowledge-base-public/
wc -l fixtures/eval/golden_cases.jsonl   # expect 22–24 (18 easy + 4–6 hard-neg)
rg -n '"kind": "hard_negative"' fixtures/eval/golden_cases.jsonl
uv run pytest tests/test_eval_ce_honesty.py tests/test_eval_neg_at_k.py -q   # adjust path if combined
uv run python -m src.eval
# Inspect JSON: fusion.neg_at_k, ce.neg_at_k, fusion.hit_at_k still over easy only,
# ce_keep still from Guide 06 rules (not neg alone)
rg -n 'neg_at_k|hard_negative|forbidden_source' \
  docs/2026-07-12_ce_keep_note.md GETTING_STARTED.md INTERVIEW.md docs/PORTFOLIO_VISION.md
```

**DoD:**

1. Harness computes `neg_at_k` on both arms; hard-neg excluded from hit@K / CE-success keep denominators.  
2. Invalid hard-neg schema fails closed.  
3. 4–6 `hn*` cases grounded in fixtures; `g1`–`g18` preserved.  
4. Unit tests cover neg_ok + exclusion + keep isolation.  
5. Eval re-run + honesty docs match; no fake lift; `ce_keep` not set from `neg_at_k` alone.  
6. No CE/embedding/private flips.

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| Corrupt hit@K by counting hard-neg | Explicit easy-only denominator |
| `ce_keep=true` from noisy neg lift | Locked: keep rules ignore `neg_at_k` |
| Trivial traps → `neg_at_k=1.0` forever | Spot-check B2; prefer fusion currently fails |
| Unknown forbidden ids | Validate against manifest |
| Doc overclaim | Same-delivery honesty; “not eval-complete” |
| Scope into easy golden growth | Soft pin: only add `hn*` |

### Rollback

Revert eval + golden + doc commits; or delete `hn*` lines and harness fields.

---

## Edge-case handling

| Case | Behavior |
|------|----------|
| Zero hard-neg in file | `neg_at_k: null`; hit@K as today over all easy |
| Empty `forbidden_source_ids` | Fail closed |
| Multiple forbidden ids | neg_ok only if **none** in top-K |
| CE `fusion_degraded` | Score neg_ok on returned fused order; stage_counts honesty unchanged |
| RetrievalError on a case | Detail error; do not count as neg_ok success |
| `must_cite: true` on hard-neg | Prefer `false`; ignore for hit@K (excluded) |
| Ollama / HF down | Same Guide 06 footguns |

---

## Stop conditions

- Harness + 4–6 cases + eval + honesty landed  
- **No** `ce_keep` flip from `neg_at_k` alone  
- **No** fake CE lift ads  
- **No** CE_ENABLED / embedding / private flip  
- **No** easy `g*` growth theater  
- Stop for human if asked to claim lift without evidence  

---

## Ready for Refine-dev-guide / Ready-check?

**Yes** after this Write. Soft pins and ordered steps are executable. Residual craft for Refine: exact JSON field names (`neg_ok_count` vs `hard_neg_hits`), whether to put `neg_at_k` on top-level report vs arms only (recommend **per arm**), and whether spot-check B2 is mandatory DoD (recommend **yes** — already soft-pinned).

**Do not Implement until Ready-check passes and Tom authorizes Implement.**
