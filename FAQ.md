# AI Knowledge Base — Technical FAQ

Short answers for people evaluating or extending this repo. Contracts live in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md); the eval lives in [`evals/`](evals/PREREGISTRATION_v2.md).

## 1. What runs by default, and what is optional?

The default path uses only committed synthetic documents: `uv sync`, `ollama pull nomic-embed-text`, `uv run python -m src.ingest --fixtures`, then search and `src.eval`. It sends no documents or queries off the machine and needs no personal corpus or `channels.local.json`; the only download after setup is the reranker's model weights on first use. With `AI_KB_EMBEDDINGS=stub` it needs no Ollama either.

Syncing your own YouTube channels is optional: copy `channels.local.example.json` to the git-ignored `channels.local.json`, edit the handles, run `src.youtube_sync` (default `BACKFILL_DAYS = 7`), then ingest `data/raw/youtube_transcripts/`. Nothing syncs on clone. See [`GETTING_STARTED.md`](GETTING_STARTED.md).

## 2. Which MCP tools are public, and which are gated?

Public (default) profile, all read-only and advertising `readOnlyHint`:

| Tool | Purpose |
|------|---------|
| `search(query)` | Shared retrieval (hybrid → fusion → optional cross-encoder) |
| `discover(mode)` | Browse: channel groups, recent digest, random picks, frequent terms |
| `get_context(query)` | Shared retrieval plus an optional recent digest |
| `get_status()` | Index statistics and embedder version |

`add_channel` and `sync_now` register only with `AI_KB_MCP_PRIVATE=1`. Personal channel changes belong in `channels.local.json` and the CLI sync.

## 3. Why `nomic-embed-text` at 768 dimensions?

It is a strong open embedding model that runs locally through Ollama, and the stack is built around it. Changing the model means a full rebuild and a new eval run. Every chunk stores its `embedding_version` (for example `nomic-embed-text@768`), and ingest and search refuse to mix versions.

For CI and offline work, `AI_KB_EMBEDDINGS=stub` swaps in a deterministic hashing embedder (`stub-hash@768`). It is not a semantic model; it exists so ingest, search and the eval can run anywhere.

## 4. What is the ranking order, and what does `fusion_degraded` mean?

Vector search and keyword search run as independent legs, RRF merges them into a shortlist of N, an optional cross-encoder reorders the shortlist, and the top K are returned. Each hit carries `ranking_stage`:

| `ranking_stage` | Meaning |
|-----------------|---------|
| `vector` | Vector leg only |
| `keyword` | Keyword leg only |
| `fusion` | Cross-encoder off; fused top K returned |
| `ce` | Cross-encoder reordered the fused shortlist |
| `fusion_degraded` | Cross-encoder failed or was unavailable; fused order returned, with the error in `error` |

`fusion_degraded` is a safety path, not the same as turning the cross-encoder off with `--no-ce`.

## 5. When does the cross-encoder run?

By default, whenever the `ce` extra is installed (`uv sync --extra ce`). It reorders the fused shortlist with `cross-encoder/ms-marco-MiniLM-L-6-v2`. `AI_KB_CE=0` or `--no-ce` turns it off; `AI_KB_CE=1` or `--ce` forces it on. Decision record: [`docs/2026-07-12_ce_keep_note.md`](docs/2026-07-12_ce_keep_note.md).

## 6. How good is retrieval?

On the 48 blind held-out queries, the default pipeline (hybrid search + cross-encoder) puts the right document first 90% of the time: MRR@10 0.948, nDCG@10 0.962, hit@1 0.896, against 0.061, 0.096 and 0.021 for a random order, with a higher nDCG@10 than keyword-only (0.939; the margin is within the 95% confidence interval) or vector-only (0.922) search. Method: [`evals/PREREGISTRATION_v2.md`](evals/PREREGISTRATION_v2.md).

## 7. What do citations use instead of file paths?

Public MCP and shared retrieval cite `source_id` and `source_url` (or a fixture id like `fixture:<slug>`), never local file paths. YouTube chunks use the video ID as `source_id`. Moving a file does not change its `source_id`, so clones and MCP configs stay portable.

---

**Clone path:** [`GETTING_STARTED.md`](GETTING_STARTED.md) · **Overview:** [`README.md`](README.md)
