# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-24

Initial public release of AI Knowledge Base: a local-first hybrid RAG knowledge spine and read-only MCP server for coding agents.

### Added
- **Local Hybrid RAG Spine**: LanceDB vector search (`nomic-embed-text` @ 768) and full-text search (BM25) combined via Reciprocal Rank Fusion (RRF).
- **Optional Cross-Encoder Extra**: `sentence-transformers` moved to optional `[ce]` dependency extra; default installation runs without torch/CUDA overhead while preserving the pluggable reranker seam.
- **Read-Only Model Context Protocol (MCP) Server**: Public tools (`search`, `discover`, `get_status`, `get_context`) advertise `readOnlyHint=True`. Data mutation tools (`add_channel`, `sync_now`) strictly isolated behind `AI_KB_MCP_PRIVATE=1`.
- **Shared Discovery Architecture**: Unified `src.discover` implementation shared between CLI and MCP server across all modes (`random`, `digest`, `concepts`, `channels`).
- **Sync Failure Classification**: Structured failure classes distinguishing confirmed `no_subs` (terminal skip) from retryable failures (network timeouts, rate limits, subprocess errors).
- **Security Policy**: Comprehensive `SECURITY.md` covering responsible vulnerability disclosure and local-first architectural probing boundaries.
- **CI Quality Gate**: GitHub Actions workflow running `ruff check`, `ruff format --check`, and `pytest`.

### Changed
- **CLI Usability**: Search CLI maps `-h` to `--help`, documents result count clamping (5–10 per config), and supports `--ce` / `--no-ce` flags.
- **Error Sanitization**: Public MCP handlers sanitize exception messages to prevent exposing local host filesystem paths.
- **Documentation Alignment**: README and `pyproject.toml` ledes positioned around committed synthetic fixtures, hybrid architecture, and evaluation honesty (no live crawl or LinkedIn claims).
