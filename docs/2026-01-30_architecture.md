# AI Knowledge Base - Technical Architecture

**Last Updated:** 2026-01-30  
**Status:** HISTORICAL ONLY — **NON-BINDING**  
**Approach (historical):** Clean rewrite — **REJECTED** (KB4, 2026-07-12)

> **DO NOT EXECUTE THIS DOCUMENT.** Binding architecture is [`ARCHITECTURE.md`](./ARCHITECTURE.md) (KB1–KB5).  
> January “clean rewrite,” `mxbai-embed-large` migration, HTTP/FastAPI fan-out, and speculative Source protocols are **rejected**. Preserve LanceDB + Ollama `nomic-embed-text` @ 768d; fix seams only.  
> Embeddings are **not** Gemma (D1 `gemma4:e2b` is a chat/generator default elsewhere in the portfolio — N/A to this repo’s embedding path).

> **Related (personal, non-binding):** [`2026-01-30_vision.md`](./2026-01-30_vision.md)

---

> **Historical note (superseded):** This file once proposed a complete rewrite. That plan is **not** the portfolio plan. Keep for archaeology only.

---

## 1. User Flows Reference

These flows define what the system must support. See [vision.md](vision.md) for why.

### Flow 1: Daily Sync
```
aikb sync (or scheduled via cron/launchd)

1. Process inbox (articles, URLs, channels)
2. List videos from configured channels (parallel, 60-day window)
3. For each new video:
   - Download subtitles (skip if no subs)
   - Convert SRT → clean markdown
   - Chunk and embed into LanceDB
4. Report: "Added 12 new transcripts, 3 failed, 45 skipped"
```

### Flow 2: Semantic Search
```
aikb search "Claude Code hooks best practices"

1. Embed query using Ollama (mxbai-embed-large)
2. Vector search in LanceDB
3. Return top results with channel, title, date, snippet, link
```

### Flow 3: MCP Integration
```
Claude Code session:
User: "How should I structure my MCP server?"

Claude (via MCP):
1. Calls search("MCP server structure")
2. Gets relevant transcript snippets
3. Synthesizes answer grounded in practitioner advice
```

### Flow 4: Cross-Project Integration
```
from ai_knowledge_base import search
context = search("topic for video", limit=5)
```

---

## 2. Unified Vector Space

**Decision:** Single vector space with `tags` and `source` metadata for filtering.

| Single Space | Multiple Spaces |
|--------------|-----------------|
| ✅ Simpler architecture | ❌ Complex federation |
| ✅ Cross-topic queries work | ❌ Need query routing |
| ✅ Unified "second brain" | ❌ Fragmented knowledge |

**Organization Strategy: Tags + Embeddings Only**

- Use `tags` for topic labeling: `["llm", "inference", "python"]`
- Use embeddings for semantic similarity
- **No explicit domain field** — simpler schema, fewer classification errors
- Filter by tag when needed: `search("query", tag="transformers")`

If coarse domain filtering is ever needed, derive it from tags at query time (see Section 2).

---

## 3. Integration Interfaces

### 3.1 Three-Layer Architecture
```
┌─────────────────────────────────────────────────────┐
│  External Consumers                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ Claude Code  │ │ Content App  │ │ Other Python │ │
│  │ (via MCP)    │ │ (via HTTP)   │ │ (via SDK)    │ │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │
└─────────┼────────────────┼────────────────┼─────────┘
          │                │                │
┌─────────▼────────────────▼────────────────▼─────────┐
│  Interface Layer                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ MCP Server   │ │ HTTP API     │ │ Python SDK   │ │
│  │ (mcp_server) │ │ (api.py)     │ │ (direct use) │ │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │
└─────────┼────────────────┼────────────────┼─────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│  Core Library                                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐  │
│  │ search  │ │ ingest  │ │ sync    │ │ discover  │  │
│  └─────────┘ └─────────┘ └─────────┘ └───────────┘  │
│                                                      │
│  ┌─────────────────────────────────────────────────┐│
│  │ storage/ (files, db)   youtube/ (client, parser)││
│  └─────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────┘
```

### 3.2 Interface Comparison

| Interface | Use Case | Overhead | Language Support |
|-----------|----------|----------|------------------|
| **Python SDK** | Same-machine Python apps | None | Python only |
| **MCP Server** | AI coding agents | Minimal | Any MCP client |
| **HTTP API** | Cross-language, network | HTTP server running | Any language |

### 3.3 Python SDK (Core Library)
Direct import for Python projects on same machine:
```python
from ai_knowledge_base import search, ingest, discover

# Search
results = search("Claude Code hooks", limit=10, tag="mcp")

# Ingest new content
ingest.file(Path("transcript.md"), source="youtube")

# Discovery
digest = discover.recent(days=7)
```

**Best for:** simple_content_platform (Python, same machine)

### 3.4 MCP Server
Already implemented. AI agents call tools:
- `search(query, limit, tag)` - semantic search
- `discover(mode, days)` - content discovery
- `get_context(query)` - comprehensive context retrieval
- `sync_now()` - trigger sync
- `get_status()` - system status

**Best for:** Claude Code, other MCP-compatible AI tools

### 3.5 HTTP API (New)
Simple REST API for cross-language access:
```
GET  /search?q=query&limit=10&tag=transformers
GET  /discover?mode=digest&days=7
GET  /status
POST /ingest  (with file upload)
POST /sync
```

**Implementation:** FastAPI or Flask, runs as background service.
**Best for:** Non-Python apps, web interfaces, remote access

### 3.6 Integration Examples

**simple_content_platform → knowledge_base:**
```python
# Option A: Direct SDK (recommended - same machine, Python)
from ai_knowledge_base import search
context = search("topic for video", tag="ai", limit=5)

# Option B: HTTP API (if running as service)
import httpx
response = httpx.get("http://localhost:8765/search", params={"q": "topic"})
context = response.json()
```

**Claude Code → knowledge_base:**
```
# Already works via MCP
# Claude calls search() tool automatically when relevant
```

---

## 4. Tech Stack & Extensibility

### 4.1 Current Stack
| Component | Choice | Why |
|-----------|--------|-----|
| **Vector DB** | LanceDB | Local-first, embedded, no server, fast |
| **Embeddings** | Ollama + mxbai-embed-large | Local, free, 1024d, best quality/size |
| **Language** | Python 3.11+ | Ecosystem, simplicity |
| **CLI** | Click + Rich | Nice UX |
| **Async HTTP** | httpx | Modern, async-capable |

### 4.2 Why These Choices Scale

**LanceDB:**
- Built on Lance columnar format (like Parquet but for ML)
- HNSW indexing for fast approximate nearest neighbor
- Handles millions of vectors efficiently
- No external server process
- ✅ Good to 100K+ documents on M2

**Ollama + mxbai-embed-large:**
- 1024 dimensions (best quality/size ratio per Section 4.7)
- Strong benchmark performance on MTEB
- ~50-100 embeddings/second on M2
- General-purpose (works across domains)
- ✅ Can swap models without code changes

### 4.3 Abstraction Layers for Future-Proofing

**Embedder Interface:**
```python
# embedder.py
class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
    
class OllamaEmbedder(Embedder):
    def __init__(self, model: str = "mxbai-embed-large"): ...

# Future: swap to different model
class MxbaiEmbedder(Embedder): ...
class HuggingFaceEmbedder(Embedder): ...
```

**Source Interface:**
```python
# sources/base.py
class Source(Protocol):
    def list_items(self, since: date) -> list[SourceItem]: ...
    def download(self, item: SourceItem) -> Content | None: ...

class YouTubeSource(Source): ...
class PodcastSource(Source): ...  # Future
class RSSSource(Source): ...       # Future
```

**Storage Interface:**
```python
# Already abstracted via storage/db.py and storage/files.py
# Could swap LanceDB for Qdrant, Chroma, etc.
```

### 4.4 Upgrade Paths

| If We Need | Current → Upgrade |
|------------|-------------------|
| Larger embeddings | mxbai-embed-large (1024d) → BGE-M3 (1024d) or higher-dim models |
| More storage | Local filesystem → S3-compatible (MinIO) |
| Distributed search | LanceDB embedded → LanceDB Cloud or Qdrant |
| Faster sync | Sequential → async/parallel downloads |
| Web UI | CLI only → Gradio or Streamlit dashboard |

### 4.5 What NOT to Plan For
- **Multi-user/auth** - Personal knowledge base, not needed
- **Real-time sync** - Daily is fine, complexity not worth it
- **Sharding** - Single machine handles our scale
- **Kubernetes** - Running on laptop, not cloud

### 4.6 LLM Model Selection for Metadata Extraction

**Use Case:** Extract title, summary, and tags from unstructured article text dropped in inbox.

**Hardware Constraints (M2 Pro MacBook Pro 16GB):**
- System needs: ~4-6GB
- Available for ML: ~10-12GB unified memory
- With Q4 quantization: ~0.5-0.6GB per billion parameters
- Target: <3 seconds per extraction
- Must run locally via Ollama

**Research Findings (January 2026):**

| Model | Parameters | VRAM (Q4) | Speed | Quality | Fit |
|-------|------------|-----------|-------|---------|-----|
| Qwen3-0.6B | 752M | ~0.4GB | Very fast | Limited nuance | ⚠️ Too small |
| Qwen3-1.7B | 2B | ~1.2GB | Fast | Moderate | ✅ Minimum viable |
| **Qwen3-4B** | 4B | ~2.5GB | Fast | Good | ⭐ **Sweet spot** |
| **Phi-4-mini** | 3.8B | ~2.3GB | Fast | Excellent JSON | ⭐ **Alternative** |
| Qwen3-8B | 8B | ~5GB | Moderate | High | ✅ Quality option |

**Recommended Configuration:**

```python
# config.py
LLM_EXTRACT_MODEL = "qwen3:4b"  # Primary: best balance quality/speed for M2 Pro
# Alternatives:
# LLM_EXTRACT_MODEL = "phi4-mini"    # Microsoft, excellent structured output
# LLM_EXTRACT_MODEL = "qwen3:8b"     # Higher quality if speed not critical

LLM_MAX_INPUT_CHARS = 6000      # 4B models handle more context
LLM_TEMPERATURE = 0.3           # Low for consistent JSON
LLM_RETRIES_PER_PROMPT = 2
```

**Why 3-4B over 0.6B-1.7B:**
- **Nuanced extraction:** Summary generation and tag extraction need reasoning
- **Quality matters:** Poor metadata = poor search results
- **Plenty of headroom:** 2.5GB model leaves ~8GB for system + embeddings
- **Fast enough:** <2 seconds per extraction on M2 Pro
- **Sweet spot:** 3-4B is the quality/speed intersection for structured extraction

**Available in Ollama:**
```bash
ollama pull qwen3:4b      # Primary recommendation
ollama pull phi4-mini     # Alternative (Microsoft)
ollama pull qwen3:8b      # Higher quality option
```

**Note:** Qwen 3 introduced thinking mode. For metadata extraction,
use `/no_think` or set `enable_thinking: false` for faster responses.

**Ollama Structured Output Support:**
```python
from ollama import chat
from pydantic import BaseModel

class ArticleMetadata(BaseModel):
    title: str
    summary: str
    tags: list[str]    # Up to 5 topic tags (lowercase, hyphenated)

response = chat(
    model='qwen3:4b',
    messages=[{'role': 'user', 'content': 'Extract metadata...'}],
    format=ArticleMetadata.model_json_schema(),  # Enforce schema
    options={'temperature': 0.3}
)
```

**Testing Plan:**
1. Download candidate models: `ollama pull qwen3:4b phi4-mini`
2. Test on 20 sample articles with varied formats
3. Measure: accuracy, speed, JSON validity rate, tag quality
4. Choose best performer for production

---

### 4.7 Embedding Model Selection for Vector Search

**Use Case:** Generate embeddings for semantic search across transcripts and articles.

**Hardware Constraints (M2 Pro MacBook Pro 16GB):**
- Budget: Model should fit comfortably with LLM model (~2.5GB) simultaneously
- Target: <1 second per chunk embedding
- Must run locally via Ollama

**Hardware Clarification (M2 Pro MacBook Pro):**
- 16GB unified memory (shared RAM/VRAM) - affects model loading and computation
- 500GB SSD storage - affects data persistence (NOT a bottleneck for vectors)

**Storage is not a constraint:** Even 1M chunks at 1024d = ~4GB. Your 500GB SSD can handle this trivially.
The real constraint is unified memory during search/inference.

**Dimension Analysis for 16GB Unified Memory:**

| Dimensions | Storage/chunk | 100K chunks | Memory Impact | Best For |
|------------|--------------|-------------|---------------|----------|
| 384d | 1.5KB | 150MB | ~25MB index | Basic, fast, small corpora |
| 768d | 3KB | 300MB | ~50MB index | Good balance, works well |
| **1024d** | 4KB | 400MB | ~70MB index | **Sweet spot for quality + performance** |
| 1536d+ | 6KB+ | 600MB+ | ~100MB+ index | Not available locally, overkill |

**Note:** Storage (500GB SSD) is not a constraint. Even 1M chunks at 1024d = ~4GB, trivial.
The real constraint is unified memory during model loading and inference.

**Research Findings (January 2026) - Models Available in Ollama:**

| Model | Dimensions | Parameters | Ollama Pulls | License | Notes |
|-------|------------|------------|--------------|---------|-------|
| all-minilm | 384d | 22-33M | 2.3M | Apache 2.0 | Fast, small, basic |
| nomic-embed-text | 768d | 137M | 52.6M | Apache 2.0 | Good balance |
| **mxbai-embed-large** | **1024d** | 335M | 6.9M | Apache 2.0 | ⭐ **Recommended** |
| bge-m3 | 1024d | 567M | 3.1M | MIT | Multilingual, larger |
| snowflake-arctic-embed2 | 1024d | 568M | 235K | Apache 2.0 | Multilingual |
| qwen3-embedding | varies | 0.6B-8B | 429K | Apache 2.0 | New, larger variants |

**Updated Decision: mxbai-embed-large (1024 dimensions)**

**Why mxbai-embed-large over bge-m3:**
1. **Smaller & faster:** 335M params vs 567M (40% smaller)
2. **Same quality:** Both are 1024d with excellent MTEB scores
3. **Well-proven:** 63.8M HuggingFace downloads
4. **Apache 2.0 license:** Same permissive license as nomic

**Rationale for 1024d:**
1. **Better semantic separation:** More dimensions = finer distinctions between topics
2. **Future-proof:** Growing multi-topic knowledge base benefits from granularity
3. **Comfortable on your hardware:** 335M model + 1024d index fits easily in 16GB
4. **Minimal overhead:** ~33% more storage than 768d, imperceptible speed difference

**Ollama Setup:**
```bash
ollama pull mxbai-embed-large  # 1024d, 335M params, fast
# Fallback if mxbai not available:
ollama pull bge-m3             # 1024d, 567M params, multilingual
ollama pull nomic-embed-text   # 768d, smaller, simpler
```

**Configuration:**
```python
# config.py
EMBEDDING_MODEL = "mxbai-embed-large"  # Primary: 1024d, best quality/size ratio
EMBEDDING_DIMENSIONS = 1024

# mxbai uses instruction prefixes for best results
EMBEDDING_PREFIX = "Represent this document for retrieval: "
QUERY_PREFIX = "Represent this query for retrieval: "

# Alternative (768d, slightly faster):
# EMBEDDING_MODEL = "nomic-embed-text"
# EMBEDDING_DIMENSIONS = 768
# EMBEDDING_PREFIX = "search_document: "
# QUERY_PREFIX = "search_query: "
```

**Fallback option (if mxbai performance issues arise):**
1. Switch to nomic-embed-text (768d) for faster iteration
2. Re-embed by dropping and recreating the LanceDB table
3. Update `config.py` to use commented alternative settings

**Validation Plan:**
1. Test mxbai-embed-large search quality on multi-domain queries
2. Verify M2 Pro performance with 1024d embeddings
3. Compare results against nomic baseline if quality concerns arise

---

### 4.8 Domain Strategy: Coarse Categories vs Free-form

**Design Question:** How should content domains be defined and organized?

**Options Considered:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Strict predefined list** | LLM picks from fixed set | Consistent, filterable | Maintenance, edge cases |
| **Free-form ad-hoc** | LLM invents any domain | Flexible, zero maintenance | Inconsistent naming, duplicates |
| **Skip domains entirely** | Just use tags + embeddings | Simplest | No coarse filtering |
| **Hybrid (chosen)** | Predefined list + free-form tags | Best of both | Slight complexity |

**Decision: Tags + Embeddings (No Explicit Domains)**

After careful analysis, the simplest and most robust design is to **skip explicit domains entirely** and rely on tags + embeddings:

| Layer | Purpose | Example | Query Support |
|-------|---------|---------|---------------|
| **Tags** | Topic labels | ["transformers", "local-llm", "python"] | `--tag transformers` |
| **Embeddings** | Semantic similarity | 1024-dim vector | Natural language query |

**Why This is Best:**

1. **Zero maintenance:** No domain list to manage, no classification errors
   
2. **More flexible:** Tags can express exactly what the content is about

3. **Embeddings do the heavy lifting:** Similar content clusters naturally in vector space

4. **Queries still work:**
   - Want "all AI stuff"? → Semantic search: `aikb search "machine learning AI"`
   - Want specific topic? → Filter by tag: `aikb search --tag transformers`
   - Want discovery? → Embeddings find related content automatically

5. **Simpler LLM prompt:** Just extract title, summary, and 5 tags (less can go wrong)

6. **No inconsistency:** No "AI" vs "ai" vs "ml" drift in domain classification

**If You Later Want Coarse Filtering:**

Derive a "domain" on-the-fly from tags instead of storing it:

```python
def infer_domain(tags: list[str]) -> str:
    """Derive coarse domain from tags. Zero configuration."""
    AI_TAGS = {"transformers", "llm", "ml", "neural-network", "ai", "deep-learning"}
    ENG_TAGS = {"python", "architecture", "api", "infrastructure", "devops"}
    TOOLS_TAGS = {"ollama", "lancedb", "fastapi", "click", "pytest"}
    
    tag_set = set(tags or [])
    if tag_set & AI_TAGS:
        return "ai"
    if tag_set & TOOLS_TAGS:
        return "tools"
    if tag_set & ENG_TAGS:
        return "engineering"
    return "general"

# Usage in search:
# aikb search --domain ai  →  infer domain from tags, filter results
```

This gives you domain-like filtering with:
- **No stored domain field** (tags are the source of truth)
- **No LLM classification errors** (no domain extraction needed)
- **Easy to adjust** (just update tag sets, no re-processing)
- **Backward compatible** (can add later without schema change)

---

## 5. Deployment & Integration Patterns

### 5.1 The Core Insight: Thin Wrappers

All interface layers share 99% of code. The architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     CORE LIBRARY                         │
│  ─────────────────────────────────────────────────────  │
│  search(), sync_channel(), ingest(), get_stats()        │
│  ~800 lines of actual domain logic                      │
└─────────────────────────────────────────────────────────┘
           ▲              ▲              ▲
           │              │              │
     ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
     │   CLI     │  │    MCP    │  │   HTTP    │
     │  ~100 LOC │  │  ~150 LOC │  │  ~100 LOC │
     │  (Click)  │  │ (FastMCP) │  │ (FastAPI) │
     └───────────┘  └───────────┘  └───────────┘
```

Each wrapper only handles:
1. Input parsing (CLI args / JSON-RPC / HTTP request)
2. Calling core library function
3. Output formatting (text / JSON / HTTP response)

### 5.2 Four Integration Layers

| Layer | Use Case | Implementation | Lifecycle |
|-------|----------|----------------|-----------|
| **Library** | Python apps, same machine | `from ai_knowledge_base import search` | Imported on demand |
| **CLI** | Debug, scripts, any language | `aikb search "query" --json` | Process per call |
| **MCP** | Claude Code, AI agents | FastMCP stdio transport | Started by MCP client |
| **HTTP** | Web, mobile, network | FastAPI on localhost | Optional persistent |

### 5.3 Wrapper Code Structure

All three wrappers call identical core functions:

**Core Library (the real work):**
```python
# ai_knowledge_base/core/search.py
def search(
    query: str,
    limit: int = 10,
    channel: str = None,
    tag: str = None,
) -> list[dict]:
    """Semantic search across knowledge base."""
    db = get_db()
    embedding = embed_text(query)
    results = db.search(embedding).limit(limit)
    if channel:
        results = results.where(f"channel = '{channel}'")
    if tag:
        results = results.where(f"'{tag}' IN tags")
    return results.to_list()
```

**CLI Wrapper (~20 lines):**
```python
# ai_knowledge_base/cli.py
@click.command()
@click.argument("query")
@click.option("--limit", "-n", default=10)
@click.option("--channel", "-c", default=None)
@click.option("--tag", "-t", default=None)
@click.option("--json", "as_json", is_flag=True)
def search_cmd(query, limit, channel, tag, as_json):
    results = search(query, limit, channel, tag)  # ← Core function
    if as_json:
        click.echo(json.dumps(results))
    else:
        for r in results:
            click.echo(f"{r['title']}: {r['text'][:100]}...")
```

**MCP Wrapper (~15 lines):**
```python
# ai_knowledge_base/mcp_server.py
@mcp.tool()
def search_knowledge(
    query: str,
    limit: int = 10,
    channel: str = None,
    tag: str = None,
) -> list[dict]:
    """Search the AI knowledge base."""
    return search(query, limit, channel, tag)  # ← Same core function
```

**HTTP Wrapper (~10 lines):**
```python
# ai_knowledge_base/api.py
@app.get("/search")
def search_endpoint(
    query: str,
    limit: int = 10,
    channel: str = None,
    tag: str = None,
):
    return search(query, limit, channel, tag)  # ← Same core function
```

### 5.4 Realistic Line Counts

| Component | Lines | Complexity | Maintenance |
|-----------|-------|------------|-------------|
| **Core Library** | ~800 | Medium | Where bugs live |
| **CLI wrapper** | ~100 | Low | Rarely changes |
| **MCP wrapper** | ~150 | Low | Rarely changes |
| **HTTP wrapper** | ~100 | Low | Rarely changes |
| **Total** | ~1,150 | — | — |

When adding a new feature to core, add ~5 lines per wrapper to expose it.

### 5.5 Lifecycle & Deployment

**Library:** No deployment - just `import`

**CLI:** 
- Installed via `pip install -e .` or as package
- Each invocation is a fresh process
- ~1-2 second startup (mostly Ollama connection)
- Ideal for scripts, debugging, manual use

**MCP Server:**
- MCP clients (Claude Desktop, Cursor) manage lifecycle automatically
- Starts on first tool call, stays alive for session
- No manual "keep running" needed
- Already on-demand!

**HTTP API (if needed):**
- Option A: Run manually when needed (`python -m ai_knowledge_base.api`)
- Option B: launchd socket activation (macOS - starts on first request, stops when idle)
- Option C: Background service (`launchctl load ...`)

### 5.6 macOS Socket Activation (Advanced)

For true on-demand HTTP without keeping a server running:

```xml
<!-- ~/Library/LaunchAgents/com.aikb.api.plist -->
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aikb.api</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/python</string>
        <string>-m</string>
        <string>ai_knowledge_base.api</string>
    </array>
    <key>Sockets</key>
    <dict>
        <key>Listeners</key>
        <dict>
            <key>SockPathName</key>
            <string>/tmp/aikb.sock</string>
        </dict>
    </dict>
    <key>TimeOut</key>
    <integer>300</integer>  <!-- Stop after 5 min idle -->
</dict>
</plist>
```

launchd starts the service on first connection, stops after idle timeout.

### 5.7 Implementation Priority

| Layer | Priority | When to Build |
|-------|----------|---------------|
| **Core Library** | P0 | First - everything depends on this |
| **CLI** | P0 | Essential for development and debugging |
| **MCP Server** | P1 | Already exists, update to use new core |
| **HTTP API** | P2 | Build only when needed (web UI, mobile, etc.) |

**Recommendation:** Focus on core + CLI + MCP. Add HTTP when a use case appears.

### 5.8 Cross-Project Integration

For `simple_content_platform` (Python, same machine):
```python
# simple_content_platform/research_service.py
from ai_knowledge_base import search

def get_context_for_topic(topic: str) -> list[dict]:
    """Get knowledge base context for video research."""
    return search(topic, limit=10)  # Cross-topic by default
```

No server, no network, no startup time. Direct function call.

---

## 6. Current State Problems

### 6.1 Filename Pattern Chaos
- Multiple formats exist: `YYYYMMDD_title.md`, `YYYYMMDD_[video_id]_title.md`
- Glob patterns with brackets `[video_id]` are interpreted as character classes
- No single source of truth for filename generation/parsing

### 6.2 Code Duplication
- `sync_channel()` and `sync_all()` have duplicated video processing loops
- File existence checks scattered across multiple functions
- Same logic repeated with slight variations

### 6.3 Mixed Responsibilities
- `youtube_sync.py` is 700+ lines handling:
  - yt-dlp subprocess execution
  - File naming and detection
  - SRT→MD conversion
  - State management
  - Database ingestion
  - CLI interface

### 6.4 Brittle Detection
- `find_existing_files()` uses unreliable glob patterns
- No canonical way to map video_id → file path
- Edge cases in title sanitization cause mismatches

### 6.5 Implicit Data Model
- Video metadata passed as loose dicts `{"id": ..., "title": ..., "date": ...}`
- No validation, no type safety
- Easy to introduce bugs

---

## 7. Design Principles

### 7.1 Single Responsibility
Each module does one thing well. No module exceeds ~200 lines.

### 7.2 Explicit Data Models
Use dataclasses for Video, Transcript, ChunkRecord. Validate at boundaries.

### 7.3 One Canonical Format
One function generates filenames. One function parses them. Everyone uses these.

### 7.4 Idempotency by Design
Every operation is safe to re-run. State is derived, not authoritative.

### 7.5 Fail Gracefully
Partial failures don't corrupt state. Can always resume from filesystem/DB.

### 7.6 Minimal State
- Filesystem (MD files exist) = source of truth for "downloaded"
- Database (doc_id exists) = source of truth for "ingested"
- State file = only caches "videos with no subtitles" to avoid re-trying

---

## 8. Proposed Architecture

### 8.1 Source Code Structure

```
src/
├── __init__.py
├── config.py              # Configuration constants
├── models.py              # Data models (dataclasses)
│
├── youtube/               # YouTube-specific operations
│   ├── __init__.py
│   ├── client.py          # yt-dlp wrapper (list videos, download subs)
│   ├── parser.py          # SRT parsing and cleaning
│   └── inbox.py           # YouTube URL/channel inbox processing
│
├── storage/               # File and database operations
│   ├── __init__.py
│   ├── files.py           # Transcript file naming, finding, reading
│   ├── db.py              # LanceDB operations (schema, ingest, search)
│   ├── inbox.py           # Article inbox processing
│   └── llm_extract.py     # LLM-based metadata extraction
│
├── sync.py                # Orchestration (sync_channel, sync_all)
├── search.py              # Search interface
├── discover.py            # Discovery features
│
├── cli.py                 # All CLI entry points
└── mcp_server.py          # MCP interface
```

### 8.2 Data Directory Structure

```
data/
├── inbox/                        # Drop zone for ad-hoc content
│   ├── articles/                 # Drop .md files here
│   ├── youtube_urls.txt          # Paste video URLs (one per line)
│   └── youtube_channels.txt      # Paste channel handles (one per line)
│
├── processed/                    # Successfully processed inbox items
│   ├── articles/                 # Moved from inbox after ingestion
│   └── logs/                     # Processing logs
│
├── failed/                       # Failed items with error logs
│   ├── articles/                 # Failed articles
│   └── youtube/                  # Failed video/channel entries
│
├── raw/
│   └── youtube_transcripts/
│       ├── @ChannelName/         # Per-channel transcripts
│       ├── @AnotherChannel/
│       └── _adhoc/               # Ad-hoc video transcripts (from inbox)
│
├── channel_status.json           # Channel processing status
├── sync_state.json               # Sync state (no-subs tracking)
└── lancedb/                      # Vector database
```

### Module Dependency Flow
```
config.py ← models.py ← youtube/client.py ← youtube/inbox.py ← sync.py ← cli.py
                      ← storage/llm_extract.py ← storage/inbox.py ↗       ← mcp_server.py
                      ← storage/files.py ← storage/db.py ← search.py
                                                        ← discover.py
```

**New flow additions:**
- `storage/llm_extract.py`: Depends only on config + external Ollama
- `storage/inbox.py`: Uses llm_extract and db
- `youtube/inbox.py`: Uses youtube/client and config
- Both inbox modules called from sync.py

---

## 9. Data Models

```python
# models.py

from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Video:
    """A YouTube video identified during channel listing."""
    id: str           # YouTube video ID (11 chars)
    title: str        # Original title
    upload_date: date # Upload date
    channel: str      # Channel handle (@name)
    
    @property
    def safe_title(self) -> str:
        """Title sanitized for filesystem use."""
        # Remove/replace problematic characters
        ...


@dataclass
class Transcript:
    """A downloaded and converted transcript."""
    video: Video
    text: str         # Clean transcript text (no timestamps)
    filepath: Path    # Absolute path to MD file
    
    @property
    def doc_id(self) -> str:
        """Unique document ID for database."""
        # Hash of filepath or video_id + channel
        ...


@dataclass
class ChunkRecord:
    """A chunk ready for database insertion."""
    id: str           # {doc_id}_{chunk_index}
    doc_id: str       # Parent document ID
    chunk_index: int  # Position in document
    text: str         # Chunk content
    channel: str
    title: str
    date: str         # ISO format
    source: str       # "youtube" | "article"
    tags: list[str]   # Topic tags (lowercase, hyphenated)
    filepath: str
    # vector: computed by LanceDB


@dataclass
class ArticleDocument:
    """An article ingested from the inbox."""
    filepath: Path    # Original file path
    title: str        # Extracted or derived title
    text: str         # Full article text
    source: str = "article"
    tags: list[str] = None  # Up to 5 topic tags
    date: date = None
    summary: str = None
    
    @property
    def doc_id(self) -> str:
        """Unique document ID for database."""
        # Hash of filepath
        ...
```

---

## 10. Module Specifications

### 10.1 config.py
```python
# Paths
ROOT_DIR, DATA_DIR, TRANSCRIPTS_DIR, LANCEDB_DIR
INBOX_DIR = DATA_DIR / "inbox"
PROCESSED_DIR = DATA_DIR / "processed"
FAILED_DIR = DATA_DIR / "failed"

# Embedding
EMBEDDING_MODEL = "bge-m3"            # Primary: 1024d, best quality for multi-domain
EMBEDDING_DIMENSIONS = 1024
EMBEDDING_PREFIX = "Represent this document for retrieval: "
QUERY_PREFIX = "Represent this query for retrieval: "
OLLAMA_BASE_URL = "http://localhost:11434"

# LLM Extraction (see Section 4.6 for model research)
LLM_EXTRACT_MODEL = "qwen3:4b"  # Primary: best balance quality/speed for M2 Pro
# Alternatives (test before switching):
# LLM_EXTRACT_MODEL = "qwen3:1.7b"   # Newer Qwen3 architecture
# LLM_EXTRACT_MODEL = "gemma3:1b"    # Fastest, Google model
# LLM_EXTRACT_MODEL = "phi4-mini"    # Higher quality, slower
LLM_MAX_INPUT_CHARS = 4000          # ~1000 tokens
LLM_TEMPERATURE = 0.3               # Low for consistent structured output
LLM_RETRIES_PER_PROMPT = 2

# Chunking
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

# Sync
BACKFILL_DAYS = 60
PARALLEL_WORKERS = 8
RETRY_ATTEMPTS = 2

# Channel configuration with default tags
YOUTUBE_CHANNELS = [
    {"handle": "@AndrejKarpathy", "default_tags": ["ai", "neural-networks"]},
    {"handle": "@3blue1brown", "default_tags": ["math", "visualization"]},
    {"handle": "@indydevdan", "default_tags": ["ai", "mcp", "claude-code"]},
    # ... etc
]

def get_channel_tags(handle: str) -> list[str]:
    """Get default tags for channel."""
```

### 10.2 youtube/client.py
```python
def check_network() -> bool:
    """Check YouTube connectivity."""

def list_channel_videos(channel: str, since_date: date) -> list[Video]:
    """List videos from channel since date. Returns newest-first."""

def get_video_info(video_id: str) -> dict | None:
    """
    Get metadata for a single video by ID.
    
    Used for ad-hoc video ingestion from inbox.
    Returns: {"title": str, "upload_date": date, "channel": str} or None
    """

def download_subtitles(video: Video, output_dir: Path) -> Path | None:
    """Download SRT for video. Returns SRT path or None if unavailable."""
```

**Key decisions:**
- Always pass `Video` objects, not loose dicts
- Return `None` for no subtitles (don't raise)
- Suppress yt-dlp warnings to stderr

### 10.3 youtube/parser.py
```python
def parse_srt(srt_path: Path) -> str | None:
    """Parse SRT file, return clean text without timestamps."""

def is_valid_srt(content: str) -> bool:
    """Check if content looks like valid SRT."""
```

### 10.4 storage/files.py
```python
# THE canonical filename format
FILENAME_PATTERN = "{date}_{video_id}_{title}.md"
# Example: 20260128_Ke4iqmdD5iI_Build a Synced Web App.md

def generate_filename(video: Video) -> str:
    """Generate canonical filename for a video."""

def parse_filename(filename: str) -> tuple[date, str, str] | None:
    """Parse filename into (date, video_id, title). None if invalid."""

def find_transcript(video_id: str, channel_dir: Path) -> Path | None:
    """Find existing transcript by video_id. None if not found."""

def save_transcript(video: Video, text: str, channel_dir: Path) -> Path:
    """Save transcript to canonical location. Atomic write."""

def list_transcripts(channel_dir: Path) -> list[Path]:
    """List all transcript files in channel directory."""
```

**Critical:** These 4-5 functions are the ONLY place filename logic lives.

### 10.5 storage/db.py
```python
def get_db() -> lancedb.DBConnection:
    """Get or create database connection."""

def doc_exists(db: DBConnection, doc_id: str) -> bool:
    """Check if document already ingested."""

def ingest_transcript(transcript: Transcript, db: DBConnection) -> int:
    """Chunk and ingest transcript. Returns chunk count. Idempotent."""

def search(
    query: str, 
    limit: int = 10, 
    channel: str = None,
    tag: str = None,       # Filter by single tag
    tags: list[str] = None, # Filter by multiple tags (AND)
) -> list[dict]:
    """
    Semantic search across the unified knowledge base.
    
    Cross-topic by default (no filter) - this is a feature!
    Filter by tag or tags for focused searches.
    """

def get_stats() -> dict:
    """Database statistics."""
```

### 10.6 sync.py
```python
class SyncState:
    """Tracks videos with no subtitles (to avoid re-trying)."""
    
    def get_no_subs(channel: str) -> set[str]
    def add_no_subs(channel: str, video_ids: list[str])
    def save()

def sync_channel(channel: str, state: SyncState) -> SyncResult:
    """
    Sync one channel:
    1. List videos (60-day window)
    2. Filter out: existing transcripts, known no-subs
    3. Download remaining
    4. Ingest new transcripts
    """

def sync_all(parallel: bool = True) -> dict:
    """
    Full sync including inbox processing:
    1. Process inbox (articles, videos, channels)
    2. Parallel: list all channels
    3. Sequential: process each channel
    """

def process_inbox() -> dict:
    """
    Process all inbox items before regular sync.
    Called automatically at start of sync_all.
    
    1. Process article inbox (data/inbox/articles/)
    2. Process YouTube URL inbox (data/inbox/youtube_urls.txt)
    3. Process channel inbox (data/inbox/youtube_channels.txt)
    """
    from .storage.inbox import process_article_inbox
    from .youtube.inbox import process_youtube_inbox
    
    return {
        "articles": process_article_inbox(),
        "youtube": process_youtube_inbox(),
    }

def repair_orphans() -> dict:
    """Convert orphan SRT files and ingest them."""
```

### 10.7 cli.py
Consolidate all CLI entry points:
```python
@click.group()
def cli():
    """AI Knowledge Base CLI."""

@cli.command()
def sync():
    """Full sync: process inbox, then sync all channels."""
    ...

@cli.command()  
def search():
    """Semantic search across knowledge base."""
    ...

@cli.command()
def status():
    """Show database and channel status."""
    ...

@cli.command()
def discover():
    """Discover new videos/transcripts."""
    ...

@cli.command()
def inbox():
    """Process inbox only (without full channel sync)."""
    ...

@cli.command()
def channels():
    """List/manage tracked channels."""
    ...
```

### 10.8 storage/llm_extract.py
```python
"""LLM-based metadata extraction with robust error handling."""

from dataclasses import dataclass
from typing import Optional
import json
import re


# Configuration
MODEL = "qwen3:4b"  # 3-4B model for quality metadata extraction
MAX_INPUT_CHARS = 4000  # ~1000 tokens, safe for context window
RETRIES_PER_PROMPT = 2
TEMPERATURE = 0.3       # Low temp for consistent structured output


@dataclass
class ExtractedMetadata:
    """Metadata extracted from unstructured content."""
    title: str
    summary: Optional[str] = None
    tags: list[str] = None        # Up to 5 topic tags (lowercase, hyphenated)
    content_type: str = "article" # article, tutorial, reference, news
    source: str = "llm"           # "llm", "heuristic", or "filename"


# --- Simplified Design (see Section 2) ---
# No explicit domain field. Tags + embeddings handle organization.
# Domain can be inferred from tags if needed (see infer_domain() in Section 2).


def extract_metadata(text: str, filename: str = None) -> ExtractedMetadata:
    """
    Extract title, summary, and tags from raw text.
    
    Tries LLM first, falls back to heuristics, then filename.
    Never fails - always returns something usable.
    """
    # Truncate for LLM context window
    truncated = truncate_smart(text, MAX_INPUT_CHARS)
    
    # Try LLM with escalating prompts
    for prompt_level in ["simple", "explicit", "minimal"]:
        for attempt in range(RETRIES_PER_PROMPT):
            result = _try_llm_extract(truncated, prompt_level)
            if result and _validate_metadata(result):
                return ExtractedMetadata(
                    title=result["title"],
                    summary=result.get("summary"),
                    tags=result.get("tags", []),
                    source="llm"
                )
    
    # Fallback to heuristics
    title = _extract_title_heuristic(text)
    if title:
        return ExtractedMetadata(title=title, source="heuristic")
    
    # Final fallback: filename
    if filename:
        return ExtractedMetadata(
            title=_title_from_filename(filename),
            source="filename"
        )
    
    return ExtractedMetadata(title="Untitled Article", source="filename")


def truncate_smart(text: str, max_chars: int) -> str:
    """
    Truncate preserving start and end (where titles often appear).
    
    Strategy: 70% from start, 30% from end with [...] separator.
    """
    if len(text) <= max_chars:
        return text
    
    start_chars = int(max_chars * 0.7)
    end_chars = int(max_chars * 0.3) - 20  # Reserve space for separator
    
    return text[:start_chars] + "\n\n[...content truncated...]\n\n" + text[-end_chars:]


def _try_llm_extract(text: str, prompt_level: str) -> dict | None:
    """
    Single LLM extraction attempt.
    
    Prompt levels:
    - simple: Basic instruction
    - explicit: More detailed with examples
    - minimal: Just ask for title (when other fields fail)
    """
    prompts = {
        "simple": '''Extract metadata from this article.
Return JSON: {"title": "...", "summary": "...", "tags": [...]}

Tags: up to 5 relevant lowercase topic keywords (hyphenate multi-word tags)

Article:
{text}''',
        
        "explicit": '''You must extract metadata from this article.
Return ONLY valid JSON with exactly this format:
{{
  "title": "The Article Title Here",
  "summary": "One sentence describing what the article is about.",
  "tags": ["transformers", "local-llm", "inference"]
}}

Rules:
- title: The main title of the article (5-200 characters)
- summary: One sentence describing what the article is about
- tags: Up to 5 lowercase topic keywords (hyphenated if multi-word)
- Return ONLY the JSON, no other text

Article:
{text}''',
        
        "minimal": '''What is the title of this article?
Return ONLY: {{"title": "..."}}

{text}'''
    }
    
    prompt = prompts[prompt_level].format(text=text)
    
    try:
        response = ollama_generate(MODEL, prompt, temperature=TEMPERATURE)
        return _parse_json_response(response)
    except Exception:
        return None


def _parse_json_response(response: str) -> dict | None:
    """
    Parse JSON from LLM response with multiple strategies.
    
    Handles common LLM quirks like markdown code blocks, 
    extra text, and slightly malformed JSON.
    """
    # Strategy 1: Direct parse
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Extract from markdown code block
    code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Find first {...} in response
    json_match = re.search(r'\{[^}]+\}', response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Strategy 4: Fix common issues (single quotes, trailing commas)
    cleaned = response.replace("'", '"')
    cleaned = re.sub(r',\s*}', '}', cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    return None


def _validate_metadata(result: dict) -> bool:
    """
    Validate extracted metadata is usable.
    
    Rejects:
    - Too short (< 5 chars) or too long (> 200 chars) titles
    - Known bad patterns (LLM confusion)
    - Empty/placeholder values
    """
    if "title" not in result:
        return False
    
    title = result["title"].strip()
    
    # Length checks
    if len(title) < 5 or len(title) > 200:
        return False
    
    # Known bad patterns
    bad_patterns = [
        r"^article title",
        r"^title:",
        r"^untitled$",
        r"^the article",
        r"^\.\.\.$",
        r"^n/a$",
        r"^null$",
    ]
    for pattern in bad_patterns:
        if re.match(pattern, title.lower()):
            return False
    
    return True


def _extract_title_heuristic(text: str) -> str | None:
    """
    Extract title using pattern matching.
    
    Strategies:
    1. First markdown heading (# Title)
    2. First non-empty line if short enough (<100 chars)
    3. First sentence if it looks like a title
    """
    lines = text.strip().split('\n')
    
    # Look for markdown heading
    for line in lines[:10]:  # Check first 10 lines
        if line.startswith('# '):
            return line[2:].strip()
    
    # First non-empty line if short
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) < 100 and not line.startswith(('#', '-', '*', '>')):
            return line
    
    return None


def _title_from_filename(filename: str) -> str:
    """Convert filename to readable title."""
    # Remove extension
    name = filename.rsplit('.', 1)[0]
    # Remove date prefix if present
    name = re.sub(r'^\d{4}[-_]?\d{2}[-_]?\d{2}[-_]?', '', name)
    # Underscores to spaces
    name = name.replace('_', ' ').replace('-', ' ')
    return name.strip().title() or "Untitled Article"


def ollama_generate(model: str, prompt: str, temperature: float = 0.3) -> str:
    """
    Call Ollama API for text generation.
    
    Uses the /api/generate endpoint for simple completions.
    For structured output, consider using /api/chat with format parameter.
    """
    import httpx
    from ..config import OLLAMA_BASE_URL
    
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature}
        },
        timeout=30.0
    )
    response.raise_for_status()
    return response.json()["response"]
```

### 10.9 storage/inbox.py
```python
"""Article inbox processing - zero-friction content ingestion."""

from pathlib import Path
from datetime import datetime
import shutil

from .llm_extract import extract_metadata
from .db import ingest_document
from ..config import DATA_DIR


INBOX_DIR = DATA_DIR / "inbox" / "articles"
PROCESSED_DIR = DATA_DIR / "processed" / "articles"
FAILED_DIR = DATA_DIR / "failed" / "articles"


def process_article_inbox() -> dict:
    """
    Process all articles in the inbox.
    
    For each .md file:
    1. Extract metadata via LLM
    2. Ingest into database
    3. Move to processed/ or failed/
    
    Returns: {"processed": [...], "failed": [...]}
    """
    results = {"processed": [], "failed": []}
    
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    
    for article_path in INBOX_DIR.glob("*.md"):
        try:
            text = article_path.read_text()
            
            # Extract metadata
            metadata = extract_metadata(text, article_path.name)
            
            # Create document record
            doc = ArticleDocument(
                filepath=article_path,
                title=metadata.title,
                summary=metadata.summary,
                tags=metadata.tags,  # Topic tags from LLM extraction
                text=text,
                source="article",
                date=datetime.now().date(),
            )
            
            # Ingest into database
            ingest_document(doc)
            
            # Move to processed
            dest = PROCESSED_DIR / article_path.name
            shutil.move(article_path, dest)
            
            results["processed"].append({
                "file": article_path.name,
                "title": metadata.title,
                "source": metadata.source,  # "llm", "heuristic", or "filename"
            })
            
        except Exception as e:
            # Move to failed with error log
            dest = FAILED_DIR / article_path.name
            shutil.move(article_path, dest)
            
            # Write error log
            error_log = FAILED_DIR / f"{article_path.stem}.error.txt"
            error_log.write_text(f"Error: {e}\n\nFile: {article_path.name}")
            
            results["failed"].append({
                "file": article_path.name,
                "error": str(e),
            })
    
    return results
```

### 10.10 youtube/inbox.py
```python
"""YouTube inbox processing - ad-hoc videos and channel subscriptions."""

from pathlib import Path
from datetime import datetime
import re

from ..config import DATA_DIR
from .client import download_subtitles, get_channel_handle, list_channel_videos


INBOX_DIR = DATA_DIR / "inbox"
URLS_FILE = INBOX_DIR / "youtube_urls.txt"
CHANNELS_FILE = INBOX_DIR / "youtube_channels.txt"
ADHOC_DIR = DATA_DIR / "raw" / "youtube_transcripts" / "_adhoc"
STATUS_FILE = DATA_DIR / "channel_status.json"


def process_youtube_inbox() -> dict:
    """
    Process YouTube inbox files.
    
    1. youtube_urls.txt: Download ad-hoc video transcripts
    2. youtube_channels.txt: Add channels for regular syncing
    
    Returns: {"videos": {...}, "channels": {...}}
    """
    results = {"videos": [], "channels": []}
    
    # Process video URLs
    if URLS_FILE.exists():
        results["videos"] = _process_video_urls()
    
    # Process channel subscriptions
    if CHANNELS_FILE.exists():
        results["channels"] = _process_channels()
    
    return results


def _process_video_urls() -> list[dict]:
    """Process youtube_urls.txt - one URL per line."""
    results = []
    remaining_lines = []
    
    lines = URLS_FILE.read_text().strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            remaining_lines.append(line)
            continue
        
        video_id = _extract_video_id(line)
        if not video_id:
            remaining_lines.append(f"# ERROR: Invalid URL: {line}")
            results.append({"url": line, "error": "Invalid URL format"})
            continue
        
        try:
            # Download to _adhoc directory
            ADHOC_DIR.mkdir(parents=True, exist_ok=True)
            result = download_adhoc_video(video_id, ADHOC_DIR)
            results.append(result)
            # Don't keep successful lines
        except Exception as e:
            remaining_lines.append(f"# ERROR: {e}: {line}")
            results.append({"url": line, "error": str(e)})
    
    # Rewrite file with only failed/commented lines
    if remaining_lines:
        URLS_FILE.write_text('\n'.join(remaining_lines) + '\n')
    else:
        URLS_FILE.unlink()
    
    return results


def _process_channels() -> list[dict]:
    """
    Process youtube_channels.txt - register channels for syncing.
    
    Accepts:
    - @ChannelHandle
    - channel handle (without @)
    - Full channel URL
    """
    results = []
    remaining_lines = []
    status = _load_channel_status()
    
    lines = CHANNELS_FILE.read_text().strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            remaining_lines.append(line)
            continue
        
        handle = _normalize_channel_handle(line)
        if not handle:
            remaining_lines.append(f"# ERROR: Invalid format: {line}")
            results.append({"input": line, "error": "Invalid format"})
            continue
        
        # Add to channel status if not already tracked
        if handle not in status:
            status[handle] = {
                "status": "pending",
                "added": datetime.now().isoformat(),
                "domain": "ai",  # Default domain
            }
            results.append({"handle": handle, "status": "added"})
        else:
            results.append({"handle": handle, "status": "already_tracked"})
        # Don't keep processed lines
    
    # Save updated status
    _save_channel_status(status)
    
    # Rewrite file with only failed/commented lines
    if remaining_lines:
        CHANNELS_FILE.write_text('\n'.join(remaining_lines) + '\n')
    else:
        CHANNELS_FILE.unlink()
    
    return results


def download_adhoc_video(video_id: str, output_dir: Path) -> dict:
    """
    Download transcript for a single ad-hoc video.
    
    Uses youtube/client.py functions to:
    1. Get video metadata
    2. Download subtitles
    3. Convert to markdown
    4. Ingest into database
    
    Returns dict with video info and status.
    """
    from .client import get_video_info, download_subtitles
    from .parser import parse_srt
    from ..storage.files import save_transcript
    from ..storage.db import ingest_transcript
    
    # Get video metadata
    video_info = get_video_info(video_id)
    if not video_info:
        raise ValueError(f"Could not fetch video info for {video_id}")
    
    # Create Video object with _adhoc as channel
    video = Video(
        id=video_id,
        title=video_info["title"],
        upload_date=video_info["upload_date"],
        channel="_adhoc",
    )
    
    # Download subtitles
    srt_path = download_subtitles(video, output_dir)
    if not srt_path:
        raise ValueError(f"No subtitles available for {video_id}")
    
    # Parse and save
    text = parse_srt(srt_path)
    transcript_path = save_transcript(video, text, output_dir)
    
    # Ingest
    transcript = Transcript(video=video, text=text, filepath=transcript_path)
    ingest_transcript(transcript)
    
    return {
        "video_id": video_id,
        "title": video.title,
        "status": "success",
        "path": str(transcript_path)
    }


def _extract_video_id(url_or_id: str) -> str | None:
    """Extract video ID from URL or return if already an ID."""
    # Direct ID (11 chars)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Full URL patterns
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None


def _normalize_channel_handle(input_str: str) -> str | None:
    """
    Normalize channel input to @Handle format.
    
    Accepts:
    - @ChannelHandle -> @ChannelHandle
    - ChannelHandle -> @ChannelHandle
    - youtube.com/@ChannelHandle -> @ChannelHandle
    - youtube.com/channel/UC... -> @UC... (needs API lookup)
    """
    input_str = input_str.strip()
    
    # Already a handle
    if input_str.startswith('@'):
        return input_str
    
    # URL with handle
    match = re.search(r'youtube\.com/@([a-zA-Z0-9_-]+)', input_str)
    if match:
        return f"@{match.group(1)}"
    
    # Plain handle without @
    if re.match(r'^[a-zA-Z0-9_-]+$', input_str):
        return f"@{input_str}"
    
    return None
```

### 10.11 Channel Status Tracking
```python
# data/channel_status.json structure

{
  "@AndrejKarpathy": {
    "status": "active",           # pending | backfilling | active | failed
    "added": "2026-01-28T10:00:00",
    "domain": "ai",
    "last_sync": "2026-01-28T15:30:00",
    "video_count": 47,
    "error": null
  },
  "@NewChannel": {
    "status": "pending",          # Just added, not yet synced
    "added": "2026-01-29T09:00:00",
    "domain": "ai",
    "last_sync": null,
    "video_count": 0,
    "error": null
  },
  "@FailedChannel": {
    "status": "failed",           # Repeated failures
    "added": "2026-01-25T10:00:00",
    "domain": "ai",
    "last_sync": "2026-01-27T10:00:00",
    "video_count": 12,
    "error": "Network timeout after 3 retries"
  }
}
```

**Status Transitions:**
```
pending → backfilling → active
                     ↘ failed → (manual retry) → backfilling
```

- **pending**: Newly added, never synced
- **backfilling**: Currently downloading historical videos
- **active**: Regular sync active, up to date
- **failed**: Multiple sync failures, needs attention

---

## 11. Key Design Decisions

### 11.1 Filename Format
**Decision:** `{YYYYMMDD}_{video_id}_{safe_title}.md`

**Rationale:**
- Date first for natural sorting
- Video ID for reliable lookup (11 chars, unique, stable)
- Title for human readability
- No brackets or special characters that break glob

**Example:** `20260128_Ke4iqmdD5iI_Build a Synced Web App.md`

### 11.2 Video ID as Primary Key
- YouTube video ID is globally unique and immutable
- Use it for file lookup, not title matching
- `find_transcript(video_id)` scans for `*_{video_id}_*.md`

### 11.3 State File Minimalism
Only store what can't be derived:
- `no_subs`: Videos confirmed to have no subtitles
- `last_sync`: (optional) For rate limiting

Do NOT store:
- Known videos (derived from filesystem)
- Ingested documents (derived from database)

### 11.4 Parallel Listing, Sequential Processing
- Channel listing is I/O bound → parallelize (8 workers)
- Downloading/ingesting has side effects → sequential per channel
- This keeps state management simple

### 11.5 Atomic File Writes
All file writes use temp-file-then-rename pattern:
```python
with tempfile.NamedTemporaryFile(delete=False) as f:
    f.write(content)
Path(f.name).replace(target_path)
```

---

## 12. Migration Plan

### 12.1 Approach: Clean Rewrite with Data Migration

After extensive planning, we've chosen a **clean rewrite** approach:

1. **Archive old code** - Move existing `src/` to `src_archive/` for reference
2. **Implement new architecture** - Fresh implementation following this spec
3. **Migrate data** - Run migration script to rename files to canonical format
4. **Re-ingest** - Rebuild vector database from migrated transcripts
5. **Validate** - Compare document counts, test search quality
6. **Delete archive** - Once confident, remove old code

**Why clean rewrite over incremental refactor:**
- Existing code (2,056 lines) has mixed responsibilities
- New architecture is fundamentally different (thin wrappers, inbox pattern)
- Clean implementation is faster than untangling dependencies
- No risk of breaking production during transition

### 12.2 Handle Existing Files
Existing files have mixed formats:

**Strategy:** Migration script to rename all files to canonical format:
```bash
# data/scripts/migrate_filenames.py
# Scans all transcript directories
# Renames files to: {YYYYMMDD}_{video_id}_{safe_title}.md
# Logs all changes for verification
```

### 12.3 Implementation Order (Dev Guides)

**Phase 1: Core Foundation**
1. Create `config.py` - paths, constants, channel list
2. Create `models.py` - dataclasses (Video, Transcript, ChunkRecord, ArticleDocument)
3. Create `storage/files.py` - canonical naming, atomic writes
4. Create `storage/db.py` - LanceDB operations

**Phase 2: YouTube Pipeline**
5. Create `youtube/client.py` - yt-dlp wrapper
6. Create `youtube/parser.py` - SRT parsing
7. Create `sync.py` - orchestration for channel sync

**Phase 3: Inbox & LLM Extraction**
8. Create `storage/llm_extract.py` - LLM-based metadata extraction
9. Create `storage/inbox.py` - article inbox processing
10. Create `youtube/inbox.py` - URL/channel inbox processing

**Phase 4: Interfaces**
11. Create `cli.py` - consolidated CLI with Click
12. Create `mcp_server.py` - FastMCP interface
13. Create `search.py` and `discover.py`

**Phase 5: Migration & Validation**
14. Create migration script for existing files
15. Run migration, rebuild database
16. Validate against old system
17. Archive old code

---

## 13. Testing Strategy

### 13.1 Unit Tests
- `test_files.py`: filename generation/parsing
- `test_parser.py`: SRT parsing
- `test_models.py`: dataclass validation
- `test_llm_extract.py`: JSON parsing strategies, validation logic

### 13.2 Integration Tests
- `test_sync.py`: mock yt-dlp, verify flow
- `test_db.py`: real LanceDB, verify ingestion
- `test_inbox.py`: article and YouTube inbox processing
- `test_llm_integration.py`: mock Ollama, verify extraction pipeline

### 13.3 LLM Extraction Testing

**Mock Ollama for unit tests:**
```python
@pytest.fixture
def mock_ollama(monkeypatch):
    def mock_generate(model, prompt, temperature):
        return '{"title": "Test Article", "summary": "A test summary."}'
    monkeypatch.setattr("storage.llm_extract.ollama_generate", mock_generate)
```

**Test cases for LLM extraction:**
- Valid JSON response → parsed correctly
- Markdown code block response → extracted correctly
- Malformed JSON with single quotes → fixed and parsed
- Too short title → rejected, fallback used
- Known bad pattern ("Article Title") → rejected
- Heuristic fallback → first markdown heading extracted
- Filename fallback → date stripped, underscores replaced

### 13.4 Manual Validation
- Full sync of all configured channels
- Verify file count matches expected
- Search functionality works
- Drop test articles in inbox, verify ingestion
- Test LLM extraction on varied article formats

---

## 14. Open Questions → Decisions

### Core Pipeline

1. **Title sanitization:** What characters to allow?
   - **Decision:** Alphanumeric, spaces, hyphens, underscores. Replace others with underscore.
   - **Rationale:** Simple, filesystem-safe, readable. Avoid over-engineering.
   ```python
   safe = re.sub(r'[^a-zA-Z0-9\s_-]', '_', title)
   safe = re.sub(r'\s+', ' ', safe).strip()[:80]  # Max 80 chars
   ```

2. **SRT variants:** Handle `.en.srt`, `.en-US.srt`, etc?
   - **Decision:** Accept any English variant: `en`, `en-US`, `en-GB`, `en-AU`
   - **Rationale:** yt-dlp handles this with `--sub-langs "en*"` flag.

3. **Rate limiting:** Add delays between yt-dlp calls?
   - **Decision:** Not initially. Add 0.5s delay only if we see rate limiting.
   - **Rationale:** Start simple, optimize only if needed. yt-dlp has built-in retry logic.

4. **Chunk overlap:** Is 200 chars enough?
   - **Decision:** Yes, 200 chars (~50 words) is sufficient. Make configurable via `config.py`.
   - **Rationale:** Standard practice. Higher overlap = more chunks = slower search. 200 is good balance.

5. **Channel removal:** Delete data if channel removed from config?
   - **Decision:** No automatic deletion. Keep data, just stop syncing.
   - **Rationale:** Data is valuable, avoid accidental deletion. Add `aikb cleanup` command for explicit deletion.

### Inbox & LLM

6. **LLM model selection:** Which model for metadata extraction?
   - **Decision:** Primary: `qwen3:4b`. Alternative: `phi4-mini` or `qwen3:8b`.
   - **Rationale:** 3-4B models are the sweet spot for M2 Pro 16GB. Good quality for nuanced extraction (title, summary, domain, tags) while staying fast (<2s/extraction). See Section 4.6.

7. **Article domain/category detection:** Should we have explicit domains?
   - **Decision:** No explicit domains. Use tags + embeddings only.
   - **Rationale:** Zero-maintenance approach. Tags provide topic labels, embeddings provide semantic clustering. Domain-like filtering can be inferred from tags if needed. See Section 2.

8. **Inbox polling frequency:** Only during sync or separate task?
   - **Decision:** Only during sync (`aikb sync` includes inbox processing).
   - **Rationale:** Simplicity. One command does everything. No need for separate cron job.

9. **Failed item retention:** How long to keep?
   - **Decision:** Keep indefinitely until manually deleted or `aikb cleanup --failed` run.
   - **Rationale:** Failed items need human review. Auto-deletion could lose important content.

10. **Channel backfill depth:** How far back for new channels?
    - **Decision:** Use `BACKFILL_DAYS` config (default 60 days). First sync does full backfill.
    - **Rationale:** 60 days catches recent content without overwhelming initial sync.

### Embedding Model

11. **Embedding model selection:** Which embedding model for vector search?
    - **Decision:** Use `mxbai-embed-large` (1024d, 335M params).
    - **Rationale:** 1024d better for multi-topic knowledge base. 335M params (40% smaller than bge-m3), 6.9M Ollama pulls, Apache 2.0 license. Best quality/size tradeoff. See Section 4.7.

12. **Embedding dimensions:** Consider higher (1024d, 1536d)?
    - **Decision:** 1024d is optimal for multi-domain corpus. M2 Pro 16GB handles 400K+ chunks easily.
    - **Rationale:** Better topic separation across AI, engineering, business domains. 1536d offers diminishing returns.

---

## 15. Success Criteria

After rewrite, the system should:

**Core Sync:**
- [ ] Sync all configured channels without errors
- [ ] Be fully idempotent (re-running produces no changes)
- [ ] Handle partial failures gracefully
- [ ] Have no duplicate files
- [ ] Have consistent filename format
- [ ] Complete full sync in < 10 minutes
- [ ] Have no module > 200 lines

**Inbox Processing:**
- [ ] Process articles dropped in inbox/articles/ automatically
- [ ] Extract titles via LLM with >90% accuracy
- [ ] Fall back to heuristics gracefully when LLM fails
- [ ] Process YouTube URLs from youtube_urls.txt
- [ ] Register new channels from youtube_channels.txt
- [ ] Move processed items to processed/ directory
- [ ] Move failed items to failed/ with error logs

**Channel Management:**
- [ ] Track channel status (pending/backfilling/active/failed)
- [ ] Support adding channels via inbox file
- [ ] Persist channel status across syncs

**Testing:**
- [ ] Pass all unit tests
- [ ] Integration tests for inbox processing
- [ ] LLM extraction tests with mocked Ollama

---

## 16. Next Steps

1. ✅ Review and refine this design document (Done: 2026-01-29)
2. ⏳ Resolve open questions (see Section 14)
3. 📝 Create dev guides for each implementation phase (5 guides):
   - `docs/dev_guides/01_core_foundation.md` - config, models, storage/files, storage/db
   - `docs/dev_guides/02_youtube_pipeline.md` - youtube/client, youtube/parser, sync
   - `docs/dev_guides/03_inbox_llm_extraction.md` - storage/llm_extract, storage/inbox, youtube/inbox
   - `docs/dev_guides/04_interfaces.md` - cli, mcp_server, search, discover
   - `docs/dev_guides/05_migration_validation.md` - migration script, data validation, testing
4. 🔨 Implement following dev guides (clean rewrite)
5. 🧪 Test thoroughly with integration tests
6. 🗄️ Archive old code after validation

**Reference Guides:**
- `/second_brain/docs/guides/best_practices_local_llm.md` - Local LLM patterns
- `/second_brain/docs/guides/meta_creating_best_practices_guides.md` - Guide structure
- `/second_brain/docs/guides/best_practices_python_testing.md` - Testing patterns

---

## Appendix A: Current Codebase Inventory

### Lines of Code
| File | Lines | Responsibility |
|------|-------|----------------|
| `youtube_sync.py` | 754 | **Too big!** yt-dlp, files, state, ingestion, CLI |
| `mcp_server.py` | 387 | MCP interface (OK) |
| `ingest.py` | 360 | Chunking, DB ops, CLI (mixed) |
| `discover.py` | 242 | Discovery features (OK) |
| `search.py` | 135 | Search interface (OK) |
| `config.py` | 65 | Configuration (OK) |
| `embed.py` | 63 | Embedding util (OK) |
| `schema.py` | 47 | LanceDB schema (OK) |
| **Total** | **2,056** | (excluding `__init__.py`) |

### Current File State
- **5 channel directories** with transcripts
- **32 markdown files** (.md transcripts)
- **80 SRT files** (many orphans without .md)
- **48 orphan SRTs** need conversion

### Filename Patterns in Use
Current files use inconsistent patterns:
```
20260115_Will.i.am's $3 Billion Airbnb Mistake.md       # No video ID
20260119_Claude + Gemini： My Game Art Workflow.md      # Unicode chars
20251221_i let two AIs redesign my website.md          # Lowercase
20260126_[Ke4iqmdD5iI]_Stop Installing Codebases...    # Bracketed ID (broken glob)
```

**Problem:** No video ID in most filenames makes reliable lookup impossible.

## Appendix B: Canonical Filename Format

### Requirements
1. Sortable by date (date first)
2. Lookupable by video ID (ID must be present and findable)
3. Human readable (title included)
4. Filesystem safe (no special chars that break)
5. Consistent (one format, always)

### Chosen Format
```
{YYYYMMDD}_{video_id}_{sanitized_title}.md
```

**Example:**
```
20260128_Ke4iqmdD5iI_Build_a_Synced_Web_App_in_16_Mins.md
```

### Title Sanitization Rules
1. Replace spaces with underscores
2. Remove: `/ \ : * ? " < > | [ ] ( )`
3. Replace unicode with ASCII equivalent or remove
4. Truncate to 80 chars max
5. Strip leading/trailing underscores

### Video ID Lookup
To find a file by video_id:
```python
# Simple glob - video ID is always after first underscore
files = list(channel_dir.glob(f"*_{video_id}_*.md"))
```

No brackets, no ambiguity, no character class issues.

## Appendix C: Future Extensibility

### Potential Future Sources
| Source | Effort | Value |
|--------|--------|-------|
| **Podcasts** (audio→transcript) | High | High |
| **RSS/Blogs** | Low | Medium |
| **arXiv papers** | Medium | High |
| **GitHub READMEs** | Low | Medium |

### Extension Points
The architecture supports adding sources by:
1. Add new client module in `sources/` (e.g., `sources/podcast.py`)
2. Implement same interface: `list_items()`, `download_content()`
3. Reuse existing: `storage/files.py`, `storage/db.py`
4. Add to sync orchestration

### MCP Tool Expansion
Current: `search`, `discover`, `get_context`, `sync_now`, `get_status`

Future possibilities:
- `summarize_topic(topic)` - AI-generated summary of a concept
- `compare_approaches(topic)` - What do different channels say?
- `timeline(topic)` - How has thinking evolved over time?

---

## Appendix D: Decision Log

| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| Filename format | `[id]`, `(id)`, `id` | `_{id}_` | Underscores are glob-safe |
| State file content | Full video list vs minimal | Minimal | Filesystem is source of truth |
| Parallel vs sequential | Full parallel, hybrid, sequential | Hybrid | Parallel listing, sequential download |
| Embedding model | nomic 768d, bge-m3 1024d, mxbai 1024d | mxbai-embed-large 1024d | 335M params (40% smaller than bge-m3), Apache 2.0, proven Ollama support |
| Database | SQLite+pgvector, Chroma, LanceDB | LanceDB | Simple, native embedding support |
| LLM for extraction | Qwen3-0.6B, Qwen3-4B, Phi-4-mini | Qwen3-4B | 3-4B sweet spot: quality + speed on M2 Pro |
| Embedding dimensions | 768d, 1024d, 1536d | 1024d | Better topic separation, minimal overhead |
| Domain strategy | Strict list, free-form, tags only | Tags + embeddings | Zero-maintenance: tags for labels, embeddings for clustering, no explicit domain field |
| Architecture approach | Refactor, clean rewrite | Clean rewrite | Cleaner than untangling legacy |
| Dev guide location | docs/guides/, docs/dev_guides/ | docs/dev_guides/ | Clear separation |
| Channel data on removal | Auto-delete, keep | Keep | Data valuable, avoid accidental loss |
| Inbox polling | Separate cron, during sync | During sync | Simplicity, one command |

---

## Appendix E: Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| YouTube rate limiting | Medium | High | Respect delays, parallel limited to 8 |
| yt-dlp breaking changes | Medium | Medium | Pin version, check on upgrade |
| Ollama unavailable | Low | High | Check at startup, clear error message |
| Large transcript (3+ hours) | Medium | Low | Chunk size handles gracefully |
| Channel goes private | Low | Low | Skip gracefully, keep existing |

---

## Appendix F: Glossary

| Term | Definition |
|------|------------|
| **chunk** | A segment of text (typically 500-1000 tokens) created by splitting a document for embedding. Each chunk becomes a separate vector in the database. |
| **doc_id** | Unique identifier for a document, derived from video ID or filepath hash. Used as the primary key linking chunks to their source. |
| **embedding** | A fixed-length vector (1024 dimensions) representing the semantic meaning of text. Similar meanings produce similar vectors. |
| **idempotent** | An operation that produces the same result whether run once or multiple times. Safe to re-run without side effects. |
| **inbox pattern** | A drop-zone workflow where users place items (URLs, files) in designated folders. The system polls and processes them during sync. |
| **HNSW** | Hierarchical Navigable Small World. An algorithm for fast approximate nearest neighbor search in high-dimensional vector spaces. |
| **LanceDB** | An embedded vector database using the Lance columnar format. Runs in-process without a separate server. |
| **MCP** | Model Context Protocol. A standard for AI assistants to access external tools and data sources. |
| **vector space** | A mathematical space where documents are represented as points. Semantic similarity = geometric distance between points. |
| **yt-dlp** | A command-line tool for downloading YouTube videos and metadata, including auto-generated subtitles. |
