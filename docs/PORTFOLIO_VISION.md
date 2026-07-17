# AI Knowledge Base — Public Portfolio Vision (v1)

**Status:** Active for public packaging intent  
**Created:** 2026-07-12  
**Updated:** 2026-07-17 (Guide 07 — hard-negative / `neg_at_k` honesty)  
**Owner:** Tom  
**Binding architecture:** [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md) (KB1–KB5)  
**Related personal vision:** `docs/2026-01-30_vision.md` (personal second-brain — private use; stack choices **non-binding**)  
**January architecture:** `docs/2026-01-30_architecture.md` — **NON-BINDING / HISTORICAL** (clean rewrite **rejected** under KB4; do not execute)

---

## 1. What is this project?

A **local-first AI knowledge base**: ingest content → embed → **hybrid retrieve → fusion → optional pluggable CE** → expose to agents via **MCP** (and CLI).

It is **not** a cloud SaaS, not a chatbot product, and not a rewrite of second_brain docs. For the **public portfolio**, it proves:

| Skill | How |
|-------|-----|
| Local embeddings | Ollama **`nomic-embed-text` @ 768** (not Gemma; not mxbai) |
| Hybrid + fusion + CE seam | LanceDB + RRF + local MiniLM CE (KB5); CE may degrade to fusion |
| Agent tooling | Read-only public MCP allowlist |
| Local-first packaging | `uv`, synthetic fixtures, fixture-first smoke |

**Guide 01 (retrieval spine) is implemented.** **Guide 02 packaging DoD is implemented** (LICENSE, empty committed channels + ignored overlay, portable MCP/plist paths). **Guide 03:** this public sibling is the portfolio public surface with optional BYO live path. **Guide 04:** root `GETTING_STARTED.md` + `INTERVIEW.md` landed — stranger-clone + FAQ shell. **Guide 05:** fixture golden growth to **18 easy** cases. **Guide 06:** CE load observability + CE-success-gated eval — CE ran **18/18** `ce` but **no** hit@K lift vs fusion ceiling. **Guide 07:** **6** hard-negative goldens + per-arm `neg_at_k` (fusion and CE both **0.0** on this set); `ce_keep` still hit@K-gated; **still not** portfolio v1 complete, **not** private-flip ready, **not** eval-complete. Private archive (`ai_knowledge_base`) remains private; scrubbing private tip history is optional hygiene, **not** a blocker for “having a public AI KB.”

---

## 2. What data does it include? (honest answer)

### Public / stranger-runnable (default story)

- **Committed fixtures** under `fixtures/` (≈6 synthetic markdown docs + provenance/manifest + **24** golden eval lines: 18 easy + 6 hard-neg).
- Fixture ingest + temp/local LanceDB smoke — **no** personal `data/raw/` required.
- Public MCP cites `source_id` / documented URL — never owner filepaths.
- Tip-transcript paths inventoried on the private archive (§10) are **absent** on this sibling (curated out at sibling creation).

### Private / local only (not the public demo path)

- Optional BYO YouTube sync under ignored `data/raw/youtube_transcripts/` (user’s own channels via `channels.local.json`).
- Personal channels load from ignored `channels.local.json` (committed default is empty — Guide 02 / KB1).
- Private archive may still hold tip transcripts; that is **not** this repo’s tip tree.

### Not first-class today

PDFs of books, private Slack, email, Lowd Capital data, OEM manuals, article inbox, podcast/RSS plugins.

---

## 3. Foundation strategy

| Layer | Decision |
|-------|----------|
| Binding architecture | `docs/ARCHITECTURE.md` (KB1–KB5) |
| January rewrite / mxbai migration | **Rejected** — non-binding archaeology |
| Code | Package existing spine (`ingest`, `search`, `rerank`, `mcp_server`, …) — seams only |
| Public v1 gate | Fixtures (done) + LICENSE (done) + empty channel default + overlay (done) + **this public sibling repo** — not “scrub private first” |
| Scratch / rewrite? | **No** |

---

## 4. v1 public success

| Item | Status | Notes |
|------|--------|-------|
| Fixture corpus committed (no private content) | **Done** | `fixtures/` + PROVENANCE/manifest |
| `uv sync` + `nomic-embed-text` pull + smoke search documented | **Done** | README thin Quick Start + `GETTING_STARTED.md` |
| Root GETTING_STARTED + INTERVIEW (Guide 04) | **Done** | Stranger-clone + FAQ; not v1 / eval-complete |
| Fixture golden growth N≥18 (Guide 05) | **Done** | 18 easy; not eval-complete |
| CE-effectiveness measure (Guide 06) | **Done** | CE-success 18/18 `ce`; fusion+CE-success hit@K 1.0; `ce_keep=false`; degrade `error` + stage-gated metrics |
| Hard-negative / `neg_at_k` (Guide 07) | **Done** | 6 `hn*` cases; per-arm `neg_at_k` 0.0/0.0; excluded from hit@K + keep math; no fake lift |
| Shared hybrid → fusion → CE spine (Guide 01) | **Done** | Pass 8/9; portfolio surface = this sibling |
| CE honesty: no false “CE improves relevance” | **Done** | `ce_keep_note`; seam kept without lift claim |
| MCP example without owner absolute `cwd` | **Done** | Guide 02: `mcp-config.example.json` uses portable placeholder |
| Personal channels out of committed public default | **Done** | Guide 02: empty default + ignored `channels.local.json` |
| Public sibling as portfolio surface | **Done** | This repo (`ai-knowledge-base-public`) |
| KB3-exec tip-transcript scrub | **N/A on public sibling / optional private hygiene** | Private remote flip would still need scrub — out of scope here |
| LICENSE file present | **Done** | Root MIT `LICENSE` (Tom Chacko 2026) |
| Launchd plist owner paths | **Done** | Guide 02: `REPLACE_WITH_REPO_ROOT` template |
| Optional BYO live path (7-day backfill) | **Done** | Documented; not default / not CI |
| No execution of January clean rewrite | **Held** | KB4 |

---

## 5. Alignment with senior AI eng portfolio

Fills **local hybrid RAG + MCP** on LanceDB — same ranking *shape* as Mechanic (MR2/KB5), different store. Differentiates from Mechanic (product/web RAG + Postgres) and AlphaGuard (agents/streaming/ML gate). Eyeglass remains untouched for MLE/MLOps.

**CE no-lift honesty:** On Guide 06/07, easy fusion-only hit@K was **1.0** and CE-success hit@K was **1.0** (18/18 `ranking_stage=ce`) — flat at the easy-golden ceiling; `ce_keep=false`. Guide 07 adds hard-negatives: both arms report `neg_at_k` **0.0** (0/6) — still no CE rejection lift, and **`ce_keep` is not flipped by `neg_at_k`**. Keep the pluggable CE seam + degrade path (`fusion_degraded` + `error`); do not market CE as proven relevance lift.
