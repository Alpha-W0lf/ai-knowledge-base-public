# AI Knowledge Base — Current Architecture (binding)

**Status:** Binding for portfolio public success / private operation  
**Created:** 2026-07-12  
**Updated:** 2026-07-18 (Guide 09 — build MV Met packaging; eval-complete Parked E3)  
**Vision:** `docs/PORTFOLIO_VISION.md`  
**Guides 01–08:** Implemented + Aligned on this public sibling (spine, packaging, surface, GETTING_STARTED/FAQ, eval growth, CE measure, hard-neg, confusable traps). **Guide 09:** build-MV packaging — **portfolio public success / build MV Met**; **eval-complete claim Parked (E3)**; private flip out of scope for this repo’s build %. Optional private tip scrub remains separate hygiene — not required for “having a public AI KB.”

This document describes the **current intended system** after pass-1 critical review and pass-4 KB5 reconcile. It is implementation-shaped and binding. Do not treat the January mega-doc as an executable plan.

**Embeddings (KB4):** Ollama `nomic-embed-text` @ 768d only. **Not** Gemma, **not** `mxbai-embed-large`. Portfolio D1 (`gemma4:e2b`) is a chat/generator default for other repos — AI KB Guide 01 has no chat LLM.

---

## 0. Locked decisions (KB1–KB5)

| ID | Decision | Why |
|----|----------|-----|
| **KB1** | Tiny synthetic/licensed fixtures (≈3–8 docs); public default = no real channels; personal channels in an **ignored** local overlay | Stranger-runnable without private corpus; legal/privacy-safe; smoke path needs no network |
| **KB2** | Public MCP is **read-only**; sync/channel mutation stays private CLI | Proves retrieval + agent tooling without agent-driven mutation, races, or unbounded sync |
| **KB3** | Inventory tracked transcripts **before** any public flip; full third-party transcripts → remove/replace unless redistribution is documented | Private today; public flip without inventory would publish history and third-party text |
| **KB4** | January clean rewrite **rejected** — keep LanceDB + Ollama (`nomic-embed-text` / 768d); fix seams only | Working private corpus exists; rewrite burns portfolio time without invalidating the stack |
| **KB5** | Ranking stack = hybrid → fusion (RRF / LanceDB-equivalent) → **pluggable cross-encoder (CE) rerank** → answer; local CE preferred; **degrade to fused ranks** if CE fails; keep LanceDB (no Postgres rewrite) | Same pipeline *shape* as Mechanic (MR2) on the preserved stack; CE is a bounded ranking stage, not a stack rewrite |

**Ranking (portfolio RAG / KB5):** hybrid retrieve (vector + lexical FTS) → rank fusion → pluggable CE on shortlist **N→K** → answer/citations. Local CE preferred (offline/privacy). CE failure → **fail-open to fused ranks** (honest degrade; do not silently advertise hybrid+CE while returning vector-only). Eval must show lift or justify keep. LanceDB + Ollama remain.

**KB5 vs KB4:** KB5 does **not** reopen the January rewrite. It adds one pluggable ranking seam on the preserved LanceDB/Ollama stack. It is **not** permission to revive HTTP/plugins/embedding migration/Source protocols.

---

## 1. What this system is

A **local-first** ingest → embed → retrieve → (optional CE) knowledge base for YouTube (and fixture) transcripts, exposed via **CLI** and **MCP**.

```
raw files (durable)  →  chunk + embed  →  LanceDB index (derived)
                              ↑
                     Ollama nomic-embed-text
                              ↓
         shared retrieval: hybrid → fusion → pluggable CE (N→K)
                              ↓
              CLI adapter | MCP adapter (read-only public)
```

**Not in v1:** cloud SaaS, HTTP/FastAPI layer, article inbox + LLM metadata extraction, podcast/RSS plugins, multi-space federation, embedding migration, Kubernetes/auth/multi-user, hosted black-box rerank as the default (Cohere/Voyage without N/K/degrade/eval).

---

## 2. Stack (preserve)

| Layer | Choice | Notes |
|-------|--------|-------|
| Vector store | LanceDB (embedded) | Single `transcripts` table; rebuildable from files |
| Embeddings | Ollama + `nomic-embed-text` | 768 dims; do not migrate without eval + rebuild |
| Ranking | Hybrid + fusion + pluggable local CE | KB5; CE after fusion on shortlist; LanceDB stays |
| Sync | `yt-dlp` → SRT → markdown under `data/raw/` | Ignored by git |
| Package | `uv` + Python modules under `src/` | Thin CLI/MCP over shared core |
| Ops | Optional local launchd/CLI sync | Personal only; not the public demo path |

January invariants **kept:** raw files as durable inputs; LanceDB as derived; YouTube video ID as stable source identity; local-only; thin interfaces over shared core; parallel listing + sequential mutation once sync semantics are fixed.

January items **rejected:** clean rewrite/archive/migrate; HTTP API + four-interface fan-out; speculative Source/Embedder/Storage protocols; `mxbai-embed-large` migration; tags/LLM extraction; unsubstantiated scale SLOs; “no module over 200 lines” as a goal.

---

## 3. Module ownership (current shape)

| Module | Owns | Must not own alone |
|--------|------|--------------------|
| `config.py` | Paths, embedding model/dims, chunk sizes, public defaults, N/K + CE enable flags; loads ignored `channels.local.json` when present | Personal channel list must not be committed defaults |
| `embed.py` | Query/document embedding calls | Schema import side effects when Ollama is down |
| `schema.py` | LanceDB chunk schema | Contacting Ollama at import for non-embed paths |
| `ingest.py` | Chunking, identity, content hash, table writes, FTS ensure | Duplicate search/discovery logic |
| `search.py` | **Shared** retrieval spine (hybrid → fusion → optional CE); CLI + MCP call this | A second hybrid/CE path |
| CE adapter (new seam) | Pluggable query–document scoring on fused shortlist | Own LanceDB connection, hybrid, or fusion policy |
| `discover.py` | Honest browse/digest/random/heuristics | Fake “clustering” claims; competing ranking product |
| `youtube_sync.py` | Download, convert, sync-state, failure classes | Index identity (ingest owns DB truth) |
| `mcp_server.py` | MCP tool adapters | Independent search/DB connection logic |
| CLI entrypoints | UX adapters | Business/retrieval policy |

**Targeted seams only (KB4 + KB5):** (1) one shared retrieval function, (2) one discovery/read model, (3) one per-video sync processing path, (4) one pluggable CE adapter behind the shared spine. No directory rewrite. No second MCP-owned search path.

**Implement order (later guides):** identity + FTS + shared hybrid/fusion **before** CE plug-in. CE must not rank garbage/stale chunks or paper over reconciliation bugs.

---

## 4. Shared retrieval contract

CLI and MCP **must** call one function. Behavior:

### Pipeline stages (KB5)

| Stage | Behavior |
|-------|----------|
| 1. Retrieve | `vector`: embed query → ANN. `hybrid`: vector + FTS on `text` (both legs). |
| 2. Fuse | Combine legs with **RRF** or LanceDB-equivalent hybrid fusion over stable chunk IDs. Produce ordered shortlist of size **N**. |
| 3. Rerank (pluggable CE) | Score `(query, passage)` on the fused shortlist; return top **K**. Local CE preferred. |
| 4. Return | Typed hits + stage provenance for CLI/MCP/answer assembly. |

### Modes

| Mode | Behavior |
|------|----------|
| `vector` | Embed query → ANN over `vector`; always available when table + Ollama are healthy. No CE required. |
| `hybrid` | Vector + FTS → fusion → **pluggable CE** (when enabled) → top K |

### Hybrid readiness

Before hybrid runs:

1. Confirm `transcripts` table exists.
2. Confirm FTS index on `text` exists (or create/ensure it once, same path as ingest).
3. If FTS cannot be ensured → **fail closed** with a clear error (do not silently fall back to vector while advertising hybrid).

`HYBRID_VECTOR_WEIGHT` is **not** the fusion API unless wired to a real weighted combiner; prefer explicit RRF / LanceDB hybrid fusion. Do not invent a second scoring system.

### N→K and latency (placeholders until first fixture baseline)

| Knob | Intent | Placeholder default (guide may lock after eval) |
|------|--------|--------------------------------------------------|
| **N** | Fused shortlist size into CE | 20–50 |
| **K** | Post-CE (or fused-only) return size | 5–10 |
| Latency | CE stage on shortlist must stay demo-acceptable | Exact p95 budget locked after first honest fixture run; prefer small K and async-friendly adapter boundary |

Do not ship Cohere/Voyage (or any hosted CE) as default without measured justification vs local.

### Pluggable CE boundary

- **Interface (conceptual):** `rerank(query, candidates[]) → ranked[]` where each candidate has at least `chunk_id`, passage text/snippet, and fusion rank/score; output adds `rerank_score` and final order.
- **Ownership:** one adapter module/seam called only from shared retrieval after fusion — never a parallel MCP path.
- **Preference:** local cross-encoder (offline/privacy). Exact model id is an implement/guide choice; architecture locks *local-first + pluggable*, not a brand.
- **Enablement:** config flag; when CE disabled, return fused top K with `ranking_stage=fusion`.
- **Degrade (KB5):** if CE errors, times out, or is unavailable → **return fused ranks unchanged**, set `ranking_stage=fusion_degraded` (or equivalent), do **not** silently drop to vector-only while claiming hybrid+CE.
- **Eval gate:** keep CE only if fixture eval shows lift (or document an explicit justify-keep). No lift + no justification → disable CE, keep fusion.

### Result shape (one typed contract)

Every hit exposes at least: `chunk_id`, `source_id`, `title`, `channel` (or fixture label), `date`, `snippet`/`text`, durable citation (`source_url` or fixture id — **not** absolute owner filepath in public MCP).

Ranking fields (public/shared):

| Field | Required? | Meaning |
|-------|-----------|---------|
| `fusion_rank` / fused score | Yes on hybrid | Position/score after fusion, before CE |
| `retriever_scores` | Optional | Per-leg scores (vector / FTS) when available |
| `rerank_score` | When CE ran | Cross-encoder score |
| `ranking_stage` | Yes | `vector` \| `fusion` \| `ce` \| `fusion_degraded` |

Shared post-steps: optional channel/date filters; dedupe by `doc_id`/`source_id` (best chunk wins); same limit semantics for CLI and MCP. Dedup may run before CE (shortlist hygiene) and/or after; name the policy in the implement guide — do not invent a second undocumented pass.

### Ranking policy

- v1 ranking = **KB5:** hybrid retrieve → fusion → pluggable CE (N→K) → answer.
- Discovery modes are **not** ranking products; label them honestly (channel browse, recent digest, random explore, heuristic term counts). Do **not** advertise “topic clustering” as a product — `discover clusters` today is channel grouping, not embedding clustering.
- **CE honesty (eval):** fixture golden set showed **no hit@K lift** required to keep the seam (`docs/2026-07-12_ce_keep_note.md`; `ce_keep=false`). Keep pluggable CE + degrade path; do **not** claim “CE improves relevance” until a larger baseline shows lift.

---

## 5. Identity, hashing, embedding version

| Field | Rule |
|-------|------|
| `source_id` | Stable: YouTube **video ID** for YouTube; explicit fixture/source id for fixtures (see §7.1). **Not** absolute filepath. |
| `doc_id` | May equal `source_id` or a deterministic hash of `(source_type, source_id)`. Path moves must not change identity. |
| `content_hash` | Hash of normalized file bytes/text used for chunking. Content change → replace chunks. |
| `embedding_version` | Store model name + dimension (e.g. `nomic-embed-text@768`). Search/ingest **stop** on mismatch with clear rebuild instruction. |

CE does **not** replace identity/reconcile. **Guide 01 (done):** chunks persist stable `source_id`, `source_type`, `content_hash`, `embedding_version` (`nomic-embed-text@768`); `doc_id` is deterministic from `(source_type, source_id)` — not filepath MD5. Mismatch → fail closed with rebuild instruction. **Guide 02 (done):** packaging DoD (LICENSE, empty committed channels + ignored overlay, portable MCP/plist). **Guide 03:** portfolio public surface = this sibling; private tip scrub is optional hygiene on the private archive only.

---

## 6. Filesystem vs index reconciliation

| Role | Truth for |
|------|-----------|
| Raw markdown under `data/raw/` (or fixture dir) | Durable content |
| LanceDB | Derived search index only |
| `data/sync_state.json` (ignored) | Sync progress / terminal skips — **not** index completeness |

Reconciliation rules:

1. File exists, index missing → **ingest**.
2. File `content_hash` changed → **replace** document chunks (delete old + insert new, or equivalent).
3. Index row with no file → orphan; remove on rebuild/reconcile (do not invent silent “heal” that skips files).
4. Sync must **not** treat “markdown exists” as “indexed.” Sync may skip re-download; ingest/reconcile owns DB presence.
5. Embedding/schema version mismatch → refuse query/ingest until rebuild.

Do not build a general migration framework. Rebuild from files is the supported escape hatch.

---

## 7. Public vs private boundary

| Surface | Public v1 | Private / local |
|---------|-----------|-----------------|
| Corpus | Committed fixtures (≈3–8), provenance documented | Ignored `data/raw/youtube_transcripts/` |
| Channels | Empty committed default (`YOUTUBE_CHANNELS = []`) | Ignored `channels.local.json` (Guide 02) |
| MCP | **Allowlist only** (below) | Optional mutation via CLI only |
| Sync | Not required for smoke | CLI / launchd (plist templatized; not required for smoke) |

**Public MCP tool allowlist (KB2):** `search`, honest `discover`, `get_status`; `get_context` only if it calls shared retrieval. Mutation tools (`add_channel`, `sync_now`, and equivalents) are **absent from the public profile** or gated behind a non-default private profile — never the stranger-runnable default.

Personal channel list must **not** ship as the committed public default (**Guide 02 closed:** empty default + ignored overlay).

### 7.1 Fixture contract (shape only — no scrub / no corpus authoring here)

Exact fixture texts remain human (`KB1` / `KB3-exec`). Architecture binds layout and identity:

| Item | Contract |
|------|----------|
| Layout | `fixtures/` at repo root (or `fixtures/transcripts/`); committed markdown (or plain text) only — no private `data/raw/` |
| Count | ≈3–8 docs for public smoke |
| `source_id` | Explicit stable id, e.g. `fixture:<slug>` — never absolute path |
| `source_type` | `fixture` |
| Provenance file | `fixtures/PROVENANCE.md` (or `fixtures/manifest.json`) listing each doc |
| Provenance fields | `source_id`, title, license/redistribution basis (`synthetic` \| `licensed` \| `owner-original`), optional URL, notes |
| Ingest | Dedicated fixture ingest path reading only allowlisted `fixtures/` |
| Citations | Public MCP returns `source_id` / documented URL — never owner filepath |

---

## 8. Sync failure classification

`download_transcript` / sync must distinguish at least:

| Class | Persist as terminal skip? | Retry? |
|-------|---------------------------|--------|
| **success** | n/a | n/a |
| **no_subs** (confirmed: no usable English subtitle track) | Yes | No (until force) |
| **retryable** (network, yt-dlp crash, rate limit, transient empty) | **No** | Yes |

Do not collapse all `None` returns into `no_subs`. Prefer English subtitle variants when available. Keep the state file; fix its semantics. Single-run mutual exclusion is required only if mutation is ever re-exposed to MCP (public v1: mutation off).

---

## 9. Acceptance surface (public gate)

Minimum for stranger-runnable portfolio surface vs private-remote flip:

| # | Gate | Guide 01 / now | Still needed |
|---|------|----------------|--------------|
| 1 | Fixture corpus + fixture ingest (§7.1) | **Done** | — |
| 2 | Identity tests (`source_id`, `content_hash`, `embedding_version`) | **Done** | — |
| 3 | Temp-LanceDB vector + hybrid + fusion smoke | **Done** | — |
| 4 | CE on → `ce`; forced fail → `fusion_degraded` | **Done** | — |
| 5 | Eval stub + CE keep/justify (no false lift ads) | **Done** (`ce_keep_note`) | Guide 08 confusable baseline attempted — still flat; **eval-complete claim Parked (E3)** — not an open build gate |
| 6 | MCP RO allowlist contract test | **Done** | — |
| 7 | README fixture-first vs optional BYO sync + packaging DoD | **Done** (Guide 02–04: thin README + `GETTING_STARTED` + `FAQ`) | — |
| 8 | Tip-transcript / history scrub | **(a) Portfolio public surface = this sibling** — met by sibling existence + fixtures/packaging (tip paths curated out). **(b) Flipping the private remote public** would still need scrub — **out of scope** for this repo. | Optional private hygiene only for (b) |

Schema/import must not require Ollama for status/help that does not embed (**Done** — lazy schema).

---

## 10. KB3 inventory checklist (public sibling live status)

Historical inventory originated on the **private** archive before sibling curation. On **this public sibling**, tip-transcript rows are **not present** (do not invent files). Scrub-of-private remains optional private hygiene if Tom later flips the private remote — not required for this public surface.

| Path | On public sibling | Notes |
|------|-------------------|-------|
| `docs/2026-01-19_01_ai_second_brain_video_transcript.md` | **Not present** | Curated out; still may exist on private archive |
| `docs/2026-01-19_02_ai_second_brain_video_transcript.md` | **Not present** | Curated out; still may exist on private archive |
| `docs/2026-01-19_this_is_why_youre_still_slow_even_with_ai_video_transcript.md` | **Not present** | Curated out; still may exist on private archive |
| `docs/2026-01-19_ai_second_brain_research.md` | **Not present** | Curated out; still may exist on private archive |
| January-era planning / research files (`2026-01-*`) | **Removed** | Superseded or personal curation; see [`PORTFOLIO_VISION.md`](./PORTFOLIO_VISION.md) |
| `docs/PORTFOLIO_VISION.md` | **Present** | Active portfolio vision |
| `data/raw/` transcripts / LanceDB / `sync_state.json` | **gitignored** | Never publish; optional BYO local only |

Private scrub (tip-delete vs history rewrite) is documented on the superseded private Guide 03 runbook — not DoD for this sibling.

---

## 11. Explicit non-goals (v1)

- January clean rewrite, HTTP API, article inbox, plugin Source abstractions
- Hosted black-box rerank as default without N/K, degrade path, and eval
- Embedding model change without eval + full rebuild
- Clustering product, eval platform, observability platform
- Public MCP mutation (`add_channel`, `sync_now`)
- Deleting or scrubbing data in architecture stages
- Postgres / pgvector rewrite (Mechanic owns that stack; AI KB keeps LanceDB)

**Not a non-goal:** pluggable **local** CE after fusion (KB5). That is in-scope ranking, not a January revival.

---

## 12. Document authority

| Doc | Authority |
|-----|-----------|
| **This file** | Binding current architecture |
| `PORTFOLIO_VISION.md` | Public packaging intent |
| KB1–KB5 + `2026-07-12_hybrid_rag_reranker_decision.md` | Portfolio SSOT for ranking lock |
| `2026-01-30_architecture.md` | Historical diagnosis only; rewrite plan superseded |
| `2026-01-30_vision.md` | Personal product vision (private use) |

When code and this file disagree, **fix the code toward this file** in bounded implement/dev-guide slices — do not revive the January rewrite.

---

## 13. KB5 tradeoffs (accepted)

| Tradeoff | Choice | Mitigation |
|----------|--------|------------|
| Latency / deps vs RRF-only | Accept CE stage | Small N→K; local model; degrade to fusion |
| Demo honesty vs “hybrid” label | Fail closed on FTS; degrade-flag on CE failure | Never silent vector-only while advertising hybrid+CE |
| Skill transfer vs second research project | Same pipeline shape as Mechanic; different store | Pluggable CE seam; no Postgres rewrite |
| Eval cost | Require lift or justify-keep | Fixture stub first; numeric thresholds after baseline |
