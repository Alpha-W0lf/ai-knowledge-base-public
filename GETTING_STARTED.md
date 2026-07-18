# Getting started — AI Knowledge Base (public sibling)

Clone-depth operator path for the **fixture-first hybrid → fusion → optional CE** vertical slice. Contracts: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Interview gotchas: [`INTERVIEW.md`](INTERVIEW.md). Skim + thin Quick Start: [`README.md`](README.md). Portfolio why: [`docs/PORTFOLIO_VISION.md`](docs/PORTFOLIO_VISION.md).

This is **not** portfolio v1 complete, **not** private-archive flip ready, **not** eval-complete. Public corpus = committed `fixtures/` only.

---

## Prerequisites

- **Python 3.11+** with [`uv`](https://docs.astral.sh/uv/)
- Host **Ollama** running locally (embeddings only — no chat LLM in Guide 01)

---

## Clean-clone path (fixture ceiling)

From repo root, in order:

### 1. Install dependencies

```bash
uv sync
```

**Why:** `uv` locks the Python env and deps for a reproducible stranger clone.

### 2. Pull embedding model

```bash
ollama pull nomic-embed-text
```

**Why:** KB4 locks embeddings to **`nomic-embed-text` @ 768** — not Gemma, not `mxbai-embed-large`. Search and ingest fail closed if Ollama is down or the wrong model is loaded.

### 3. Fixture ingest (no personal corpus, no network)

```bash
uv run python -m src.ingest --fixtures
```

**Why:** The public sibling ships synthetic `fixtures/` only. Fixture ingest is the portfolio demo path — no YouTube sync, no private tip transcripts, no `channels.local.json` required.

### 4. Search smoke (hybrid)

```bash
uv run python -m src.search "reciprocal rank fusion RRF" --hybrid --db data/lancedb
```

**Why:** Proves the shared retrieval spine: vector + FTS → RRF fusion → optional CE. Expect `ranking_stage` of `ce`, `fusion`, or `fusion_degraded` in results.

### 5. Eval smoke

```bash
uv run python -m src.eval
```

**Why:** Runs the committed fixture golden set (**28** lines = **18 easy** + **10 hard-negative**). Guide 08 honesty: **8** confusable fixtures; easy fusion-only hit@K **1.0**; CE-success **18/18** `ranking_stage=ce` with `ce_success_hit_at_k` **1.0** (no lift vs fusion ceiling); `fusion.neg_at_k` / `ce.neg_at_k` both **0.0** on 10 hard-negs (no rejection lift); `ce_keep=false` (still hit@K-gated, **not** from `neg_at_k`); **not** eval-complete. See [`docs/2026-07-12_ce_keep_note.md`](docs/2026-07-12_ce_keep_note.md).

---

## Operator footguns

| Footgun | Why it bites |
|---------|----------------|
| Ollama not running | Embed calls fail; pull `nomic-embed-text` and start Ollama before ingest/search |
| Wrong embedding model | KB4 is `nomic-embed-text` @ 768 — changing models requires full rebuild + re-eval |
| HF MiniLM CE cold / Hub blocked | First CE load needs `cross-encoder/ms-marco-MiniLM-L-6-v2` in HF cache (or Hub download). If load fails → `ranking_stage=fusion_degraded` + `error` string; warm via a successful `--hybrid` search or Hub download before claiming CE metrics |
| BYO without `channels.local.json` | Live YouTube sync needs ignored overlay copied from `channels.local.example.json` |
| Committing `channels.local.json` | Personal channel list must stay gitignored — never commit the overlay |
| Expecting personal tip corpus | Tip-transcript docs from the private archive are **absent** on this sibling by design |

---

## Optional: BYO YouTube live path (advanced)

**Not** part of the fixture ceiling. No auto-sync on clone. Default `BACKFILL_DAYS = 7` in `src/config.py` (raise locally for deeper backfill).

```bash
# 1. Copy example → ignored local overlay
cp channels.local.example.json channels.local.json

# 2. Edit handles to your own channels (placeholders only in the example)

# 3. Sync (network + yt-dlp)
uv run python -m src.youtube_sync

# 4. Ingest live downloads
uv run python -m src.ingest data/raw/youtube_transcripts/

# 5. Search smoke
uv run python -m src.search "your query" --hybrid --db data/lancedb
```

---

## Honesty

| Topic | Truth |
|-------|--------|
| Packaging | Stranger-clone + FAQ shell — not portfolio v1 complete |
| Private flip | Scrubbing the private archive is **optional hygiene** — not required to have this public AI KB |
| CE | Pluggable seam + degrade path — Guide 06–08: CE-success **18/18** `ce` but **no** hit@K lift vs fusion ceiling; hard-neg `neg_at_k` also flat on 10 traps (`ce_keep=false`) |
| Corpus | **Fixtures only** on the public default path — **8** synthetic docs; no personal tip transcripts here |
| Eval | Fixture goldens **28** (18 easy + 10 hard-neg) — **not** eval-complete; per-arm `neg_at_k` reported; `ce_keep` still hit@K-gated |

---

**Interview FAQ:** [`INTERVIEW.md`](INTERVIEW.md) · **Skim:** [`README.md`](README.md)
