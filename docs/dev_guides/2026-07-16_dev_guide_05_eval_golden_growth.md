# Dev Guide 05 — Eval golden growth (fixture-first)

**Date:** 2026-07-16  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 05 — grow fixture golden cases; re-run eval; refresh CE honesty; keep sophisticated hybrid → fusion → CE seam  
**Stage that authored this:** Write-dev-guide (pass 61); Refine-dev-guide (pass 62–64)  
**Status:** Refined (pass 64 VERIFY — no material edits; scores held) — ready for Ready-check; **not implemented**

**Context SSOT:** `ai-knowledge-base-public/docs/2026-07-15_guide05_eval_growth_context_summary.md`  
**Locks:** `second_brain/docs/2026-07-16_human_locks_pass60_fan_in.md`  
**Prerequisite:** Guides 01–04 packaging shippable. Public corpus = committed `fixtures/` only.

---

## Objective

1. Grow `fixtures/eval/golden_cases.jsonl` from **6** cases to a documented **N ≥ 18** (soft pin below).  
2. Every new case must be answerable from **committed fixture transcript text** only (no invented corpus facts).  
3. Re-run `uv run python -m src.eval`; record hit@K / CE vs fusion honesty.  
4. Update `ce_keep_note`, GETTING_STARTED, INTERVIEW, PORTFOLIO_VISION — still **not** eval-complete / v1 Done.  
5. Keep the sophisticated stack: vector + FTS → RRF → optional cross-encoder with degrade — without advertising unproven lift.

**Success signal:** Stranger can run eval on a larger golden set; docs say what N is and whether CE helped on that set.

---

## Learning notes (new for this guide)

1. **Eval growth ≠ claiming lift** — More cases improve confidence in measurements; they do not automatically produce CE lift.  
2. **Fixture grounding** — Goldens that need facts outside `fixtures/transcripts/*.md` are invalid for this guide.  
3. **Sophistication** — The portfolio story is the full retrieval spine + honest metrics, not a fake “CE wins” banner.

---

## References (paths only)

- `ai-knowledge-base-public/docs/2026-07-15_guide05_eval_growth_context_summary.md`
- `ai-knowledge-base-public/docs/2026-07-12_ce_keep_note.md`
- `ai-knowledge-base-public/docs/PORTFOLIO_VISION.md`
- `ai-knowledge-base-public/docs/ARCHITECTURE.md`
- `ai-knowledge-base-public/GETTING_STARTED.md`
- `ai-knowledge-base-public/INTERVIEW.md`
- `ai-knowledge-base-public/fixtures/eval/golden_cases.jsonl`
- `ai-knowledge-base-public/fixtures/transcripts/`
- `ai-knowledge-base-public/fixtures/manifest.json`
- `second_brain/docs/2026-07-16_human_locks_pass60_fan_in.md`
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`

---

## Architecture constraints (binding)

1. **Fixture-first only** — no BYO YouTube eval; no private tip scrub; no January rewrite; no KB4 embedding model change.  
2. **Do not flip CE default** without metrics + human authorize.  
3. Keep CE seam + `fusion_degraded` path.  
4. Same-delivery honesty: larger baseline ≠ “eval-complete.”

---

## Soft pins

| Pin | Locked default |
|-----|----------------|
| Target **N** | **≥ 18** distinct cases (grow from 6 → at least `g7`…`g18`) |
| Case file | `fixtures/eval/golden_cases.jsonl` (one JSON object per line) |
| Required fields | Keep existing shape: `id`, `query`, `expected_source_ids`, `must_cite`, `kind` |
| `kind` | `lexical` \| `semantic` only (harness does not special-case other kinds) |
| Theme mix | ≥2 cases per fixture transcript; mix lexical + semantic |
| Hard negatives | **Defer this guide** — empty `expected_source_ids` always scores as a miss and would distort hit@K; do not invent harness features |
| Eval command | `uv run python -m src.eval` (calls `run_fixture_eval(..., use_ce=True)` — fusion vs CE comparison already built in) |
| Metrics to record | From printed JSON: `fusion.hit_at_k`, `ce.hit_at_k`, `ce_keep`, `ce_justify`, `cases` |
| CE keep decision | Update `ce_keep_note` from harness output; **do not** flip `CE_ENABLED` default without human authorize after metrics |
| Grounding rule | Every query must be answerable from the cited transcript file’s actual wording (paraphrase OK; invented facts forbidden) |

### Suggested case themes (implementer aid — not exhaustive)

| Fixture | source_id | Example themes |
|---------|-----------|----------------|
| rag-hooks-01.md | `fixture:rag-hooks-01` | hybrid stages; hooks ordering |
| mcp-allowlist-02.md | `fixture:mcp-allowlist-02` | public allowlist; absent mutating tools |
| embedding-version-03.md | `fixture:embedding-version-03` | stamp change → rebuild index |
| fusion-rrf-04.md | `fixture:fusion-rrf-04` | RRF combine FTS + vector |
| cross-encoder-05.md | `fixture:cross-encoder-05` | query+passage scoring; top K |
| fixture-ingest-06.md | `fixture:fixture-ingest-06` | fixture provenance without personal YouTube |

---

## Acceptance criteria

- [ ] `golden_cases.jsonl` has **N ≥ 18** unique `id`s  
- [ ] Each case’s `expected_source_ids` ⊆ committed fixture ids; query grounded in that doc’s text  
- [ ] Eval re-run completed; `ce_keep_note` records N + fusion vs CE hit@K + `ce_keep` / justify text  
- [ ] GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION updated — not eval-complete; CE lift only if measured  
- [ ] No tip scrub / embedding model change / MCP mutation default change / harness redesign  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Ready-check.**

### Phase A — Inventory

- [ ] **A1.** Read all six fixture transcripts; list ≥2 candidate questions per doc.  
- [ ] **A2.** Re-read `src/eval/__init__.py` field contract (`expected_source_ids`, `must_cite`) — do not break it.

### Phase B — Author goldens

- [ ] **B1.** Add cases to reach N ≥ 18 with unique ids (`g7`…).  
- [ ] **B2.** Prefer paraphrase diversity (not copy-paste of g1–g6).  
- [ ] **B3.** Spot-check: every expected source appears in manifest / transcripts; no empty `expected_source_ids`.

### Phase C — Eval + honesty

- [ ] **C1.** Run `uv run python -m src.eval` (needs Ollama + embeddings as today).  
- [ ] **C2.** Update `docs/2026-07-12_ce_keep_note.md` with new N + fusion/CE metrics + justify string.  
- [ ] **C3.** Align GETTING_STARTED / INTERVIEW Theme 6 / PORTFOLIO_VISION.  
- [ ] **C4.** Stop. Do not claim eval-complete; do not flip CE default without human.

---

## Verification / Definition of Done

```bash
# From ai-knowledge-base-public/
wc -l fixtures/eval/golden_cases.jsonl   # expect >= 18
uv run python -m src.eval                # prints fusion + ce + ce_keep JSON
rg -n 'eval-complete|ce_keep|hit@|golden|N=' docs/2026-07-12_ce_keep_note.md GETTING_STARTED.md INTERVIEW.md docs/PORTFOLIO_VISION.md
```

**DoD:** N ≥ 18; eval ran; honesty docs match printed metrics; stack still describes hybrid+fusion+CE; no unearned lift ads; CE default unchanged unless human locked a flip.

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| Invented fixture facts | Quote-only authoring from transcripts |
| Ollama missing | Document skip vs fail per existing harness |
| Overclaim eval-complete | Explicit banner |
| Accidental CE default flip | Human gate |
| Empty expected_source_ids | Forbidden this guide |

### Rollback

Revert golden_cases.jsonl + doc commits.

---

## Edge-case handling

| Case | Behavior |
|------|----------|
| Duplicate questions | Unique ids; distinct query text |
| Ambiguous multi-source | Prefer single expected source when possible |
| CE load failure | Record `fusion_degraded` in details; not an ablation “win” |
| Flat CE vs fusion | Keep seam; `ce_keep=false`; update note (expected and OK) |

---

## Stop conditions

- Goldens + eval + honesty landed  
- **No** private archive work  
- **No** embedding model change  

---

## Refine pass 62 notes

- Confirmed harness already compares fusion vs CE when `use_ce=True`.  
- Deferred hard negatives (empty expected would break hit@K math).  
- Added theme table + metrics fields to record.

---

## Ready for Ready-check?

**Yes.** Ready-check readiness score: **9.0 / 10**.  
Not 10: Implement authors the 12+ new golden questions from fixture text (themes pinned; exact wording is craft). Eval runtime needs Ollama.
