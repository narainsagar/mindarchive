# Report — repository audit, 2026-09-11

Produced on request before any change was made: *"list and give me summary report
of whats missing or incorrect or anything thats blocking"*. Read-only; nothing was
modified while it was written. Recorded here because the repository is the
permanent record — the original was written to a scratch file outside it.

**State when audited:** branch `main`, clean tree, last commit `9de86b2`.
`session.py check` — consistent, 21 sessions. `check_site_links.py` — 34 routes,
all resolve. Nothing private is tracked; `data/`, `tmp/`, `.env`, `docs/_site/`
and `docs/reference/` are all ignored.

---

## 1. Blocking — the first push will fail or publish wrong links

**1.1 The git remote and every documented URL disagree.** `origin` was
`narainsagar/mind-archive`; `project.json` and **20 URLs across 14 files** say
`mindarchive`. The site survives either way — `_config.yml` leaves `baseurl` unset
so `actions/configure-pages@v5` injects the real one — but every hardcoded link,
the launch post's `git clone` line and the application's own Source button break.
**Resolved 2026-09-12:** the name is `mindarchive`; the GitHub repository is being
renamed and the remote repointed.

**1.2 The frontend CI job will fail on its first run.** `.github/workflows/ci.yml`
sets `cache: npm` with `cache-dependency-path: apps/web/package-lock.json`, and no
lockfile exists. `actions/setup-node` errors when caching is on and no lock file
matches, before `npm install` is reached. Predicted, not observed — CI has never
run. **Still open.**

**1.3 The repository may not have existed on GitHub yet.** `PROJECT_STATE.md`
recorded a 404 from the API. Not re-checked; the audit made no network calls.

## 2. Incorrect — statements that are no longer true

| Where | Says | Reality |
|---|---|---|
| `PROJECT_STATE.md` header | Last updated 2026-09-08 | Edited through 2026-09-12 |
| `PROJECT_STATE.md` known gaps | "`project.json` still holds placeholders" | Identity is fully set |
| `PROJECT_STATE.md` known gaps | "No git remote — deliberate, D-017" | A remote exists; D-017 was reversed by D-032 |
| `PROJECT_STATE.md` known gaps | "254 backend and 64 frontend tests" | 310 and 112 |
| `PROJECT_STATE.md` publication | "rewrites `mindarchive` to `mindarchive`" | Sentence destroyed by a find-and-replace. **Fixed 2026-09-12** |
| `docs/BACKLOG.md` | Identity is a placeholder; no git remote | Both done |
| `docs/BACKLOG.md`, `docs/DEPLOYMENT.md` | Custom domain is `mindarchive.app` | `project.json` says `mindarchive.narainsagar.com` |
| `DECISIONS.md` D-031 consequences | `contactEmail` comes from `project.json` | D-044 established it does not — that is the git commit identity |
| `docs/DEPLOYMENT.md` | `set_identity.py` renames `mind-archive` repository-wide | It replaces `YOUR-USERNAME` and the copyright line in 16 files. **Fixed 2026-09-12** |

**2.4 `set_identity.py` cannot finish the job it documents.** `docs/DEPLOYMENT.md`
still contains `YOUR-USERNAME` at three places and is not in `TARGETS`, so
following its own instructions leaves them. Also unmanaged: `homepage` in
`package.json`, `repositoryUrl` in `support.ts`, `contact_email` in `support.yml`,
`documentation.html`, `_posts/`. **The list is now stated in DEPLOYMENT.md;
adding the file to `TARGETS` is still open.**

**2.5 `CHANGELOG.md` stops at Milestone 5** — nothing about the documentation site
(D-043), the contact address (D-044) or the header work (D-045). **Still open.**

## 3. Unverified — believed true, never checked

- Nothing has been clicked through in a browser since Milestone 3, including the
  floating Back to top and the fixed brand link, and the six palette/theme
  combinations they must survive. There is no screenshot tooling here.
- The Claude importer has never seen a real Claude export (D-042).
- `scripts/browser/chatgpt-export.js` output has never been compared against an
  official export — more doubtful now the official one shards.
- `info@narainsagar.com` has never been tested. Nothing here sends mail.
- Neither workflow has ever run.
- `feed.xml` carries relative links locally and absolute ones when published —
  check the published feed after the first deploy.

## 4. Missing by design

Milestone 6 (cloud, `SyncProvider`, `StorageProvider` per D-028) and Milestone 7
(production frontend image, release process, security review) are not started.
From the backlog, most likely to be asked for first: attachments are not imported,
a long import reports no progress, donation URLs are blank pending a
merchant-of-record account, and **a Contributor Licence Agreement is blocking for
accepting any outside pull request**.

## 5. Structural risks with nothing checking them

1. **Two copies of the palette labels** — `apps/web/src/theme.ts` and
   `docs/_layouts/default.html`. Drifted once, nearly drifted twice.
2. **Two copies of the contact address** — `support.ts` and `support.yml`.
   Unavoidable; nothing compares them.
3. **Repo-wide find-and-replace has twice damaged `project-memory/sessions/`** —
   the Ink & violet rename and the narainsagar rename, the second rewriting three
   verbatim `PROMPTS.md` files. Both caught and reverted by hand.

A script comparing pairs 1 and 2 would sit beside `check_site_links.py` and
`check_css_bands.py` in `dev.py verify`.
