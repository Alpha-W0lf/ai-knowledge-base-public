# Docs index — AI Knowledge Base (public)

**Stranger start:** root [`README.md`](../README.md) · [`GETTING_STARTED.md`](../GETTING_STARTED.md) · [`FAQ.md`](../FAQ.md)

## Source of truth (read these)

| Doc | Role |
|-----|------|
| [`PORTFOLIO_VISION.md`](./PORTFOLIO_VISION.md) | Public packaging intent + build MV honesty |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Binding KB1–KB5 contracts |
| [`2026-07-12_ce_keep_note.md`](./2026-07-12_ce_keep_note.md) | Why CE stays without claimed lift |
| [`assets/`](./assets/) | Demo screenshots (when present) |

## Implementation guides

Executable guides: [`dev_guides/`](./dev_guides/). Needed for rebuild/review — **not** required for fixture smoke.

## Historical / non-binding

| Doc | Note |
|-----|------|
| [`2026-01-30_vision.md`](./2026-01-30_vision.md) | Personal second-brain vision — **non-binding** stack |
| [`2026-01-30_architecture.md`](./2026-01-30_architecture.md) | Historical — **do not execute** |

## Working notes (not stranger SSOT)

Dated `2026-07-*.md` context/review/ready notes are build process artifacts. If they conflict with `PORTFOLIO_VISION.md` / `ARCHITECTURE.md` / root README, **trust the SSOT table**.

## Demo surfaces (honest)

- Default: CLI ingest → search → eval on `fixtures/`  
- Agent path: read-only **MCP** (`src/mcp_server.py`)  
- There is **no** shipped browser UI in this repo (optional later — Operate-mode only)
