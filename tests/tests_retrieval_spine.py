"""
Targeted tests for retrieval spine (A4, C5, D4, E4, F1–F3).
"""

from __future__ import annotations

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
    table_exists,
)
from src.models import RetrievalError
from src.rerank import IdentityReranker
from src.search import retrieve


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Path:
    return tmp_path / "lancedb"


@pytest.fixture()
def fixture_db(tmp_db: Path) -> Path:
    ingest_fixtures(db_path=tmp_db, ensure_fts=True)
    return tmp_db


# --- A4 identity / hash / version ---


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
    # Corrupt one row's embedding_version via overwrite is hard; assert helper directly
    # by writing a tiny table simulation: monkeypatch pandas check path
    df = table.to_pandas()
    assert "embedding_version" in df.columns
    # Direct unit: check_embedding_version via assert on wrong value
    from src.identity import check_embedding_version

    with pytest.raises(ValueError, match="[Rr]ebuild"):
        check_embedding_version("wrong-model@1")

    # Force mismatch in DB by re-adding is complex; use assert_table after patching config
    original = config.EMBEDDING_VERSION
    try:
        config.EMBEDDING_VERSION = "other-model@999"
        with pytest.raises(ValueError, match="[Rr]ebuild"):
            assert_table_embedding_version(db)
        with pytest.raises(RetrievalError):
            retrieve("hooks", mode="vector", db_path=fixture_db, ce_enabled=False)
    finally:
        config.EMBEDDING_VERSION = original


# --- A5 schema import side effects ---


def test_schema_import_does_not_require_ollama():
    import importlib

    import src.schema as schema_mod

    importlib.reload(schema_mod)
    # Module import succeeded without calling get_transcript_schema
    assert schema_mod._transcript_schema is None


# --- C5 hybrid smoke ---


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


def test_hybrid_fails_closed_without_table(tmp_db: Path):
    with pytest.raises(RetrievalError) as ei:
        retrieve("anything", mode="hybrid", db_path=tmp_db)
    assert ei.value.code in {"empty_index", "fts_unavailable"}


def test_empty_query_errors(fixture_db: Path):
    with pytest.raises(RetrievalError, match="Empty query"):
        retrieve("  ", mode="vector", db_path=fixture_db)


# --- D4 CE degrade ---


def test_ce_forced_failure_degrades_to_fusion(fixture_db: Path):
    result = retrieve(
        "cross encoder rerank",
        mode="hybrid",
        limit=5,
        db_path=fixture_db,
        ce_enabled=True,
        force_ce_failure=True,
    )
    assert result.ranking_stage == "fusion_degraded"
    assert all(h.ranking_stage == "fusion_degraded" for h in result.hits)


def test_ce_disabled_uses_fusion_stage(fixture_db: Path):
    result = retrieve(
        "fixture provenance",
        mode="hybrid",
        limit=5,
        db_path=fixture_db,
        ce_enabled=False,
    )
    assert result.ranking_stage == "fusion"


# --- E4 MCP public allowlist ---


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

    # FastMCP registered tools on public profile
    tool_manager = getattr(mcp_mod.mcp, "_tool_manager", None) or getattr(
        mcp_mod.mcp, "tool_manager", None
    )
    if tool_manager is not None and hasattr(tool_manager, "list_tools"):
        listed = tool_manager.list_tools()
        if isinstance(listed, dict):
            registered = set(listed.keys())
        else:
            registered = {
                getattr(t, "name", t) if not isinstance(t, str) else t for t in listed
            }
        assert "add_channel" not in registered
        assert "sync_now" not in registered
        assert "search" in registered
    elif tool_manager is not None and hasattr(tool_manager, "_tools"):
        registered = set(tool_manager._tools.keys())
        assert "add_channel" not in registered
        assert "sync_now" not in registered
        assert "search" in registered


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
    assert payload.get("ranking_stage") in {"fusion", "ce", "fusion_degraded"}
    assert payload["results"]
    row = payload["results"][0]
    assert "source_id" in row
    assert "ranking_stage" in row
    assert "filepath" not in row
    assert not str(row.get("source_url", "")).startswith(str(Path.home()))


# --- F1–F3 eval stub ---


def test_fixture_eval_hit_and_groundedness(tmp_db: Path):
    from src.eval import groundedness_ok, run_fixture_eval

    assert groundedness_ok(["a"], ["a", "b"])
    assert not groundedness_ok(["z"], ["a", "b"])

    report = run_fixture_eval(tmp_db, k=5, use_ce=False)
    assert report["fusion"]["cases"] >= 5
    assert report["fusion"]["hit_at_k"] >= 0.5  # half the golden set at least
    assert report["fusion"]["groundedness_failures"] == 0
    assert report["fusion"]["latencies"]


def test_ensure_fts_raises_when_missing(tmp_db: Path):
    db = get_db(tmp_db)
    with pytest.raises(FTSIndexError):
        ensure_fts_index(db)
