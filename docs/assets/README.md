# Packaging assets — AI Knowledge Base (public)

Fixture / portfolio visuals only — **no private corpus**, no owner home paths.

| File | Purpose |
|------|---------|
| [`pipeline_overview.png`](./pipeline_overview.png) | Storefront proof card — Sources → Transcripts → RAG + MCP → Agents (fixtures-labeled) |
| [`get_status.json`](./get_status.json) / [`get_status.txt`](./get_status.txt) | Static MCP `get_status` on a clean clone (fixture_files=8; index empty until ingest) |
| [`search_cited.json`](./search_cited.json) / [`search_cited.txt`](./search_cited.txt) | Static cited-search envelope for `fixture:fusion-rrf-04` (`source_id` / `source_url`, no filepath) |
| [`mcp_tools.json`](./mcp_tools.json) | Public profile tools with advertised `readOnlyHint=true` (mcp-audit dogfood) |

`pipeline_overview.png` is the README proof strip (2026-07-31 sales-first pass). JSON/txt captures are committed static proof — not a live sync and not a CE lift claim (`ranking_stage=fusion`; no-lift on n=28).
