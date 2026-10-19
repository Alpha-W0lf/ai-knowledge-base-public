"""
Embeddings for ingest and query: one code path for both.

config.EMBEDDINGS picks the embedder:
- "ollama" (default): nomic-embed-text through Ollama's /api/embed.
- "stub": a deterministic hashing embedder. It runs offline, so CI can exercise
  ingest, search and the eval without Ollama. It is a bag of words and character
  trigrams, not a semantic model: results measured with it describe the pipeline,
  not nomic-embed-text.
"""

from __future__ import annotations

import hashlib
import math
import re

from . import config

_TOKEN = re.compile(r"[a-z0-9]+")
# Small fixed English stopword list so function words do not dominate stub vectors.
_STOPWORDS = frozenset(
    "a an and are as at be by can do does for from has have how i if in into is it its "
    "not of on or so than that the then there these this to was we what when which "
    "while who why will with without you your".split()
)


def _bucket(feature: str, dims: int) -> tuple[int, float]:
    digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
    value = int.from_bytes(digest, "little")
    return value % dims, (1.0 if (value >> 63) & 1 else -1.0)


def stub_embedding(text: str, dims: int | None = None) -> list[float]:
    """Deterministic L2-normalised hashing embedding (words + in-word trigrams)."""
    dims = dims or config.EMBEDDING_DIMENSIONS
    counts: dict[str, float] = {}
    for word in _TOKEN.findall(text.lower()):
        if word in _STOPWORDS:
            continue
        counts["w:" + word] = counts.get("w:" + word, 0.0) + 1.0
        padded = f"#{word}#"
        for i in range(len(padded) - 2):
            gram = "c:" + padded[i : i + 3]
            counts[gram] = counts.get(gram, 0.0) + 0.25
    vec = [0.0] * dims
    for feature, count in counts.items():
        idx, sign = _bucket(feature, dims)
        vec[idx] += sign * (1.0 + math.log(count)) if count >= 1 else sign * count
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm > 0 else vec


def _ollama_embed(inputs: str | list[str], timeout: float) -> list[list[float]]:
    import httpx

    response = httpx.post(
        f"{config.OLLAMA_BASE_URL}/api/embed",
        json={"model": config.EMBEDDING_MODEL, "input": inputs},
        timeout=timeout,
    )
    response.raise_for_status()
    embeddings = response.json().get("embeddings")
    expected = 1 if isinstance(inputs, str) else len(inputs)
    if not isinstance(embeddings, list) or len(embeddings) != expected:
        raise RuntimeError(
            f"Ollama /api/embed returned {0 if not embeddings else len(embeddings)} "
            f"vectors for {expected} inputs (model {config.EMBEDDING_MODEL})."
        )
    return embeddings


def get_embedding(text: str) -> list[float]:
    """Embed one query string with the configured embedder."""
    if config.EMBEDDINGS == "stub":
        return stub_embedding(text)
    return _ollama_embed(text, timeout=30.0)[0]


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Embed many chunks with the configured embedder (ingest path)."""
    if not texts:
        return []
    if config.EMBEDDINGS == "stub":
        return [stub_embedding(t) for t in texts]
    return _ollama_embed(list(texts), timeout=120.0)
