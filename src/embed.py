"""
Embedding utilities for the knowledge base.

Provides a simple interface to get embeddings for search queries.
Uses the same Ollama model configured in the schema.
"""

from typing import List

from . import config


def get_embedding(text: str) -> List[float]:
    """
    Get embedding vector for a text string.
    
    Uses Ollama's embedding API directly for query-time embedding.
    This is separate from LanceDB's automatic embedding for ingestion.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector as list of floats
    """
    import httpx
    
    response = httpx.post(
        f"{config.OLLAMA_BASE_URL}/api/embed",
        json={"model": config.EMBEDDING_MODEL, "input": text},
        timeout=30.0,
    )
    response.raise_for_status()
    
    data = response.json()
    # Ollama returns {"embeddings": [[...vectors...]]} for /api/embed
    if "embeddings" in data:
        return data["embeddings"][0]
    # Fallback for older API: {"embedding": [...]}
    return data.get("embedding", [])


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for multiple texts in one call.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    import httpx
    
    response = httpx.post(
        f"{config.OLLAMA_BASE_URL}/api/embed",
        json={"model": config.EMBEDDING_MODEL, "input": texts},
        timeout=60.0,
    )
    response.raise_for_status()
    
    data = response.json()
    return data.get("embeddings", [])
