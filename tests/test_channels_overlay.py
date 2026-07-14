"""
Unit tests for channels.local.json overlay load (Guide 02 packaging).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import load_youtube_channels


def test_missing_overlay_returns_empty(tmp_path: Path):
    assert load_youtube_channels(tmp_path / "missing.json") == []


def test_empty_array_returns_empty(tmp_path: Path):
    path = tmp_path / "channels.local.json"
    path.write_text("[]", encoding="utf-8")
    assert load_youtube_channels(path) == []


def test_valid_overlay_maps_to_tuples(tmp_path: Path):
    path = tmp_path / "channels.local.json"
    path.write_text(
        json.dumps(
            [
                {"handle": "@Alpha", "description": "first"},
                {"handle": "@beta", "description": "second"},
            ]
        ),
        encoding="utf-8",
    )
    assert load_youtube_channels(path) == [
        ("@Alpha", "first"),
        ("@beta", "second"),
    ]


def test_dedupe_case_insensitive_keeps_first(tmp_path: Path):
    path = tmp_path / "channels.local.json"
    path.write_text(
        json.dumps(
            [
                {"handle": "@Same", "description": "keep"},
                {"handle": "@same", "description": "drop"},
            ]
        ),
        encoding="utf-8",
    )
    assert load_youtube_channels(path) == [("@Same", "keep")]


def test_invalid_json_fails_closed(tmp_path: Path):
    path = tmp_path / "channels.local.json"
    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(ValueError, match=str(path)):
        load_youtube_channels(path)


def test_wrong_shape_fails_closed(tmp_path: Path):
    path = tmp_path / "channels.local.json"
    path.write_text(json.dumps({"handle": "@x"}), encoding="utf-8")
    with pytest.raises(ValueError, match=str(path)):
        load_youtube_channels(path)


def test_missing_handle_fails_closed(tmp_path: Path):
    path = tmp_path / "channels.local.json"
    path.write_text(json.dumps([{"description": "no handle"}]), encoding="utf-8")
    with pytest.raises(ValueError, match=str(path)):
        load_youtube_channels(path)
