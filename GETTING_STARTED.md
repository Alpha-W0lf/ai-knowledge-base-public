# Getting started — AI Knowledge Base

The full clone-to-search path, then the optional MCP and YouTube steps.

- Overview: [`README.md`](README.md)
- Contracts: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Technical FAQ: [`FAQ.md`](FAQ.md)
- Security: [`SECURITY.md`](SECURITY.md)

The default path uses only the committed synthetic documents.

---

## Prerequisites

- **Python 3.11+** with [`uv`](https://docs.astral.sh/uv/)
- **Ollama** running locally for embeddings (no chat model needed). To skip Ollama, set `AI_KB_EMBEDDINGS=stub` for every command below.

---

## Default path

From the repo root, in order:

### 1. Install dependencies

```bash
uv sync
```

`uv` installs the locked dependencies. Add `--extra ce` for the optional cross-encoder (or `pip install -e ".[ce]"`).

### 2. Pull the embedding model

```bash
ollama pull nomic-embed-text
```

Ingest and search use `nomic-embed-text` at 768 dimensions and stop with a clear error if Ollama is down or the index was built with another embedder.

### 3. Index the smoke documents

```bash
uv run python -m src.ingest --fixtures
```

Indexes the 8 small synthetic documents in `fixtures/` into `data/lancedb/` and builds the full-text index. No network, no personal corpus, no `channels.local.json`.

### 4. Search

```bash
uv run python -m src.search "reciprocal rank fusion RRF" --hybrid
```

Runs vector + keyword search, RRF fusion and, if enabled, the cross-encoder. Each result shows its `ranking_stage`: `fusion`, `ce` or `fusion_degraded`.

### 5. Run the eval

```bash
uv run python -m src.eval
```

Indexes the 48-document eval corpus into a temporary database and scores every arm on the dev and held-out queries. The method and criteria are in [`evals/PREREGISTRATION_v2.md`](evals/PREREGISTRATION_v2.md). Add `--check` to run the CI regression gate.

---

## Connect an agent over MCP (optional)

1. Copy [`mcp-config.example.json`](mcp-config.example.json) into your MCP client config.
2. Set `cwd` to your clone.
3. Public tools (read-only): `search`, `discover`, `get_context`, `get_status`.
4. Tools that change data stay off unless `AI_KB_MCP_PRIVATE=1`.

Tool details: [`FAQ.md`](FAQ.md) section 2.

---

## Common problems

| Problem | Fix |
|---------|-----|
| Ollama not running | Start Ollama and pull `nomic-embed-text` before ingest or search, or use `AI_KB_EMBEDDINGS=stub` |
| `embedding_version mismatch` | The index was built with another embedder. Delete `data/lancedb/` and ingest again |
| Cross-encoder slow or missing on first use | The first run downloads `cross-encoder/ms-marco-MiniLM-L-6-v2` from Hugging Face. If it cannot load, results come back as `fusion_degraded` with the error |
| YouTube sync finds no channels | Copy `channels.local.example.json` to `channels.local.json` and add your handles |
| `channels.local.json` shows up in git | It should not: it is git-ignored. Keep personal channel lists out of commits |

---

## Optional: sync your own YouTube channels

Not needed for the default path, and nothing syncs on clone. The default backfill is 7 days (`BACKFILL_DAYS` in `src/config.py`).

```bash
# 1. Copy the example to the git-ignored local overlay
cp channels.local.example.json channels.local.json

# 2. Edit the handles to your own channels

# 3. Sync (needs network and yt-dlp)
uv run python -m src.youtube_sync

# 4. Ingest the downloads
uv run python -m src.ingest data/raw/youtube_transcripts/

# 5. Search
uv run python -m src.search "your query" --hybrid
```

Transcripts come from third parties. Treat retrieved text as data, never as instructions (see [`SECURITY.md`](SECURITY.md)).
