# Repository audit — what is missing, incorrect, or blocking

**Audited 2026-09-11** at commit `9de86b2` · **updated 2026-09-12** at `1435ea8`
· 3 of 14 findings resolved

This is a living document while the findings are open. Each one says whether it is
**Resolved**, **Partly done** or **Open**, so the file can be read as a checklist
rather than a snapshot of one afternoon. Delete it when everything here is closed
— it is a punch list, not a permanent record. What is worth keeping long-term is
already in `project-memory/DECISIONS.md` and `SESSION_LOG.md`.

## Context

Mind Archive is feature-complete through Milestone 5 and is being prepared for its
first public push (D-032). Six working sessions landed in two days — the site
generator, the contact address, an identity rename, and two UI fixes — and the
documentation had not kept pace with them. The audit itself was read-only;
everything marked resolved below was fixed afterwards, deliberately.

**State when audited:** branch `main`, clean tree, last commit `9de86b2`.
`session.py check` — memory consistent, 21 sessions. `check_site_links.py` — 34
routes, every internal link resolves. Nothing private is tracked (`git ls-files`
against the secret patterns returns nothing; `data/`, `tmp/`, `.env`,
`docs/_site/`, `docs/reference/` all ignored).

**Still true on 2026-09-12:** clean tree, 34 routes, memory consistent (22
sessions), nothing private tracked.

---

## 1. Blocking — the first push will fail or publish wrong links

### 1.1 The git remote and every documented URL disagree — **Partly done**

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

**Decided 2026-09-12: the name is `mindarchive`**, without a hyphen, and the
GitHub repository is being renamed to match. The repository side needed almost
nothing — everything except the remote already said `mindarchive`, and the single
literal `mind-archive` in the tree was inside a false claim about
`set_identity.py`, now corrected (see the last row of section 2).

**What is left is one command**, after the GitHub rename:

```bash
git remote set-url origin git@github.com:narainsagar/mindarchive.git
git remote -v                                  # compare against project.json
```

As of 2026-09-12 the remote still reads `narainsagar/mind-archive`, so this is
not yet done. **Check the two against each other before the first push** — if
they ever disagree again, the clone command in the launch post and the Source
link inside the application are the first things to break.

### 1.2 The frontend CI job will fail on its first run — **Open**

`.github/workflows/ci.yml:65-69` sets `cache: npm` with
`cache-dependency-path: apps/web/package-lock.json` — **and there is no
package-lock.json.** `actions/setup-node` errors out when caching is on and no lock
file matches, before `npm install` is ever reached.

Committing a lockfile fixes it and makes CI reproducible. This is predicted, not
observed: CI has never run.

### 1.3 The repository may not exist on GitHub yet — **Open**

`PROJECT_STATE.md` recorded that the GitHub API returned 404 for it and that
`narainsagar` is an organisation needing a token with write access. **Never
re-checked** — neither the audit nor the work since has made a network call. That
stale claim was removed from `PROJECT_STATE.md` on 2026-09-12 rather than
repeated: a remote now exists, and asserting a 404 nobody has seen recently is
worse than saying nothing.

---

## 2. Incorrect — statements in the repository that are no longer true

Line numbers are deliberately not used below — they shifted the moment the first
of these was fixed. Each row names the file and the section instead.

| Where | Says | Reality | Status |
|---|---|---|---|
| `PROJECT_STATE.md`, header | Last updated 2026-09-08 | Edited daily since | **Open** |
| `PROJECT_STATE.md`, Known gaps | "`project.json` still holds placeholders" | Identity is fully set | **Open** |
| `PROJECT_STATE.md`, Known gaps | "No git remote — deliberate, D-017" | A remote exists; D-017 was reversed by D-032 | **Open** |
| `PROJECT_STATE.md`, Known gaps | "254 backend and 64 frontend tests" | 310 and 112 | **Open** |
| `PROJECT_STATE.md`, Publication | "`set_identity.py` rewrites `mindarchive` to `mindarchive`" | Sentence destroyed by a find-and-replace; it originally read `mind-archive` → `mindarchive` | **Resolved** `1435ea8` |
| `docs/BACKLOG.md`, Known gaps from Milestone 1 | Identity is a placeholder; no git remote | Both done | **Open** |
| `docs/BACKLOG.md` and `docs/DEPLOYMENT.md`, custom domain | Custom domain is `mindarchive.app` | `project.json` says `mindarchive.narainsagar.com` | **Open** |
| `DECISIONS.md`, D-031 consequences | `contactEmail` comes from `project.json`'s author block | D-044 established it does not; `author.email` is the git commit identity | **Open** |
| `docs/DEPLOYMENT.md`, after the identity block | `set_identity.py` "rewrites `mind-archive` to `mindarchive` across the whole repository" | It does no such thing — it replaces the literal `YOUR-USERNAME` and the copyright line, in 16 named files, and cannot rename one real name to another at all | **Resolved** `1435ea8` |

### 2.4 `set_identity.py` cannot finish the job it documents — **Partly done**

`docs/DEPLOYMENT.md` is the guide to publishing, still contains `YOUR-USERNAME` in
three of its example commands — and is **not in `TARGETS`**
(`scripts/set_identity.py`), so running the script as that page instructs leaves
them in place.

**Done 2026-09-12:** `DEPLOYMENT.md` and `PROJECT_STATE.md` now both state what
the script replaces and list the six files a rename has to reach by hand —
`package.json` (`homepage`), `support.ts` (`repositoryUrl`), `support.yml`
(`contact_email`), `documentation.html`, `_posts/`, and `DEPLOYMENT.md` itself.

**Still open:** the three `YOUR-USERNAME` placeholders, and the choice between
adding `DEPLOYMENT.md` to `TARGETS` or leaving it hand-maintained and documented
as such. Adding it would fix the placeholders on the next run.

### 2.5 The changelog stops at Milestone 5 — **Open**

`CHANGELOG.md`'s `[Unreleased]` covers Claude import, export, tags and inbox — and
says nothing about the documentation site (D-043), the contact address (D-044) or
the header and Back to top work (D-045). Grep for those decisions in it returns
nothing.

---

## 3. Unverified — believed true, never checked

**All still unverified on 2026-09-12.** Nothing in this section is a defect; each
is a claim the repository makes that nobody has tested.

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
4. **`git add -A` sweeps up whatever the maintainer is mid-way through.** On
   2026-09-12 it pulled an untracked `AUDIT_REPORT.md` into a commit about
   documentation wording, and the commit was reported as three files when it was
   four. Staging by explicit path, or reading `git status` immediately before
   committing rather than only after, is the fix. Two people editing one working
   tree is the underlying condition and it is not going away.

A single script comparing the duplicated pairs (1) and (2) would fit beside
`check_site_links.py` and `check_css_bands.py` in `dev.py verify`.

---

## What is left, in order

1. ~~Settle the repository name~~ — **done**. `mindarchive`. One command left
   after the GitHub rename: `git remote set-url origin` (1.1).
2. **Commit a `package-lock.json`** (1.2). The only item here that fails a build
   rather than misleading a reader, and the only one that touches no prose.
3. **Correct the seven remaining false statements** in section 2 — `PROJECT_STATE`
   ×4, `BACKLOG` ×2, D-031's consequences. One pass, all of it prose.
4. **Bring `CHANGELOG.md` up to date** (2.5) — D-043, D-044 and D-045 are missing
   from `[Unreleased]`.
5. **Decide `DEPLOYMENT.md`'s three `YOUR-USERNAME` placeholders** (2.4): add the
   file to `TARGETS`, or fill them in by hand.
6. Optional: the drift check for the two duplicated pairs (5).

Items 3–5 are documentation only. Item 2 is one command and a commit.

**Done since the audit**, all in `1435ea8`: the repository name settled, the
`set_identity.py` claim corrected in both places it appeared, and the list of
hand-maintained files written down where a reader will meet it.

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
