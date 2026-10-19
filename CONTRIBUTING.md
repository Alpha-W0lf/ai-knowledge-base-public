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
uv sync --extra dev
ollama pull nomic-embed-text      # or set AI_KB_EMBEDDINGS=stub to work offline
uv run python -m src.ingest --fixtures
```

## Tests, lint and the eval

CI runs `uv run ruff check`, `uv run ruff format --check` and `uv run pytest -q` on every push and pull request. Pytest collects every `tests/test_*.py` file. Tests use the offline stub embedder by default, so the whole suite, including ingest, hybrid search, MCP search and the eval harness, runs without Ollama or the Hugging Face Hub.

```bash
uv run ruff check && uv run ruff format --check
uv run pytest -q
```

To run the same tests on the real model, start Ollama with `nomic-embed-text` and run `AI_KB_EMBEDDINGS=ollama uv run pytest -q`.

The Eval workflow runs on pull requests that touch ranking code, ingest, embeddings or `evals/`. Run it locally the same way:

```bash
AI_KB_EMBEDDINGS=stub uv run python -m src.eval --check --no-ce
```

## Ground rules

- Fixtures stay synthetic — never commit personal corpora or real transcripts.
- Public MCP tools remain read-only; mutations stay behind explicit private-profile flags.
- Retrieval claims need evidence: if you touch ranking, include the before-and-after eval table, and claim a lift only with a measured delta and its confidence interval. Tune on `evals/dev.jsonl`; the held-out file is for reporting.
