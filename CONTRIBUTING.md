# Contributing

Thanks for your interest in improving this project.

## The short version

- Bug fixes, documentation improvements, and test additions are welcome.
- Open an issue first for anything that changes behavior or adds scope.
- Keep PRs small and focused; include a test for any bug fixed.

## License terms for contributors

This project is licensed under the [PolyForm Noncommercial 1.0.0](LICENSE) — source-available, non-commercial use only. By submitting a pull request, you agree your contribution is licensed under the same terms.

Commercial licensing inquiries: reach out via [LinkedIn](https://www.linkedin.com/in/tchacko1/).

## Local setup

```bash
uv sync
ollama pull nomic-embed-text
uv run python -m src.ingest --fixtures
```

## Tests (hub-free vs Ollama)

CI runs `uv run pytest -q` on every push and pull request. Pytest collects every `tests/test_*.py` file, including `test_retrieval_spine.py` (the 14 spine / MCP / ingest tests). The older `tests_retrieval_spine.py` name was never collected.

**Hub-free** (no Ollama, no Hugging Face Hub) — identity, schema-import, overlay, MCP allowlist, FTS-missing, hybrid-fail-closed, and eval-honesty helpers:

```bash
uv run pytest -q
```

Ingest, hybrid retrieve, MCP search, and fixture-eval cases in `test_retrieval_spine.py` **skip** when Ollama + `nomic-embed-text` are not reachable, so the default clone stays green.

**Ollama spine** (ingest / hybrid / MCP search / fixture eval) — same file, live embeddings:

```bash
ollama pull nomic-embed-text
uv run pytest -q tests/test_retrieval_spine.py
```

Requires a running Ollama with `nomic-embed-text`. Cross-encoder cases that load MiniLM still degrade honestly if the Hub model is cold (`ranking_stage=fusion_degraded`).

## Ground rules

- Fixtures stay synthetic — never commit personal corpora or real transcripts.
- Public MCP tools remain read-only; mutations stay behind explicit private-profile flags.
- Retrieval claims need evidence: if you touch ranking, run `src.eval` and report honest numbers (no lift claims without a measured delta).
