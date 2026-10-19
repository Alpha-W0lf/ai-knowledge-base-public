# AGENTS.md

Local hybrid search (vector + keyword → RRF → optional cross-encoder) served to coding agents through a read-only MCP server. Python 3.11+, uv, LanceDB, Ollama.

## Commands

- Install: `uv sync --extra dev` (add `--extra ce` for the cross-encoder)
- Lint and format check: `uv run ruff check && uv run ruff format --check`
- Tests (offline stub embedder by default): `uv run pytest -q`
- One test file: `uv run pytest -q tests/test_search_readonly.py`
- Same tests on the real model (Ollama with `nomic-embed-text` running): `AI_KB_EMBEDDINGS=ollama uv run pytest -q`
- Eval and regression gate, as CI runs it: `AI_KB_EMBEDDINGS=stub uv run python -m src.eval --check --no-ce`

## Done means

- Lint, format and tests pass locally, and CI is green on the PR.
- A bug fix includes a test that fails on the old code.
- A change to ranking, ingest, embeddings or `evals/` passes the eval gate, and the PR shows the before-and-after eval table. A lift claim needs a measured delta with its confidence interval.
- Held-out queries are for reporting only. Tune on `evals/dev.jsonl`; changing eval data needs a new pre-registration version.
- A ranking change that moves the metrics refreshes the CI baseline with `AI_KB_EMBEDDINGS=stub uv run python -m src.eval --write-baseline --no-ce` at a clean, committed tree, so its `git_sha` names the code it measured.
- The PR says what is verified, what is unverified and what is unknown.

## Design rules

- All ranking goes through `retrieve()` in `src/search.py`. CLI, MCP and the eval are thin callers.
- Every hit reports its `ranking_stage`. A failed stage surfaces as an error code or `fusion_degraded`, so callers always know what ran.
- Embeddings come from `src/embed.py` for both ingest and queries. Every chunk carries `embedding_version`; a model change means a full rebuild and a new eval run.
- Ingest owns every write, including the full-text index. Search and the public MCP tools only read and never create the data directory; `tests/test_search_readonly.py` checks this.
- New MCP tools join the public profile only if they are read-only and advertise `readOnlyHint`. Tools that write register only under `AI_KB_MCP_PRIVATE=1`. `tests/test_mcp_readonly_hints.py` enforces this.
- Public citations use `source_id` and `source_url`. MCP errors pass through `sanitize_error`.

## Data

- Commit only synthetic or owner-original documents, listed with their license in a `manifest.json` (`fixtures/` for smoke docs, `evals/corpus/` for the eval).
- Personal channels live in the git-ignored `channels.local.json`. Transcripts and the index live under the git-ignored `data/`.

## Map

- Read `docs/ARCHITECTURE.md` when you change retrieval, identity, sync or the MCP surface.
- Read `evals/PREREGISTRATION_v2.md` when you touch the eval, its data or the cross-encoder default.
- Read `GETTING_STARTED.md` when you work on the optional YouTube sync path.
- Read `CONTRIBUTING.md` for PR size and license terms.
