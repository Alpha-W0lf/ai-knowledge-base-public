# AI Knowledge Base: Planning & Architecture

**Date:** January 26, 2026  
**Status:** Planning  
**Goal:** Design a robust, scalable knowledge base for AI domain research

---

## 1. Executive Summary

Build a standalone AI knowledge base repository that:
- Indexes video transcripts + other content via vector embeddings
- Supports both **query-based search** and **discovery without queries**
- Runs 100% locally on M2 MacBook Pro (no API costs)
- Scales to 1000+ documents effortlessly
- Can serve multiple projects (Second Brain, Simple Content Platform, future AI projects)

---

## 2. The Discovery Problem

### Challenge
Traditional vector search requires a query. But often we need to:
- **Discover patterns** we don't know to ask about
- **Surface insights** that aren't obvious
- **Find connections** between disparate sources
- **Identify trends** across many transcripts

### Solutions

#### A. Automatic Topic Clustering
Group similar content together automatically, then explore clusters:
- "What are the major themes across all transcripts?"
- Surface related videos you might not have connected

#### B. Periodic AI Synthesis
Run batch jobs that generate:
- Weekly digest of new insights
- Cross-transcript theme extraction
- "What's changed since last week?"
- Contrarian or surprising viewpoints

#### C. Serendipity Search
"Show me something interesting I haven't seen" - random sampling weighted by recency/relevance

#### D. Concept Extraction + Graph
Extract entities (tools, people, techniques) and build a knowledge graph:
- "What tools are mentioned most?"
- "Who references Claude Code alongside MCP?"
- "What techniques appear across multiple creators?"

#### E. Guided Exploration Prompts
Pre-built queries for common exploration:
- "What workflows are recommended for X?"
- "What pitfalls should I avoid with Y?"
- "What's new in the past 2 weeks?"

---

## 3. Tool Assessment (Late January 2026)

### Vector Database Options

| Tool | Benchmark Score | Hybrid Search | Local | Stars | Best For |
|------|-----------------|---------------|-------|-------|----------|
| **LanceDB** | 91.7 | ✅ Vector + FTS | ✅ | 8.6K | Our use case |
| ChromaDB | 82.3 | ✅ | ✅ | 25.8K | Simple prototyping |
| SQLite + sqlite-vec | N/A | Partial | ✅ | N/A | Minimal deps |

**Recommendation: LanceDB**
- Highest benchmark score (91.7)
- Native **hybrid search** (vector + full-text in one query)
- **No server process** - just files
- Python, Rust, TypeScript SDKs
- Active development (v0.27.1 released today)
- Integrates with LangChain, LlamaIndex

### Embedding Models (Local via Ollama)

| Model | Dimensions | Speed | Quality | Size |
|-------|------------|-------|---------|------|
| `nomic-embed-text` | 768 | Fast | Excellent | ~274MB |
| `mxbai-embed-large` | 1024 | Medium | Excellent | ~670MB |
| `all-minilm` | 384 | Very Fast | Good | ~45MB |

**Recommendation: `nomic-embed-text`**
- Best balance of speed/quality
- 768 dimensions is sufficient
- Well-tested with Ollama
- OpenAI-compatible API

### Current Stack Assessment
- **Ollama:** Already widely used, excellent for local embeddings
- **LanceDB:** Best-in-class for our requirements
- **Python:** Primary interface language

---

## 4. Recommended Architecture

```
ai_knowledge_base/                    # Standalone repository
├── README.md
├── pyproject.toml                    # uv/pip dependencies
├── .env.example
│
├── data/
│   ├── raw/                          # Original transcripts
│   │   ├── youtube_transcripts/
│   │   │   ├── @indydevdan/
│   │   │   ├── @engineerprompt/
│   │   │   └── ...
│   │   └── other_sources/            # Future: blogs, papers, etc.
│   │
│   └── processed/
│       └── lancedb/                  # Vector database files
│
├── src/
│   ├── __init__.py
│   ├── config.py                     # Settings, paths
│   ├── embed.py                      # Embedding generation
│   ├── ingest.py                     # Document ingestion pipeline
│   ├── search.py                     # Query interface
│   ├── discover.py                   # Topic clustering, synthesis
│   └── cli.py                        # Command-line interface
│
├── scripts/
│   ├── ingest_youtube.py             # Batch ingest transcripts
│   ├── weekly_digest.py              # Generate weekly summary
│   └── extract_concepts.py           # Build concept index
│
└── outputs/
    ├── digests/                      # Weekly AI-generated summaries
    └── exports/                      # Query results, reports
```

---

## 5. Core Workflows

### A. Ingest Pipeline
```bash
# Add new transcripts
python -m src.ingest data/raw/youtube_transcripts/

# Incremental update (only new files)
python -m src.ingest --incremental
```

### B. Search Interface
```bash
# Semantic search
python -m src.search "best practices for MCP servers"

# Hybrid search (keyword + semantic)
python -m src.search "Claude Code hooks" --hybrid

# Filter by source
python -m src.search "agentic workflows" --source @indydevdan
```

### C. Discovery Mode
```bash
# Topic clusters
python -m src.discover clusters

# Weekly digest
python -m src.discover digest --since "7 days"

# Random exploration
python -m src.discover random --n 5

# Concept extraction
python -m src.discover concepts --top 50
```

---

## 6. Implementation Plan

### Phase 1: Foundation (Day 1)
- [ ] Create repository structure
- [ ] Set up LanceDB + Ollama integration
- [ ] Basic ingest pipeline for markdown files
- [ ] Simple search CLI

### Phase 2: Discovery Features (Day 2-3)
- [ ] Topic clustering via embeddings
- [ ] Concept/entity extraction
- [ ] Weekly digest generator
- [ ] Serendipity exploration

### Phase 3: Integration (Day 4+)
- [ ] MCP server wrapper (for use with Claude Code)
- [ ] Export utilities for other projects
- [ ] Automated ingestion from YouTube

---

## 7. Why a Separate Repository?

### Pros
✅ **Reusable** across multiple projects  
✅ **Clean separation** of concerns  
✅ **Independent versioning** and maintenance  
✅ **Portable** - can run on any machine  
✅ **Focused** - single responsibility  

### Cons
❌ Another repo to maintain  
❌ Need to sync raw data or use symlinks  

### Recommendation
**Yes, create a separate repo** called `ai_knowledge_base` or similar.

The second_brain repo can reference it, and the simple_content_platform can query it for research. The knowledge base becomes a shared resource.

---

## 8. Cost Analysis

| Component | One-Time | Ongoing |
|-----------|----------|---------|
| Ollama + nomic-embed-text | Free | Free |
| LanceDB | Free | Free |
| Storage (embeddings) | ~50-100MB per 1K docs | Free |
| Compute (M2 Mac) | Already owned | ~100W peak |
| **Total** | **$0** | **$0** |

---

## 9. Scaling Considerations

| Scale | Documents | Embedding Time | Query Time | Storage |
|-------|-----------|----------------|------------|---------|
| Current | 122 | ~2 min | <100ms | ~10MB |
| 6 months | 500 | ~10 min | <100ms | ~50MB |
| 1 year | 1,000 | ~20 min | <100ms | ~100MB |
| 2 years | 5,000 | ~1.5 hr | <200ms | ~500MB |

LanceDB handles millions of vectors efficiently. We won't hit limits.

---

## 10. Alternative Approaches Considered

### A. Just Use Claude's Context Window
**Rejected:** 200K tokens can't hold 122 transcripts (~150K+ tokens each session). Not scalable.

### B. Cloud Vector DB (Pinecone, Supabase)
**Rejected:** Adds latency, costs, and external dependency. Local is faster and free.

### C. Build RAG Chatbot
**Deferred:** More complex, requires LLM calls. Can add later on top of vector search.

### D. Manual Tagging / Obsidian
**Rejected:** Doesn't scale, requires manual effort. Embeddings are automatic.

---

## 11. Open Questions

1. **Chunking strategy:** Full documents vs. paragraphs vs. sentences?
   - Recommendation: Paragraph chunks with overlap for transcripts

2. **Metadata schema:** What to store alongside embeddings?
   - Proposed: source, date, channel, title, url, chunk_index

3. **Update frequency:** How often to re-embed?
   - Recommendation: On-demand for new content, weekly digest runs

4. **Cross-project access:** How do other repos consume this?
   - Options: Symlink, Python package, MCP server, REST API

---

## 12. Next Steps

1. **Confirm architecture** with user
2. **Create repository** with basic structure
3. **Migrate transcripts** from second_brain
4. **Build ingestion pipeline**
5. **Implement search CLI**
6. **Add discovery features**

---

## 13. Appendix: Sample Commands

### Ollama Embeddings
```bash
# Install model
ollama pull nomic-embed-text

# Generate embeddings (API call)
curl http://localhost:11434/api/embed -d '{
  "model": "nomic-embed-text",
  "input": ["Why is the sky blue?"]
}'
```

### LanceDB Python
```python
import lancedb

# Connect to database
db = lancedb.connect("data/processed/lancedb")

# Create table with embeddings
table = db.create_table("transcripts", data)

# Search
results = table.search("Claude Code workflows").limit(10).to_pandas()

# Hybrid search
results = (
    table.search("hooks", query_type="hybrid")
    .vector_search_weight(0.7)
    .limit(10)
    .to_pandas()
)
```

---

## 14. References

- [LanceDB Documentation](https://lancedb.com/docs)
- [Ollama Embeddings API](https://github.com/ollama/ollama)
- [ChromaDB](https://docs.trychroma.com/) (alternative)
- [nomic-embed-text](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
