# Assets

Captures from the public smoke fixtures only: no private corpus, no local file paths.

| File | What it shows |
|------|---------------|
| [`pipeline_overview.png`](./pipeline_overview.png) | Overview card: sources → transcripts → hybrid search + MCP → agents |
| [`get_status.json`](./get_status.json) / [`get_status.txt`](./get_status.txt) | MCP `get_status` on a clean clone before ingest (index empty, 8 fixture files) |
| [`search_cited.json`](./search_cited.json) / [`search_cited.txt`](./search_cited.txt) | MCP `search("reciprocal rank fusion RRF", limit=5)` on the 8 smoke fixtures, captured 2026-10-19 with the offline stub embedder: 5 cited hits with per-leg ranks and stage timings |
| [`mcp_tools.json`](./mcp_tools.json) | Public profile tools, each advertising `readOnlyHint=true` |
