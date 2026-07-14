# Dev Guide 01 — Shared retrieval spine (hybrid → fusion → pluggable CE)

**Date:** 2026-07-12  
**Repo:** `ai_knowledge_base`  
**Work item:** Shared retrieval spine — identity/hash/`embedding_version`, hybrid+fusion+pluggable CE, RO MCP allowlist behavior, fixture expectations, degrade, minimal eval  
**Stage that authored this:** Write dev guide  
**Status:** Implemented (pass 8); review shippable (pass 9); docs aligned (pass 10). Aligned to `docs/ARCHITECTURE.md` (KB1–KB5). Guide DoD met via shared spine + fixtures + tests.  
**Post-implement note:** Constraint bullets below that describe “today’s debt” (path-hash `doc_id`, MCP dual path, `--hybrid` no-op, missing fixtures) are **historical authoring context** — resolved in pass 8. Remaining open work is **outside** this guide: KB3-exec scrub, public flip, channel overlay, LICENSE file. CE: **no hit@K lift claim** (`docs/2026-07-12_ce_keep_note.md`). Embeddings: **`nomic-embed-text@768`** (not Gemma).

---

## Objective

Deliver one **shared retrieval function** that CLI and MCP both call, proving the portfolio ranking story on the **preserved** LanceDB + Ollama stack:

**fixture docs → identity + `content_hash` + `embedding_version` → ingest (temp LanceDB) → hybrid (vector + FTS) → fusion (RRF / LanceDB-equivalent) → pluggable local CE (N→K) → typed hits with `ranking_stage`**, plus **fail-closed hybrid readiness**, **CE degrade to fused ranks**, **public MCP read-only allowlist**, and a **minimal fixture eval** (golden relevance + stage latency + groundedness stub).

This guide is the first implementable **vertical slice** (contracts → fixture path → hybrid/fusion → CE seam → RO MCP → minimal eval on one shared spine). It does **not** scrub tip transcripts (KB3-exec), flip the repo public, or rewrite to FastAPI/Postgres.

---

## References (paths only)

- `ai_knowledge_base/docs/ARCHITECTURE.md` (KB1–KB5 binding; §§3–9, §11, §13)
- `ai_knowledge_base/docs/PORTFOLIO_VISION.md`
- `second_brain/docs/2026-07-12_portfolio_vision_workspace_and_decisions.md` (KB1–KB5)
- `second_brain/docs/2026-07-12_hybrid_rag_reranker_decision.md`
- `second_brain/docs/2026-07-12_ai_kb_write_dev_guide_pass5_handoff.md`
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`
- Current debt surfaces (read before editing): `src/search.py`, `src/ingest.py`, `src/schema.py`, `src/mcp_server.py`, `src/config.py`, `src/embed.py`

---

## Architecture constraints (binding)

1. **KB4:** Keep LanceDB + Ollama `nomic-embed-text` @ 768d. No January clean rewrite. No HTTP/FastAPI layer. No Postgres/pgvector. No embedding model migration without eval + full rebuild.  
2. **KB5:** Ranking = hybrid retrieve → fusion → **pluggable CE** (N→K) → return. Local CE preferred. Architecture locks *local-first + pluggable*, not a brand; this guide **pins a default model id** in Locked knobs so Implement does not stall — swap stays adapter-only.  
3. **One shared spine:** CLI and MCP must call the same retrieval function in `src/search.py` (or a clearly named module that `search.py` re-exports). **Delete / stop owning** the duplicate LanceDB search path inside `src/mcp_server.py`.  
4. **Implement order:** identity + `content_hash` + `embedding_version` + FTS ensure + shared hybrid/fusion **before** wiring CE. CE must not rank garbage/stale chunks.  
5. **Hybrid honesty:** Before hybrid runs, confirm `transcripts` table + FTS on `text`. If FTS cannot be ensured → **fail closed** (clear error). Do **not** silently fall back to vector while advertising hybrid. Prefer explicit RRF / LanceDB hybrid fusion; do not treat `HYBRID_VECTOR_WEIGHT` as fusion unless wired to a real weighted combiner.  
6. **CE degrade:** On CE error/timeout/unavailable → return fused ranks unchanged with `ranking_stage=fusion_degraded` (or equivalent). Do **not** silently drop to vector-only while claiming hybrid+CE. When CE disabled → fused top K with `ranking_stage=fusion`.  
7. **Identity:** `source_id` = YouTube video ID or `fixture:<slug>` — **never** absolute filepath. Path-hash `doc_id` (today’s `compute_doc_id`) is **debt to replace**, not the binding contract. Persist `content_hash` + `embedding_version` on chunks; mismatch → refuse query/ingest with rebuild instruction.  
8. **KB1 fixtures (shape only in this guide):** ≈3–8 committed synthetic/licensed markdown under `fixtures/` (+ `fixtures/PROVENANCE.md` or manifest). Dedicated fixture ingest path. Public citations return `source_id` / documented URL — **never** owner filepath. **Pinned for DoD:** placeholders are **accepted** — schema/ingest/eval must run on committed shape + stable `source_id`s even if body prose is stub text. Real authored prose is optional polish, not a gate.  
9. **KB2 public MCP:** Allowlist only: `search`, honest `discover`, `get_status`; `get_context` only if it calls shared retrieval. Mutation tools (`add_channel`, `sync_now`, equivalents) absent from public/default profile (or gated behind non-default private profile).  
10. **Enhancement filter for this slice:** golden eval cases + **per-stage latency** (at least fusion vs CE) + **groundedness** stub (answer/citation claims must map to returned chunk ids). Keep LanceDB. No January rewrite.  
11. **Out of scope here (hard — do not expand this guide or its Implement diff):** KB3-exec tip-transcript scrub/deletion / history rewrite; public GitHub visibility flip / LICENSE packaging ceremony; personal-channel overlay polish beyond not requiring personal channels for smoke; sync/`no_subs` semantics; discovery “clustering”; hosted Cohere/Voyage as default CE; FastAPI/Postgres.  
12. Prefer ≤300 lines/file (hard max 400 unless already larger). Smallest correct change; targeted seams only.

### Locked knobs (pinned defaults; latency p95 after first baseline)

| Knob | Pinned default | Notes |
|------|----------------|-------|
| **N** (fused shortlist → CE) | 30 | Clamp to 20–50; document if changed |
| **K** (return size) | 8 | Clamp to 5–10 |
| CE enable flag | config default **on** for hybrid when local CE loads; **off** path must work | `ranking_stage` must reflect reality |
| **Default local CE model** | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Architecture locks *local-first + pluggable*, not a brand. This is the **default pin** so Implement does not stall; swap only via adapter + README note. Install: `uv add sentence-transformers` (or project-equivalent) and load that model id. Hosted CE is **not** default. |
| Latency | Measure CE stage on fixture shortlist; **numeric p95 remains TBD** until first honest fixture baseline | Prefer small K; async-friendly adapter boundary; record timings in F2 even before p95 lock |

---

## Ordered step checklist

### Phase A — Contracts, identity, schema debt

- [x] **A1.** Define a typed hit / result contract (dataclass or Pydantic) used by CLI + MCP. Required fields per ARCHITECTURE §4: at least `chunk_id`, `source_id`, `title`, `channel` (or fixture label), `date`, `snippet`/`text`, durable citation (`source_url` or fixture id — **not** absolute filepath for public MCP), `fusion_rank` (or fused score on hybrid), `ranking_stage` ∈ {`vector`, `fusion`, `ce`, `fusion_degraded`}, optional `retriever_scores`, `rerank_score` when CE ran.  
- [x] **A2.** Extend ingest/schema so each chunk stores: stable `source_id`, `source_type` (`youtube` \| `fixture`), `content_hash` (hash of normalized text used for chunking), `embedding_version` (e.g. `nomic-embed-text@768`). Keep `id` = `{doc_id}_{chunk_index}` or equivalent stable chunk id. Stop treating filepath MD5 as the long-term public identity.  
- [x] **A3.** Reconciliation helpers (minimal, not a migration framework): content_hash change → replace chunks for that `source_id`; embedding_version mismatch on search/ingest → **fail closed** with rebuild instruction; orphans documented as “rebuild from files” escape hatch.  
- [x] **A4.** Unit tests (temp dir / no personal corpus): `source_id` stability under path move; content change flips `content_hash` and replaces chunks; embedding_version mismatch refuses search with clear message.  
- [x] **A5.** Reduce schema import side effects: status/help/MCP tools that do not embed must not require Ollama at import time (lazy embedding function; ARCHITECTURE §9). **Implement note (pass-6 debt):** today’s `TranscriptChunk` calls `_get_func()` in the **class body**, so a “lazy helper” that still runs at class definition still forces Ollama on import — move `SourceField`/`VectorField` off import-time class evaluation.

### Phase B — Fixture corpus expectations (shape; no scrub)

- [x] **B1.** Add `fixtures/` (or `fixtures/transcripts/`) with ≈3–8 committed markdown docs and `fixtures/PROVENANCE.md` (or `fixtures/manifest.json`) listing `source_id`, title, license basis (`synthetic` \| `licensed` \| `owner-original`), optional URL, notes. Use explicit ids like `fixture:rag-hooks-01`. **Placeholder body prose is DoD-complete**; do not block on human-authored essay-quality fixtures.  
- [x] **B2.** Fixture ingest path reads **only** allowlisted `fixtures/`; writes to a **temp or gitignored** LanceDB for tests/smoke (do not require personal `data/raw/`).  
- [x] **B3.** Golden eval stub file (e.g. `fixtures/eval/golden_cases.jsonl` or `eval/golden_cases.jsonl`): ≥5 cases with `query`, expected `source_id`(s) and/or chunk ids, optional `must_cite`. Include at least one lexical-heavy and one semantic-heavy query so hybrid lift is testable. Expected ids must match committed fixture `source_id`s (placeholders OK).  
- [x] **B4.** Do **not** delete tip transcripts, rewrite git history, or flip repo visibility in this guide (KB3-exec + public-flip are **later human-gated stages**, not part of this slice’s DoD).

### Phase C — Shared hybrid + fusion (before CE)

- [x] **C1.** Implement `ensure_fts_index` as a real hybrid precondition (reuse/fix `ingest.ensure_fts_index`). Hybrid path: if table missing or FTS cannot be ensured → raise/return typed error; **no silent vector fallback** when mode is hybrid.  
- [x] **C2.** Implement shared `retrieve(...)` (name flexible) in the search module:  
  - `mode=vector`: ANN only; `ranking_stage=vector`; no CE required.  
  - `mode=hybrid`: vector + FTS → fuse over stable chunk ids (RRF or LanceDB `query_type="hybrid"` **only if** fused ranks + stage provenance are honest) → shortlist size **N**.  
- [x] **C3.** Post-steps (same for CLI/MCP): optional channel/date filters; dedupe by `doc_id`/`source_id` (best chunk wins). **Name the policy once** (before CE, after CE, or both) in code comments / this guide’s implement notes — no second undocumented pass. Default recommendation: dedupe **before** CE for shortlist hygiene, then take top **K**.  
- [x] **C4.** Wire CLI `src/search.py` to the shared function. Remove the lie that `--hybrid` is a no-op flag over vector-only.  
- [x] **C5.** Temp-LanceDB smoke: ingest fixtures → vector works → hybrid works with FTS present → fusion path returns `ranking_stage=fusion` when CE off.  
- [x] **C6.** Config: add `RETRIEVAL_N`, `RETRIEVAL_K`, `CE_ENABLED` (names flexible). Deprecate or honestly document `HYBRID_VECTOR_WEIGHT` if unused.

### Phase D — Pluggable CE seam

- [x] **D1.** Add one CE adapter module/seam with conceptual interface: `rerank(query, candidates[]) → ranked[]` where candidates carry `chunk_id`, passage text, fusion rank/score; output adds `rerank_score` + final order. Adapter must **not** open its own LanceDB connection or reimplement hybrid/fusion.  
- [x] **D2.** Default local CE: `cross-encoder/ms-marco-MiniLM-L-6-v2` via sentence-transformers (see Locked knobs). Document model id + install one-liner in README/dev notes. Hosted CE is **not** default. Adapter stays pluggable so a later swap does not rewrite hybrid/fusion.  
- [x] **D3.** Wire CE only after fusion inside shared retrieve: enabled → top **K** with `ranking_stage=ce`; disabled → fused top **K** with `ranking_stage=fusion`.  
- [x] **D4.** Forced CE failure (inject/raise in test): return fused order, `ranking_stage=fusion_degraded`, not vector-only.  
- [x] **D5.** Record per-stage latency counters (retrieve/fuse ms, CE ms, total ms) on the result envelope or debug struct for the eval stub. Do **not** invent a locked p95 before the first fixture baseline; store/print honest timings first (F2).

### Phase E — Read-only MCP allowlist behavior

- [x] **E1.** Refactor `src/mcp_server.py` so `search` and `get_context` (if kept) call **shared retrieve only** — no independent `table.search` / second DB policy.  
- [x] **E2.** Public/default profile tools: `search`, honest `discover`, `get_status` (+ `get_context` only if shared). Ensure `add_channel` / `sync_now` are **absent** from the public profile or behind an explicit private profile flag that defaults **off**.  
- [x] **E3.** Public result formatting: never emit absolute owner `filepath`; emit `source_id` / provenance URL.  
- [x] **E4.** Contract test: public tool list contains only allowlisted names; mutation tools not registered on public profile; one search call returns typed fields including `ranking_stage`.

### Phase F — Minimal eval + verification wiring

- [x] **F1.** Fixture ranking eval stub: run golden cases against temp index; report hit@K / source_id recall (or equivalent). **CE keep gate:** keep advertising CE only if lift vs fusion-only **or** write an explicit justify-keep note in `docs/` / eval report. No lift + no justification → disable CE default, keep fusion.  
- [x] **F2.** Stage latency: print/store fusion-only vs CE-enabled timings on the golden set (honest demo budget; numeric p95 may remain TBD after first run).  
- [x] **F3.** Groundedness stub: given a fixture “answer” or citation list (can be heuristic: returned top chunk ids must be subset of retrieved set; if a tiny answer helper exists, each citation id must appear in retrieved hits). Fail the stub if citations invent ids. Full LLM answer quality suite is **out of scope**.  
- [x] **F4.** README note (minimal): fixture-first smoke path separate from optional personal sync; do **not** claim public-flip complete. Point to ARCHITECTURE for KB1–KB5.  
- [x] **F5.** Stop. Do **not** scrub tip docs (KB3-exec), package for public GitHub flip, or start FastAPI/Postgres — those remain out of this guide even if “almost done.”

---

## Verification / Definition of Done (this guide)

**Done when all are true:**

1. Shared retrieve is the **only** ranking path used by CLI and MCP search/context.  
2. Chunks persist `source_id`, `content_hash`, `embedding_version`; path-move identity test passes; mismatch fails closed with rebuild guidance.  
3. Fixture layout + provenance file exist; fixture ingest works into temp LanceDB without personal channels/`data/raw`.  
4. Hybrid smoke: FTS present; hybrid fails closed if FTS cannot be ensured; hybrid does not silently become vector-only.  
5. CE enabled → `ranking_stage=ce` and top K; CE forced failure → `fusion_degraded` with fused order preserved.  
6. CE disabled → `ranking_stage=fusion`.  
7. Public MCP profile is read-only allowlist; mutation tools not on default profile; no filepath citations on public results.  
8. Minimal eval runs: golden relevance + stage latency numbers + groundedness stub; CE keep/disable decision recorded.  
9. No January rewrite, no Postgres, no public-flip, no tip transcript scrub in the diff for this guide.  
10. Unit/smoke tests cover A4, C5, D4, E4, F1–F3 at least.

**Explicitly not required for this guide’s DoD (and not started by Implement of this guide):**

- KB3-exec tip-transcript scrub/deletion / history rewrite  
- Public GitHub visibility flip / LICENSE packaging ceremony  
- Essay-quality fixture prose (placeholders + provenance + golden ids suffice)  
- Locked numeric CE p95 (measure first; lock after baseline)  
- Personal channel overlay packaging polish  
- Hosted CE, embedding migration, HTTP API / FastAPI / Postgres  
- Full observability platform or large eval suite  
- Sync failure-class rewrite (`no_subs` vs retryable)

---

## Blast radius and risks

| Risk | Blast radius | Mitigation in steps |
|------|----------------|---------------------|
| Second search path in MCP | Divergent ranking; false “hybrid” claims | E1–E4; single function ownership |
| Silent vector fallback on hybrid | Interview/demo honesty failure | C1 fail-closed; DoD #4 |
| CE failure advertised as hybrid+CE | Fake production judgment | D4 `fusion_degraded`; never vector-only under hybrid+CE claim |
| Path-based `doc_id` kept as identity | Broken citations after move; filepath leaks | A2–A4; public citation rules |
| Schema import requires Ollama | Status/help/MCP broken when Ollama down | A5 lazy embed |
| CE before identity/FTS fixed | Reranking stale/orphan chunks | Phase order C before D (ARCHITECTURE §3) |
| Scope creep to scrub/public flip | Burns slice; legal/privacy risk | B4, F5, out-of-scope list |
| Hosted CE default | Privacy/cost/latency without eval | D2 local-first |
| Eval theater (no lift check) | Checkbox ranking | F1 keep gate |
| Large module growth | Unmaintainable agent edits | 300/400 line preference; extract CE adapter |

---

## Edge-case handling (must appear in implementation or tests)

| Edge case | Expected behavior |
|-----------|-------------------|
| Empty query | Clear validation error; no crash |
| Empty / missing table | Clear error; empty results only if honestly documented for vector UI — hybrid must not pretend success |
| FTS ensure fails | Hybrid **fail closed**; message to rebuild/ensure index |
| `--hybrid` / `hybrid=True` without FTS | Same as above — not silent vector |
| Ollama down on vector/hybrid | Fail with start/pull guidance; status/help still works (A5) |
| `embedding_version` mismatch | Refuse search/ingest; instruct rebuild |
| Content changed, same `source_id` | Replace chunks via `content_hash` |
| Path moved, same `source_id` | Same identity; no duplicate docs |
| CE timeout / import error / OOM | `fusion_degraded`; fused ranks returned |
| CE disabled in config | `ranking_stage=fusion`; no CE dependency load required for that path |
| Duplicate chunks / multi-chunk same doc | Dedupe policy applied as named; stable top K |
| Public MCP lists mutation tools | Fail E4 contract test |
| Result includes absolute `filepath` on public MCP | Fail E3/E4 |
| Golden case expects wrong `source_id` | Eval reports miss; do not “fix” by weakening ids |
| Groundedness stub cites unknown id | Fail stub |
| N < K | Clamp / error clearly; do not silently invert |
| Fixture provenance missing a file | Ingest/eval fails closed with actionable list |

---

## Learning notes

- **Vertical slice:** Ship one thin path that proves the whole story end-to-end (here: fixture → identity → hybrid → fusion → CE → RO MCP → minimal eval), instead of finishing every layer of the whole product first. Like cutting one full piece of cake so you can taste frosting *and* cake — not baking three unfinished layers. This guide’s slice stops before KB3 scrub / public-flip packaging.  
- **Content hash:** A fingerprint of the *bytes/text you actually chunked*. If the transcript file changes but you keep the same `source_id`, the hash tells ingest “delete old chunks, write new ones.” Without it, the index can look “up to date” while serving stale text — like a cache that never invalidates.  
- **Fail-closed vs fail-open:** Hybrid **fails closed** on missing FTS (better a loud error than a fake hybrid). CE **fails open to fusion** (still useful ranked results, but `ranking_stage` must admit the degrade). Mixing those policies up is how demos lie.  
- **Why CE is after fusion (N→K):** Cross-encoders score *(query, passage)* pairs and are too slow/expensive for the whole corpus. Retrieve broadly, fuse to a shortlist of size **N**, then rerank to **K**. That is the standard senior RAG shape (same *pipeline* as Mechanic; different store — LanceDB here).

### Implement pass 8 — new concepts

- **Adapter (pluggable CE):** An adapter is a thin plug that speaks one interface (`rerank(query, candidates) → ranked`) while hiding the vendor/model. Swap MiniLM for another local CE later without rewriting hybrid/RRF — like a phone charger tip: same port, different brick. See `src/rerank.py`.  
- **Allowlist (public MCP):** An allowlist is “only these tools exist” (search / discover / get_status / get_context). Mutation tools are absent unless `AI_KB_MCP_PRIVATE=1`. Safer than a denylist (“block the bad ones”) because new tools do not accidentally become public.  
- **RRF (reciprocal rank fusion):** Combine two ranked lists without needing comparable scores: for each id add `1/(60 + rank)` from each leg, then sort. Honest fusion provenance → `ranking_stage=fusion` before CE.

---

## Suggested verification commands (implementer)

```bash
cd /Users/tom/Documents/Git/ai_knowledge_base
uv sync
# Ollama up with nomic-embed-text pulled
uv run pytest -q
# fixture ingest + hybrid + CE smoke (exact entrypoint names may match implement choices)
uv run python -m src.ingest --fixtures   # or documented fixture ingest CLI
uv run python -m src.search "fixture golden query" --hybrid
# MCP public profile contract test included in pytest
```

Expected signals: hybrid returns `ranking_stage` of `fusion` or `ce`; forced CE failure test asserts `fusion_degraded`; public MCP tool list has no `add_channel`/`sync_now`; eval stub prints lift + stage latencies.

---

## Stop conditions for the implementer

- Stop when this guide’s DoD is met.  
- Do **not** scrub tip transcripts (KB3-exec), flip public visibility, or open a FastAPI/Postgres rewrite — even as “follow-on while you’re in the files.”  
- If a stack change seems required (leave LanceDB, change embedding model, hosted CE default), **stop and ask** — do not reopen KB4/KB5.

---

## Honest readiness (refine pass 7)

- **Still ready for Implement** of this retrieval-spine guide after human approval (Pass 6 Ready stands; this pass only pinned optionals).  
- **Pinned this pass:** default CE model id + install expectation; fixture placeholders accepted for DoD; CE p95 stays post-baseline; A5 class-body `_get_func()` implement note; KB3 scrub + public-flip reaffirmed **out of guide**.  
- Encodes current debt as steps, not as already-fixed claims (CLI `--hybrid` no-op; MCP dual search + mutations; path-hash `doc_id`; no fixtures/tests yet).  
- Outside this slice (do not treat as Implement of guide 01): KB3-exec scrub execution; public-flip packaging; essay fixture prose; locked CE p95.  
- **Next:** human-gated **Implement** of this guide only — not scrub, not public flip.
