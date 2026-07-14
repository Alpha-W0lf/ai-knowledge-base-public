"""
Discovery features - explore the knowledge base without specific queries.
"""

import random
from collections import Counter
from datetime import datetime, timedelta

import click
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import config
from .ingest import get_db, table_exists

console = Console()


def get_all_documents() -> pd.DataFrame:
    """Load all documents from the database."""
    db = get_db()
    
    if not table_exists(db, "transcripts"):
        return pd.DataFrame()
    
    table = db.open_table("transcripts")
    return table.to_pandas()


def random_explore(n: int = 5) -> pd.DataFrame:
    """
    Get random document chunks for serendipitous discovery.
    
    Weighted toward more recent content.
    """
    df = get_all_documents()
    if df.empty:
        return df
    
    # Weight by recency
    df = df.copy()
    df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
    df["weight"] = 1.0
    
    # More recent = higher weight
    now = pd.Timestamp.now()
    df.loc[df["date_parsed"].notna(), "weight"] = (
        1 + (30 - (now - df["date_parsed"]).dt.days.clip(0, 30)) / 30
    )
    
    # Sample with weights
    if len(df) <= n:
        return df
    
    indices = random.choices(range(len(df)), weights=df["weight"], k=n)
    return df.iloc[indices]


def get_recent_digest(days: int = 7) -> dict:
    """
    Generate a digest of content from the past N days.
    
    Returns dict with:
    - channels: content per channel
    - top_topics: frequently mentioned terms
    - count: total documents
    """
    df = get_all_documents()
    if df.empty:
        return {"channels": {}, "count": 0}
    
    # Filter to recent
    df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
    cutoff = datetime.now() - timedelta(days=days)
    recent = df[df["date_parsed"] >= cutoff]
    
    # Group by channel
    channels = {}
    for channel in recent["channel"].unique():
        channel_docs = recent[recent["channel"] == channel]
        titles = channel_docs.drop_duplicates("doc_id")["title"].tolist()
        channels[channel] = titles
    
    return {
        "channels": channels,
        "count": recent["doc_id"].nunique(),
        "total_chunks": len(recent),
    }


def extract_concepts(top_n: int = 50) -> list[tuple[str, int]]:
    """
    Extract commonly mentioned concepts/terms.
    
    Simple approach: find capitalized multi-word phrases and technical terms.
    """
    df = get_all_documents()
    if df.empty:
        return []
    
    # Combine all text
    all_text = " ".join(df["text"].tolist())
    
    # Extract patterns
    import re
    
    # Technical terms and tools (capitalized words, common patterns)
    patterns = [
        r'\b(Claude Code|Claude\s+\w+)\b',
        r'\b(MCP|RAG|LLM|API|SDK|CLI)\b',
        r'\b(Cursor|Copilot|Ollama|LangChain|OpenAI|Anthropic)\b',
        r'\b(GPT-\d+|Claude\s+\d+|Gemini\s+\d+)\b',
        r'\b(agent|workflow|pipeline|embedding|vector)\b',
        r'\b(hook|plugin|extension|integration)\b',
    ]
    
    counts = Counter()
    for pattern in patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        counts.update(m.lower() if isinstance(m, str) else m[0].lower() for m in matches)
    
    return counts.most_common(top_n)


def show_clusters() -> None:
    """
    Show document clusters based on embedding similarity.
    
    Simple approach: group by channel first, then show recent topics.
    """
    df = get_all_documents()
    if df.empty:
        console.print("[yellow]No documents in knowledge base.[/yellow]")
        return
    
    console.print("[bold]Content by Channel[/bold]")
    console.print()
    
    for channel in sorted(df["channel"].unique()):
        channel_docs = df[df["channel"] == channel]
        doc_count = channel_docs["doc_id"].nunique()
        
        # Get recent titles
        titles = channel_docs.drop_duplicates("doc_id")["title"].head(5).tolist()
        
        console.print(f"[cyan]{channel}[/cyan] ({doc_count} documents)")
        for title in titles:
            console.print(f"  • {title[:60]}")
        console.print()


@click.command()
@click.argument("mode", type=click.Choice(["random", "digest", "concepts", "clusters"]))
@click.option("--n", "-n", default=5, help="Number of results")
@click.option("--since", "-s", default="7d", help="Time period for digest (e.g., 7d, 30d)")
def main(mode: str, n: int, since: str):
    """
    Discover content in the knowledge base.
    
    Modes:
    
        random    - Show random chunks for serendipitous discovery
        
        digest    - Summary of recent content
        
        concepts  - Most mentioned terms and tools
        
        clusters  - Content grouped by channel/topic
    
    Examples:
    
        python -m src.discover random
        
        python -m src.discover digest --since 14d
        
        python -m src.discover concepts --n 30
    """
    if mode == "random":
        results = random_explore(n)
        if results.empty:
            console.print("[yellow]No documents found.[/yellow]")
            return
        
        console.print("[bold]Random Discoveries[/bold]")
        console.print()
        
        for _, row in results.iterrows():
            console.print(Panel(
                f"{row['text'][:300]}...",
                title=f"{row['channel']} | {row['title'][:40]}",
                border_style="dim",
            ))
            console.print()
    
    elif mode == "digest":
        # Parse since (e.g., "7d" -> 7)
        days = int(since.replace("d", ""))
        digest = get_recent_digest(days)
        
        if not digest["channels"]:
            console.print(f"[yellow]No content from the past {days} days.[/yellow]")
            return
        
        console.print(f"[bold]Content from the past {days} days[/bold]")
        console.print(f"[dim]{digest['count']} documents, {digest['total_chunks']} chunks[/dim]")
        console.print()
        
        for channel, titles in digest["channels"].items():
            console.print(f"[cyan]{channel}[/cyan] ({len(titles)} videos)")
            for title in titles[:5]:
                console.print(f"  • {title[:60]}")
            if len(titles) > 5:
                console.print(f"  [dim]... and {len(titles) - 5} more[/dim]")
            console.print()
    
    elif mode == "concepts":
        concepts = extract_concepts(n)
        
        if not concepts:
            console.print("[yellow]No concepts extracted.[/yellow]")
            return
        
        console.print("[bold]Top Concepts & Tools Mentioned[/bold]")
        console.print()
        
        table = Table()
        table.add_column("Concept", style="cyan")
        table.add_column("Mentions", justify="right")
        
        for concept, count in concepts:
            table.add_row(concept, str(count))
        
        console.print(table)
    
    elif mode == "clusters":
        show_clusters()


if __name__ == "__main__":
    main()
