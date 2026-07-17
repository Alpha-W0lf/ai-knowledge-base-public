# AI Knowledge Base (public portfolio)

**This repository** is the **public, stranger-runnable** portfolio surface for the local hybrid RAG + MCP knowledge base.

- **Private archive / personal corpus:** stays in a separate private repo (`ai_knowledge_base`). Do not expect personal YouTube downloads or tip transcripts here.
- **Public demo corpus:** committed synthetic `fixtures/` only. Tip-transcript docs from the private archive are **absent** on this sibling (curated out).
- **Optional advanced path:** copy `channels.local.example.json` → `channels.local.json`, add your own channels, sync with a short backfill (`BACKFILL_DAYS = 7`), then ingest — not the default smoke path. **No auto-sync on clone.**
- **MCP:** read-only public tool allowlist (`search`, `discover`, `get_status`, …). Mutation tools require an explicit private profile env flag and are not the default story here.

---

# AI Knowledge Base

A local-first, vector-powered knowledge base for AI domain research. Ingests YouTube transcripts (optional local path) and committed fixtures (public smoke), with hybrid retrieval + optional cross-encoder rerank.

**Binding architecture (KB1–KB5):** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)  
**Public packaging intent:** [`docs/PORTFOLIO_VISION.md`](docs/PORTFOLIO_VISION.md)  
**Personal vision (non-binding stack):** [`docs/2026-01-30_vision.md`](docs/2026-01-30_vision.md)  
**January architecture:** [`docs/2026-01-30_architecture.md`](docs/2026-01-30_architecture.md) — **historical / NON-BINDING** (clean rewrite **rejected**).

Guide 01 (shared retrieval spine) is **implemented**. Guide 02 packaging DoD (LICENSE, empty channels + ignored overlay, path hygiene) is **implemented**. Guide 03: this **public sibling** is the portfolio public surface; private archive remains private. Guide 04: root [`GETTING_STARTED.md`](GETTING_STARTED.md) + [`INTERVIEW.md`](INTERVIEW.md) — stranger-clone + FAQ shell. Guides 05–07: fixture eval grew to **18 easy + 6 hard-negative** goldens with per-arm `neg_at_k` — **still not** v1 complete / eval-complete; CE shows **no** claimed hit@K or hard-neg lift on fixtures ([`ce_keep_note`](docs/2026-07-12_ce_keep_note.md)). Optional private tip scrub is separate hygiene — **not** a blocker for having a public AI KB.

## Features

- **Vector search:** Semantic search via local Ollama embeddings (`nomic-embed-text` @ 768 — **not** Gemma)
- **Hybrid search:** Vector + FTS → RRF fusion → optional pluggable CE (KB5)
- **Fixture-first smoke:** Committed synthetic fixtures; no personal corpus required
- **Optional BYO sync:** Local YouTube channel sync via ignored overlay (not required for demo)
- **Discovery:** Honest browse / digest / concepts / channel grouping (not a clustering product)
- **100% local:** Ollama + LanceDB on your machine

## Quick Start

**Full clone path:** [`GETTING_STARTED.md`](GETTING_STARTED.md) · **Interview FAQ:** [`INTERVIEW.md`](INTERVIEW.md)

```bash
uv sync
ollama pull nomic-embed-text
uv run python -m src.ingest --fixtures
uv run python -m src.search "reciprocal rank fusion RRF" --hybrid --db data/lancedb
uv run python -m src.eval
```

Fixture smoke is the portfolio demo path — see GETTING_STARTED for footguns, BYO optional path, and honesty banners. CE: pluggable seam + degrade; **no** claimed hit@K lift; Guide 07 hard-neg `neg_at_k` also flat on both arms ([`ce_keep_note`](docs/2026-07-12_ce_keep_note.md)).

## Architecture

```
ai-knowledge-base-public/
├── fixtures/                 # Public synthetic corpus + provenance + golden eval
├── data/                     # Local/ignored raw + LanceDB (not committed)
├── src/
│   ├── config.py             # Settings (nomic embeddings; N/K/CE; BACKFILL_DAYS=7)
│   ├── embed.py              # Ollama embeddings (nomic-embed-text)
│   ├── identity.py           # source_id / content_hash / embedding_version
│   ├── ingest.py             # Chunk + fixture/YouTube ingest + FTS
│   ├── search.py             # Shared retrieval spine (CLI)
│   ├── rerank.py             # Pluggable local CE adapter
│   ├── mcp_server.py         # RO public MCP (mutations behind private flag)
│   ├── discover.py           # Browse / digest / concepts / channel groups
│   ├── youtube_sync.py       # Optional BYO YouTube sync
│   └── eval/                 # Fixture golden eval stub
└── docs/
    └── ARCHITECTURE.md       # Binding KB1–KB5
```

## Stack

| Component | Tool | Notes |
|-----------|------|-------|
| Vector DB | LanceDB | File-based; hybrid FTS + vector |
| Embeddings | Ollama + **nomic-embed-text** | 768 dims; **≠ gemma**; ≠ mxbai |
| Rerank (optional) | MiniLM CE via sentence-transformers | Degrade to fusion if CE fails; no lift claim yet |
| Transcripts | yt-dlp | Optional BYO sync path only |

## Usage

### Search
```bash
# Semantic search
uv run python -m src.search "best practices for MCP servers"

# Hybrid search (keyword + semantic → fusion → optional CE)
uv run python -m src.search "Claude Code hooks" --hybrid

# Disable CE for this call
uv run python -m src.search "RAG techniques" --hybrid --no-ce

# Show more results
uv run python -m src.search "RAG techniques" --limit 20
```

### Discovery
```bash
# Channel grouping (honest label — not embedding clustering)
uv run python -m src.discover clusters

# What's new this week
uv run python -m src.discover digest --since 7d

# Random exploration
uv run python -m src.discover random

# Top concepts mentioned (heuristic term counts)
uv run python -m src.discover concepts
```

### YouTube Sync (optional / local)
```bash
# Sync configured channels (new videos only) — uses ignored channels.local.json
uv run python -m src.youtube_sync

# Force re-check all channels
uv run python -m src.youtube_sync --force
```

Personal channel mutation via MCP is **off** on the public profile. Persist channels by editing ignored `channels.local.json` (not committed `src/config.py`).

## Public default vs private overlay

| Surface | Public / stranger default | Local / optional |
|---------|---------------------------|------------------|
| Channels | Committed `YOUTUBE_CHANNELS = []` | Ignored `channels.local.json` |
| Fixture smoke | Works with empty channels | Not required |
| Sync / launchd | Not required; no auto-sync on clone | Optional macOS private ops |

```bash
# Optional: copy example → ignored overlay, then edit handles
cp channels.local.example.json channels.local.json
# never commit channels.local.json
```

`get_status` reports `tracked_channels: 0` without an overlay. Launchd plist (`scripts/com.aikb.youtube-sync.plist`) is a template — replace `REPLACE_WITH_REPO_ROOT` with your clone path before `launchctl load`; macOS-only; not required for fixture smoke.

## MCP Server (AI Agent Integration)

The knowledge base exposes an MCP server for AI coding assistants.

### Setup

Add to your `.cursor/mcp.json` or Claude Code settings (replace `cwd` with **your** clone path — do not commit owner-specific absolute paths for public packaging):

```json
{
  "mcpServers": {
    "ai-knowledge-base": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.mcp_server"],
      "cwd": "/path/to/ai-knowledge-base-public"
    }
  }
}
```

### Available Tools (public / default profile — read-only)

| Tool | Purpose |
|------|---------|
| `search(query)` | Shared retrieval spine (hybrid → fusion → optional CE) |
| `discover(mode)` | Honest browse/digest/concepts/channels (not a ranker) |
| `get_context(query)` | Shared retrieve + optional recent digest |
| `get_status()` | Knowledge base statistics |

Mutation tools (`add_channel`, `sync_now`) are **not** on the public profile. Enable only with `AI_KB_MCP_PRIVATE=1` (private local profile). Public results cite `source_id` / `source_url`, never owner filepaths.

### Requirements

- **Ollama must be running** for embeddings (`nomic-embed-text`). On macOS, Ollama runs as a menu bar app with minimal idle resources (~50MB RAM).

## Configuration

Edit `src/config.py` for embedding model (keep `nomic-embed-text` unless you accept full rebuild + eval), chunk sizes, `RETRIEVAL_N` / `RETRIEVAL_K` / `CE_ENABLED`, and `BACKFILL_DAYS` (public default **7**; raise locally for deeper BYO backfill). Personal channel list lives in ignored `channels.local.json` (see example file).

## License

MIT — see root [`LICENSE`](LICENSE). Packaging DoD closed. **This public sibling** is the portfolio public surface; private archive remains private. Optional private tip scrub is separate hygiene, not required to have a public AI KB.
