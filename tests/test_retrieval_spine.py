"""
Retrieval tests: identity, hybrid search, cross-encoder fallback, MCP allowlist.

The eval harness has its own tests in test_eval_harness.py.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import pytest

from src import config
from src.identity import compute_doc_id, content_hash, resolve_source_identity
from src.ingest import (
    FTSIndexError,
    assert_table_embedding_version,
    ensure_fts_index,
    get_db,
    ingest_file,
    ingest_fixtures,
)
from src.models import RetrievalError
from src.rerank import IdentityReranker
from src.search import retrieve


class _FailingReranker:
    def rerank(self, query, candidates):
        raise RuntimeError("model failed to load")


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Path:
    return tmp_path / "lancedb"


@pytest.fixture()
def fixture_db(tmp_db: Path) -> Path:
    ingest_fixtures(db_path=tmp_db, ensure_fts=True)
    return tmp_db


# --- Identity, content hash, embedding version ---


def test_source_id_stable_under_path_move(tmp_path: Path):
    a = tmp_path / "dir_a" / "rag-hooks-01.md"
    b = tmp_path / "elsewhere" / "rag-hooks-01.md"
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    body = "stable identity body\n"
    a.write_text(body)
    b.write_text(body)

    id_a = resolve_source_identity(a, source_type="fixture", source_id="fixture:rag-hooks-01")
    id_b = resolve_source_identity(b, source_type="fixture", source_id="fixture:rag-hooks-01")
    assert id_a["source_id"] == id_b["source_id"] == "fixture:rag-hooks-01"
    assert id_a["doc_id"] == id_b["doc_id"]
    assert id_a["doc_id"] == compute_doc_id("fixture", "fixture:rag-hooks-01")


def test_content_change_flips_hash_and_replaces_chunks(tmp_db: Path, tmp_path: Path):
    f = tmp_path / "fixtures" / "transcripts" / "swap-doc.md"
    f.parent.mkdir(parents=True)
    f.write_text("version one alpha unique token\n\nmore text about version one.\n")
    n1 = ingest_file(
        f,
        get_db(tmp_db),
        source_type="fixture",
        source_id="fixture:swap-doc",
        title="Swap",
    )
    assert n1 > 0
    h1 = content_hash(f.read_text())

    f.write_text("version two beta entirely different content for replacement.\n")
    assert content_hash(f.read_text()) != h1
    n2 = ingest_file(
        f,
        get_db(tmp_db),
        skip_existing=True,
        source_type="fixture",
        source_id="fixture:swap-doc",
        title="Swap",
    )
    assert n2 > 0
    db = get_db(tmp_db)
    df = db.open_table("transcripts").to_pandas()
    rows = df[df["source_id"] == "fixture:swap-doc"]
    assert not rows.empty
    assert (rows["content_hash"] == content_hash(f.read_text())).all()
    assert "version two" in " ".join(rows["text"].tolist())
    assert "version one alpha" not in " ".join(rows["text"].tolist())


def test_embedding_version_mismatch_refuses_search(fixture_db: Path):
    db = get_db(fixture_db)
    table = db.open_table("transcripts")
    df = table.to_pandas()
    assert "embedding_version" in df.columns
    from src.identity import check_embedding_version

    with pytest.raises(ValueError, match="[Rr]ebuild"):
        check_embedding_version("wrong-model@1")

    # A runtime stamp that differs from the stored one must stop search.
    original = config.EMBEDDING_VERSION
    try:
        config.EMBEDDING_VERSION = "other-model@999"
        with pytest.raises(ValueError, match="[Rr]ebuild"):
            assert_table_embedding_version(db)
        with pytest.raises(RetrievalError):
            retrieve("hooks", mode="vector", db_path=fixture_db, ce_enabled=False)
    finally:
        config.EMBEDDING_VERSION = original


# --- Schema ---


def test_schema_has_no_embedding_function():
    """Ingest supplies vectors itself, so the schema never calls an embedder."""
    from src.schema import get_transcript_schema

    schema = get_transcript_schema().to_arrow_schema()
    assert schema.field("vector").type.list_size == config.EMBEDDING_DIMENSIONS
    assert b"embedding_functions" not in (schema.metadata or {})


# --- Search modes ---


def test_fixture_vector_and_hybrid_smoke(fixture_db: Path):
    vec = retrieve(
        "MCP allowlist",
        mode="vector",
        limit=5,
        db_path=fixture_db,
        ce_enabled=False,
    )
    assert vec.ranking_stage == "vector"
    assert len(vec.hits) >= 1

    hyb = retrieve(
        "reciprocal rank fusion RRF",
        mode="hybrid",
        limit=5,
        db_path=fixture_db,
        ce_enabled=False,
        ce_adapter=IdentityReranker(),
    )
    assert hyb.ranking_stage == "fusion"
    assert all(h.ranking_stage == "fusion" for h in hyb.hits)
    assert any(h.source_id == "fixture:fusion-rrf-04" for h in hyb.hits)


def test_keyword_mode_runs_the_full_text_leg_alone(fixture_db: Path):
    result = retrieve("reciprocal rank fusion RRF", mode="keyword", db_path=fixture_db)
    assert result.mode == result.ranking_stage == "keyword"
    assert result.hits[0].source_id == "fixture:fusion-rrf-04"
    assert all(h.ranking_stage == "keyword" for h in result.hits)
    assert "embed_ms" not in result.timings_ms


def test_hybrid_fails_closed_without_table(tmp_db: Path):
    with pytest.raises(RetrievalError) as ei:
        retrieve("anything", mode="hybrid", db_path=tmp_db)
    assert ei.value.code in {"empty_index", "fts_unavailable"}


def test_empty_query_errors(fixture_db: Path):
    with pytest.raises(RetrievalError, match="Empty query"):
        retrieve("  ", mode="vector", db_path=fixture_db)


# --- Cross-encoder fallback ---


def test_ce_forced_failure_degrades_to_fusion(fixture_db: Path):
    result = retrieve(
        "cross encoder rerank",
        mode="hybrid",
        limit=5,
        db_path=fixture_db,
        ce_enabled=True,
        ce_adapter=_FailingReranker(),
    )
    assert result.ranking_stage == "fusion_degraded"
    assert all(h.ranking_stage == "fusion_degraded" for h in result.hits)
    assert result.error is not None
    assert result.error == "RuntimeError: model failed to load"


def test_ce_identity_adapter_sets_ce_stage_without_hub(fixture_db: Path):
    from src.rerank import IdentityReranker

    result = retrieve(
        "reciprocal rank fusion RRF",
        mode="hybrid",
        limit=5,
        db_path=fixture_db,
        ce_enabled=True,
        ce_adapter=IdentityReranker(),
    )
    assert result.ranking_stage == "ce"
    assert result.error is None
    assert all(h.ranking_stage == "ce" for h in result.hits)


def test_ce_disabled_uses_fusion_stage(fixture_db: Path):
    result = retrieve(
        "fixture provenance",
        mode="hybrid",
        limit=5,
        db_path=fixture_db,
        ce_enabled=False,
    )
    assert result.ranking_stage == "fusion"
    assert result.error is None


def test_is_ce_available_matches_the_installed_extra():
    import importlib.util

    from src.rerank import is_ce_available

    assert is_ce_available() is (importlib.util.find_spec("sentence_transformers") is not None)


# --- MCP public allowlist ---


def test_mcp_public_tool_allowlist():
    # Ensure private env not set
    os.environ.pop("AI_KB_MCP_PRIVATE", None)
    import importlib

    import src.mcp_server as mcp_mod

    importlib.reload(mcp_mod)
    names = set(mcp_mod.public_tool_names())
    assert names == set(mcp_mod.PUBLIC_TOOL_ALLOWLIST)
    assert "add_channel" not in names
    assert "sync_now" not in names

    registered = {tool.name for tool in asyncio.run(mcp_mod.mcp.list_tools())}
    assert registered == set(mcp_mod.PUBLIC_TOOL_ALLOWLIST)


def test_mcp_search_returns_ranking_stage_fields(fixture_db: Path, monkeypatch):
    monkeypatch.setattr(config, "LANCEDB_DIR", fixture_db)
    monkeypatch.setattr(config, "CE_ENABLED", False)
    os.environ.pop("AI_KB_MCP_PRIVATE", None)
    import importlib

    import src.mcp_server as mcp_mod

    importlib.reload(mcp_mod)
    # Point retrieve at fixture db via config LANCEDB_DIR
    payload = json.loads(mcp_mod.search("RRF fusion", limit=5, hybrid=True))
    assert not payload.get("error"), payload
    assert payload["ranking_stage"] == "fusion"
    assert payload["results"]
    row = payload["results"][0]
    assert "source_id" in row
    assert "ranking_stage" in row
    assert "filepath" not in row
    assert not str(row.get("source_url", "")).startswith(str(Path.home()))


def test_ensure_fts_raises_when_missing(tmp_db: Path):
    db = get_db(tmp_db)
    with pytest.raises(FTSIndexError):
        ensure_fts_index(db)


@pytest.mark.parametrize(
    ("env", "installed", "expected"),
    [("", True, True), ("", False, False), ("0", True, False), ("1", False, True)],
)
def test_cross_encoder_is_the_default_when_installed(monkeypatch, env, installed, expected):
    import importlib
    import importlib.util

    real_find_spec = importlib.util.find_spec
    monkeypatch.setenv("AI_KB_CE", env)
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        lambda name, *a: (object() if installed else None)
        if name == "sentence_transformers"
        else real_find_spec(name, *a),
    )
    try:
        assert importlib.reload(config).CE_ENABLED is expected
    finally:
        monkeypatch.undo()
        importlib.reload(config)
