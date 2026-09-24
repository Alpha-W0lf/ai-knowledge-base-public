"""
Tests for shared discover implementation (JH-64.7).

Verifies that CLI and MCP share the exact same discover.py logic.
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd
import pytest

import src.mcp_server as mcp_mod
from src.discover import run_discover


def test_run_discover_empty_database():
    mock_db = MagicMock()
    # table_exists returns False
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.discover.table_exists", lambda db, name: False)
        result = run_discover("random", db=mock_db)
        assert "error" in result
        assert "Knowledge base empty" in result["error"]


def test_run_discover_modes_with_dataframe(monkeypatch):
    today_str = datetime.now().strftime("%Y-%m-%d")
    df_data = pd.DataFrame(
        [
            {
                "id": "1_0",
                "doc_id": "doc1",
                "source_id": "fixture:fusion-rrf-04",
                "title": "Rank fusion with reciprocal rank fusion",
                "channel": "fixtures",
                "date": today_str,
                "text": "RRF combines rankings from vector ANN and BM25 full-text search.",
            },
            {
                "id": "2_0",
                "doc_id": "doc2",
                "source_id": "fixture:cross-encoder-05",
                "title": "Cross encoder reranking",
                "channel": "fixtures",
                "date": today_str,
                "text": "Cross-encoders score query and document pairs directly with Hugging Face.",
            },
        ]
    )

    mock_table = MagicMock()
    mock_table.to_pandas.return_value = df_data
    mock_db = MagicMock()
    mock_db.open_table.return_value = mock_table

    monkeypatch.setattr("src.discover.table_exists", lambda db, name: True)

    # 1. random
    res_rand = run_discover("random", limit=1, db=mock_db)
    assert res_rand["mode"] == "random"
    assert len(res_rand["items"]) == 1
    assert "source_id" in res_rand["items"][0]

    # 2. digest
    res_digest = run_discover("digest", days=30, limit=5, db=mock_db)
    assert res_digest["mode"] == "digest"
    assert "channels" in res_digest
    assert len(res_digest["channels"]) == 1
    assert res_digest["channels"][0]["channel"] == "fixtures"

    # 3. concepts
    res_concepts = run_discover("concepts", limit=5, db=mock_db)
    assert res_concepts["mode"] == "concepts"
    assert "top_mentions" in res_concepts
    assert any(
        m["concept"] in {"rag", "vector", "rrf", "cross-encoder"}
        for m in res_concepts["top_mentions"]
    )

    # 4. channels
    res_channels = run_discover("channels", db=mock_db)
    assert res_channels["mode"] == "channels"
    assert len(res_channels["channels"]) == 1
    assert res_channels["channels"][0]["channel"] == "fixtures"
    assert res_channels["channels"][0]["videos"] == 2

    # 5. invalid mode
    res_invalid = run_discover("nonexistent_mode", db=mock_db)
    assert "error" in res_invalid


def test_mcp_discover_delegates_to_shared_discover(monkeypatch):
    expected_output = {
        "mode": "digest",
        "channels": [{"channel": "mock", "recent_videos": ["vid"]}],
    }
    monkeypatch.setattr("src.discover.run_discover", lambda mode, days, limit: expected_output)

    payload = json.loads(mcp_mod.discover(mode="digest", days=7, limit=5))
    assert payload == expected_output
