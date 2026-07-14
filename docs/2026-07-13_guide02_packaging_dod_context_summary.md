# Context: Guide 02 — packaging DoD (LICENSE, personal-channel ignored overlay, owner-path hygiene)

**Date:** 2026-07-13  
**Repos:** `ai_knowledge_base` (+ program notes in `second_brain` for sequencing only)  
**Status:** Ready for dev guide  
**Mode last used:** spoke  
**Stage:** Refine context (pass 15 verify; pass 14 refine) — prior Gather = pass 13  
**Handoff:** `second_brain/docs/2026-07-13_ai_kb_refine_context_guide02_pass14_handoff.md`  
**Shared rules:** `second_brain/docs/2026-07-13_refine_context_guide02_pass14_shared_handoff.md` (Spoke C)  
**Lens:** Staff AI eng — stranger-default packaging vs Guide 01 slice-done; public-claim honesty before KB3-exec / visibility flip  
**Out of this stage:** Scrub execution, Write-dev-guide body, Implement, public GitHub flip, January rewrite, CE eval expansion, product Guide 02+ (sync/`no_subs`, ingest split)

---

## Problem

Guide 01 proved an honest **retrieval vertical slice** (fixtures → hybrid → fusion → pluggable CE → RO MCP → eval stub). That does **not** prove a **stranger-default packaging** story.

Today a clone still inherits:

1. **No `LICENSE` file** while README claims MIT — license ambiguity for portfolio reviewers and redistributors.  
2. **Personal taste as committed default** — `src/config.py` hardcodes **23** personal `@handle`s in `YOUTUBE_CHANNELS` (KB1 wants empty/illustrative committed default + **ignored** local overlay).  
3. **Owner absolute paths** still tracked in packaging-adjacent files (`mcp-config.example.json`, `scripts/com.aikb.youtube-sync.plist`; guide 01 verification snippet also uses an owner `cd` path).  
4. **`.gitignore` has no overlay ignore rules** for `config.local.py` / `channels.local.json` (or equivalent).  
5. **Private-ops UX still points at editing committed config** (`youtube_sync` / private MCP `add_channel` “persist → edit `src/config.py`”).

Pass 12 ranked this packaging DoD as **#1 next engineering work** — before KB3-exec scrub (#2) and before any product “guide 02+” (#4). Gather (pass 13) scoped **Guide 02** as that packaging slice only; Refine (pass 14) re-verified the inventory — still not tip scrub / visibility flip.

---

## Acceptance criteria

- [ ] Root `LICENSE` file exists and matches the MIT claim in README (and optionally `pyproject.toml` license metadata if added in the same slice).  
- [ ] Committed public default for channels is **empty or illustrative non-personal** — no personal handle list in `src/config.py` as the stranger default (KB1).  
- [ ] Personal channel list loads from an **ignored** overlay (e.g. `channels.local.json` or `config.local.py`) when present; fixture-first smoke and public MCP status do **not** require it.  
- [ ] `.gitignore` ignores the chosen overlay path(s); committed example/template (if any) uses placeholders only.  
- [ ] Tracked public packaging surfaces have **no** owner absolute paths: at least `mcp-config.example.json`; README MCP example stays portable (already `/path/to/...`); launchd plist either templatized / private-only documented / removed from “public story.”  
- [ ] Private-ops copy (`youtube_sync`, private MCP persist note) points at the overlay, not “edit committed `config.py`.”  
- [ ] Docs honesty: PORTFOLIO_VISION / ARCHITECTURE §9 packaging rows updated when Implement lands (or called out as Align-docs follow-on) — **not** claiming public flip complete.  
- [ ] **No** KB3-exec tip deletion / history rewrite in this guide’s Implement.  
- [ ] **No** public GitHub visibility flip in this guide’s Implement.  
- [ ] Fixture-first smoke path remains the documented stranger path (`uv sync` → `nomic-embed-text` → `--fixtures` → search/eval).

---

## In scope

- Add MIT `LICENSE` (README already states MIT; file missing).  
- Channel default + ignored overlay load path (KB1 half still open).  
- Owner-path hygiene on committed packaging/example/ops surfaces inventored below.  
- Minimal caller updates so sync / private MCP / status do not assume personal channels live in committed defaults.  
- Short README / packaging notes for “public default vs private overlay” (no full GETTING_STARTED rewrite required unless guide pins it).  
- Explicit non-goals and DoD for Write-dev-guide → Implement of **Guide 02 packaging only**.

---

## Out of scope

- **KB3-exec** tip-transcript scrub / tip deletion vs `git filter-repo` (ARCHITECTURE §10; pass 12 #2).  
- Public GitHub **visibility flip** (pass 12 #5; needs packaging + KB3-exec).  
- Larger CE eval / flip `CE_ENABLED` default (`ce_keep_note`; pass 12 #3 / pass 10 decision #5).  
- Product follow-ons: sync `no_subs` semantics, discover rename `clusters` → `by_channel`, `ingest.py` line-count split (pass 9 R1).  
- January clean rewrite / embedding migration / FastAPI / Postgres.  
- Authoring essay-quality fixtures (fixtures already done).  
- Changing ranking spine behavior (Guide 01 done).  
- Cross-repo portfolio D9 flip order (hub-owned).

---

## Prior art (paths only)

### Binding / intent

- `ai_knowledge_base/docs/PORTFOLIO_VISION.md` — public packaging intent; open LICENSE / channels / MCP path rows  
- `ai_knowledge_base/docs/ARCHITECTURE.md` — KB1–KB5; §7 public vs private; §9 gate table (LICENSE + overlay still open)  
- `ai_knowledge_base/README.md` — MIT claim; fixture-first; MCP cwd placeholder; LICENSE “still to be added”  
- `ai_knowledge_base/docs/2026-07-12_ce_keep_note.md` — CE seam kept; no lift ads (orthogonal; do not reopen)  
- `ai_knowledge_base/docs/dev_guides/2026-07-12_dev_guide_01_retrieval_spine_hybrid_ce.md` — slice DoD met; packaging explicitly out of Guide 01  

### Sequencing / decisions

- `second_brain/docs/2026-07-13_ai_kb_prioritize_next_work_pass12.md` — packaging DoD = #1 next  
- `second_brain/docs/2026-07-13_ai_kb_align_docs_pass10.md` — human decisions: LICENSE yes; overlay yes; KB3 after packaging checklist  
- `second_brain/docs/2026-07-12_portfolio_vision_workspace_and_decisions.md` — KB1–KB5 SSOT (load as needed at Write)  

### Debt surfaces (code / tracked files)

- `ai_knowledge_base/src/config.py` — committed personal `YOUTUBE_CHANNELS`  
- `ai_knowledge_base/src/youtube_sync.py` — reads `config.YOUTUBE_CHANNELS`; persist hint → edit `config.py`  
- `ai_knowledge_base/src/mcp_server.py` — `tracked_channels` length; private `add_channel` persist note → `config.py`  
- `ai_knowledge_base/mcp-config.example.json` — owner absolute `cwd`  
- `ai_knowledge_base/scripts/com.aikb.youtube-sync.plist` — owner absolute ProgramArguments / WorkingDirectory / log paths  
- `ai_knowledge_base/scripts/sync_youtube.sh` — portable relative `SCRIPT_DIR` (good pattern to keep)  
- `ai_knowledge_base/.gitignore` — no overlay ignore entries yet  
- `ai_knowledge_base/pyproject.toml` — no `license` field (optional hygiene)  

### Explicitly not packaging blockers (inventory only)

- Tip third-party transcripts under `docs/2026-01-19_*` — KB3-exec, not Guide 02 Implement  
- `GETTING_STARTED.md` — **absent**; PORTFOLIO_VISION mentions GETTING_STARTED/LICENSE as gate — decide in Write whether README fixture-first is enough or a thin GETTING_STARTED is in DoD  

---

## Evidence file inventory — packaging gaps

| Gap | Evidence (re-verified pass 14) | Severity for packaging DoD |
|-----|----------|----------------------------|
| **No `LICENSE` file** | No `LICENSE*` on disk; `git ls-files` has no license path; README §License: MIT + “still to be added”; `pyproject.toml` has **no** `license` field | **P0** — required for DoD |
| **Personal channels committed** | `src/config.py` lines 44–73: **23** `@handle` tuples (regex count pass 14; Gather said 24 — **corrected**); comment labels “overlay debt”; ARCHITECTURE §7 / PORTFOLIO_VISION §2 | **P0** — KB1 unmet |
| **No ignored overlay mechanism** | No `channels.local.json` / `config.local.py` on disk; `.gitignore` covers data/sync/env only — **not** channel overlay; ARCHITECTURE §7 names overlay as intent only | **P0** — needed to preserve private ops after emptying default |
| **Owner path in MCP example** | Tracked `mcp-config.example.json` → `"cwd": "/Users/tom/Documents/Git/ai_knowledge_base"` | **P0** — stranger-facing packaging surface |
| **Owner paths in launchd plist** | Tracked `scripts/com.aikb.youtube-sync.plist` — **4** absolute `/Users/tom/Documents/Git/ai_knowledge_base/...` (ProgramArguments, stdout/stderr logs, WorkingDirectory) | **P1** — private-ops; templatize, document private-only, or drop from public story |
| **README MCP cwd** | README line ~131: `/path/to/ai_knowledge_base` | **Closed** for README |
| **PORTFOLIO_VISION stale row** | §4 row “MCP example…” notes say “**README** still shows personal path” — **wrong surface**; README fixed; **`mcp-config.example.json` still open** | **P1 docs debt** — fix when packaging docs update (Guide 02 Align touch or same PR) |
| **Guide 01 owner `cd`** | `docs/dev_guides/2026-07-12_dev_guide_01_...` verification block still `cd /Users/tom/...` | **P2** — historical notes; optional hygiene |
| **Persist UX → committed config** | `youtube_sync.py:726` “edit src/config.py”; `mcp_server.py:299` private `add_channel` note same | **P1** — breaks KB1 story after overlay if left unchanged |
| **`get_status` channel count** | `mcp_server.py:240` `len(config.YOUTUBE_CHANNELS)` — after empty default + no overlay → honest `0` | **P1** — document expected behavior |
| **Tests vs empty channels** | `rg YOUTUBE_CHANNELS\|channels` under `tests/` → **no hits** (pass 14) | **Lower risk** than Gather feared; still re-check at Implement |
| **GETTING_STARTED missing** | No `GETTING_STARTED.md` at repo root; VISION public-v1 gate wording still names it | **P2 / open decision** — recommend README-only unless human wants file |
| **KB3 tip inventory still tracked** | Tip-style `docs/2026-01-19_*` still present (inventory only); ARCHITECTURE §10 | **Out of Guide 02** — flip gate, not packaging Implement |
| **CE / nomic honesty** | `ce_keep_note`; README; ARCHITECTURE; guide 01 out-of-scope | **Already aligned** — do not expand Guide 02 into ranking claims |

**`/Users/tom` ripgrep inventory (pass 14, exclude this context file’s own citations):** tracked hits = `mcp-config.example.json`, `scripts/com.aikb.youtube-sync.plist` (×4), guide 01 verification `cd` only.

---

## Risks and blast radius

| Risk | Blast radius | Mitigation in Guide 02 |
|------|--------------|------------------------|
| Emptying channels without overlay load | Owner’s private sync silently tracks nothing after pull | Require ignored overlay + load-before-sync; document one-time migrate copy of current list into overlay (local only; not committed) |
| Overlay format mismatch (JSON vs `.py`) | Import side effects vs parse errors; discoverability | Prefer **JSON/list file** over executable `config.local.py` (simpler, no import surprises); load from `config.py` helper |
| Leaving plist with owner paths | Stranger clones “install” broken launchd; looks unprofessional | Template with `$REPO_ROOT` instructions **or** mark scripts private-only in README; do not claim launchd is stranger-ready |
| LICENSE text wrong / wrong SPDX | Legal confusion | Use standard MIT text; align README “MIT” |
| Scope creep into KB3 scrub | Irreversible tip/history work during packaging | Hard non-goal; inventory stays reference-only |
| Claiming “public ready” after packaging | Flip still blocked on KB3-exec + hub D9 | Docs must say packaging DoD ≠ visibility flip |
| Private MCP still says “edit config.py” | Re-teaches the bad pattern | Update persist note to overlay path |
| Tests assuming non-empty channel list | CI/local test failures | Pass 14: no test references found; re-grep at Implement; fixture smoke must not need channels |

**Blast angles (QUALITY_STANDARD):** (1) stranger clone experience; (2) owner private sync continuity; (3) legal/license clarity; (4) interviewer packaging honesty; (5) future maintainer — where do personal channels live?

---

## Edge cases

- Overlay **missing** → channels = `[]`; sync no-ops or clear “no channels configured”; fixture ingest/search/eval still work.  
- Overlay **present but malformed** → fail closed with clear error (do not silently ignore corrupt file as empty without message).  
- Overlay present + empty list → same as missing (honest empty).  
- Duplicate handles in overlay → dedupe or reject with message (pick one in Write).  
- Private `add_channel` runtime append with empty committed default → still non-durable unless overlay write is in scope; **smallest correct:** update note to “edit ignored overlay”; optional write-to-overlay is **nice-to-have**, not required for DoD.  
- `get_status` on public profile with empty channels → `tracked_channels: 0` is correct.  
- Launchd plist on a machine without owner path → must not be required for fixture smoke.  
- Concurrent edit of overlay while sync runs → accept eventual consistency; no lock framework in this slice.  
- Windows/Linux strangers → plist is macOS-only private ops; do not make packaging DoD depend on launchd.  
- MIT year / copyright holder string — human preference (open decision).

---

## Unknowns (must resolve or escalate)

| Unknown | How to resolve | Blocking? |
|---------|----------------|-----------|
| Overlay file format: `channels.local.json` vs `config.local.py` vs both | Recommend JSON list + gitignore in Write; human can override | **Soft** — recommend default in Write; not blocking Gather |
| Whether to commit `channels.local.example.json` (placeholders) | Write-dev-guide DoD choice; helps strangers | Soft |
| Launchd plist: templatize in-repo vs move to private docs vs delete from public story | Prefer templatize **or** README “private only — replace paths”; do not leave owner paths | Soft for Gather; **must** decide in Write |
| Include thin `GETTING_STARTED.md` in Guide 02 DoD? | PORTFOLIO_VISION wording vs sufficient README; recommend README-only unless human wants file | Soft |
| Copyright holder line for MIT (`Tom Chacko` vs GitHub handle) | Human | Soft — standard MIT file still shippable with chosen name |
| Migrate owner’s current **23** channels into local overlay during Implement? | Local-only file write outside git; optional operator step in guide | Soft — do not commit the list |
| Update PORTFOLIO_VISION “README personal path” row as stale in Align vs in Guide 02 docs touch | Note here; fix when packaging docs update | Soft |

**Not unknown:** LICENSE is missing; personal channels are committed; KB3-exec is out of this guide; Guide 01 is shippable.

---

## Recommended approach

**Smallest correct packaging slice (Guide 02):**

1. **Add** root `LICENSE` (MIT text matching README).  
2. **Replace** committed `YOUTUBE_CHANNELS` with `[]` or a tiny illustrative non-personal example (prefer `[]` for honesty).  
3. **Add** ignored overlay load (recommended: `channels.local.json` under repo root or `data/`, listed in `.gitignore`; optional committed `*.example.json` with `[]` / comments).  
4. **Wire** `config` (or thin helper) so sync/MCP/status read effective channel list = overlay ∪ default.  
5. **Hygiene:** fix `mcp-config.example.json` cwd to `/path/to/ai_knowledge_base`; resolve plist owner paths (template or private-only docs).  
6. **Copy:** point persist/sync hints at overlay; README one-liner for private channels.  
7. **Stop.** No scrub. No flip. No ranking changes. No CE policy change.

**Why this order:** LICENSE is pure add; overlay is the KB1 behavioral fix; path hygiene closes stranger-facing residue. Matches pass 12 #1 and pass 10 human decisions #2–#3.

**Pattern name:** *ignored local overlay* — committed defaults are safe for any clone; machine-specific taste lives in a gitignored file the owner keeps locally (same idea as `.env`, different content type).

---

## Open decisions (human)

1. Overlay format: accept recommendation **`channels.local.json` + gitignore**?  
2. Committed default: empty list vs 1–2 fictional/illustrative handles? (Recommend **empty**.)  
3. Launchd plist strategy: template in-repo vs document-as-private-only vs remove from tracked public story?  
4. Is README fixture-first enough, or must Guide 02 add `GETTING_STARTED.md`? (Recommend **README-only**.)  
5. MIT copyright identity string?  
6. Confirm Guide 02 Implement still **must not** run KB3-exec (recommended: confirm).  
7. When packaging docs update: fix PORTFOLIO_VISION §4 MCP row to name **`mcp-config.example.json`**, not README (README already portable).

---

## Learning notes (Gather pass 13)

**Packaging DoD vs slice DoD.** Guide 01’s DoD asked: “Does one shared retrieval path work on fixtures with honest `ranking_stage`?” Guide 02’s DoD asks: “Can a stranger clone without inheriting your channel taste, license ambiguity, or home-directory paths?” Passing the first does not check the second.

**Ignored overlay.** Think of committed `config.py` as the *product default* (empty channels) and `channels.local.json` as a *personal preference file* git refuses to publish — like leaving your bookmarks out of the app binary. Sync reads the overlay when present; the public story never needs it.

**License claim vs license file.** Saying “MIT” in a README is a *claim*; a root `LICENSE` file is the *artifact* redistributors and GitHub’s license detector expect. Packaging closes the gap between claim and artifact.

**Owner-path residue.** Absolute `/Users/tom/...` in tracked examples is a form of *environment leakage*: it works on one machine and teaches every other clone the wrong `cwd`. Portable placeholders (`/path/to/ai_knowledge_base`) or relative scripts (`sync_youtube.sh` already uses `SCRIPT_DIR`) are the packaging fix.

### Learning notes (Refine pass 14 — new)

**Wrong-surface gate rows.** A checklist can stay “Open” for the right *problem* while blaming the wrong *file*. PORTFOLIO_VISION still says the README MCP path is personal; README is already portable — the live leak is `mcp-config.example.json`. Fixing packaging without correcting that row would leave a false “README debt” for the next agent.

**Count as evidence.** “~24 channels” felt right from a glance; a regex count found **23**. Packaging inventories should prefer countable evidence over approximate memory — interviewers notice off-by-one claims the same way they notice missing LICENSE files.

**Fail-closed overlay parse.** If `channels.local.json` exists but is corrupt, treating it as “no channels” without an error hides operator mistakes (silent empty sync). Prefer: missing → empty OK; present+invalid → hard error with path. That is the packaging analogue of retrieval fail-closed on identity mismatch.

---

## Evidence opened this pass (Gather — pass 13)

- Rails: `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`, `ALWAYS.md`, `LEARNING_MODE.md`  
- Stage/template: `stages/gather-context.md`, `templates/context-summary.md`  
- Handoff: `second_brain/docs/2026-07-13_ai_kb_gather_context_guide02_pass13_handoff.md`  
- Repo truth: `docs/PORTFOLIO_VISION.md`, `docs/ARCHITECTURE.md`, `README.md`, `src/config.py`, `docs/2026-07-12_ce_keep_note.md`, guide 01, `.gitignore`, `mcp-config.example.json`, `scripts/com.aikb.youtube-sync.plist`, `scripts/sync_youtube.sh`, `pyproject.toml`, `src/mcp_server.py` (status + private persist note), `src/youtube_sync.py` (channel consumers)  
- Sequencing: `second_brain/docs/2026-07-13_ai_kb_prioritize_next_work_pass12.md`, `second_brain/docs/2026-07-13_ai_kb_align_docs_pass10.md`  
- Shell inventory: no LICENSE; no GETTING_STARTED; tracked packaging files listed above; `/Users/tom` ripgrep limited to plist + mcp example + guide 01 `cd`

**Did not (Gather):** scrub tip docs; edit product code; write Guide 02 body; flip visibility.

---

## Evidence opened this refine pass (pass 14)

- Rails: QUALITY_STANDARD, ALWAYS, LEARNING_MODE; stage `refine-context.md`; template `context-summary.md`  
- Handoffs: `2026-07-13_ai_kb_refine_context_guide02_pass14_handoff.md`, shared `2026-07-13_refine_context_guide02_pass14_shared_handoff.md` (Spoke C); prior Gather handoff for lineage  
- Re-read / re-check: this context summary; `.gitignore`; `mcp-config.example.json`; `src/config.py` (handle count); `README.md` License + MCP cwd; `pyproject.toml` (no license field); `scripts/com.aikb.youtube-sync.plist`; `scripts/sync_youtube.sh`; `src/mcp_server.py` (`tracked_channels`, `add_channel` note); `src/youtube_sync.py:726`; PORTFOLIO_VISION §4 gate table; ARCHITECTURE KB1/KB3/§7/§9; guide 01 out-of-scope (LICENSE + overlay explicit)  
- Commands: no `LICENSE*` / no git-tracked license; no `GETTING_STARTED.md`; no overlay files on disk; `rg '/Users/tom'` → plist + mcp example + guide 01 `cd`; handle count **23**; `tests/` has no `YOUTUBE_CHANNELS` references; tip `docs/2026-01-19_*` still present (KB3 untouched)

**Did not (Refine):** scrub; Write-dev-guide; Implement; visibility flip; product-code edits.

---

## Evidence opened this refine pass (pass 15 — verify)

**Live re-verify:** `NO_LICENSE`; `YOUTUBE_CHANNELS` count **23**; `/Users/tom` still in `mcp-config.example.json` + `scripts/com.aikb.youtube-sync.plist`.

**Material content changes this pass:** **None.** Pass 14 inventory and soft pins remain accurate.

---

## Honest readiness

- **Ready for Write dev guide?** **Yes** — pass 14 holds; pass 15 live re-verify found **no material gaps**. Soft prefs (overlay format, plist strategy, GETTING_STARTED, copyright string) stay for Write-dev-guide.  
- **Ready for Implement?** **No** — Refine only; need approved Guide 02.  
- **Ready for public flip?** **No** — packaging DoD ≠ KB3-exec; tip inventory still tracked.  
- **Trivial enough to skip Write?** **No** — multi-file behavioral change + hard non-goals vs KB3; guide prevents scope creep.  
- **Pass 15:** Stopped for human — no Write/Implement/scrub/flip.

**Still weak (honest, non-blocking):** soft human prefs unpinned; plist public-story strategy undecided; VISION gate row names wrong file until docs touch; optional `pyproject` license metadata and guide 01 `cd` hygiene are polish. None block Write.

---

## QUALITY_STANDARD §5 (Refine)

- [x] Assumptions re-checked with file evidence; Gather “24 channels” corrected to 23  
- [x] Did not rush; no scrub / no Write / no Implement  
- [x] Mode/Stage/artifacts declared (spoke / Refine / this summary + handoffs)  
- [x] Edge cases retained + fail-closed overlay parse emphasized  
- [x] Blast radius ≥2 angles (stranger clone, owner sync, legal, docs wrong-surface)  
- [x] Findings written here + handoff Results  
- [x] Spoke stayed in Refine / packaging slice; KB3 out of scope  
- [x] Verification = re-inventory (appropriate for Refine)  
- [x] Honest readiness: Write **Yes**; Implement/flip **No**  
- [x] QUALITY_STANDARD not skipped 
