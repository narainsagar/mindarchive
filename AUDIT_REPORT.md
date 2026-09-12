# Repository audit — what is missing, incorrect, or blocking

## Context

Mind Archive is feature-complete through Milestone 5 and is being prepared for its
first public push (D-032). Six working sessions landed in two days — the site
generator, the contact address, an identity rename, and two UI fixes — and the
documentation has not kept pace with them. This is a read-only audit of the whole
repository: nothing was changed.

**State when audited:** branch `main`, clean tree, last commit `9de86b2`.
`session.py check` — memory consistent, 21 sessions. `check_site_links.py` — 34
routes, every internal link resolves. Nothing private is tracked (`git ls-files`
against the secret patterns returns nothing; `data/`, `tmp/`, `.env`,
`docs/_site/`, `docs/reference/` all ignored).

---

## 1. Blocking — the first push will fail or publish wrong links

### 1.1 The git remote and every documented URL disagree

```
git remote:   git@github.com:narainsagar/mind-archive.git     ← hyphen
project.json: "repository": "mindarchive"                      ← no hyphen
```

**20 URLs across 14 files** say `narainsagar/mindarchive` or
`narainsagar.github.io/mindarchive` — `README.md`, `CHANGELOG.md`, `docs/index.html`,
`docs/documentation.html`, `docs/_layouts/default.html`, `apps/web/package.json`
(`homepage`), `apps/web/src/support.ts` (`repositoryUrl`, the app's Source link),
`.github/ISSUE_TEMPLATE/config.yml`, and the launch blog post's `git clone` line.

If the real repository is `mind-archive`, all twenty are dead links the day the
repo goes public. The site itself survives — `docs/_config.yml:34-44` leaves
`baseurl` unset on purpose so `actions/configure-pages@v5` injects the real one —
but every hardcoded link, the clone command and the app's own Source button break.

**Decide which name is real**, then either rename the GitHub repo to `mindarchive`
(cheapest — nothing in the repo changes) or set `repository` to `mind-archive` and
re-propagate. `set_identity.py` only covers 16 files, so a rename needs manual
passes over `support.ts`, `package.json`, `docs/documentation.html`, `_posts/` and
`docs/DEPLOYMENT.md` (see 2.4).

### 1.2 The frontend CI job will fail on its first run

`.github/workflows/ci.yml:65-69` sets `cache: npm` with
`cache-dependency-path: apps/web/package-lock.json` — **and there is no
package-lock.json.** `actions/setup-node` errors out when caching is on and no lock
file matches, before `npm install` is ever reached.

Committing a lockfile fixes it and makes CI reproducible. This is predicted, not
observed: CI has never run.

### 1.3 The repository may not exist on GitHub yet

`PROJECT_STATE.md` records that the GitHub API returned 404 for it and that
`narainsagar` is an organisation needing a token with write access. **Not
re-checked here** — this audit made no network calls.

---

## 2. Incorrect — statements in the repository that are no longer true

| Where | Says | Reality |
|---|---|---|
| `project-memory/PROJECT_STATE.md:9` | Last updated 2026-09-08 | Edited through 2026-09-11 |
| `PROJECT_STATE.md:260` | "`project.json` still holds placeholders" | Identity is fully set |
| `PROJECT_STATE.md:263` | "No git remote — deliberate, D-017" | A remote exists; D-017 was reversed by D-032 |
| `PROJECT_STATE.md:284` | "254 backend and 64 frontend tests" | 310 and 112 |
| `PROJECT_STATE.md:74-76` | "`set_identity.py` rewrites `mindarchive` to `mindarchive`" | Sentence destroyed by a find-and-replace; it originally read `mind-archive` → `mindarchive` |
| `docs/BACKLOG.md:17-22` | Identity is a placeholder; no git remote | Both done |
| `docs/BACKLOG.md:45`, `docs/DEPLOYMENT.md:211-230` | Custom domain is `mindarchive.app` | `project.json` says `mindarchive.narainsagar.com` |
| `project-memory/DECISIONS.md` D-031 consequences | `contactEmail` comes from `project.json`'s author block | D-044 established it does not; `author.email` is the git commit identity |
| `docs/DEPLOYMENT.md:41-45` | `set_identity.py` "rewrites `mind-archive` to `mindarchive` across the whole repository" | It does no such thing — it replaces the literal `YOUR-USERNAME` and the copyright line, in 16 named files |

### 2.4 `set_identity.py` cannot finish the job it documents

`docs/DEPLOYMENT.md` is the guide to publishing, still contains `YOUR-USERNAME` at
lines 142, 174 and 231 — and is **not in `TARGETS`** (`scripts/set_identity.py:29-46`),
so running the script as that page instructs leaves the placeholders in place.

Also unmanaged and maintained by hand: `apps/web/package.json` (`homepage`),
`apps/web/src/support.ts` (`repositoryUrl`), `docs/_data/support.yml`,
`docs/documentation.html`, `docs/_posts/*`. DEPLOYMENT.md admits two of these; the
rest are silent.

### 2.5 The changelog stops at Milestone 5

`CHANGELOG.md`'s `[Unreleased]` covers Claude import, export, tags and inbox — and
says nothing about the documentation site (D-043), the contact address (D-044) or
the header and Back to top work (D-045). Grep for those decisions in it returns
nothing.

---

## 3. Unverified — believed true, never checked

- **Nothing has been clicked through in a browser since Milestone 3.** That now
  includes the floating Back to top and the fixed brand link, and the six
  palette/theme combinations they must survive. There is no screenshot tooling in
  this repository.
- **The Claude importer has never seen a real Claude export** (D-042). Synthetic
  fixtures only; it may shard the way ChatGPT's does.
- **`scripts/browser/chatgpt-export.js` output has never been compared** against an
  official export — and is more doubtful now that the official one shards.
- **`info@narainsagar.com` has never been tested.** Nothing in the repository sends
  mail; the address is published on every page of the site.
- **Neither workflow has ever run.** CI and Pages are committed and dormant.
- **`feed.xml` carries relative links locally and absolute ones when published**
  (`_config.yml:41-44`) — check the published feed after the first deploy.

---

## 4. Missing by design — tracked, not forgotten

Milestone 6 (cloud, `SyncProvider`, `StorageProvider` — deferred by D-028) and
Milestone 7 (production frontend image, release process, security review) are both
⬜ not started. From `docs/BACKLOG.md`, the items most likely to be asked for first:
attachments are not imported, a long import reports no progress, donation URLs are
blank pending a merchant-of-record account, and a **Contributor Licence Agreement
is blocking for accepting any outside pull request**.

---

## 5. Structural risks — real, with nothing checking them

1. **Two copies of the palette labels** — `apps/web/src/theme.ts` and
   `docs/_layouts/default.html`. They have drifted once and nearly drifted twice.
2. **Two copies of the contact address** — `apps/web/src/support.ts` and
   `docs/_data/support.yml`. Unavoidable (neither build reads the other's file),
   and D-044 says change both, but nothing compares them.
3. **Repo-wide find-and-replace has twice damaged `project-memory/sessions/`** —
   the Ink & violet rename and the narainsagar rename, the latter rewriting three
   verbatim `PROMPTS.md` files. Both were caught and reverted by hand. A search
   scope that excludes that directory, or a check that fails when a committed
   session record changes, would stop the third.

A single script comparing the duplicated pairs (1) and (2) would fit beside
`check_site_links.py` and `check_css_bands.py` in `dev.py verify`.

---

## Recommended order

1. Settle the repository name (1.1) — everything else about publishing depends on it.
2. Commit a `package-lock.json` (1.2).
3. Correct the false statements in section 2 — one pass, they are all prose.
4. Bring `CHANGELOG.md` up to date (2.5).
5. Add `docs/DEPLOYMENT.md` to `set_identity.py`'s `TARGETS`, or say plainly in it
   which files are hand-maintained (2.4).
6. Then the optional drift check (5).

Items 3–5 are documentation only and touch no code. Item 1 may need nothing in the
repository at all, depending on which way it is decided.

## Verification

Nothing here needs new tooling to confirm:

```bash
git remote -v                                  # 1.1 — compare against project.json
grep -rn "YOUR-USERNAME" docs/                 # 2.4
python scripts/session.py check                # memory consistency
python scripts/check_site_links.py             # 34 routes
python scripts/dev.py verify                   # the gate, site build included
```

After any documentation change, `dev.py verify` is the gate — it regenerates the
eleven published pages, walks every internal link and builds the site, so a broken
statement in `PROJECT_STATE.md` or `DECISIONS.md` cannot reach the published site
unnoticed.
