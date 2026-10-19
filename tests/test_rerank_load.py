"""The cross-encoder loads offline from the cache and downloads only a pinned revision."""

from __future__ import annotations

import sys
import types

from src import config
from src.rerank import LocalCrossEncoder


def _fake_sentence_transformers(monkeypatch, cached: bool) -> list[dict]:
    calls: list[dict] = []

    class FakeCrossEncoder:
        def __init__(self, model_id, **kwargs):
            calls.append({"model_id": model_id, **kwargs})
            if kwargs.get("local_files_only") and not cached:
                raise OSError("not in the local cache")

    module = types.ModuleType("sentence_transformers")
    module.CrossEncoder = FakeCrossEncoder
    monkeypatch.setitem(sys.modules, "sentence_transformers", module)
    return calls


def test_cached_model_loads_without_network(monkeypatch) -> None:
    calls = _fake_sentence_transformers(monkeypatch, cached=True)
    LocalCrossEncoder()._load()
    assert calls == [
        {
            "model_id": config.CE_MODEL_ID,
            "revision": config.CE_MODEL_REVISION,
            "local_files_only": True,
        }
    ]


def test_first_load_downloads_the_pinned_revision(monkeypatch) -> None:
    calls = _fake_sentence_transformers(monkeypatch, cached=False)
    LocalCrossEncoder()._load()
    assert len(calls) == 2
    assert calls[0]["local_files_only"] is True
    assert calls[1] == {"model_id": config.CE_MODEL_ID, "revision": config.CE_MODEL_REVISION}
