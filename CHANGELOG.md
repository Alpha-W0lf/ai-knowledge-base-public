# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-18

### Added
- **Hybrid retrieval**: LanceDB vector search (`nomic-embed-text`, 768 dimensions) and full-text search (BM25) merged with Reciprocal Rank Fusion (RRF), then reranked by a local cross-encoder (`ms-marco-MiniLM-L-6-v2`) whenever the `ce` extra is installed (`AI_KB_CE=0` turns it off). A reranker that fails at query time falls back to the fused order as `fusion_degraded`. `retrieve()` also runs vector-only or keyword-only.
- **Read-only search path**: ingest builds the full-text index; search, `get_status` and `discover` only read and never create the data directory. Hybrid search fails closed with `fts_unavailable` if the index is missing, and an index built with another embedder is refused until rebuilt.
- **One embedding path**: ingest and queries both embed through `src/embed.py`. `AI_KB_EMBEDDINGS=stub` selects a deterministic offline embedder (`stub-hash@768`) so ingest, search and the eval run anywhere, including CI.
- **Read-only MCP server**: public tools (`search`, `discover`, `get_status`, `get_context`) advertise `readOnlyHint=True`; `add_channel` and `sync_now` register only under `AI_KB_MCP_PRIVATE=1`. Public errors are sanitized.
- **Pre-registered retrieval eval**: 48 synthetic documents in 12 look-alike clusters and 96 graded queries (dev plus a blind held-out set). `evals/PREREGISTRATION_v2.md` fixes the data hashes, metrics (MRR@10, nDCG@10, hit@1 against a random baseline), paired-bootstrap CIs and criteria. `python -m src.eval` scores every arm and writes a report with the commit, model revisions and dataset hashes.
- **CI**: ruff, format check and pytest on every push and PR; an Eval workflow on ranking, ingest, embedding and eval-data changes that fails when a fusion metric on the offline embedder drops more than 0.02 below `evals/baseline/`.
- **Optional YouTube sync** into git-ignored storage, with failure classes that separate confirmed missing subtitles from retryable errors.
- **`AGENTS.md`** agent guide (`CLAUDE.md` imports it) and `SECURITY.md`.
