"""
Discovery features - explore the knowledge base without specific queries.

Shared implementation used by both CLI and MCP server.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

import click
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .ingest import get_db, table_exists

console = Console()


def get_all_documents(db: Any | None = None) -> pd.DataFrame:
    """Load all documents from the database."""
    if db is None:
        db = get_db()

    if not table_exists(db, "transcripts"):
        return pd.DataFrame()

    table = db.open_table("transcripts")
    return table.to_pandas()


def run_discover(
    mode: str = "digest",
    days: int = 7,
    limit: int = 5,
    db: Any | None = None,
) -> dict:
    """
    Shared discovery logic for CLI and MCP server (honest browse / digest / heuristics).

    Modes:
      - random: sample of document chunks (honors limit)
      - digest: recent content grouped by channel (honors days, limit)
      - concepts: top mentioned entities and terms (honors limit)
      - channels (or clusters): stats on indexed channels and document/chunk counts
    """
    if db is None:
        db = get_db()

    if not table_exists(db, "transcripts"):
        return {"error": "Knowledge base empty. Run ingestion first."}

    table = db.open_table("transcripts")
    df = table.to_pandas()

    if df.empty:
        if mode == "random":
            return {"mode": "random", "items": []}
        if mode == "digest":
            return {"mode": "digest", "period_days": days, "channels": []}
        if mode == "concepts":
            return {"mode": "concepts", "top_mentions": []}
        if mode in {"channels", "clusters"}:
            return {"mode": "channels", "channels": []}

    if mode == "random":
        n_sample = min(limit, len(df))
        sample = df.sample(n=n_sample)
        items = []
        for _, row in sample.iterrows():
            text = str(row.get("text", ""))
            items.append(
                {
                    "text": text[:500] + "..." if len(text) > 500 else text,
                    "channel": row.get("channel", ""),
                    "title": row.get("title", ""),
                    "source_id": row.get("source_id", ""),
                }
            )
        return {"mode": "random", "items": items}

    if mode == "digest":
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()[:10]
        recent = (
            df[df["date"] >= cutoff] if "date" in df.columns and df["date"].notna().any() else df
        )

        channels_content: dict[str, list[str]] = {}
        for _, row in recent.iterrows():
            ch = str(row.get("channel", ""))
            title = str(row.get("title", ""))
            if ch not in channels_content:
                channels_content[ch] = []
            if title not in channels_content[ch]:
                channels_content[ch].append(title)

        summary = [
            {"channel": ch, "recent_videos": titles[:limit]}
            for ch, titles in channels_content.items()
        ]
        return {
            "mode": "digest",
            "period_days": days,
            "channels": summary,
        }

    if mode == "concepts":
        patterns = [
            r"\b(Claude Code|Cursor|Copilot|ChatGPT|GPT-4|GPT-5)\b",
            r"\b(LangChain|LangGraph|LlamaIndex|CrewAI)\b",
            r"\b(RAG|MCP|vector|embedding|agent|prompt)\b",
            r"\b(Ollama|vLLM|Hugging Face|OpenAI|Anthropic)\b",
        ]
        all_text = " ".join(df["text"].astype(str).tolist())
        mentions: Counter[str] = Counter()
        for pattern in patterns:
            for match in re.findall(pattern, all_text, re.IGNORECASE):
                mentions[match.lower()] += 1
        top_concepts = mentions.most_common(limit)
        return {
            "mode": "concepts",
            "top_mentions": [{"concept": c, "count": n} for c, n in top_concepts],
        }

    if mode in {"channels", "clusters"}:
        if "doc_id" in df.columns:
            channel_stats = (
                df.groupby("channel")
                .agg(videos=("doc_id", "nunique"), chunks=("text", "count"))
                .reset_index()
            )
        else:
            channel_stats = df.groupby("channel").agg(chunks=("text", "count")).reset_index()
        return {
            "mode": "channels",
            "channels": channel_stats.to_dict(orient="records"),
        }

    return {"error": f"Unknown mode: {mode}. Use random, digest, concepts, or channels."}


# Canonical alias so callers can do `from src.discover import discover`
discover = run_discover


def random_explore(n: int = 5) -> pd.DataFrame:
    """Helper for CLI: get random document chunks."""
    df = get_all_documents()
    if df.empty or len(df) <= n:
        return df
    return df.sample(n=min(n, len(df)))


def get_recent_digest(days: int = 7) -> dict:
    """Helper for backwards compatibility: generate digest."""
    res = run_discover("digest", days=days)
    channels_map = {item["channel"]: item["recent_videos"] for item in res.get("channels", [])}
    df = get_all_documents()
    return {
        "channels": channels_map,
        "count": len(channels_map),
        "total_chunks": len(df),
    }


def extract_concepts(top_n: int = 50) -> list[tuple[str, int]]:
    """Helper for backwards compatibility: extract concepts."""
    res = run_discover("concepts", limit=top_n)
    return [(item["concept"], item["count"]) for item in res.get("top_mentions", [])]


def show_clusters() -> None:
    """CLI output: show document clusters/channels."""
    res = run_discover("channels")
    if "error" in res:
        console.print(f"[yellow]{res['error']}[/yellow]")
        return
    channels = res.get("channels", [])
    if not channels:
        console.print("[yellow]No documents in knowledge base.[/yellow]")
        return

    console.print("[bold]Content by Channel[/bold]\n")
    for ch in channels:
        name = ch.get("channel", "Unknown")
        videos = ch.get("videos", 0)
        chunks = ch.get("chunks", 0)
        console.print(f"[cyan]{name}[/cyan] ({videos} videos, {chunks} chunks)")
    console.print()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("mode", type=click.Choice(["random", "digest", "concepts", "clusters", "channels"]))
@click.option("--n", "--limit", "-n", "limit", default=5, help="Number of results")
@click.option("--since", "-s", default="7d", help="Time period for digest (e.g., 7d, 30d)")
def main(mode: str, limit: int, since: str):
    """Discover content in the knowledge base without a specific query."""
    if mode == "random":
        res = run_discover("random", limit=limit)
        if "error" in res:
            console.print(f"[yellow]{res['error']}[/yellow]")
            return
        items = res.get("items", [])
        if not items:
            console.print("[yellow]No documents found.[/yellow]")
            return

        console.print("[bold]Random Discoveries[/bold]\n")
        for item in items:
            console.print(
                Panel(
                    item["text"],
                    title=f"{item['channel']} | {item['title'][:40]}",
                    border_style="dim",
                )
            )
            console.print()

    elif mode == "digest":
        days = int(since.replace("d", ""))
        res = run_discover("digest", days=days, limit=limit)
        if "error" in res:
            console.print(f"[yellow]{res['error']}[/yellow]")
            return
        channels = res.get("channels", [])
        if not channels:
            console.print(f"[yellow]No content from the past {days} days.[/yellow]")
            return

        console.print(f"[bold]Content from the past {days} days[/bold]\n")
        for ch in channels:
            console.print(f"[cyan]{ch['channel']}[/cyan] ({len(ch['recent_videos'])} videos)")
            for title in ch["recent_videos"]:
                console.print(f"  • {title[:60]}")
            console.print()

    elif mode == "concepts":
        res = run_discover("concepts", limit=limit)
        if "error" in res:
            console.print(f"[yellow]{res['error']}[/yellow]")
            return
        mentions = res.get("top_mentions", [])
        if not mentions:
            console.print("[yellow]No concepts extracted.[/yellow]")
            return

        console.print("[bold]Top Concepts & Tools Mentioned[/bold]\n")
        table = Table()
        table.add_column("Concept", style="cyan")
        table.add_column("Mentions", justify="right")
        for m in mentions:
            table.add_row(m["concept"], str(m["count"]))
        console.print(table)

    elif mode in {"clusters", "channels"}:
        show_clusters()


if __name__ == "__main__":
    main()
