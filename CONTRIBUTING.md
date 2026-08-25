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

The unit-test suite is designed to run **without** Ollama:

```bash
uv run pytest -q
```

CI runs `pytest` on every push and pull request.

## Ground rules

- Fixtures stay synthetic — never commit personal corpora or real transcripts.
- Public MCP tools remain read-only; mutations stay behind explicit private-profile flags.
- Retrieval claims need evidence: if you touch ranking, run `src.eval` and report honest numbers (no lift claims without a measured delta).
