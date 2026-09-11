# Session: Set the project contact address

**ID:** 2026-09-11-04-set-the-project-contact-address
**Started:** 2026-09-11
**Ended:** 2026-09-11
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Replace the personal contact address with the project address the maintainer
chose: `info@rootedglobal.co`. This was the exact next step left by sessions 02
and 03, blocked until an address existed.

## Starting state

Branch `main`, last commit `c1f3cc3`, clean tree. `kishor3947@gmail.com` was
published on every page of the site and in the application's Support panel.

## What was done

**The address is now `info@rootedglobal.co`** in the two places that define it:
`contact_email` in `docs/_data/support.yml` for the site, and `contactEmail` in
`apps/web/src/support.ts` for the application. Nothing else hardcodes it — the
footer, `/support/` and every generated page read the data file.

**The previous sessions' list of places to change was wrong in both directions.**

*`project.json` was on the list and should not have been.* Its `author.email` is
the **git commit identity** — `scripts/set_identity.py` writes it into the local
git config (D-015), nothing reads it as a contact address, and it does not reach
the site or the application. Put to the maintainer as a separate question, since
changing it changes who future commits are authored by: **deliberately left as
`kishor3947@gmail.com`**, so the history keeps one author.

*`App.test.tsx` was on the list and should not need to be.* The test named the
address inside a regex, so changing the address broke a test that was not about
the address. It now asserts against `SUPPORT.contactEmail` — that the panel
shows whoever the configuration says to write to. That is the property worth
testing; the value is configuration.

**D-044 records the choice**, including why not `mindarchive.app` (no DNS — an
address there would bounce), why the value is unavoidably defined twice (Jekyll
cannot read TypeScript, Vite cannot read Jekyll's data files), and why
`project.json` is not a third place.

## Decisions made

**D-044 — the published contact address is `info@rootedglobal.co`.** Accepted.
Indexed in `docs/DECISIONS.md`.

## Files changed

```
modified: docs/_data/support.yml            (contact_email)
modified: apps/web/src/support.ts           (contactEmail; stale comment about project.json)
modified: apps/web/src/App.test.tsx         (assert the configured value, not a copy)
modified: docs/DECISIONS.md                 (D-044 in the index)
modified: project-memory/DECISIONS.md       (D-044)
modified: project-memory/PROJECT_STATE.md   (the address, and where it is defined)
added:    project-memory/sessions/2026-09-11-04-set-the-project-contact-address/
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Frontend tests | `python scripts/dev.py test frontend` | **107 passed** |
| Lint | `python scripts/dev.py lint` | **Passed** |
| Types | `python scripts/dev.py types` | **Passed** |
| Generated pages | `scripts/sync_site_pages.py` | 11 pages |
| Site links | `scripts/check_site_links.py` | **0 problems — 34 routes** |
| Site build | `jekyll build` in Docker | **Passed** — 33 pages |
| The address as published | grep every `mailto:` in the built site | **`info@rootedglobal.co` everywhere; no trace of the old address** |

Backend was not touched, so the backend suite was not re-run in this session; it
passed in full an hour earlier under `verify` (310 tests).

## What remains

Nothing from this session. The mailbox is assumed to exist — that was the
maintainer's call and it was not tested from here, since nothing in this
repository sends mail.

## Exact next step

Milestone 6 work, or whatever the maintainer chooses next. The contact address
question that has closed the last three session records is closed.
