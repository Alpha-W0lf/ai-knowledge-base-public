# AI Knowledge Base — Public Portfolio Vision (v1)

**Status:** Active for public packaging intent · Build MV Met · Eval-complete claim parked · Private flip out of scope  
**Created:** 2026-07-12  
**Updated:** 2026-08-02 (R3 — product-why first; delivery ledger moved to appendix)  
**Owner:** Tom  
**Binding architecture:** [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md) (KB1–KB5)  
**Related personal vision / January architecture:** historical private notes in-repo — **non-binding**; do not execute January rewrite

---

## 1. What is this project?

A **local-first AI knowledge base**: ingest content → embed → **hybrid retrieve → fusion → optional pluggable CE** → expose to agents via **MCP** (and CLI).

It is **not** a cloud SaaS, not a chatbot product, and not a rewrite of a private second-brain docs archive. For the **public portfolio**, it proves:

| Skill | How |
|-------|-----|
| Local embeddings | Ollama **`nomic-embed-text` @ 768** (not Gemma; not mxbai) |
| Hybrid + fusion + CE seam | LanceDB + RRF + local MiniLM CE (KB5); CE may degrade to fusion |
| Agent tooling | Read-only public MCP allowlist |
| Local-first packaging | `uv`, synthetic fixtures, fixture-first smoke |

**Three-lane honesty (do not conflate):**

1. **Build MV Met** — public stranger-runnable delivery checklist closed.  
2. **Eval-complete claim = Parked** — flat hard-neg / no CE rejection lift; do **not** tick eval-complete without a later unlock.  
3. **Private flip** — out of scope for this repo’s build %; optional hygiene on the private archive only.

Private archive (`ai_knowledge_base`) remains private; scrubbing private tip history is **not** a blocker for having a public AI KB. CE shows **no** claimed relevance lift (`ce_keep=false`; see `ce_keep_note`).

---

## 2. What data does it include? (honest answer)

### Public / stranger-runnable (default story)

- **Committed fixtures** under `fixtures/` (**8** synthetic markdown docs + provenance/manifest + **28** golden eval lines: 18 easy + 10 hard-neg).
- Fixture ingest + temp/local LanceDB smoke — **no** personal `data/raw/` required.
- Public MCP cites `source_id` / documented URL — never owner filepaths.
- Tip-transcript paths from the private archive are **absent** on this sibling (curated out at sibling creation).

### Private / local only (not the public demo path)

- Optional BYO YouTube sync under ignored `data/raw/youtube_transcripts/` (user’s own channels via `channels.local.json`).
- Personal channels load from ignored `channels.local.json` (committed default is empty).
- Private archive may still hold tip transcripts; that is **not** this repo’s tip tree.

### Not first-class today

PDFs of books, private Slack, email, private trading data, OEM manuals, article inbox, podcast/RSS plugins.

---

## 3. Foundation strategy

| Layer | Decision |
|-------|----------|
| Binding architecture | `docs/ARCHITECTURE.md` (KB1–KB5) |
| January rewrite / mxbai migration | **Rejected** — non-binding archaeology |
| Code | Package existing spine (`ingest`, `search`, `rerank`, `mcp_server`, …) — seams only |
| Public v1 gate | Fixtures + LICENSE + empty channel default + overlay + **this public sibling repo** — not “scrub private first” |
| Scratch / rewrite? | **No** |

---

## 4. Alignment with senior AI eng portfolio

Fills **local hybrid RAG + MCP** on LanceDB — same ranking *shape* as Mechanic, different store. Differentiates from Mechanic (product/web RAG + Postgres) and AlphaGuard (agents/streaming/ML gate). Eyeglass remains untouched for MLE/MLOps.

**CE no-lift honesty:** Easy fusion-only hit@K was **1.0** and CE-success hit@K was **1.0** (18/18 `ranking_stage=ce`) — flat at the easy-golden ceiling; `ce_keep=false`. Confusable corpus + 10 hard-negatives: both arms report `neg_at_k` **0.0** (0/10) — still no CE rejection lift, and **`ce_keep` is not flipped by `neg_at_k`**. Keep the pluggable CE seam + degrade path (`fusion_degraded` + `error`); do not market CE as proven relevance lift. Packaging build MV Met is separate from the parked eval-complete claim — packaging ≠ CE lift and ≠ eval-complete tick.

---

## Appendix A — Delivery ledger (build MV checklist)

**Status: Met.** Prefer “portfolio public success / build MV Met” over ambiguous “v1 complete.” Detailed gate notes also live in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

| Item | Status | Notes |
|------|--------|-------|
| Fixture corpus committed (no private content) | **Done** | `fixtures/` + PROVENANCE/manifest |
| `uv sync` + `nomic-embed-text` pull + smoke search documented | **Done** | README + `GETTING_STARTED.md` |
| Root GETTING_STARTED + FAQ | **Done** | Stranger-clone + Technical FAQ |
| Fixture golden growth N≥18 | **Done** | 18 easy |
| CE-effectiveness measure | **Done** | CE-success 18/18 `ce`; fusion+CE-success hit@K 1.0; `ce_keep=false`; degrade `error` + stage-gated metrics |
| Hard-negative / `neg_at_k` | **Done** | First 6 `hn*` + harness; per-arm `neg_at_k`; excluded from hit@K + keep math |
| Harder CE-discriminative / confusable | **Done** | +2 confusable fixtures (8 total); 10 hard-neg; fusion/CE `neg_at_k` 0.0/0.0 |
| Build-MV packaging honesty | **Done** | Three-lane prose; eval-complete parked |
| Shared hybrid → fusion → CE spine | **Done** | Portfolio surface = this sibling |
| CE honesty: no false “CE improves relevance” | **Done** | `ce_keep_note`; seam kept without lift claim |
| MCP example without owner absolute `cwd` | **Done** | `mcp-config.example.json` uses portable placeholder (`ai-knowledge-base-public`) |
| Personal channels out of committed public default | **Done** | Empty default + ignored `channels.local.json` |
| Public sibling as portfolio surface | **Done** | This repo (`ai-knowledge-base-public`) |
| Tip-transcript scrub | **N/A on public sibling / optional private hygiene** | Private remote flip would still need scrub — out of scope here |
| LICENSE file present | **Done** | Root PolyForm Noncommercial 1.0.0 `LICENSE` (Tom Chacko 2026) |
| Launchd plist owner paths | **Done** | `REPLACE_WITH_REPO_ROOT` template |
| Optional BYO live path (7-day backfill) | **Done** | Documented in GETTING_STARTED; not default / not CI |
| No execution of January clean rewrite | **Held** | KB4 |
| Eval-complete claim | **Parked** | Flat hard-neg arms; **not** a build MV blocker |
