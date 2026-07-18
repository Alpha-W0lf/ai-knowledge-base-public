# Dev Guide 08 — Harder CE-discriminative eval (confusable fixtures)

**Date:** 2026-07-18  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 08 — harder CE-discriminative traps via B1 confusable corpus growth + `neg_at_k` re-baseline  
**Stage that authored this:** Write-dev-guide (pass 152)  
**Status:** **Align-docs done** 2026-07-18 — Gather/Ready-check superseded; slice closed. Implement `ec6d8fe`; Review shippable.  

**Context SSOT:** `ai-knowledge-base-public/docs/2026-07-18_harder_ce_discriminative_eval_context_summary.md`  
**Handoff:** `second_brain/docs/2026-07-18_spoke_aikb_align_ce_eval_pass153_handoff.md`  
**Review note:** `docs/2026-07-18_guide08_harder_ce_discriminative_review.md`  
**Align note:** `docs/2026-07-18_guide08_harder_ce_discriminative_align.md`  
**Prerequisite:** Guide 07 Align done — harness + `hn1`–`hn6`; fusion/CE `neg_at_k` **0.0**; `ce_keep=false`; not eval-complete.

**Tom / hub locks (do not reopen — pass 152):**

| Lock | Value |
|------|--------|
| Trap strategy | **B1** — add **1–2** confusable synthetic fixtures (total fixtures **≤8**, KB1) |
| Eval-complete bar | **E3** — do **not** auto-check eval-complete / portfolio “eval-complete” on a flat run |
| Review residual R1 | **Fold** — thin Hub-free exclusion smoke in `tests/test_eval_neg_at_k.py` |
| Metric formula | Guide 06/07 unchanged — `neg_ok` / per-arm `neg_at_k`; hard-neg excluded from hit@K + keep |
| `ce_keep` | **Not** flipped by `neg_at_k` alone |
| Honesty | Ship **flat** if CE still fails hard-negs; no fake lift ads |
| Stack | No `CE_ENABLED` flip; no private flip; no KB4 embedding change |

---

## Objective

1. Keep the Guide 07 eval harness (**no metric redesign**). Fold thin **R1** exclusion smoke.  
2. Add **1–2** confusable synthetic fixture docs (overlapping lexical tokens, **distinct** facts) so CE *might* demote a forbidden sibling that fusion keeps.  
3. Author **+4–6** new hard-negative goldens (`hn7`…) targeting those confusable pairs; keep `hn1`–`hn6` + `g1`–`g18` as regression.  
4. Re-run `uv run python -m src.eval`; record fusion vs CE `neg_at_k` + easy hit@K / CE-success.  
5. Refresh honesty docs — **still not eval-complete** (E3); claim CE hard-neg lift **only** if CE `neg_at_k` > fusion `neg_at_k`.

**Success signal:** Stranger runs eval; sees updated per-arm `neg_at_k` after corpus growth; docs match metrics; flat outcome is shippable honesty; no unearned CE relevance ads; `ce_keep` still hit@K-gated.

---

## Learning notes (interview-portable)

1. **Confusable corpus** — on tiny fixture sets, paraphrase-only queries rarely create cross-encoder vs fusion asymmetry; overlapping-but-distinct docs are the usual next lever.  
2. **Hard negative** — success = forbidden `source_id` absent from top-K (not merely gold present).  
3. **Anti–eval gaming** — do not CE-probe during authoring to cherry-pick only CE-win rows; measure after honest craft.  
4. **Keep vs report** — higher CE `neg_at_k` is evidence to *report*; it does not flip product `ce_keep` without an explicit keep-policy lock.

---

## References (paths only)

- `ai-knowledge-base-public/docs/2026-07-18_harder_ce_discriminative_eval_context_summary.md`
- `ai-knowledge-base-public/docs/2026-07-12_ce_keep_note.md`
- `ai-knowledge-base-public/docs/2026-07-17_guide07_hard_negative_review.md` (R1)
- `ai-knowledge-base-public/docs/dev_guides/2026-07-17_dev_guide_07_hard_negative_neg_at_k.md`
- `ai-knowledge-base-public/docs/PORTFOLIO_VISION.md`
- `ai-knowledge-base-public/docs/ARCHITECTURE.md` (KB1 ≈3–8; KB5)
- `ai-knowledge-base-public/GETTING_STARTED.md`
- `ai-knowledge-base-public/INTERVIEW.md`
- `ai-knowledge-base-public/fixtures/eval/golden_cases.jsonl`
- `ai-knowledge-base-public/fixtures/manifest.json`
- `ai-knowledge-base-public/fixtures/PROVENANCE.md`
- `ai-knowledge-base-public/fixtures/transcripts/`
- `ai-knowledge-base-public/src/eval/__init__.py`
- `ai-knowledge-base-public/tests/test_eval_neg_at_k.py`
- `mechanic_rag/docs/2026-07-17_guide08_harder_discriminative_ce_traps_context_summary.md` (T1 lesson — flat still possible)
- `second_brain/docs/2026-07-18_spoke_aikb_write_ce_eval_pass152_handoff.md`
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`

---

## Architecture constraints (binding)

1. **KB5 stack unchanged:** hybrid → RRF → pluggable local CE; degrade `fusion_degraded` + `error`.  
2. **KB1 ceiling:** total committed fixtures **≤8** after this guide (today = 6; add **1 or 2**).  
3. **Guide 06/07 keep math stays:** `_decide_ce_keep` uses CE-success hit@K vs fusion hit@K only — **never** `ce_keep=true` solely from CE `neg_at_k` > fusion.  
4. **Harness contract unchanged** except optional R1 test coverage — no new metric formula, no top-level `neg_at_k`.  
5. **Fixture-first only** — synthetic committed fixtures; no BYO YouTube as eval DoD; no private tip / flip work.  
6. **E3 honesty:** Implement **must not** check PORTFOLIO_VISION / INTERVIEW “eval-complete” from a flat Guide 08 run.  
7. **No** `CE_ENABLED` / embedding / private flip; **no** easy `g*` theater growth.

---

## Soft pins

| Pin | Locked default |
|-----|----------------|
| Corpus growth | **B1:** add **1–2** new `fixtures/transcripts/*.md` + `manifest.json` + `PROVENANCE.md` rows |
| Prefer count | Prefer **2** if both confusable pairs author cleanly; **1** is OK if ≥4 new fusion-tempting traps exist |
| New source_id shape | `fixture:<slug>-07` and optional `fixture:<slug>-08` (do not reuse `01`–`06`) |
| Confusable pair A (required if only one doc) | **Fusion twin:** overlaps “rank fusion / combine ranked lists / shortlist” language with `fixture:fusion-rrf-04`, but states a **different** method (e.g. CombSUM / score-sum fusion — **not** RRF `1/(k+rank)`). Distinct title + facts. |
| Confusable pair B (second doc when shipping 2) | **CE twin:** overlaps “rerank shortlist / query and passage / N→K” language with `fixture:cross-encoder-05`, but states a **different** mechanism (e.g. bi-encoder late score or different N/K defaults / no `fusion_degraded` wording). Distinct title + facts. |
| Anti-paraphrase | New `hn*` must **not** be near-paraphrases of `hn1`–`hn6`; ground in **new** fixture wording + gold sibling contrast |
| Anti-probe | During authoring, do **not** iterate CE-on solely to cherry-pick CE-win rows. Fusion spot-check (B2) is mandatory; CE comparison is Phase D measurement |
| New hard-neg count | Soft **+4–6** (`hn7`…); hard max **total** hard-neg rows **≤10** (existing 6 + new ≤4 → prefer quality; if +6 new, total 12 only if Tom later unlocks — **default hard max total = 10**) |
| Case ids | Continue `hn7`…; never reuse `g1`–`g18` or `hn1`–`hn6` |
| Case file | Append to `fixtures/eval/golden_cases.jsonl`; preserve all existing 24 lines |
| Hard-neg schema | Same as Guide 07: `kind: "hard_negative"`, non-empty `forbidden_source_ids`, `must_cite: false`; optional `expected_source_ids` (informational; still excluded from hit@K) |
| Forbidden targeting | Prefer forbidden = **new confusable twin** when query is about the **original** sibling (or reverse) — not a distant unrelated fixture |
| Spot-check B2 | **Mandatory:** for each **new** `hn*`, hybrid retrieve with CE off; prefer fusion returns forbidden. If fewer than 4 new fusion-failing traps after honest craft, ship best set + note in `ce_keep_note` |
| Easy regression | After corpus growth, easy `g1`–`g18` fusion hit@K should remain **1.0**; if not, investigate before claiming success |
| R1 smoke | Extend `tests/test_eval_neg_at_k.py` with Hub-free monkeypatched `retrieve` (or equivalent) asserting hard-neg rows do **not** inflate `hits` / `hit_at_k` over easy-only math |
| R2 / R3 | **Parked** — do not expand validate/`must_cite` or easy-error counting unless free one-liner |
| Docs | Update `ce_keep_note`, GETTING_STARTED, INTERVIEW, PORTFOLIO_VISION — Guide 08 honesty; **do not** check eval-complete (E3) |
| Files likely touched | `fixtures/transcripts/` (+1–2), `fixtures/manifest.json`, `fixtures/PROVENANCE.md`, `fixtures/eval/golden_cases.jsonl`, `tests/test_eval_neg_at_k.py`, honesty docs; **usually not** `src/eval/__init__.py` unless R1 needs a tiny test-only hook |
| Non-goals | Fake lift; `ce_keep` from neg; eval-complete auto-check; query-only B2-as-sole strategy; private flip; CE/embedding flip; easy `g*` growth; R2/R3; ranking redesign |

### Suggested new temptation themes (implementer aid)

| Theme | Gold lean (optional expected) | Forbidden lean |
|-------|-------------------------------|----------------|
| True RRF vs CombSUM twin | `fixture:fusion-rrf-04` | new fusion-twin id |
| CombSUM twin vs true RRF | new fusion-twin id | `fixture:fusion-rrf-04` |
| True CE degrade vs bi-encoder twin | `fixture:cross-encoder-05` | new CE-twin id |
| Bi-encoder twin vs true CE | new CE-twin id | `fixture:cross-encoder-05` |
| RRF shortlist feeds CE (original) vs twin distraction | `fixture:fusion-rrf-04` or `fixture:cross-encoder-05` | the twin that shares vocab but wrong fact |

Exact slug names and body prose are **Implement invent** within these pins — keep docs short (same scale as existing ~5–10 line stubs).

---

## Acceptance criteria

- [x] R1: Hub-free test proves hard-neg excluded from easy `hits` / `hit_at_k` (monkeypatched retrieve smoke)  
- [x] +1 or +2 confusable fixtures landed; total fixtures ≤8; manifest + PROVENANCE updated  
- [x] +4–6 new `hn*` (total hard-neg ≤10); `hn1`–`hn6` + `g1`–`g18` preserved  
- [x] B2 spot-check documented for new traps (prefer fusion-failing)  
- [x] Live eval re-run; `ce_keep_note` records fusion/CE `neg_at_k`, easy metrics, B2 notes  
- [x] Honesty docs updated; **eval-complete remains unchecked** (E3); no fake lift; `ce_keep` not from `neg_at_k`  
- [x] No `CE_ENABLED` / private / embedding flip  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Refine-dev-guide / Ready-check.**

### Phase A — R1 exclusion smoke (thin)

- [x] **A1.** In `tests/test_eval_neg_at_k.py`, add a Hub-free test that runs `run_fixture_eval` (or a thin helper) with `retrieve` monkeypatched to return deterministic hits for one easy + one hard-neg case.  
- [x] **A2.** Assert easy `hits` / `hit_at_k` ignore the hard-neg row (hard-neg must not increment `hits`; `easy_cases` counts only easy). Prefer temp golden file or monkeypatch `load_golden_cases` to avoid depending on live Ollama.  
- [x] **A3.** Keep existing neg_ok / validate / keep tests green. **Do not** change production metric formula.

### Phase B — Confusable fixtures (B1)

- [x] **B1.** Author **1–2** new synthetic markdown transcripts under `fixtures/transcripts/` per soft pins (fusion twin required if only one; add CE twin when shipping two).  
- [x] **B2.** Register each in `fixtures/manifest.json` (`source_id`, title, license `synthetic`, file path, notes).  
- [x] **B3.** Update `fixtures/PROVENANCE.md` table.  
- [x] **B4.** Confirm total fixture count ∈ {7, 8}. Re-ingest path is existing `ingest_fixtures` — no new ingest code unless broken.

### Phase C — New hard-neg goldens

- [x] **C1.** Draft **+4–6** trap queries targeting confusable pairs (anti-paraphrase vs `hn1`–`hn6`).  
- [x] **C2.** **Mandatory B2:** for each new `hn*`, hybrid retrieve `ce_enabled=False`; prefer forbidden currently in top-K; record outcomes for `ce_keep_note`.  
- [x] **C3.** Append `hn7`… to `golden_cases.jsonl`; preserve existing 24 lines; `must_cite: false`; forbidden ids ∈ updated manifest.  
- [x] **C4.** Do **not** CE-probe to cherry-pick wins (anti-probe pin).

### Phase D — Eval + honesty

- [x] **D1.** `uv run pytest tests/test_eval_ce_honesty.py tests/test_eval_neg_at_k.py -q`  
- [x] **D2.** `uv run python -m src.eval` (Ollama + HF MiniLM).  
- [x] **D3.** Confirm easy fusion hit@K still **1.0** (regression). If broken, fix fixtures/queries before honesty claims.  
- [x] **D4.** Update `docs/2026-07-12_ce_keep_note.md`: fixture N; hard-neg N; `fusion.neg_at_k` / `ce.neg_at_k`; B2 notes; `ce_keep` still hit@K-gated; state flat or lift honestly.  
- [x] **D5.** Update GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION — Guide 08 landed; **do not** check eval-complete (E3); no CE relevance ads unless CE `neg_at_k` > fusion.  
- [x] **D6.** Stop. No CE flip. No private flip. No easy `g*` growth.

---

## Verification / Definition of Done

```bash
# From ai-knowledge-base-public/
python -c "import json; print(len(json.load(open('fixtures/manifest.json'))['fixtures']))"
# expect 7 or 8

wc -l fixtures/eval/golden_cases.jsonl
# expect 28–30 (24 prior + 4–6 new hn*) — hard max total hard-neg ≤10 ⇒ ≤30 lines

rg -n '"kind": "hard_negative"' fixtures/eval/golden_cases.jsonl | wc -l
# expect 10–12 soft; prefer ≤10 hard-neg rows total

uv run pytest tests/test_eval_ce_honesty.py tests/test_eval_neg_at_k.py -q
uv run python -m src.eval
# Inspect: fusion.neg_at_k, ce.neg_at_k, easy_cases=18, hit_at_k over easy only,
# ce_keep from Guide 06 rules (not neg alone); no top-level neg_at_k

rg -n 'Guide 08|neg_at_k|eval-complete|confusable' \
  docs/2026-07-12_ce_keep_note.md GETTING_STARTED.md INTERVIEW.md docs/PORTFOLIO_VISION.md
# eval-complete must remain unchecked / explicitly not claimed
```

**DoD:**

1. R1 exclusion smoke present and green (Hub-free).  
2. +1–2 confusable fixtures; total ≤8; manifest + PROVENANCE match.  
3. +4–6 new `hn*`; total hard-neg ≤10; prior goldens preserved; B2 documented.  
4. Live eval recorded; easy hit@K regression held (or failure investigated — not ignored).  
5. Honesty docs match metrics; **E3:** eval-complete **not** checked; no fake lift; `ce_keep` not from `neg_at_k`.  
6. No CE / embedding / private flips.

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| Confusable docs CE-probed into fake lift | Anti-probe pin; ship flat; no keep flip |
| Exceed KB1 (>8 fixtures) | Hard stop at 8 |
| New corpus breaks easy hit@K | D3 regression gate before honesty |
| Query-only traps slip in as sole strategy | B1 locked; new fixtures required |
| Eval-complete theater after flat | E3 lock — leave unchecked |
| R1 expands into harness rewrite | Test-only monkeypatch; no formula change |
| Mechanic freeze confusion | AI KB metric remains `neg_at_k`, not paired-ask delta |
| Private flip / channels | Locked out |

### Rollback

Revert fixture + golden + test + doc commits; or delete new `hn*` / new transcripts and restore manifest to 6.

---

## Edge-case handling

| Case | Behavior |
|------|----------|
| Only 1 confusable doc authors cleanly | Ship 1 (total fixtures = 7); still prefer ≥4 new traps |
| <4 new fusion-failing traps after honest craft | Ship best set; note in `ce_keep_note` (Guide 07 B2 precedent) |
| CE `neg_at_k` > fusion | Report rejection lift; **still** no auto `ce_keep` flip; **still** no eval-complete check without later Tom lock |
| CE `neg_at_k` == fusion (flat) | Shippable honesty; E3 holds |
| CE `neg_at_k` < fusion | Document; keep seam; no CE disable without authorize |
| Easy hit@K drops below 1.0 | Block honesty “success”; fix or escalate |
| HF / Ollama down | Unit tests still green; live eval required for `ce_keep_note` (Guide 06/07 pattern) |
| New forbidden id missing from manifest | `validate_hard_negatives` → `ValueError` |
| Temptation to grow easy `g*` | Out of scope — stop |

---

## Stop conditions

- R1 + B1 fixtures + new `hn*` + B2 + eval + honesty landed  
- **No** eval-complete auto-check (E3)  
- **No** `ce_keep` flip from `neg_at_k` alone  
- **No** fake CE lift ads  
- **No** `CE_ENABLED` / embedding / private flip  
- **No** query-only-only path as substitute for B1  
- Stop for human if asked to claim lift or eval-complete without evidence / lock  

---

## Open invent (Implement — not Write blockers)

Exact markdown bodies, slug strings, and final `hn7+` query wording are Implement craft within soft pins above. Optional short Refine only if Ready-check finds pin conflicts (none expected).

---

## Ready-check / Implement / Review / Align

### Ready-check result (2026-07-18)

| Track | Implement ready? | Score (0–10) | Why not 10 |
|-------|------------------|--------------|------------|
| Guide 08 harder CE-discriminative eval | **Yes** (await Tom authorize Implement) | **8.7** | Fixture slug/body invent; `hn7+` + B2 yield; easy hit@K regression runtime; Ollama/HF live eval; prefer +4 new hn to keep total hard-neg ≤10 |

**Artifact:** `docs/2026-07-18_guide08_harder_ce_discriminative_ready_check.md`  
**Further Refine-dev-guide:** **Not required.**  
**Implement now:** **Authorized** (pass 152) — Implement done below.

---

## Implement result (2026-07-18)

| Item | Outcome |
|------|---------|
| Confusable fixtures | `fixture:combsum-fusion-07` + `fixture:bi-encoder-rerank-08` (total **8**) |
| Hard-neg cases | `hn1`–`hn10` (10); `g1`–`g18` preserved; total **28** JSONL lines |
| B2 spot-check (new) | **4/4** `hn7`–`hn10` fusion returned forbidden |
| R1 | `test_run_fixture_eval_excludes_hard_neg_from_hit_at_k` Hub-free |
| Unit tests | honesty + neg_at_k → **16 passed** |
| Live eval | easy hit@K fusion/CE **1.0**; CE-success **18/18**; `fusion.neg_at_k` **0.0**; `ce.neg_at_k` **0.0**; `ce_keep=false` |
| Honesty | Docs updated; **E3** eval-complete **unchecked**; no fake lift; no `CE_ENABLED` / private / embedding flip |
| Next | **Await Tom authorize Review** — do not self-start |

---

## Review result (2026-07-18)

| Call | Value |
|------|--------|
| Shippable as-is? | **Yes** |
| Must-fix? | **None** |
| Review note | `docs/2026-07-18_guide08_harder_ce_discriminative_review.md` |
| Re-verify | pytest honesty + neg_at_k → **16 passed**; fixtures **8**; goldens **28**; hard-neg **10** |
| E3 / flat | Confirmed shippable — fusion/CE `neg_at_k` 0.0; eval-complete unchecked |
| Next | **Await Tom authorize Align** (optional banners) — do not self-start |

---

## Align-docs result (2026-07-18)

| Item | Outcome |
|------|---------|
| Gather context | Superseded banner + Outcome table → `ce_keep_note` SSOT |
| Ready-check | Superseded banner; pre-Implement invent historical |
| Review G08-R1 | Closed |
| Verified current | `ce_keep_note`, PORTFOLIO_VISION, GETTING_STARTED, INTERVIEW, README — Guide 08 flat honesty; E3 eval-complete unchecked |
| Private flip / CE lift / eval-complete check | **Not** done (locks held) |
| Slice | **Closed** pending any new hub work |
