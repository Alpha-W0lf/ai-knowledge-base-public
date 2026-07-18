# AI Knowledge Base — Interview FAQ

Staff-interview gotchas for the **fixture-first hybrid → fusion → optional CE** vertical slice on the public sibling. Contracts SSOT: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Portfolio intent: [`docs/PORTFOLIO_VISION.md`](docs/PORTFOLIO_VISION.md). CE keep honesty: [`docs/2026-07-12_ce_keep_note.md`](docs/2026-07-12_ce_keep_note.md).

**Three-lane honesty:** (1) **portfolio public success / build MV Met**; (2) **eval-complete claim Parked (E3)** — do not tick from flat Guide 08; (3) **private flip** — not this repo’s build gate.

---

## 1. Why are fixtures the default path, and when is BYO YouTube sync optional?

**Fixtures** (`fixtures/` + `uv run python -m src.ingest --fixtures`) are the stranger-runnable demo: no network, no personal corpus, no `channels.local.json`. The portfolio smoke path is `uv sync` → `nomic-embed-text` pull → fixture ingest → hybrid search → `src.eval`.

**BYO YouTube sync** is optional advanced only: copy `channels.local.example.json` → ignored `channels.local.json`, edit your handles, run `src.youtube_sync` (default `BACKFILL_DAYS = 7`), then ingest `data/raw/youtube_transcripts/`. No auto-sync on clone. See [`GETTING_STARTED.md`](GETTING_STARTED.md) optional section and README “Optional: BYO YouTube live path.”

## 2. Why is private tip-history scrub not required to “have a public AI KB”?

**This public sibling repo** (`ai-knowledge-base-public`) **is** the portfolio public surface. It ships committed synthetic fixtures and curated docs — tip-transcript paths from the private archive (`ai_knowledge_base`) were **absent by design** at sibling creation.

Scrubbing or flipping the **private** remote public would still need KB3 hygiene — that is separate optional work on the private archive, **not** a blocker for strangers to clone and run this repo. See PORTFOLIO_VISION §1–2 and ARCHITECTURE §7 / §10.

## 3. Which MCP tools are public vs private-gated?

**Public / default profile (read-only allowlist — KB2):**

| Tool | Purpose |
|------|---------|
| `search(query)` | Shared retrieval spine (hybrid → fusion → optional CE) |
| `discover(mode)` | Honest browse / digest / concepts / channel groups |
| `get_context(query)` | Shared retrieve + optional recent digest |
| `get_status()` | Knowledge base statistics |

**Private-gated only** (`AI_KB_MCP_PRIVATE=1`): `add_channel`, `sync_now`. These do **not** register on the stranger-runnable default. Personal channel changes belong in ignored `channels.local.json` + CLI sync, not the public MCP story.

## 4. Why `nomic-embed-text` @ 768 — not Gemma / not mxbai?

**KB4** locks the stack: Ollama `nomic-embed-text` @ **768 dimensions**. Gemma is a chat/generator default in other portfolio repos (D1) — it is **not** the embedding model here. The January `mxbai-embed-large` migration was **rejected**; changing embeddings requires full rebuild, identity/version checks, and re-eval.

`embedding_version` is stored per chunk; ingest/search **fail closed** on mismatch. CE model (MiniLM cross-encoder) is a separate ranking stage — not the embedder.

## 5. What is the ranking order, and what does `fusion_degraded` mean?

**KB5 ranking order:** hybrid retrieve (vector + FTS, independent legs) → **RRF fusion** (shortlist **N**) → optional **pluggable local CE** (top **N → K**) → return hits with `ranking_stage` provenance.

| `ranking_stage` | Meaning |
|-----------------|---------|
| `vector` | Vector-only mode |
| `fusion` | CE disabled; fused top **K** returned |
| `ce` | CE ran successfully on fused shortlist |
| `fusion_degraded` | CE failed, timed out, or was unavailable — **fail-open to fused ranks**, not silent vector-only while advertising hybrid+CE |

Do not conflate `fusion_degraded` with intentionally disabling CE (`--no-ce`). Degrade is a production safety path. See ARCHITECTURE §4.

## 6. Does CE improve relevance here? Where is the keep note?

**No — do not claim CE improves relevance.** Guide 06–08: easy fusion-only hit@K **1.0**, CE-success **18/18** `ranking_stage=ce` with `ce_success_hit_at_k` **1.0** (flat vs fusion ceiling). Guide 08 grew to **8** fixtures + **10** hard-negative goldens (`hn1`–`hn10`, including CombSUM/bi-encoder confusable twins): both `fusion.neg_at_k` and `ce.neg_at_k` are **0.0** — still **no** CE win. `ce_keep=false` stays **hit@K-gated**; never flip keep from `neg_at_k` alone. Do not confuse attempt/fallback hit@K with CE-success metrics. On CE load failure, expect `fusion_degraded` plus an `error` string — that is fail-open, not a CE win.

The **keep note** is [`docs/2026-07-12_ce_keep_note.md`](docs/2026-07-12_ce_keep_note.md). Guide 01 DoD is the **pluggable CE seam** + `ranking_stage` provenance + degrade path — not proven relevance lift. Hard negatives use `kind: hard_negative` + `forbidden_source_ids` and are **excluded** from hit@K / CE-success denominators. Do not flip `CE_ENABLED` default without human authorize after metrics.

## 7. What do citations use instead of owner filepaths?

Public MCP and shared retrieval cite **`source_id`** and **`source_url`** (or fixture id like `fixture:<slug>`) — **never** absolute owner filepaths. YouTube chunks use stable **video ID** as `source_id`; fixtures use explicit fixture ids per ARCHITECTURE §7.1.

Identity fields (`source_id`, `content_hash`, `embedding_version`) are binding; path moves must not change `source_id`. This keeps stranger clones and MCP configs portable.

## 8. Does packaging mean build MV Met / private flip / eval-complete?

**Separate the lanes:**

| Lane | Status |
|------|--------|
| Portfolio public success / **build MV Met** | **Yes** — Guides 01–08 delivery + §4 / §9(a); Guide 09 packages the honesty |
| **Eval-complete** claim | **Parked (E3)** — flat Guide 08 metrics; do **not** tick without Tom unlock |
| Private flip | **Out of scope** for this repo’s build % (optional private-archive hygiene only) |
| CE proven relevance lift | **No** — `ce_keep=false`; see `ce_keep_note` |

Root `GETTING_STARTED` + `INTERVIEW` remain the stranger-clone + FAQ shell. Packaging DoD (LICENSE, empty channels + overlay, fixture smoke, this sibling repo) is **implemented**. Guide 08 re-baselined harder hard-neg traps without claiming CE lift. Guide 09 marks build MV Met without inventing an eval-complete tick. Private scrub / January rewrite remain **out of scope** unless a new guide authorizes them.

---

**Clone path:** [`GETTING_STARTED.md`](GETTING_STARTED.md) · **Skim:** [`README.md`](README.md)
