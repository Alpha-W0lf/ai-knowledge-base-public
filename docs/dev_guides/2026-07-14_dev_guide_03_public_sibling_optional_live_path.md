# Dev Guide 03 — Public sibling honesty + optional BYO live path

**Date:** 2026-07-14  
**Repo:** `ai-knowledge-base-public` (primary)  
**Also touch (honesty only):** `ai_knowledge_base` — mark old scrub Guide 03 **superseded for portfolio public story**  
**Work item:** Guide 03 re-scope — fixtures-first DoD + optional BYO YouTube live path; retire same-repo history-scrub as default public path  
**Stage that authored this:** Write-dev-guide (pass 35)  
**Status:** **READY** (Ready check pass 35 — awaiting Implement authorize)

**Context SSOT:** `docs/2026-07-14_guide03_public_sibling_optional_live_path_context_summary.md`  
**Prerequisite:** Guide 01 retrieval spine + Guide 02 packaging DoD shippable on the lineage that produced this public sibling. Public sibling already exists on GitHub.

**Critical:** This guide does **not** authorize deleting private tip transcripts, `git filter-repo`, force-push, or flipping the **private** remote to public. Those stay optional private hygiene behind a separate scrub-authorize stamp on the superseded private guide.

---

## Objective

Make the **public portfolio surface** honest and stranger-complete for Guide 03:

1. **Default path (required):** fixture ingest + search (and optional MCP status) works with **zero** YouTube sync and no network dependency on YouTube.  
2. **Optional live path (documented + configured):** copy `channels.local.example.json` → ignored `channels.local.json`, add **user’s own** channel handles, sync with **`BACKFILL_DAYS = 7`**, ingest, search — without auto-sync on clone and without committing a real channel catalog.  
3. **Docs honesty:** PORTFOLIO_VISION / ARCHITECTURE / README no longer claim that **KB3-exec scrub of the private repo** is the blocker for “having a public AI KB.” Public sibling **is** the public surface; private archive remains private.  
4. **Supersession:** Private scrub runbook remains on disk as optional hygiene only; portfolio Guide 03 SSOT moves here.

**Success signal:** A stranger clones `ai-knowledge-base-public`, follows fixture Quick Start, gets search hits from fixtures. A motivated stranger can optionally BYO channels for a short 7-day sync without the docs treating that as the default or CI path.

---

## Learning notes (new for this guide)

1. **Sibling vs scrub.** History rewrite cleans one remote’s attic. A **public sibling** is a second house with only the furniture you want visitors to see. Portfolio public story uses the sibling; private attic can stay messy while private.

2. **Fixtures vs live populate.** Committed synthetic fixtures = reproducible, offline-friendly, legal-safe default. Live YouTube sync = optional advanced path (network, yt-dlp, copyrighted third-party text under ignored `data/`). Do not conflate them in DoD.

3. **Backfill window.** `BACKFILL_DAYS` is how far back sync looks for videos. **60** is a deep personal backfill; **7** is a short demo window. Public default → **7**. Private may keep **60** for owner convenience.

4. **Authorize ladder still exists for private scrub.** Ready/Implement of *this* guide ≠ scrub authorize on private. If Tom later wants tip-delete or filter-repo on private, use the superseded scrub guide + separate stamp.

5. **Docs-as-delivery.** Changing the public story without updating VISION/ARCHITECTURE/README in the same delivery recreates status theater (Workflow OS ALWAYS / QUALITY docs trustworthiness).

---

## References (paths only)

### Binding / truth

- `ai-knowledge-base-public/docs/2026-07-14_guide03_public_sibling_optional_live_path_context_summary.md`
- `second_brain/docs/2026-07-14_ai_kb_public_sibling_decision.md`
- `second_brain/docs/2026-07-14_ai_kb_public_strategy_options.md`
- `ai-knowledge-base-public/docs/ARCHITECTURE.md`
- `ai-knowledge-base-public/docs/PORTFOLIO_VISION.md`
- `ai-knowledge-base-public/README.md`
- `ai-knowledge-base-public/src/config.py`
- `ai-knowledge-base-public/channels.local.example.json`
- `ai-knowledge-base-public/fixtures/`
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`

### Superseded (optional private hygiene only)

- `ai_knowledge_base/docs/dev_guides/2026-07-14_dev_guide_03_kb3_exec_scrub.md`
- `ai_knowledge_base/docs/2026-07-14_guide03_kb3_exec_scrub_context_summary.md`

### Do not reopen as core DoD

- Guide 01 spine redesign, CE freeze claims, January architecture rewrite, committing personal channel lists, auto-sync-on-clone

---

## Architecture constraints (binding)

1. **Public sibling is the portfolio public surface.** Do not require private-repo history scrub for “public AI KB exists.”  
2. **Fixture-first default.** CI and stranger Quick Start must not require YouTube, yt-dlp success, or `channels.local.json`.  
3. **Optional live path is BYO only.** Example file may contain placeholders only (`@example-channel`). Never commit Tom’s real channel catalog to public.  
4. **`BACKFILL_DAYS = 7` on public** after Implement. Document that deeper backfill is an explicit local edit/override.  
5. **Private `BACKFILL_DAYS` stays 60** unless a later human asks to align.  
6. **No auto-sync on clone** (no postinstall hook that calls `youtube_sync`).  
7. **MCP public profile stays read-only** (mutation tools remain private-profile gated).  
8. **Ignored data stays ignored:** `channels.local.json`, `data/raw/`, LanceDB paths — never force-add.  
9. **Same-delivery docs honesty** on public repo for VISION / ARCHITECTURE gate-8 language / README flip-blocker lines.  
10. **Private tip transcripts are not deleted** by this guide.

---

## Ordered steps (Implement checklist)

### Phase 0 — Preflight (fail closed)

0.1 Confirm working tree is `ai-knowledge-base-public` on `main` (or agreed branch); remote is `Alpha-W0lf/ai-knowledge-base-public`.  
0.2 Re-read context SSOT pins; do not invent auto-sync or committed real channels.  
0.3 Baseline: `BACKFILL_DAYS` still 60 until Phase 2; fixtures dir present; `git check-ignore -v channels.local.json` still ignored.  
0.4 Do **not** run filter-repo / tip scrub on private as part of this guide.

### Phase 1 — Config: short public backfill

1.1 Set `BACKFILL_DAYS = 7` in `src/config.py` (comment: public demo default; raise locally for deeper BYO backfill).  
1.2 Grep public repo for “60 days” / `BACKFILL_DAYS = 60` in operator-facing docs; update callouts to **7** where they describe the public default.  
1.3 Leave private repo `BACKFILL_DAYS` unchanged in this guide.

### Phase 2 — README: default vs optional live path

2.1 Keep top-of-README public sibling framing (fixtures default; optional advanced path).  
2.2 Ensure Quick Start **leads** with fixture ingest + search + eval; sync commands live under a clearly labeled **Optional: BYO YouTube live path** section.  
2.3 Optional section must include, in order:  
    - `cp channels.local.example.json channels.local.json`  
    - edit handles (user’s own; never commit)  
    - note `BACKFILL_DAYS` default **7**  
    - `uv run python -m src.youtube_sync`  
    - ingest from `data/raw/youtube_transcripts/` (or current in-repo ingest path)  
    - search smoke  
2.4 Explicit negatives: no auto-sync on clone; live path not required for portfolio demo; do not commit transcripts or `channels.local.json`.  
2.5 Remove or rewrite the README line that says packaging DoD closed but **public GitHub visibility flip still blocked on KB3-exec tip scrub** — that was private-repo flip language. Replace with: public surface is this repo; private archive remains private; optional private scrub is separate hygiene.

### Phase 3 — PORTFOLIO_VISION + ARCHITECTURE honesty (public repo)

3.1 Update `docs/PORTFOLIO_VISION.md`: public sibling = portfolio public surface; KB3-exec scrub of **private** tip history is **not** a blocker for “public AI KB exists.” Mark private archive status honestly.  
3.2 Update `docs/ARCHITECTURE.md` §9 gate 8 (and any parallel “blocks public flip” rows): distinguish **(a)** stranger-runnable public sibling (this repo) vs **(b)** flipping the private remote to public (still would need scrub — out of scope / not the portfolio path).  
3.3 Do not invent CE freeze or “v1 complete” claims.  
3.4 Keep KB1 fixtures + KB2 MCP public allowlist language intact unless wording conflicts with sibling story.

### Phase 4 — Supersede private scrub Guide 03 (honesty only)

4.1 At top of `ai_knowledge_base/docs/dev_guides/2026-07-14_dev_guide_03_kb3_exec_scrub.md`, add a **Superseded for portfolio public story** banner pointing to this public guide path.  
4.2 Same banner / status note on private context summary.  
4.3 Do **not** delete the scrub guide; it remains optional private hygiene if Tom later authorizes A|B scrub.  
4.4 Optional one-line pointer in private README/PORTFOLIO_VISION: public portfolio surface lives in sibling repo (path/URL).

### Phase 5 — Verification (fixture default)

5.1 From clean public clone semantics (or fresh venv): `uv sync` → `ollama pull nomic-embed-text` (if needed) → `uv run python -m src.ingest --fixtures` → search one known fixture query → expect hits.  
5.2 Confirm DoD does **not** require running `youtube_sync` for green.  
5.3 Confirm `BACKFILL_DAYS == 7` in `src/config.py`.  
5.4 Confirm no `channels.local.json` committed (`git status` / `git ls-files`).  
5.5 Confirm README + VISION + ARCHITECTURE no longer claim private KB3-exec scrub blocks having a public AI KB surface.  
5.6 Optional manual only (not CI): BYO one public channel + sync — document pass/fail in Implement note; failure of live path must **not** fail fixture DoD.

### Phase 6 — Stop

6.1 Record Implement evidence in a dated hub/spoke note.  
6.2 Do not flip private remote visibility. Do not scrub private tips unless separate authorize.

---

## Definition of Done

- [ ] Public `BACKFILL_DAYS = 7`  
- [ ] README: fixture-first Quick Start + explicit optional BYO live path (7-day) + no auto-sync claim  
- [ ] Public PORTFOLIO_VISION + ARCHITECTURE gate-8 language match sibling strategy  
- [ ] Private scrub Guide 03 + context marked superseded for portfolio public story (files retained)  
- [ ] Fixture ingest + search smoke green without YouTube  
- [ ] No committed `channels.local.json` / raw transcripts / secrets  
- [ ] Private tip transcripts untouched  
- [ ] Implement note written; Ready≠done until Review  

---

## Blast radius and risks

| Risk | Mitigation |
|------|------------|
| Reviewers think live sync is required | README structure + CI fixture-only |
| Copyrighted transcripts committed | `.gitignore` + review checklist + docs |
| Private scrub still looks like Guide 03 SSOT | Supersession banners |
| Private BACKFILL accidentally changed | Guide forbids touching private config default |
| Over-claiming “public flip complete” on private remote | Docs distinguish sibling vs private visibility |

**Rollback:** revert the single Implement commit(s) on public (+ supersession banner commit on private). No history rewrite.

---

## Edge-case handling

| Case | Expected behavior |
|------|-------------------|
| No `channels.local.json` | Fixtures work; sync fails closed / no-op with clear messaging |
| yt-dlp / network fail | Live path fails; fixture DoD still pass |
| Empty overlay channels | Sync does nothing useful; fixtures still work |
| User sets BACKFILL to 60 locally | Allowed as local edit; not public default |
| Someone opens private scrub guide | Banner redirects to public Guide 03 for portfolio story |

---

## Out of scope

- Executing private tip-delete or filter-repo  
- Flipping `ai_knowledge_base` to public  
- Auto-populate on clone  
- CE ranking freeze / hit@K lift claims  
- Changing private `BACKFILL_DAYS` default  
- Eyeglass / Ford / other repos  

---

## QUALITY_STANDARD §5

- [x] Assumptions eliminated via locked pins  
- [x] Blast radius and edges listed  
- [x] Steps + DoD executable without inventing material policy  
- [x] No code implemented in Write stage  
