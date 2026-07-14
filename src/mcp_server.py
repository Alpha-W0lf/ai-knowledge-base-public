"""
MCP Server for AI Knowledge Base.

Public/default profile is read-only allowlist (KB2):
  search, discover, get_status, get_context (shared retrieve only).

Mutation tools (add_channel, sync_now) register only when
AI_KB_MCP_PRIVATE=1 (non-default private profile).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .models import RetrievalError

# Initialize MCP server
mcp = FastMCP("AI Knowledge Base")

PUBLIC_TOOL_ALLOWLIST = frozenset({"search", "discover", "get_status", "get_context"})
PRIVATE_MUTATION_TOOLS = frozenset({"add_channel", "sync_now"})


def private_profile_enabled() -> bool:
    """Non-default private profile — mutation tools only when explicitly enabled."""
    return os.environ.get("AI_KB_MCP_PRIVATE", "").strip() in {"1", "true", "TRUE", "yes"}


def check_ollama() -> tuple[bool, str]:
    """Check if Ollama is running and accessible."""
    try:
        import httpx

        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        return response.status_code == 200, "Ollama is running"
    except Exception as e:
        return False, f"Ollama not accessible: {e}. Start Ollama first."


def get_db():
    """Get LanceDB connection (status/discover only — search uses shared retrieve)."""
    from . import config
    import lancedb

    config.LANCEDB_DIR.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(str(config.LANCEDB_DIR))


def table_exists(db, table_name: str) -> bool:
    """Check if a table exists in the database."""
    tables = db.list_tables()
    return table_name in tables.tables


def public_tool_names() -> list[str]:
    """Tool names registered on the public/default profile."""
    names = list(PUBLIC_TOOL_ALLOWLIST)
    if private_profile_enabled():
        names.extend(sorted(PRIVATE_MUTATION_TOOLS))
    return sorted(names)


@mcp.tool()
def search(query: str, limit: int = 5, hybrid: bool = True) -> str:
    """
    Search the AI knowledge base for relevant content.

    Uses the shared retrieval spine (hybrid → fusion → optional CE).
    Public results cite source_id / source_url — never absolute filepath.
    """
    ok, msg = check_ollama()
    if not ok:
        return json.dumps({"error": msg})

    try:
        from .search import retrieve

        result = retrieve(
            query,
            mode="hybrid" if hybrid else "vector",
            limit=limit,
            ce_enabled=None if hybrid else False,
        )
        return json.dumps(result.to_public_dict(), indent=2)
    except RetrievalError as e:
        return json.dumps({"error": e.message, "code": e.code})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def discover(mode: str = "digest", days: int = 7, limit: int = 5) -> str:
    """
    Discover AI content without a specific query (honest browse/digest/heuristics).

    Modes: random, digest, concepts, channels — not a ranking product.
    """
    try:
        db = get_db()
        if not table_exists(db, "transcripts"):
            return json.dumps({"error": "Knowledge base empty. Run ingestion first."})

        table = db.open_table("transcripts")
        df = table.to_pandas()

        if mode == "random":
            sample = df.sample(n=min(limit, len(df)))
            items = []
            for _, row in sample.iterrows():
                text = row["text"]
                items.append(
                    {
                        "text": text[:500] + "..." if len(text) > 500 else text,
                        "channel": row["channel"],
                        "title": row["title"],
                        "source_id": row.get("source_id", ""),
                    }
                )
            return json.dumps({"mode": "random", "items": items})

        if mode == "digest":
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()[:10]
            recent = (
                df[df["date"] >= cutoff]
                if "date" in df.columns and df["date"].notna().any()
                else df
            )

            channels_content: dict[str, set] = {}
            for _, row in recent.iterrows():
                ch = row["channel"]
                channels_content.setdefault(ch, set()).add(row["title"])

            summary = [
                {"channel": ch, "recent_videos": list(titles)[:5]}
                for ch, titles in channels_content.items()
            ]
            return json.dumps(
                {"mode": "digest", "period_days": days, "channels": summary},
                indent=2,
            )

        if mode == "concepts":
            import re
            from collections import Counter

            patterns = [
                r"\b(Claude Code|Cursor|Copilot|ChatGPT|GPT-4|GPT-5)\b",
                r"\b(LangChain|LangGraph|LlamaIndex|CrewAI)\b",
                r"\b(RAG|MCP|vector|embedding|agent|prompt)\b",
                r"\b(Ollama|vLLM|Hugging Face|OpenAI|Anthropic)\b",
            ]
            all_text = " ".join(df["text"].tolist())
            mentions = Counter()
            for pattern in patterns:
                for match in re.findall(pattern, all_text, re.IGNORECASE):
                    mentions[match.lower()] += 1
            top_concepts = mentions.most_common(limit)
            return json.dumps(
                {
                    "mode": "concepts",
                    "top_mentions": [{"concept": c, "count": n} for c, n in top_concepts],
                }
            )

        if mode == "channels":
            if "doc_id" in df.columns:
                channel_stats = (
                    df.groupby("channel")
                    .agg(videos=("doc_id", "nunique"), chunks=("text", "count"))
                    .reset_index()
                )
            else:
                channel_stats = (
                    df.groupby("channel").agg(chunks=("text", "count")).reset_index()
                )
            return json.dumps(
                {"mode": "channels", "channels": channel_stats.to_dict(orient="records")},
                indent=2,
            )

        return json.dumps(
            {"error": f"Unknown mode: {mode}. Use random, digest, concepts, or channels."}
        )

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_context(query: str, include_recent: bool = True) -> str:
    """
    Get comprehensive context via shared retrieval (+ optional recent digest).
    """
    ok, msg = check_ollama()
    if not ok:
        return json.dumps({"error": msg})

    try:
        from .search import retrieve

        result = retrieve(query, mode="hybrid", limit=5)
        payload = {
            "query": query,
            "ranking_stage": result.ranking_stage,
            "search_results": [h.to_public_dict() for h in result.hits],
            "timings_ms": result.timings_ms,
        }
        if include_recent:
            digest = json.loads(discover(mode="digest", days=7))
            payload["recent_activity"] = digest.get("channels", [])
        return json.dumps(payload, indent=2)
    except RetrievalError as e:
        return json.dumps({"error": e.message, "code": e.code})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_status() -> str:
    """
    Get current status of the AI knowledge base.

    Does not require embedding / Ollama for index stats (Ollama health is reported).
    """
    try:
        from . import config

        db = get_db()

        status = {
            "ollama": check_ollama()[0],
            "mcp_profile": "private" if private_profile_enabled() else "public",
            "public_tools": sorted(PUBLIC_TOOL_ALLOWLIST),
            "tracked_channels": len(config.YOUTUBE_CHANNELS),
            "embedding_version": config.EMBEDDING_VERSION,
        }

        if table_exists(db, "transcripts"):
            table = db.open_table("transcripts")
            df = table.to_pandas()
            status["indexed"] = {
                "documents": int(df["doc_id"].nunique()) if "doc_id" in df.columns else 0,
                "chunks": len(df),
                "channels_with_content": int(df["channel"].nunique())
                if "channel" in df.columns
                else 0,
            }
        else:
            status["indexed"] = {
                "documents": 0,
                "chunks": 0,
                "channels_with_content": 0,
            }

        transcript_dir = config.TRANSCRIPTS_DIR
        if transcript_dir.exists():
            status["transcript_files"] = len(list(transcript_dir.glob("**/*.md")))

        fixture_dir = config.FIXTURES_TRANSCRIPTS_DIR
        if fixture_dir.exists():
            status["fixture_files"] = len(list(fixture_dir.glob("*.md")))

        return json.dumps(status, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


def _register_private_tools() -> None:
    """Register mutation tools only for explicit private profile."""

    @mcp.tool()
    def add_channel(handle: str, description: str = "") -> str:
        """
        [PRIVATE PROFILE] Add a YouTube channel to track (runtime only).
        """
        from . import config

        if not handle.startswith("@"):
            handle = f"@{handle}"
        existing = [ch[0] for ch in config.YOUTUBE_CHANNELS]
        if handle in existing:
            return json.dumps(
                {"status": "exists", "message": f"{handle} is already being tracked"}
            )
        config.YOUTUBE_CHANNELS.append((handle, description))
        return json.dumps(
            {
                "status": "added",
                "channel": handle,
                "description": description,
                "message": f"Added {handle}. Run sync_now() to fetch transcripts.",
                "note": (
                    "Runtime only — to persist, add to ignored "
                    "channels.local.json (see channels.local.example.json)"
                ),
            }
        )

    @mcp.tool()
    def sync_now(channel: Optional[str] = None) -> str:
        """
        [PRIVATE PROFILE] Trigger YouTube transcript sync immediately.
        """
        ok, msg = check_ollama()
        if not ok:
            return json.dumps({"error": msg})
        try:
            from .youtube_sync import SyncState, sync_all, sync_channel

            if channel:
                state = SyncState()
                stats = sync_channel(channel, state, force=False)
            else:
                stats = sync_all()
            return json.dumps({"sync_stats": stats, "status": "complete"}, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})


if private_profile_enabled():
    _register_private_tools()


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
