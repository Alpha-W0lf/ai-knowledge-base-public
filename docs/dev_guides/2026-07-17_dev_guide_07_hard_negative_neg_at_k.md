# Dev Guide 07 — Hard-negative goldens / `neg_at_k`

**Date:** 2026-07-17  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 07 — discriminative hard-negative cases + `neg_at_k` harness; report fusion vs CE without corrupting hit@K  
**Stage that authored this:** Write-dev-guide (pass 102); **Refine-dev-guide** (pass 104)  
**Status:** Ready-check **PASSED** 2026-07-17 (Implement readiness **8.8/10**) — **do not Implement until Tom authorizes Implement Stage**

**Context SSOT:** `ai-knowledge-base-public/docs/2026-07-17_guide07_hard_negative_neg_at_k_context_summary.md`  
**Handoff:** `second_brain/docs/2026-07-17_spoke_ai_kb_guide07_refine_pass104_handoff.md`  
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
- `second_brain/docs/2026-07-17_spoke_ai_kb_guide07_refine_pass104_handoff.md`
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
| Required hard-neg fields | `id`, `query`, `kind: "hard_negative"`, `forbidden_source_ids` (non-empty list of `fixture:*` ids), `must_cite: false` |
| Optional field | `expected_source_ids` — informational only if present; **still excluded** from hit@K |
| Load validation | Validate in `load_golden_cases` (or immediately after): on `kind=hard_negative`, **raise `ValueError`** if `forbidden_source_ids` missing/empty/non-list, or any id ∉ manifest `source_id` set |
| `neg_ok` | `set(forbidden_source_ids) ∩ set(returned_source_ids) == ∅` |
| Arm JSON fields (both fusion + CE) | Always set: `cases` (total goldens loaded), `easy_cases` (non-hard-neg count), `hard_negative_cases`, `neg_ok_count`, `neg_at_k` (`null` if `hard_negative_cases==0`), plus existing Guide 06 keys |
| `neg_at_k` placement | **Per arm only** (`fusion.neg_at_k`, `ce.neg_at_k`) — do **not** add a top-level `neg_at_k` |
| hit@K | `hits` / `hit_at_k` computed **only** over easy cases; denominator `max(easy_cases, 1)` |
| CE-success metrics | Count `ranking_stage=="ce"` **and** easy-case only for `ce_success_cases` / `ce_success_hits` / `ce_success_hit_at_k` |
| `_decide_ce_keep` coverage | Prefer `easy_cases` when present: use `int(ce.get("easy_cases") or ce.get("cases") or 0)` (and same idea for comparing coverage). Do **not** pass total `cases` including hard-neg as keep coverage |
| Detail rows | Hard-neg: `neg_ok` (bool), `kind`, `returned_source_ids`; do **not** increment easy `hits` |
| Spot-check B2 | **Mandatory DoD** — for each `hn*`, run hybrid retrieve; prefer temptations where fusion **currently returns** a forbidden id. If fewer than 4 such traps exist after honest authoring, ship best 4–6 anyway and note in `ce_keep_note` that some traps are not currently fusion-failing |
| Docs | Update `ce_keep_note`, GETTING_STARTED, INTERVIEW, PORTFOLIO_VISION — report per-arm `neg_at_k`; do not claim CE lift unless CE `neg_at_k` clearly exceeds fusion **and** prose says that is separate from `ce_keep` |
| Tests | New `tests/test_eval_neg_at_k.py` (keep `test_eval_ce_honesty.py` intact): `neg_ok`; hit@K exclusion; keep uses `easy_cases`; load reject empty/unknown forbidden |
| Files likely touched | `src/eval/__init__.py`, `tests/test_eval_neg_at_k.py`, `fixtures/eval/golden_cases.jsonl`, honesty docs |
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

- [ ] Harness: `hard_negative` + `forbidden_source_ids` → per-arm `neg_ok_count` / `neg_at_k`  
- [ ] Hard-neg excluded from hit@K and CE-success hit@K / keep coverage (`easy_cases`)  
- [ ] Load raises on invalid hard-neg schema  
- [ ] **4–6** fixture-grounded `hn*` cases; easy `g1`–`g18` preserved  
- [ ] B2 spot-check documented (prefer fusion currently fails forbidden)  
- [ ] Unit tests in `tests/test_eval_neg_at_k.py`  
- [ ] Eval re-run; `ce_keep_note` includes fusion/CE `neg_at_k` + `ce_keep` still hit@K-gated  
- [ ] GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION updated — not eval-complete; no fake lift  
- [ ] No `CE_ENABLED` flip; no private/embedding scope  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Refine-dev-guide / Ready-check.**

### Phase A — Harness

- [ ] **A1.** Helpers: `is_hard_negative`, `neg_ok`, `validate_hard_negatives(cases, manifest_ids)` → raise `ValueError` on bad rows.  
- [ ] **A2.** Call validate after `load_golden_cases` in `run_fixture_eval`.  
- [ ] **A3.** Split easy vs hard-neg; `hit_at_k` / `hits` over easy only; set `cases`, `easy_cases`, `hard_negative_cases`.  
- [ ] **A4.** Per arm: `neg_ok_count`, `neg_at_k` (`null` if zero hard-neg).  
- [ ] **A5.** CE-success_* only on easy rows with `ranking_stage=="ce"`; `_decide_ce_keep` coverage via `easy_cases`.  
- [ ] **A6.** Detail: hard-neg get `neg_ok`; never increment easy hits.  
- [ ] **A7.** `tests/test_eval_neg_at_k.py`: neg_ok; exclusion; keep+`easy_cases`; reject empty/unknown forbidden.

### Phase B — Author goldens

- [ ] **B1.** Read six fixture transcripts; draft **4–6** trap queries.  
- [ ] **B2.** **Mandatory:** hybrid retrieve spot-check each; prefer fusion currently returns forbidden id; note outcomes for `ce_keep_note` if some do not.  
- [ ] **B3.** Append `hn1`…; keep `g1`–`g18`.  
- [ ] **B4.** Every forbidden id ∈ manifest.

### Phase C — Eval + honesty

- [ ] **C1.** `uv run python -m src.eval` (Ollama + HF MiniLM).  
- [ ] **C2.** Update `ce_keep_note`: easy metrics; hard-neg N; `fusion.neg_at_k` / `ce.neg_at_k`; `ce_keep` not from neg.  
- [ ] **C3.** Update GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION.  
- [ ] **C4.** Stop. No CE flip. No easy-golden growth. No fake lift.

---

## Verification / Definition of Done

```bash
# From ai-knowledge-base-public/
wc -l fixtures/eval/golden_cases.jsonl   # expect 22–24 (18 easy + 4–6 hard-neg)
rg -n '"kind": "hard_negative"' fixtures/eval/golden_cases.jsonl
uv run pytest tests/test_eval_ce_honesty.py tests/test_eval_neg_at_k.py -q
uv run python -m src.eval
# Inspect: fusion.neg_at_k, ce.neg_at_k, easy_cases=18, hit_at_k over easy only,
# ce_keep from Guide 06 rules (not neg alone); no top-level neg_at_k
rg -n 'neg_at_k|hard_negative|forbidden_source|easy_cases' \
  docs/2026-07-12_ce_keep_note.md GETTING_STARTED.md INTERVIEW.md docs/PORTFOLIO_VISION.md
```

**DoD:**

1. Per-arm `neg_at_k` / `neg_ok_count` / `hard_negative_cases` / `easy_cases`; hard-neg excluded from hit@K + CE-success keep denominators.  
2. Invalid hard-neg schema raises at load/validate.  
3. 4–6 `hn*` grounded; `g1`–`g18` preserved; **B2 spot-check done**.  
4. `tests/test_eval_neg_at_k.py` covers neg_ok + exclusion + keep/`easy_cases` + validation.  
5. Eval + honesty docs match; no fake lift; `ce_keep` not from `neg_at_k` alone.  
6. No CE/embedding/private flips.

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| Corrupt hit@K by counting hard-neg | Easy-only denominator + tests |
| Keep coverage uses total `cases` incl. hard-neg | Pin `easy_cases` into `_decide_ce_keep` |
| `ce_keep=true` from noisy neg lift | Locked: keep ignores `neg_at_k` |
| Trivial traps → `neg_at_k=1.0` | Mandatory B2; note in ce_keep_note |
| Unknown forbidden ids | Validate vs manifest |
| Doc overclaim | Same-delivery honesty |
| Scope into easy golden growth | Only add `hn*` |

### Rollback

Revert eval + golden + doc commits; or delete `hn*` lines and harness fields.

---

## Edge-case handling

| Case | Behavior |
|------|----------|
| Zero hard-neg in file | `neg_at_k: null`; `hard_negative_cases: 0`; hit@K over easy (=all) |
| Empty `forbidden_source_ids` | `ValueError` at validate |
| Multiple forbidden ids | neg_ok only if **none** in top-K |
| CE `fusion_degraded` | Score neg_ok on returned fused order |
| RetrievalError on hard-neg | Detail error; not neg_ok success; not easy hit |
| Ollama / HF down | Guide 06 footguns |

---

## Stop conditions

- Harness + 4–6 cases + B2 + eval + honesty landed  
- **No** `ce_keep` flip from `neg_at_k` alone  
- **No** fake CE lift ads  
- **No** CE_ENABLED / embedding / private flip  
- **No** easy `g*` growth theater  
- Stop for human if asked to claim lift without evidence  

---

## Refine pass notes (pass 104)

- Locked arm JSON: `easy_cases`, `hard_negative_cases`, `neg_ok_count`, `neg_at_k` (null when 0); **per arm only**.  
- Locked `_decide_ce_keep` to prefer `easy_cases` for coverage.  
- Locked load validation → `ValueError`; B2 spot-check **mandatory DoD**.  
- Tests file pinned: `tests/test_eval_neg_at_k.py`.

---

## Ready-check result (2026-07-17)

| Track | Implement ready? | Score (0–10) | Why not 10 |
|-------|------------------|--------------|------------|
| Guide 07 hard-negative / `neg_at_k` | **Yes** (await Tom authorize Implement) | **8.8** | `hn*` query craft; B2 may find <4 fusion-failing traps (ship-with-note OK); Phase C Ollama/HF runtime; minor docs labeling craft. No pin conflicts. |

**Artifact:** `docs/2026-07-17_guide07_hard_negative_ready_check.md`  
**Implement now:** **No** until Tom authorizes Implement Stage.  
**Further Refine-dev-guide:** **Not required.**
