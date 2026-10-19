# AI Knowledge Base — Architecture

**Created:** 2026-07-12 · **Updated:** 2026-10-18

This document describes the shipped system and the contracts the code must keep. When code and this file disagree, fix one of them in the same PR.

---

## 0. Decisions

| Decision | What | Why |
|----------|------|-----|
| Fixtures | The public repo ships small synthetic documents: 8 smoke docs in `fixtures/` and a 48-doc eval corpus in `evals/corpus/`. Personal channels live in a git-ignored overlay | Anyone can clone and run it without a private corpus; no licensing or privacy risk |
| Read-only MCP | The public MCP profile only reads. Sync and channel changes stay in the CLI or behind `AI_KB_MCP_PRIVATE=1` | Agents can search freely without changing data, racing a sync or triggering unbounded downloads |
| Public data hygiene | Only synthetic or owner-original text is committed; transcripts, the index and sync state are git-ignored | Third-party transcripts are not redistributed |
| Keep the stack | LanceDB plus Ollama `nomic-embed-text` (768 dimensions), with fixes at the seams rather than a rewrite | The stack works; a rewrite would cost time without changing what the system can do |
| Ranking order | Hybrid retrieve → RRF fusion → local cross-encoder → results, with a fallback to the fused order if the cross-encoder fails | Search stays useful when the reranker is slow, missing or broken |

---

## 1. What this system is

A local ingest → embed → retrieve → (optional rerank) knowledge base for YouTube transcripts and committed documents, exposed through a CLI and an MCP server.

```
source files (durable)  →  chunk + embed  →  LanceDB index (derived)
                                ↑
                 src/embed.py: Ollama nomic-embed-text, or the offline stub
                                ↓
            shared retrieval: hybrid → RRF fusion → optional cross-encoder
                                ↓
             CLI  |  MCP (read-only public profile)  |  eval harness
```

Out of scope: a hosted service, an HTTP API, article or podcast plugins, multi-user auth, an embedding migration framework, and a hosted reranker as the default.

---

## 2. Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Vector + full-text store | LanceDB (embedded) | One `transcripts` table, rebuildable from source files |
| Embeddings | Ollama `nomic-embed-text`, 768 dims | `AI_KB_EMBEDDINGS=stub` selects a deterministic offline embedder for CI and tests |
| Ranking | Vector + keyword → RRF → optional cross-encoder | `cross-encoder/ms-marco-MiniLM-L-6-v2` through the `ce` extra |
| Sync | `yt-dlp` → SRT → markdown under `data/raw/` | Git-ignored; optional |
| Package | `uv`, Python modules under `src/` | Thin CLI and MCP over a shared core |

---

## 3. Module ownership

| Module | Owns | Does not own |
|--------|------|--------------|
| `config.py` | Paths, embedder choice and version stamp, chunk sizes, N and K, cross-encoder flag, channel overlay loading | A committed personal channel list |
| `embed.py` | Every embedding call, for ingest and for queries | Table writes |
| `schema.py` | The LanceDB chunk schema (vectors are supplied by ingest) | Embedding calls |
| `ingest.py` | Chunking, identity, content hash, embedding, table writes, full-text index build | Search or ranking |
| `search.py` | The shared `retrieve()` used by CLI, MCP and the eval | Any write |
| `rerank.py` | The cross-encoder adapter, scoring a fused shortlist | Its own database access or fusion |
| `discover.py` | Browse modes: channel groups, recent digest, random picks, frequent terms | Ranking |
| `youtube_sync.py` | Download, conversion, sync state, failure classes | Index identity (ingest owns that) |
| `mcp_server.py` | MCP tool adapters, the public allowlist, error sanitising | Its own search path |
| `eval/` | The pre-registered eval, metrics and CI gate | Ranking code (it calls `retrieve()`) |

---

## 4. Shared retrieval contract

CLI, MCP and the eval call one function, `retrieve()`.

| Mode | Behaviour |
|------|-----------|
| `vector` | Embed the query, search the vector column |
| `keyword` | Full-text search on `text` alone |
| `hybrid` | Both legs → RRF fusion over chunk ids → shortlist of N → optional cross-encoder → top K |

**Before hybrid or keyword search runs,** the `transcripts` table and its full-text index on `text` must exist. Ingest builds the index; search only checks for it. If it is missing, search fails with `fts_unavailable` instead of silently running vector-only. Search never writes and never creates the database directory.

**N and K.** N (fused shortlist into the cross-encoder) is clamped to 20-50, default 30. K (results returned) is clamped to 5-10, default 8. Results are deduplicated by `source_id` before the cross-encoder, keeping the best-ranked chunk.

**Cross-encoder.** The adapter interface is `rerank(query, candidates) → ranked`, adding `rerank_score`. It runs only from `retrieve()`, after fusion. When it is off, hits report `ranking_stage=fusion`. When it fails, hits keep the fused order with `ranking_stage=fusion_degraded` and the result carries the error message. It is on by default when the `ce` extra is installed (`AI_KB_CE=0` turns it off).

**Result shape.** Every hit has `chunk_id`, `source_id`, `title`, `channel`, `date`, `text`, `source_url` (never a local file path), `fusion_rank`, `retriever_scores` (per-leg ranks), `rerank_score` when the cross-encoder ran, and `ranking_stage` (`vector`, `keyword`, `fusion`, `ce` or `fusion_degraded`). Results also carry per-stage `timings_ms`.

**Discovery is not ranking.** `discover` modes (`random`, `digest`, `concepts`, `channels`) are browse views, labelled for what they are.

---

## 5. Identity, hashing, embedding version

| Field | Rule |
|-------|------|
| `source_id` | YouTube video ID, or an explicit id such as `fixture:<slug>` or `eval:<slug>`. Never a file path |
| `doc_id` | Deterministic hash of `(source_type, source_id)`; moving a file does not change it |
| `content_hash` | Hash of the normalised text. Same hash: skip. Different hash: replace that source's chunks |
| `embedding_version` | Embedder name and dimension, such as `nomic-embed-text@768` or `stub-hash@768`. Ingest and search stop on a mismatch and say to rebuild |

---

## 6. Source files versus the index

Source markdown is the durable content; LanceDB is a derived index; `data/sync_state.json` tracks sync progress only.

1. A file with no index rows gets ingested.
2. A changed `content_hash` replaces that document's chunks.
3. Rebuilding from files is the supported recovery path. There is no migration framework.
4. Sync never treats "markdown exists" as "indexed"; ingest owns what is in the index.
5. A version mismatch blocks search and ingest until the index is rebuilt.

---

## 7. Public versus private

| Surface | Public default | Private, local only |
|---------|----------------|---------------------|
| Corpus | Committed synthetic docs with a `manifest.json` listing source id, title and license | Git-ignored `data/raw/youtube_transcripts/` |
| Channels | Empty committed default | Git-ignored `channels.local.json` |
| MCP | `search`, `get_context`, `discover`, `get_status` | `add_channel`, `sync_now` with `AI_KB_MCP_PRIVATE=1` |
| Sync | Not needed for the quickstart | CLI or a launchd template |

Fixture and eval corpora are ingested only from the files their `manifest.json` lists, with `source_type=fixture`.

---

## 8. Sync failure classes

| Class | Saved as a terminal skip? | Retried? |
|-------|---------------------------|----------|
| success | n/a | n/a |
| `no_subs` (confirmed: no usable English subtitles) | Yes | No, unless forced |
| retryable (network, yt-dlp crash, rate limit, empty output) | No | Yes |

---

## 9. Evaluation

[`evals/PREREGISTRATION_v2.md`](../evals/PREREGISTRATION_v2.md) fixes the corpus, the dev and held-out queries, the metrics (MRR@10, nDCG@10, hit@1 against a random baseline), the arms and the pass criteria. `python -m src.eval` runs it and can write a full report with the commit, embedder and dataset hashes. The CI Eval workflow compares every change to ranking code or eval data against the committed baseline in `evals/baseline/`.
