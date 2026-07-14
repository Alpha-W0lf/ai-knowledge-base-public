# AI Knowledge Base — Public Portfolio Vision (v1)

**Status:** Active for public packaging intent  
**Created:** 2026-07-12  
**Updated:** 2026-07-13 (Guide 02 packaging DoD)  
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

**Guide 01 (retrieval spine) is implemented.** **Guide 02 packaging DoD is implemented** (LICENSE, empty committed channels + ignored overlay, portable MCP/plist paths). That is **not** “v1 public complete.” Public flip still needs **KB3-exec** tip scrub. **Packaging DoD ≠ visibility flip.**

---

## 2. What data does it include? (honest answer)

### Public / stranger-runnable (default story)

- **Committed fixtures** under `fixtures/` (≈6 synthetic markdown docs + provenance/manifest + golden eval cases).
- Fixture ingest + temp/local LanceDB smoke — **no** personal `data/raw/` required.
- Public MCP cites `source_id` / documented URL — never owner filepaths.

### Private / local only (not the public demo path)

- Personal YouTube sync under ignored `data/raw/youtube_transcripts/`.
- Personal channels load from ignored `channels.local.json` (committed default is empty — Guide 02 / KB1).
- Tip docs with third-party transcripts remain in-repo until **KB3-exec** (inventory in ARCHITECTURE §10; **no scrub in this pass**).

### Not first-class today

PDFs of books, private Slack, email, Lowd Capital data, OEM manuals, article inbox, podcast/RSS plugins.

---

## 3. Foundation strategy

| Layer | Decision |
|-------|----------|
| Binding architecture | `docs/ARCHITECTURE.md` (KB1–KB5) |
| January rewrite / mxbai migration | **Rejected** — non-binding archaeology |
| Code | Package existing spine (`ingest`, `search`, `rerank`, `mcp_server`, …) — seams only |
| Public v1 gate | Scrub (KB3-exec) + fixtures (done) + LICENSE (done) + empty channel default + overlay (done) |
| Scratch / rewrite? | **No** |

---

## 4. v1 public success

| Item | Status | Notes |
|------|--------|-------|
| Fixture corpus committed (no private content) | **Done** | `fixtures/` + PROVENANCE/manifest |
| `uv sync` + `nomic-embed-text` pull + smoke search documented | **Done** | README fixture-first path |
| Shared hybrid → fusion → CE spine (Guide 01) | **Done** | Pass 8/9; not public-flip |
| CE honesty: no false “CE improves relevance” | **Done** | `ce_keep_note`; seam kept without lift claim |
| MCP example without owner absolute `cwd` | **Done** | Guide 02: `mcp-config.example.json` uses `/path/to/ai_knowledge_base` (README was already portable) |
| Personal channels out of committed public default | **Done** | Guide 02: empty default + ignored `channels.local.json` |
| KB3-exec tip-transcript scrub | **Open** | Human-gated; **no scrub this pass** — still blocks public flip |
| LICENSE file present | **Done** | Root MIT `LICENSE` (Tom Chacko 2026); packaging DoD ≠ flip |
| Launchd plist owner paths | **Done** | Guide 02: `REPLACE_WITH_REPO_ROOT` template |
| No execution of January clean rewrite | **Held** | KB4 |

---

## 5. Alignment with senior AI eng portfolio

Fills **local hybrid RAG + MCP** on LanceDB — same ranking *shape* as Mechanic (MR2/KB5), different store. Differentiates from Mechanic (product/web RAG + Postgres) and AlphaGuard (agents/streaming/ML gate). Eyeglass remains untouched for MLE/MLOps.

**CE no-lift honesty:** On the tiny fixture golden set, hit@K lift was **not** shown; keep the pluggable CE seam + `ranking_stage` / degrade for demos; do not market CE as proven relevance lift until a larger eval says so.
