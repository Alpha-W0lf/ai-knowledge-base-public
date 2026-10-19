"""
Search is read-only: hybrid retrieve() must not write to the LanceDB directory.

Runs without Ollama: the table is built directly with tiny vectors and the
query embedder is stubbed. The FTS index is built the ingest way (ensure_fts_index).
"""

from __future__ import annotations

from pathlib import Path

import lancedb
import pytest

from src import config
from src import search as search_mod
from src.ingest import ensure_fts_index, has_fts_index, ingest_directory, source_content_hash
from src.models import RetrievalError
from src.search import retrieve

DIM = 4


def _rows(version: str) -> list[dict]:
    topics = [
        "reciprocal rank fusion merges vector and keyword legs",
        "cross encoder reranks the fused shortlist",
        "mcp public tools are read only",
        "fixture provenance lives in the manifest",
        "embedding version mismatch refuses search",
        "chunking splits transcripts with overlap",
    ]
    rows = []
    for i, text in enumerate(topics):
        sid = f"fixture:doc-{i}"
        rows.append(
            {
                "id": f"doc{i}_0",
                "doc_id": f"doc{i}",
                "chunk_index": 0,
                "source_id": sid,
                "source_type": "fixture",
                "content_hash": f"hash-{i}",
                "embedding_version": version,
                "text": text,
                "vector": [float(i == j) for j in range(DIM)],
                "channel": "fixtures",
                "title": f"Doc {i}",
                "date": "",
                "source": "fixture",
                "filepath": "",
                "source_url": sid,
            }
        )
    return rows


def _make_db(
    db_path: Path, *, version: str | None = None, fts: bool = True
) -> lancedb.DBConnection:
    db = lancedb.connect(str(db_path))
    db.create_table("transcripts", _rows(version or config.EMBEDDING_VERSION))
    if fts:
        ensure_fts_index(db)  # ingest-side build
    return db


@pytest.fixture(autouse=True)
def stub_embedder(monkeypatch):
    monkeypatch.setattr(search_mod, "get_embedding", lambda _q: [1.0, 0.0, 0.0, 0.0])


def _snapshot(root: Path) -> dict[str, tuple[int, int]]:
    return {
        str(p.relative_to(root)): (p.stat().st_mtime_ns, p.stat().st_size) for p in root.rglob("*")
    }


def test_hybrid_search_writes_nothing(tmp_path: Path):
    db_path = tmp_path / "lancedb"
    db = _make_db(db_path)
    version_before = db.open_table("transcripts").version
    files_before = _snapshot(db_path)

    for _ in range(10):
        result = retrieve("rank fusion", mode="hybrid", db_path=db_path, ce_enabled=False)
        assert result.ranking_stage == "fusion"
        assert result.hits
        assert any("fts_rank" in h.retriever_scores for h in result.hits)

    assert db.open_table("transcripts").version == version_before
    assert _snapshot(db_path) == files_before


@pytest.mark.parametrize("mode", ["hybrid", "keyword"])
def test_full_text_modes_fail_closed_when_fts_index_missing(tmp_path: Path, mode: str):
    db_path = tmp_path / "lancedb"
    db = _make_db(db_path, fts=False)
    files_before = _snapshot(db_path)

    with pytest.raises(RetrievalError) as ei:
        retrieve("rank fusion", mode=mode, db_path=db_path, ce_enabled=False)
    assert ei.value.code == "fts_unavailable"
    assert db.open_table("transcripts").list_indices() == []
    assert _snapshot(db_path) == files_before


def test_search_on_missing_db_does_not_create_it(tmp_path: Path):
    db_path = tmp_path / "lancedb"
    with pytest.raises(RetrievalError) as ei:
        retrieve("anything", mode="hybrid", db_path=db_path)
    assert ei.value.code == "empty_index"
    assert not db_path.exists()


def test_embedding_version_mismatch_refuses_search(tmp_path: Path):
    db_path = tmp_path / "lancedb"
    _make_db(db_path, version="other-model@999")
    for mode in ("vector", "hybrid"):
        with pytest.raises(RetrievalError, match="[Rr]ebuild") as ei:
            retrieve("rank fusion", mode=mode, db_path=db_path, ce_enabled=False)
        assert ei.value.code == "embedding_version_mismatch"


def test_source_content_hash_filters_by_source_id(tmp_path: Path):
    db = _make_db(tmp_path / "lancedb", fts=False)
    assert source_content_hash(db, "fixture:doc-3") == "hash-3"
    assert source_content_hash(db, "fixture:missing") is None
    assert source_content_hash(db, "it's-not-there") is None


# --- every ingest writer leaves the index that search requires ---


def test_ingest_directory_builds_missing_index_without_new_files(tmp_path: Path):
    db_path = tmp_path / "lancedb"
    db = _make_db(db_path, fts=False)
    empty_dir = tmp_path / "raw"
    empty_dir.mkdir()

    ingest_directory(empty_dir, db_path=db_path)

    assert has_fts_index(db.open_table("transcripts"))


def test_sync_channel_builds_index_after_new_chunks(tmp_path: Path, monkeypatch):
    from src import youtube_sync

    db = _make_db(tmp_path / "lancedb", fts=False)
    monkeypatch.setattr(youtube_sync.config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(youtube_sync.config, "TRANSCRIPTS_DIR", tmp_path / "transcripts")
    monkeypatch.setattr(
        youtube_sync,
        "list_channel_videos",
        lambda *a, **k: [{"id": "vid1", "title": "New", "date": "20260101"}],
    )

    def fake_download(vid_id: str, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        md = output_dir / f"{vid_id}.md"
        md.write_text("new transcript", encoding="utf-8")
        return md

    monkeypatch.setattr(youtube_sync, "download_transcript", fake_download)
    monkeypatch.setattr(youtube_sync, "ingest_file", lambda *a, **k: 1)
    monkeypatch.setattr(youtube_sync, "get_db", lambda: db)

    stats = youtube_sync.sync_channel("@chan", youtube_sync.SyncState(), force=True)

    assert stats["new"] == 1
    assert has_fts_index(db.open_table("transcripts"))


def test_status_and_discover_never_create_the_data_dir(tmp_path: Path, monkeypatch):
    """The public read tools report an empty index instead of creating data/lancedb."""
    import json

    import src.mcp_server as mcp_mod

    missing = tmp_path / "lancedb"
    monkeypatch.setattr(config, "LANCEDB_DIR", missing)
    status = json.loads(mcp_mod.get_status())
    assert status["indexed"]["chunks"] == 0
    assert "Knowledge base empty" in json.loads(mcp_mod.discover(mode="random"))["error"]
    assert not missing.exists()
