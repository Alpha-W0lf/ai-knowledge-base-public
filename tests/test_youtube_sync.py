"""
Tests for sync failure classification (ARCHITECTURE §8 / JH-64.7).

Distinguishes:
- confirmed no_subs (terminal skip)
- retryable failure (network, yt-dlp timeout/crash, conversion failure; not persisted as no_subs)
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.youtube_sync import (
    NoSubtitlesError,
    RetryableSyncError,
    SyncState,
    download_transcript,
    sync_channel,
)


def test_download_transcript_retryable_on_ytdlp_failure(tmp_path: Path):
    with patch("src.youtube_sync.run_ytdlp", return_value=None):
        with pytest.raises(RetryableSyncError, match="yt-dlp failed or timed out"):
            download_transcript("vid123", tmp_path)


def test_download_transcript_no_subs_when_srt_not_found(tmp_path: Path):
    with patch("src.youtube_sync.run_ytdlp", return_value="success"):
        with patch("src.youtube_sync.find_existing_files", return_value=(None, None)):
            with pytest.raises(NoSubtitlesError, match="No usable subtitles found"):
                download_transcript("vid123", tmp_path)


def test_download_transcript_retryable_on_conversion_failure(tmp_path: Path):
    dummy_srt = tmp_path / "vid123.en.srt"
    dummy_srt.write_text("invalid srt content with no timestamps", encoding="utf-8")
    with patch("src.youtube_sync.run_ytdlp", return_value="success"):
        with patch("src.youtube_sync.find_existing_files", return_value=(dummy_srt, None)):
            with pytest.raises(RetryableSyncError, match="Failed to convert"):
                download_transcript("vid123", tmp_path)


def test_sync_channel_distinguishes_no_subs_vs_retryable(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("src.youtube_sync.config.DATA_DIR", tmp_path)
    monkeypatch.setattr("src.youtube_sync.config.TRANSCRIPTS_DIR", tmp_path / "transcripts")
    state = SyncState()

    fake_videos = [
        {"id": "vid_no_subs", "title": "No Subs Video", "date": "20260101"},
        {"id": "vid_net_err", "title": "Network Error Video", "date": "20260102"},
        {"id": "vid_success", "title": "Success Video", "date": "20260103"},
    ]

    def mock_download(vid_id: str, output_dir: Path):
        if vid_id == "vid_no_subs":
            raise NoSubtitlesError("No subtitles available")
        if vid_id == "vid_net_err":
            raise RetryableSyncError("Network timeout")
        # Success
        output_dir.mkdir(parents=True, exist_ok=True)
        md = output_dir / f"{vid_id}.md"
        md.write_text("# Title\n\nContent here.", encoding="utf-8")
        return md

    monkeypatch.setattr("src.youtube_sync.list_channel_videos", lambda *args, **kwargs: fake_videos)
    monkeypatch.setattr("src.youtube_sync.download_transcript", mock_download)
    monkeypatch.setattr("src.youtube_sync.ingest_file", lambda *args, **kwargs: 2)
    monkeypatch.setattr("src.youtube_sync.get_db", lambda: MagicMock())

    stats = sync_channel("@test_channel", state, force=True)

    assert stats["new"] == 1
    assert stats["no_subs"] == 1
    assert stats["failed"] == 1

    # Verify no_subs contains ONLY vid_no_subs, NOT vid_net_err
    no_subs_recorded = state.get_no_subs_videos("@test_channel")
    assert "vid_no_subs" in no_subs_recorded
    assert "vid_net_err" not in no_subs_recorded
