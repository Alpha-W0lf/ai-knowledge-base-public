"""
Offline embedder: ingest and hybrid search run with no Ollama and no network.
"""

from __future__ import annotations

import math
from pathlib import Path

import httpx
import pytest

from src import config
from src.embed import get_embeddings_batch, stub_embedding
from src.ingest import get_db, ingest_fixtures
from src.models import RetrievalError
from src.search import retrieve

# These tests pin the offline stub itself; CI and the default `pytest` always run them.
pytestmark = pytest.mark.skipif(config.EMBEDDINGS != "stub", reason="stub embedder tests")


@pytest.fixture()
def no_network(monkeypatch):
    def refuse(*_a, **_k):
        raise AssertionError("embedder tried to reach Ollama over the network")

    monkeypatch.setattr(httpx, "post", refuse)
    monkeypatch.setattr(httpx, "get", refuse)


def test_tests_run_on_the_stub_embedder():
    assert config.EMBEDDINGS == "stub"
    assert config.EMBEDDING_VERSION == "stub-hash@768"


def test_stub_embedding_is_deterministic_and_normalised():
    a = stub_embedding("reciprocal rank fusion merges ranked lists")
    b = stub_embedding("reciprocal rank fusion merges ranked lists")
    assert a == b
    assert len(a) == config.EMBEDDING_DIMENSIONS
    assert math.isclose(math.sqrt(sum(v * v for v in a)), 1.0, rel_tol=1e-9)


def test_stub_embedding_ranks_shared_words_closer():
    q = stub_embedding("rank fusion of ranked lists")
    near = stub_embedding("fusion merges two ranked lists by rank")
    far = stub_embedding("transport authentication for remote servers")
    dot = lambda x, y: sum(i * j for i, j in zip(x, y))  # noqa: E731
    assert dot(q, near) > dot(q, far)


def test_ingest_and_hybrid_search_run_offline(tmp_path: Path, no_network):
    db_path = tmp_path / "lancedb"
    stats = ingest_fixtures(db_path=db_path, ensure_fts=True)
    assert stats["chunks"] >= 8

    rows = get_db(db_path).open_table("transcripts").to_pandas()
    assert set(rows["embedding_version"]) == {"stub-hash@768"}

    result = retrieve("reciprocal rank fusion RRF", mode="hybrid", db_path=db_path)
    assert result.ranking_stage == "fusion"
    assert result.hits[0].source_id == "fixture:fusion-rrf-04"


def test_index_from_one_embedder_is_refused_by_another(tmp_path: Path, monkeypatch, no_network):
    db_path = tmp_path / "lancedb"
    ingest_fixtures(db_path=db_path, ensure_fts=True)
    monkeypatch.setattr(config, "EMBEDDING_VERSION", "nomic-embed-text@768")
    with pytest.raises(RetrievalError) as ei:
        retrieve("rank fusion", mode="hybrid", db_path=db_path)
    assert ei.value.code == "embedding_version_mismatch"


def test_batch_matches_single(no_network):
    texts = ["cross encoder rerank", "mcp allowlist"]
    assert get_embeddings_batch(texts) == [stub_embedding(t) for t in texts]
