# Dev Guide 05 — Eval golden growth (fixture-first)

**Date:** 2026-07-16  
**Repo:** `ai-knowledge-base-public`  
**Work item:** Guide 05 — grow fixture golden cases; re-run eval; refresh CE honesty; keep sophisticated hybrid → fusion → CE seam  
**Stage that authored this:** Write-dev-guide (pass 61)  
**Status:** Draft — ready for Refine-dev-guide / Ready-check; **not implemented**

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
| Target **N** | **≥ 18** distinct cases (grow from 6; prefer 18–20) |
| Case file | `fixtures/eval/golden_cases.jsonl` (one JSON object per line) |
| Required fields | Keep existing shape: `id`, `query`, `expected_source_ids`, `must_cite`, `kind` |
| `kind` | `lexical` \| `semantic` (and optional `negative` if harness already supports — do not invent harness features) |
| Theme mix | ≥2 cases per fixture transcript when text supports it; mix lexical + semantic |
| Negative / hard-miss | Include **≥2** cases that expect miss or empty cite **only if** current eval harness supports that shape; otherwise document defer |
| Eval command | `uv run python -m src.eval` |
| CE keep decision | Recompute; update note; default flip only with human lock after metrics |

### Fixture sources (committed)

| source_id | File |
|-----------|------|
| `fixture:rag-hooks-01` | `fixtures/transcripts/rag-hooks-01.md` |
| `fixture:mcp-allowlist-02` | `fixtures/transcripts/mcp-allowlist-02.md` |
| `fixture:embedding-version-03` | `fixtures/transcripts/embedding-version-03.md` |
| `fixture:fusion-rrf-04` | `fixtures/transcripts/fusion-rrf-04.md` |
| `fixture:cross-encoder-05` | `fixtures/transcripts/cross-encoder-05.md` |
| `fixture:fixture-ingest-06` | `fixtures/transcripts/fixture-ingest-06.md` |

---

## Acceptance criteria

- [ ] `golden_cases.jsonl` has **N ≥ 18** unique `id`s  
- [ ] Each case’s `expected_source_ids` ⊆ committed fixture ids; query grounded in that doc’s text  
- [ ] Eval re-run completed; summary numbers recorded in `ce_keep_note` (and/or eval output artifact if harness writes one)  
- [ ] GETTING_STARTED / INTERVIEW / PORTFOLIO_VISION updated — not eval-complete; CE lift only if measured  
- [ ] No tip scrub / embedding model change / MCP mutation default change  

---

## Ordered step checklist

All boxes start unchecked. **Do not check boxes in Write / Ready-check.**

### Phase A — Inventory

- [ ] **A1.** Read all six fixture transcripts; list candidate question themes per doc.  
- [ ] **A2.** Confirm eval harness field contract (do not break `src.eval`).

### Phase B — Author goldens

- [ ] **B1.** Add cases to reach N ≥ 18 with unique ids (`g7`…).  
- [ ] **B2.** Prefer paraphrase diversity (not copy-paste of g1–g6).  
- [ ] **B3.** Spot-check: every expected source appears in manifest / transcripts.

### Phase C — Eval + honesty

- [ ] **C1.** Run `uv run python -m src.eval` (Ollama required as today).  
- [ ] **C2.** Update `docs/2026-07-12_ce_keep_note.md` with new N + CE vs fusion outcome.  
- [ ] **C3.** Align GETTING_STARTED / INTERVIEW Theme 6 / PORTFOLIO_VISION.  
- [ ] **C4.** Stop. Do not claim eval-complete; do not flip CE default without human.

---

## Verification / Definition of Done

```bash
# From ai-knowledge-base-public/
wc -l fixtures/eval/golden_cases.jsonl   # expect >= 18
uv run python -m src.eval
rg -n 'eval-complete|ce_keep|hit@|golden' docs/2026-07-12_ce_keep_note.md GETTING_STARTED.md INTERVIEW.md docs/PORTFOLIO_VISION.md
```

**DoD:** N ≥ 18; eval ran; honesty docs match metrics; stack still describes hybrid+fusion+CE; no unearned lift ads.

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| Invented fixture facts | Quote-only authoring from transcripts |
| Ollama missing | Document skip vs fail per existing harness |
| Overclaim eval-complete | Explicit banner |
| Accidental CE default flip | Human gate |

### Rollback

Revert golden_cases.jsonl + doc commits.

---

## Edge-case handling

| Case | Behavior |
|------|----------|
| Duplicate questions | Unique ids; distinct query text |
| Ambiguous multi-source | Prefer single expected source when possible |
| CE load failure | Record `fusion_degraded`; not an ablation win |

---

## Stop conditions

- Goldens + eval + honesty landed  
- **No** private archive work  
- **No** embedding model change  

---

## Ready for Refine-dev-guide?

**Yes** — N soft-pinned; fixture inventory explicit; harness command known.
