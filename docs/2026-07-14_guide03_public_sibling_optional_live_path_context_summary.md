# Context summary — AI KB Guide 03 re-scope (public sibling + optional live path)

**Date:** 2026-07-14  
**Status:** Refined (pass 35 — pins locked; Write-ready)  
**Repos:** `ai-knowledge-base-public` (primary) + `ai_knowledge_base` (private archive, read-only for this slice)  
**Work item:** Guide 03 re-scope — stranger-run fixtures DoD + optional BYO YouTube live path; retire same-repo history-scrub as default  

**Stage:** Refine context — **done**. Next: Write-dev-guide (same session authorized).  

**Hub decisions:**  
- `second_brain/docs/2026-07-14_ai_kb_public_sibling_decision.md`  
- `second_brain/docs/2026-07-14_ai_kb_public_strategy_options.md`  
- `second_brain/docs/2026-07-14_hub_refresh_guide03_pass34_fan_in.md`  

---

## Problem

Portfolio needs a **public** AI Knowledge Base surface. Private repo still holds tip transcripts + personal research. Strategy locked: **public sibling** (created and pushed), not history rewrite of private remote as the default path.

Guide 03 as authored on private (`dev_guides/2026-07-14_dev_guide_03_kb3_exec_scrub.md`) no longer matches the locked strategy. Executable Guide 03 for the **public** story must cover:

1. Public sibling remains fixture-first and honest  
2. Optional **live path** is documented and configurable so public users *can* sync their own channels (short backfill) if they want  

---

## Locked pins (Refine)

| Pin | Value |
|-----|--------|
| Public surface | `Alpha-W0lf/ai-knowledge-base-public` (local: `ai-knowledge-base-public`) |
| Private archive | Keep `ai_knowledge_base` private; tip transcripts may remain; scrub optional later hygiene only |
| Default DoD path | Fixture ingest + search and/or MCP smoke — **no** YouTube / network to YouTube required |
| Optional live path | BYO `channels.local.json` from example; user’s own handles; never commit Tom’s channel list |
| Public `BACKFILL_DAYS` | **7** (change from current `60` at Implement) |
| Private `BACKFILL_DAYS` | **Leave 60** for now (deep personal backfill); document env/override for shorter windows — do not force-align in this guide |
| Auto-sync on clone | **Forbidden** |
| Old scrub guide | **Superseded for portfolio public story**; keep as optional private hygiene runbook only |
| Visibility flip of private remote | **Out of scope** |

---

## Acceptance criteria (DoD seeds for Write)

- [ ] Default stranger path: fixture ingest + search and/or MCP smoke works **without** YouTube sync or network to YouTube  
- [ ] README documents optional live path end-to-end (copy example → local overlay → own handles → sync → ingest → search) with **7-day** backfill called out  
- [ ] `src/config.py` `BACKFILL_DAYS = 7` on public sibling  
- [ ] PORTFOLIO_VISION / ARCHITECTURE gate-8 / packaging honesty: public sibling = portfolio surface; private archive remains private; scrub-of-private-history **not** required for public story  
- [ ] Private tip transcripts **not** deleted by this guide  
- [ ] No auto-sync on clone; no committed real channel catalog as public default  
- [ ] Tests / CI stay fixture-path only (live path not required in CI)  

---

## In scope / out of scope

**In:** public README/config/docs DoD; optional live-path wiring; status doc honesty; fixture-path network-free verification  

**Out:** force-push / filter-repo on private; public visibility flip of private remote; CE freeze claims; January rewrite; committing personal channels; changing private default BACKFILL unless human later asks  

---

## Prior art (paths)

- `ai-knowledge-base-public/` (GitHub public)  
- `ai_knowledge_base/` private archive  
- `docs/ARCHITECTURE.md`, `docs/PORTFOLIO_VISION.md` (both repos; public copy still says KB3-exec blocks flip — **stale vs sibling strategy**)  
- Old (superseded for default public path): `ai_knowledge_base/docs/dev_guides/2026-07-14_dev_guide_03_kb3_exec_scrub.md`  
- Hub: decision + strategy + pass-34 fan-in above  

---

## Live baselines (pre-Implement)

| Check | Evidence |
|-------|----------|
| Public remote | https://github.com/Alpha-W0lf/ai-knowledge-base-public |
| Fixtures present | `fixtures/` committed on public |
| `BACKFILL_DAYS` | Still **60** in public `src/config.py` — Implement must set **7** |
| README | Mentions optional 7-day path at top; Quick Start still shows sync without pin; LICENSE line still says KB3-exec blocks flip — **honesty lag** |
| Private tip transcripts | Still tracked in private (OK while private) |

---

## Risks / blast radius

| Risk | Mitigation |
|------|------------|
| Live path confused with default | README “default vs optional” callouts; CI only runs fixtures |
| Users paste copyrighted bulk into git | Docs: keep sync under ignored `data/raw/`; never commit transcripts |
| Config default 7 surprises private deep backfill | Private leaves 60; public only changes to 7 |
| Docs still claim KB3-exec blocks “the” public story | Same-delivery Align of PORTFOLIO_VISION + ARCHITECTURE §9 gate 8 language on **public** repo |

---

## Edge cases

- Missing `channels.local.json` → live path fails closed with clear message; fixtures still work  
- yt-dlp / network failure → live path fails honestly; does not fail fixture DoD  
- Empty channel overlay → no sync work; fixtures still work  
- Someone commits `channels.local.json` → reject in review; `.gitignore` already ignores it  

---

## Open decisions

**None material.** Soft residual at Implement: exact README section heading wording and which ARCHITECTURE paragraphs to rewrite vs footnote.

---

## Honest call

**Ready for Write-dev-guide.** Not Implement until Ready check + human Implement authorize.
