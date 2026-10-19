# Fixture provenance

Eight short synthetic docs for the quickstart and the fast tests. They are one chunk each, too small to measure ranking; the ranking eval uses the 48-doc corpus in [`evals/corpus/`](../evals/corpus/manifest.json).
Machine-readable list: [`manifest.json`](./manifest.json).

| source_id | title | license | notes |
|-----------|-------|---------|-------|
| fixture:rag-hooks-01 | RAG hooks and retrieval stages | synthetic | lexical: hooks, RRF, hybrid |
| fixture:mcp-allowlist-02 | MCP read-only allowlist patterns | synthetic | lexical: MCP, allowlist |
| fixture:embedding-version-03 | Embedding version and rebuild discipline | synthetic | semantic: stale index rebuild |
| fixture:fusion-rrf-04 | Rank fusion with reciprocal rank fusion | synthetic | lexical: RRF, fusion |
| fixture:cross-encoder-05 | Cross-encoder rerank shortlist | synthetic | semantic: N→K rerank |
| fixture:fixture-ingest-06 | Fixture-first ingest without personal corpus | synthetic | lexical: fixtures, provenance |
| fixture:combsum-fusion-07 | Rank fusion with CombSUM score summing | synthetic | confusable: CombSUM vs RRF |
| fixture:bi-encoder-rerank-08 | Bi-encoder late scoring on a shortlist | synthetic | confusable: bi-encoder vs CE |
