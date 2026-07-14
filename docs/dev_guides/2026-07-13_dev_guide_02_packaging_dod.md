# Dev Guide 02 — Packaging DoD (LICENSE, channel overlay, path hygiene)

**Date:** 2026-07-13  
**Repo:** `ai_knowledge_base`  
**Work item:** Packaging DoD — MIT `LICENSE`, empty committed channel default, ignored local overlay, owner-path hygiene  
**Stage that authored this:** Write → Refine-dev-guide (pass 17)  
**Status:** Review complete — shippable as-is (pass 23); packaging ≠ public flip  
**Context SSOT:** `docs/2026-07-13_guide02_packaging_dod_context_summary.md`  
**Aligned to:** `docs/ARCHITECTURE.md` KB1 / §7 / §9; `docs/PORTFOLIO_VISION.md` packaging rows  

**Post-Implement note:** Packaging DoD met. Do **not** scrub tips, rewrite history, or flip GitHub visibility. Packaging ≠ public flip (KB3-exec still open).

---

## Objective

Close the **stranger-default packaging** gap that Guide 01 deliberately left open: a clone must not inherit personal YouTube taste, a missing MIT license artifact, or owner absolute paths in packaging surfaces — while the owner’s private sync continues via an **ignored local overlay**.

**Done story for Implement of this guide:** root MIT `LICENSE` matches README; committed `YOUTUBE_CHANNELS = []`; effective channels load from ignored `channels.local.json` when present; `.gitignore` + optional example file; `mcp-config.example.json` uses portable cwd; launchd plist is templatized (no `/Users/tom/...`); persist UX points at the overlay; README documents public default vs private overlay; docs honesty updated (packaging DoD ≠ public flip). Fixture-first smoke path unchanged.

This is **not** KB3-exec, **not** a visibility flip, and **not** a ranking/CE change.

---

## Learning notes

- **Ignored local overlay:** Committed `config.py` holds the *product default* (empty channel list — safe for any clone). `channels.local.json` is a *personal preference file* that git refuses to publish — same idea as `.env`, different content type. Sync/MCP status read the overlay when present; the public story never needs it.  
- **Packaging DoD ≠ public flip:** Closing LICENSE + overlay + path hygiene proves “stranger clone is honest.” It does **not** prove “repo is ready to make public.” Public visibility still needs KB3-exec tip scrub (and hub D9 order). Docs after Implement must say packaging closed, flip still blocked.  
- **Fail-closed overlay parse:** Missing overlay → empty channels (OK). Present but corrupt → hard error with path (do not silently treat as empty). That is packaging’s analogue of retrieval fail-closed on identity mismatch.  
- **Wrong-surface gate row:** PORTFOLIO_VISION still blames README for a personal MCP path; README is already portable — the live leak is `mcp-config.example.json`. Fix the row when docs update so the next agent does not chase a ghost.

---

## References (paths only)

- `ai_knowledge_base/docs/2026-07-13_guide02_packaging_dod_context_summary.md` (SSOT for soft pins)
- `ai_knowledge_base/docs/ARCHITECTURE.md` (KB1, §7 public vs private, §9 gate table)
- `ai_knowledge_base/docs/PORTFOLIO_VISION.md` (§2 channel debt; §4 packaging gate rows)
- `ai_knowledge_base/README.md` (MIT claim; fixture-first; MCP cwd placeholder)
- `ai_knowledge_base/docs/dev_guides/2026-07-12_dev_guide_01_retrieval_spine_hybrid_ce.md` (slice done; packaging out of Guide 01)
- `ai_knowledge_base/docs/2026-07-12_ce_keep_note.md` (do not reopen CE policy)
- `ai_knowledge_base/src/config.py` (committed personal `YOUTUBE_CHANNELS` — **23** handles)
- `ai_knowledge_base/src/youtube_sync.py` (reads channels; persist hint → `config.py`)
- `ai_knowledge_base/src/mcp_server.py` (`tracked_channels`; private `add_channel` persist note)
- `ai_knowledge_base/mcp-config.example.json` (owner absolute `cwd`)
- `ai_knowledge_base/scripts/com.aikb.youtube-sync.plist` (owner absolute paths ×4)
- `ai_knowledge_base/scripts/sync_youtube.sh` (portable `SCRIPT_DIR` — keep pattern)
- `ai_knowledge_base/.gitignore`
- `ai_knowledge_base/pyproject.toml` (optional `license` field)
- `second_brain/docs/2026-07-13_ai_kb_prioritize_next_work_pass12.md` (packaging = #1)
- `second_brain/docs/2026-07-13_ai_kb_align_docs_pass10.md` (LICENSE yes; overlay yes)
- `second_brain/docs/workflow_os/rails/QUALITY_STANDARD.md`

---

## Architecture constraints (binding)

1. **KB1:** Public committed default = **no personal channels**. Personal list lives only in an **ignored** local overlay. Fixture smoke must not require the overlay.  
2. **KB4 / Guide 01 spine:** Do **not** change retrieval ranking, CE defaults, identity schema, or fixture corpus behavior. Packaging is orthogonal to the ranking slice.  
3. **License honesty:** README already claims MIT; Implement must add a root `LICENSE` file whose text matches that claim. Optional: add `license` metadata in `pyproject.toml` in the same slice.  
4. **Path honesty:** Tracked packaging/example/ops surfaces must not contain owner absolute paths (`/Users/tom/...`). Prefer `/path/to/ai_knowledge_base` or `$REPO_ROOT` placeholders.  
5. **Public vs private (ARCHITECTURE §7):** Channels empty in public default; overlay private/local; sync/launchd not required for stranger smoke.  
6. **Fixture-first stranger path unchanged:** `uv sync` → Ollama `nomic-embed-text` → `uv run python -m src.ingest --fixtures` → search/eval. Personal sync remains optional private ops.  
7. **Hard non-goals (do not expand Implement of this guide):** KB3-exec tip scrub / history rewrite; public GitHub visibility flip; CE/ranking changes; January rewrite; FastAPI/Postgres; sync `no_subs` semantics; discover rename; `ingest.py` split.  
8. **Packaging ≠ flip:** After Implement, docs must state packaging DoD met and visibility flip still blocked on KB3-exec (+ hub sequencing).  
9. Prefer ≤300 lines/file (hard max 400). Smallest correct change; no speculative overlay write-back framework.

### Locked knobs (pinned defaults — soft pins from pass 15 / Write)

| Knob | Pinned default | Tradeoff / notes |
|------|----------------|------------------|
| **Committed channels** | `YOUTUBE_CHANNELS = []` | Empty is more honest than fictional handles; strangers see `tracked_channels: 0`. |
| **Overlay path** | Repo-root `channels.local.json` | Simple discoverability; one gitignore line. Not under `data/` (data/ is corpus-ish). |
| **Overlay format** | JSON array of `{"handle": "@...", "description": "..."}` objects | Prefer JSON over `config.local.py` — no import side effects; easy to validate. |
| **Example file** | Commit `channels.local.example.json` with `[]` or 1–2 **placeholder** handles (not personal) | Helps strangers; never copy real 23-list into git. |
| **`.gitignore`** | Ignore `channels.local.json` (and `config.local.py` if mentioned defensively) | Prevent accidental commit of personal taste. |
| **Overlay load** | In `config.py` (or thin helper imported by config): if file missing → `[]`; if present+valid → replace effective list; if present+invalid → **fail closed** with path + reason. Map JSON objects to the same tuple/list shape callers already expect (`(handle, description)` or documented equivalent) so `youtube_sync` / `mcp_server` need minimal churn. | Missing OK; corrupt not silent. |
| **Duplicate handles** | Dedupe by handle (case-insensitive), keep first description | Simpler than reject for DoD; document in comment. |
| **LICENSE copyright** | `Copyright (c) 2026 Tom Chacko` | Human may override string before/during Implement; do not invent a different holder without ask. |
| **MIT text** | Standard MIT license body | Align README “MIT”; GitHub license detector expects root `LICENSE`. |
| **`pyproject.toml` license** | Optional in same PR: SPDX `MIT` / license field | Nice hygiene; not a blocker if README+LICENSE match. |
| **MCP example cwd** | `"/path/to/ai_knowledge_base"` in `mcp-config.example.json` | Match README already-portable example. |
| **Launchd plist** | **Templatize in-repo** with `$REPO_ROOT` (or `REPLACE_WITH_REPO_ROOT`) placeholders + short README/private-ops note on how to substitute | Prefer template over “delete from public story.” Do **not** leave `/Users/tom/...`. Launchd remains macOS private ops — not required for fixture smoke. |
| **Operator docs** | **README-only** (public default vs private overlay + migrate note) | `GETTING_STARTED.md` **not** required for this guide’s DoD. |
| **Persist UX** | Point `youtube_sync` + private MCP `add_channel` notes at editing `channels.local.json` | Write-to-overlay API is **nice-to-have**, not DoD. Runtime append may stay non-durable if noted clearly. |
| **Owner migrate** | One-time **local-only** copy of current **23** handles into `channels.local.json` during Implement (operator step) | **Never commit** the real list. Count is **23**, not 24. |
| **PORTFOLIO_VISION MCP row** | Docs touch in same Implement PR (or explicit Align-docs follow-on called out in PR): blame `mcp-config.example.json`, not README | Wrong-surface fix. |
| **Guide 01 owner `cd`** | Optional P2 hygiene only — not required for DoD | Historical verification snippet. |

---

## Ordered step checklist

### Phase A — License artifact

- [x] **A1.** Add root `LICENSE` with standard MIT text; copyright line `Copyright (c) 2026 Tom Chacko` (or human-overridden string if provided before Implement).  
- [x] **A2.** Update README License section: remove “still to be added”; keep MIT; do **not** claim public flip complete.  
- [x] **A3.** Optional: add matching license metadata to `pyproject.toml` if trivial in the same PR.

### Phase B — Empty default + ignored overlay

- [x] **B1.** Replace committed `YOUTUBE_CHANNELS` in `src/config.py` with `[]`. Remove personal `@handle` tuples from git. Keep a short comment pointing at the overlay path.  
- [x] **B2.** Add load logic so the **effective** channel list is: overlay contents if `channels.local.json` exists and parses; else `[]`. Expose one name callers already use (`config.YOUTUBE_CHANNELS` or a documented getter that all callers use — prefer keeping `YOUTUBE_CHANNELS` as the effective list after load so `youtube_sync` / `mcp_server` need minimal call-site churn).  
- [x] **B3.** Overlay schema: JSON array of objects `{"handle": string, "description": string}`. Validate types; require non-empty `handle`. Dedupe handles case-insensitively (first wins).  
- [x] **B4.** Fail closed: if `channels.local.json` exists but is invalid JSON / wrong shape → raise/print clear error including absolute or repo-relative path; do **not** silently fall back to `[]` without message.  
- [x] **B5.** Add `channels.local.json` to `.gitignore`. Optionally also ignore `config.local.py` as defensive documentation of the rejected alternate.  
- [x] **B6.** Commit `channels.local.example.json` with `[]` or placeholder-only entries + one-line comment in README on copy → `channels.local.json`.  
- [x] **B7.** **Local-only migrate (operator, not committed):** during Implement on the owner machine, write the prior **23** channels into ignored `channels.local.json` so private sync continuity is preserved. Verify `git status` does **not** stage that file.

### Phase C — Path hygiene

- [x] **C1.** Fix `mcp-config.example.json`: set `"cwd": "/path/to/ai_knowledge_base"`. Confirm no `/Users/tom` remains in that file.  
- [x] **C2.** Templatize `scripts/com.aikb.youtube-sync.plist`: replace all four owner absolute paths with `$REPO_ROOT` / `REPLACE_WITH_REPO_ROOT` placeholders (ProgramArguments script path, stdout/stderr logs, WorkingDirectory). Add a short comment block at top of plist **or** README private-ops subsection: “replace placeholders with your clone path before `launchctl load`; macOS-only; not required for fixture smoke.”  
- [x] **C3.** Re-grep tracked files for `/Users/tom` (exclude this guide / context docs if they cite inventory). Remaining hits should be zero on packaging surfaces, or only optional historical guide 01 `cd` (P2).

### Phase D — Persist UX + status honesty

- [x] **D1.** Update `youtube_sync.py` operator message: point “add a channel” at editing ignored `channels.local.json` (not `src/config.py`).  
- [x] **D2.** Update private MCP `add_channel` persist `note` in `mcp_server.py` to the same overlay path. Runtime in-memory append may remain non-durable for DoD; note must not teach editing committed config.  
- [x] **D3.** Confirm `get_status` `tracked_channels` reflects effective list length (0 without overlay; N with overlay). Document expected stranger behavior: `0`.

### Phase E — Docs honesty (packaging closed ≠ flip)

- [x] **E1.** README: short “Public default vs private overlay” note — empty committed channels; copy example → `channels.local.json`; fixture-first unchanged; personal sync optional.  
- [x] **E2.** Update `docs/PORTFOLIO_VISION.md` §4: LICENSE / channels / MCP cwd rows to reflect post-Implement truth; fix MCP row to name **`mcp-config.example.json`** (not README) as the surface that was wrong; state packaging DoD ≠ visibility flip.  
- [x] **E3.** Update `docs/ARCHITECTURE.md` §7 / §9 packaging rows for LICENSE + overlay closed (or “closed in Guide 02”) while KB3-exec / flip remain open.  
- [x] **E4.** Do **not** create `GETTING_STARTED.md` unless human overrides this pin.  
- [x] **E5.** Stop. Do **not** scrub tip transcripts, rewrite history, or flip GitHub visibility.

### Phase F — Verification wiring

- [x] **F1.** Re-grep `tests/` for `YOUTUBE_CHANNELS` / channel assumptions; add a small unit test if useful: missing overlay → `[]`; valid overlay → loaded; invalid overlay → fails closed. Prefer temp files; do not require personal corpus.  
- [x] **F2.** Fixture-first smoke still works with empty channels (ingest `--fixtures`, search/eval, public MCP status with `tracked_channels: 0`).  
- [x] **F3.** Confirm `channels.local.json` is ignored (`git check-ignore -v channels.local.json` after local create).

---

## Verification / Definition of Done (this guide)

**Done when all are true:**

1. Root `LICENSE` exists with MIT text; README MIT claim no longer says “still to be added.”  
2. Committed `src/config.py` has `YOUTUBE_CHANNELS = []` (no personal handles in git).  
3. Effective channels load from ignored repo-root `channels.local.json` when present; missing → empty; invalid → fail closed with clear error.  
4. `.gitignore` ignores `channels.local.json`; committed `channels.local.example.json` has placeholders/`[]` only.  
5. `mcp-config.example.json` cwd is `/path/to/ai_knowledge_base` (no owner path).  
6. Launchd plist has **no** `/Users/tom/...`; uses `$REPO_ROOT` / replace-me placeholders + documented substitution; fixture smoke does not require launchd.  
7. Persist / add-channel operator copy points at the overlay, not committed `config.py`.  
8. README documents public default vs private overlay; fixture-first stranger path unchanged.  
9. PORTFOLIO_VISION / ARCHITECTURE packaging rows updated; MCP wrong-surface row corrected; docs state packaging DoD ≠ public flip.  
10. Owner’s **23** channels exist only in local ignored overlay (if migrate step run) — **not** committed.  
11. No KB3-exec tip deletion/history rewrite; no GitHub visibility flip; no CE/ranking code changes in the Guide 02 diff.

**Explicitly not required for this guide’s DoD:**

- `GETTING_STARTED.md`  
- Durable write-to-overlay from private MCP `add_channel`  
- Deleting or privatizing the plist from the repo (templatize is the pin)  
- Guide 01 verification `cd` path cleanup (optional P2)  
- KB3-exec / public flip / CE policy / ranking changes  
- Committing any personal channel list

---

## Blast radius and risks

| Risk | Blast radius | Mitigation in steps |
|------|----------------|---------------------|
| Empty channels without overlay migrate | Owner sync tracks nothing after pull | B7 local-only migrate; document before emptying default |
| Silent corrupt overlay → empty | Operator thinks sync “works” with 0 channels | B4 fail closed |
| Accidental commit of real channel list | Privacy / packaging failure | B5 gitignore; B6 example only; B7 verify `git status` |
| Plist still has owner paths | Stranger “installs” broken launchd; unprofessional clone | C2 templatize; C3 ripgrep |
| Persist UX still says edit `config.py` | Re-teaches anti-KB1 pattern | D1–D2 |
| Docs claim “public ready” | False flip readiness | E2–E3; DoD #9 |
| Scope creep to KB3 scrub | Irreversible tip/history work | E5; hard non-goals |
| Test suite assumes non-empty channels | CI/local failures | F1 (pass 14: no hits found; re-check) |
| Wrong LICENSE / copyright string | Legal confusion | A1 standard MIT + pinned holder (human override allowed) |
| Wrong-surface VISION row left stale | Next agent chases README ghost | E2 |

**Blast angles (QUALITY_STANDARD):** (1) stranger clone experience; (2) owner private sync continuity; (3) license/legal clarity; (4) interviewer packaging honesty; (5) future maintainer — where personal channels live.

### Rollback (pass 18 — for Ready check)

**Rollback** = git revert the packaging PR (LICENSE, empty default, overlay load, path hygiene, docs). Owner keeps local `channels.local.json` (ignored) so private sync can continue after revert **if** they temporarily restore committed handles or keep overlay load from a patched branch — document that revert restores personal handles into `config.py` only if that file is reverted. Do **not** flip GitHub visibility as part of this guide (nothing to un-flip). Tip corpus untouched.

---

## Edge-case handling (must appear in implementation or DoD)

| Edge case | Expected behavior |
|-----------|-------------------|
| Overlay **missing** | Effective channels = `[]`; sync no-ops or clear “no channels”; fixture ingest/search/eval still work |
| Overlay **present + empty array** | Same as missing (honest empty) |
| Overlay **present + malformed JSON** | Fail closed; error names path |
| Overlay **wrong shape** (object instead of array, missing `handle`) | Fail closed; actionable message |
| Duplicate handles in overlay | Dedupe case-insensitive; keep first description |
| `get_status` without overlay | `tracked_channels: 0` |
| Private `add_channel` runtime append | May be non-durable; note must say edit `channels.local.json` — not `config.py` |
| Launchd on machine without substituted paths | Must not be required for fixture smoke; README says private/macOS-only |
| Windows/Linux strangers | Plist is macOS private ops only; packaging DoD does not depend on launchd |
| Concurrent edit of overlay during sync | Accept eventual consistency; no lock framework in this slice |
| `channels.local.json` accidentally staged | Implementer must unstage; gitignore must catch normal `git add .` |
| MIT year / copyright override | Human may change holder string; do not invent alternate without ask |

---

## Stop / non-goals

**Stop when** this guide’s DoD is met after authorized Implement.

**Do not** in Write or Implement of this guide:

- Create/scrub tip transcripts or run `git filter-repo` (KB3-exec)  
- Flip GitHub visibility / claim public-complete  
- Change CE enable default, ranking spine, fusion, or eval lift claims  
- Add `GETTING_STARTED.md` unless human overrides  
- Commit personal channel handles (the **23**-list stays local-only)  
- Expand into sync `no_subs`, discover rename, ingest split, FastAPI/Postgres, January rewrite  

**Write stage specifically:** do **not** create the `LICENSE` file, empty `YOUTUBE_CHANNELS`, edit `config.py`, or change gitignore/plist/examples — that is Implement.

---

## Open decisions pinned (defaults)

| Decision | Pin | Human override? |
|----------|-----|-----------------|
| Overlay format/path | `channels.local.json` at repo root | Yes — say so before Implement |
| Committed default | Empty `[]` | Yes |
| Launchd strategy | Templatize with `$REPO_ROOT` + docs | Yes (private-only docs alternative only if human rejects template) |
| Operator onboarding | README-only; no `GETTING_STARTED` required | Yes |
| MIT copyright | `Tom Chacko` | Yes |
| Migrate 23 channels | Local-only operator step during Implement | N/A — never commit |
| Write-to-overlay API | Out of DoD | Nice-to-have later |

---

## Suggested verification commands (implementer)

```bash
cd /path/to/ai_knowledge_base
uv sync
# License present
test -f LICENSE && head -n 5 LICENSE
# No personal handles in committed config
rg -n 'YOUTUBE_CHANNELS|@' src/config.py
# No owner paths on packaging surfaces
rg -n '/Users/tom' mcp-config.example.json scripts/com.aikb.youtube-sync.plist
# Overlay ignored
cp channels.local.example.json channels.local.json   # then populate locally; never commit
git check-ignore -v channels.local.json
# Fixture-first still works with empty committed channels
uv run python -m src.ingest --fixtures
uv run pytest -q
# Optional: status shows 0 without overlay / N with overlay
```

Expected signals: MIT `LICENSE` on disk; committed channels empty; overlay load + fail-closed covered; mcp example portable; plist templatized; README + VISION/ARCHITECTURE honesty; no tip scrub; no visibility flip in the PR.

---

## Refine pass 18 (hub verify)

**Checked:** completeness, order A–F, DoD, blast/edges, KB3/flip non-goals; Ready-check preview (rollback).

**Material edits:** Explicit **Rollback** subsection. Overlay→tuple shape pin from pass 17 unchanged.

**Honest call:** **Ready check next**. Still **not** authorized to Implement / scrub / flip.

**Readiness score (Refine preview, /10):** **9.1** — packaging DoD clear; residual is owner migrate craft + optional copyright string.

---

## Honest readiness (Implement pass 22)

- **Guide DoD met?** **Yes** — LICENSE, empty default + overlay, path hygiene, persist UX, docs honesty, tests.  
- **Ready for public flip?** **No** — packaging DoD ≠ KB3-exec.  
- **Next:** Hub fan-in → Review stage when authorized (not this spoke).
