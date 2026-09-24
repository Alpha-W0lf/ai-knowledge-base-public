# AI Knowledge Base

Keep coding agents current with local **hybrid RAG** + **MCP**.

Public demo uses synthetic fixtures; the architecture is the product.

![Sources → transcripts → RAG + MCP → agents](docs/assets/pipeline_overview.png)

### The problem

AI techniques move weekly. Coding agents that only “know” last quarter’s defaults fall behind. Teams need a **local, citable** knowledge path — retrieve what matters, cite sources, and expose tools agents can call — without shipping a private corpus to the public internet.

### How it works

```mermaid
flowchart LR
  F[Fixtures / sources] --> I[Ingest + embed]
  I --> D[(LanceDB)]
  Q[Query] --> S[Hybrid search]
  D --> S
  S --> M[CLI / MCP tools]
  M --> A[Coding agents]
```

1. Ingest documents (committed fixtures for the public demo).
2. Embed locally (Ollama `nomic-embed-text`).
3. Retrieve with **vector + keyword fusion**, optional cross-encoder.
4. Serve results via CLI and **read-only MCP** tools (`search`, `discover`, `get_context`, `get_status`).

### Key engineering decisions

1. **Hybrid fusion before cross-encoder** — the retrieval spine stays useful if the reranker degrades or is disabled.
2. **Public fixtures / private corpus split** — strangers get a working demo; personal tip libraries stay off this repo.
3. **MCP read-only by default** — mutations stay behind an explicit private profile flag.

### Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) **or** pip + venv (`python3 -m venv .venv && .venv/bin/pip install -e .`)
- [Ollama](https://ollama.com) running locally with `nomic-embed-text`

### Try it

```bash
uv sync
ollama pull nomic-embed-text
uv run python -m src.ingest --fixtures
uv run python -m src.search "reciprocal rank fusion RRF" --hybrid --db data/lancedb
uv run python -m src.eval
```

Same steps with pip/venv: skip `uv sync`, then run the modules with `.venv/bin/python` instead of `uv run python`.

MCP wiring, discovery commands, and optional BYO YouTube overlay: [`GETTING_STARTED.md`](GETTING_STARTED.md). Dogfood with [mcp-audit](https://github.com/Alpha-W0lf/mcp-audit): `mcp-audit run --server "uv run python -m src.mcp_server"` (or `.venv/bin/python -m src.mcp_server`). Public tools advertise `readOnlyHint=true`.

### Stack

| Component | Tool |
|-----------|------|
| Vector + FTS | LanceDB |
| Embeddings | Ollama · `nomic-embed-text` @ 768 |
| Rerank (optional) | MiniLM cross-encoder (degrades to fusion) |
| Agent surface | MCP (public profile = read-only) |

### Deeper docs

- [`docs/PORTFOLIO_VISION.md`](docs/PORTFOLIO_VISION.md) — packaging intent  
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — contracts / how  
- [`GETTING_STARTED.md`](GETTING_STARTED.md) — operator path  
- [`FAQ.md`](FAQ.md) — Technical FAQ  
- [`docs/2026-07-12_ce_keep_note.md`](docs/2026-07-12_ce_keep_note.md) — cross-encoder keep note  
- [`LICENSE`](LICENSE) — PolyForm Noncommercial 1.0.0 (source-available / non-commercial)  

Building agent knowledge systems? Reach me on [LinkedIn](https://www.linkedin.com/in/tchacko1/).
