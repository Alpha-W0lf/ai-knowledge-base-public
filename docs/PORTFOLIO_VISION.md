# AI Knowledge Base — What this is and why

**What it is:** a local-first AI knowledge base — ingest content → embed → hybrid retrieval → optional cross-encoder rerank → serve to agents via MCP (and CLI).

**What it is not:** a cloud SaaS, a chatbot product, or a dump of anyone's private notes.

**Current state, stated plainly:**

1. **The public demo is complete and runnable.** A stranger can clone, ingest synthetic fixtures, search, and wire up MCP. Everything needed ships in this repo.
2. **No evaluation claims are made beyond what was measured.** The cross-encoder was kept for architecture reasons but showed **no measurable relevance lift** in testing — that result is documented rather than hidden. Broader eval claims are deliberately not made.
3. **Private data stays private.** The public demo uses synthetic fixtures only; personal corpora live outside this repo by design.

---

## 1. Why this project exists

AI techniques move weekly. Coding agents that only "know" last quarter's defaults fall behind. Teams need a **local, citable** knowledge path: retrieve what matters, cite sources, and expose tools agents can call — without shipping a private corpus to the public internet.

| Skill demonstrated | How |
|--------------------|-----|
| Local embeddings | Ollama `nomic-embed-text` @ 768 |
| Hybrid retrieval with fusion + pluggable reranker | LanceDB + RRF; cross-encoder optional and degrades gracefully |
| Agent tooling | Read-only MCP allowlist (`search`, `discover`, `get_context`, `get_status`) |
| Local-first packaging | `uv`, synthetic fixtures, fixture-first smoke test |

## 2. What data is in here? (honest answer)

### Public / runnable by anyone (default)

- **Synthetic fixtures** under `fixtures/` (8 markdown docs + provenance/manifest + 28 golden eval lines: 18 easy + 10 hard negatives).
- Fixture ingest + local LanceDB smoke — no personal data required.
- MCP responses cite `source_id` / documented URLs — never owner file paths.
- Private tip-transcript paths are absent from this repo (curated out when this public repo was created).

### Private / local only (not part of the public demo)

- Optional bring-your-own YouTube sync into git-ignored `data/raw/youtube_transcripts/` via `channels.local.json`.
- The committed channel default is empty; personal channels load only from the ignored local file.
- A separate private archive may hold tip transcripts — that is not this repo.

### Not first-class today

PDFs of books, private Slack, email, private trading data, OEM manuals, article inbox, podcast/RSS plugins.

## 3. Foundation strategy

| Layer | Decision |
|-------|----------|
| Binding architecture | [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md) (decisions KB1–KB5) |
| Earlier "clean rewrite" proposals | **Rejected** — the existing spine is the product |
| Code approach | Package the existing spine (`ingest`, `search`, `rerank`, `mcp_server`, …) — seams only |
| Public v1 gate | Fixtures + LICENSE + empty channel default + local overlay + this public repo — not "scrub the private archive first" |
| Scratch / rewrite? | **No** |

## 4. How this fits a senior AI engineering portfolio

Fills **local hybrid RAG + MCP** on LanceDB — same ranking *shape* as Mechanic RAG, different store. Differentiates from Mechanic (product/web RAG + Postgres) and AlphaGuard (agents/streaming/ML gate). Eyeglass Finder covers CV/MLOps.

**Cross-encoder honesty:** on the easy golden set, fusion-only and fusion+CE both scored hit@K **1.0** (18/18) — flat at the ceiling. On the confusable corpus with 10 hard negatives, both arms scored `neg_at_k` **0.0** — no rejection lift either. The CE seam is kept with a graceful degrade path, and it is **not** marketed as improving relevance. Completeness of the public demo is a separate fact from any evaluation claim — neither implies the other.

## Appendix A — Delivery checklist

**Status: complete for the public demo.** Detailed gate notes live in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

| Item | Status | Notes |
|------|--------|-------|
| Fixture corpus committed (no private content) | **Done** | `fixtures/` + PROVENANCE/manifest |
| `uv sync` + `nomic-embed-text` pull + smoke search documented | **Done** | README + `GETTING_STARTED.md` |
| Root GETTING_STARTED + FAQ | **Done** | Clone path + Technical FAQ |
| Fixture golden set grown to N≥18 | **Done** | 18 easy |
| Cross-encoder effectiveness measured | **Done** | CE-success 18/18 `ce`; fusion+CE hit@K 1.0; `ce_keep=false`; degrade `error` + stage-gated metrics |
| Hard negatives / `neg_at_k` | **Done** | First 6 `hn*` + harness; per-arm `neg_at_k`; excluded from hit@K + keep math |
| Harder CE-discriminative / confusable set | **Done** | +2 confusable fixtures (8 total); 10 hard-neg; fusion/CE `neg_at_k` 0.0/0.0 |
| Packaging honesty | **Done** | Three-part status stated up front; broader eval claims deliberately not made |
| Shared hybrid → fusion → CE spine | **Done** | This repo is the portfolio surface |
| CE honesty: no false "CE improves relevance" | **Done** | `ce_keep_note`; seam kept without lift claim |
| MCP example without owner absolute `cwd` | **Done** | `mcp-config.example.json` uses portable placeholder |
| Personal channels out of committed default | **Done** | Empty default + ignored `channels.local.json` |
| This public repo as portfolio surface | **Done** | `ai-knowledge-base-public` |
| Tip-transcript scrub | **N/A here / optional private hygiene** | A private-remote flip would need its own scrub — out of scope |
| LICENSE file present | **Done** | Root PolyForm Noncommercial 1.0.0 `LICENSE` (Tom Chacko 2026) |
| Launchd plist owner paths | **Done** | `REPLACE_WITH_REPO_ROOT` template |
| Optional BYO live path (7-day backfill) | **Done** | Documented in GETTING_STARTED; not default / not CI |
| Earlier "clean rewrite" proposal | **Not executed (by decision)** | See Foundation strategy |
| Broader eval-completeness claim | **Deliberately not claimed** | Hard-negative arms were flat; see Cross-encoder honesty |
