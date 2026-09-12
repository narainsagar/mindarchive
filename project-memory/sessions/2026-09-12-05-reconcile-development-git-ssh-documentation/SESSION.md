# Session: Reconcile the development, Git and SSH documentation

**ID:** 2026-09-12-05-reconcile-development-git-ssh-documentation
**Started:** 2026-09-12
**Ended:** 2026-09-12
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Reconcile the setup documentation — WSL2, VS Code, Git, GitHub, SSH including the
port-443 route, the remote, and the untracked `docs/development/GIT_SSH_SETUP.md`
— into a structure that can later be divided cleanly between the private and
public repositories.

## Starting state

Branch `main` at `e0c6c34`, clean tree, one untracked file:
`docs/development/GIT_SSH_SETUP.md`.

## What was found

**The untracked file was a 37-line stub**, not a draft to merge: an overview, a
list of tools, an architecture diagram — and it stopped mid-sentence on an
unclosed code fence. **It contained no SSH instructions at all**, and nothing
about port 443. The useful technical knowledge existed only in the maintainer's
environment, so it had to be written rather than moved.

**`DEVELOPMENT.md` already covered most of the ground well**: requirements,
Docker and native paths, WSL2 notes including `code .` and the two Docker Desktop
traps, configuration, layout, working method, tests, commit conventions,
troubleshooting. Duplicating any of it would have been the wrong move.

**The real gap was authentication.** Nothing in the repository explained keys,
the agent, the remote, or what to do when a push hangs. `DEPLOYMENT.md` had two
half-answers: a bare `git config user.name` snippet and a first-push block that
offered HTTPS first with SSH as an afterthought — for a repository that is
private, where HTTPS has needed a token since 2021.

**Two stale claims surfaced while reading.** The project layout in
`DEVELOPMENT.md` still showed `docs/project-memory/` and `docs/archive/` — the
first moved to the repository root in D-039, the second deleted in `14159dc`.
And three documents still named `mindarchive.app` as the intended domain, which
the identity change had already made wrong.

## What was done

**One new page, at the path the maintainer had already chosen:**
`docs/development/GIT_SSH_SETUP.md`, published at `/git-ssh/`. It owns keys, the
agent and keeping it alive across WSL shells, the public key, the remote,
per-repository identity, the everyday command sequence, and a troubleshooting
table. **The port-443 route is written generically** — some networks drop
outbound 22; GitHub serves SSH on 443 for exactly that reason — with no
hostname, address, network name or key material anywhere in it.

**No new tree.** Twelve documents sit flat in `docs/` with explicit permalinks
and clean routes. Restructuring them into `development/` and `deployment/`
directories would have rewritten every internal link and every published URL to
gain nothing a reader can perceive. The subdirectory holds setup guides because
that is where this one already was; the next one joins it. Recorded as D-047.

**The other documents now point at it instead of half-repeating it**:
`DEVELOPMENT.md` gains a callout above Requirements and a pointer in its Git
section; `DEPLOYMENT.md`'s identity step and first-push block defer to it and now
lead with SSH.

**The domain architecture is recorded for the first time (D-047).** Four names:
the application, `api.`, `docs.`, and the GitHub Pages URL that keeps working
whatever DNS does. `mindarchive.app` is gone from `DEPLOYMENT.md`,
`GITHUB_PAGES.md` and `BACKLOG.md`. **Nothing is configured, and the decision
authorises nothing** — it records the shape so the documentation stops
contradicting itself. It also notes that a public name does not solve the API's
lack of authentication.

**The stale project layout is fixed**, and now says where project memory actually
lives and why the site cannot reach it.

## Decisions made

**D-047 — four names on one apex, and one page for Git and SSH.** Indexed in
`docs/DECISIONS.md`. Covers the domain architecture, why subdomains of an owned
apex beat a second registration, why the API gets its own name, why the
documentation stays flat rather than moving into a tree, and the no-duplication
rule between the three setup documents.

## Files changed

```
added:    docs/development/GIT_SSH_SETUP.md   (was a 37-line stub; now the guide)
modified: docs/DEVELOPMENT.md                 (SSH callout, Git pointer, layout fixed)
modified: docs/DEPLOYMENT.md                  (identity + first push defer to it; domains)
modified: docs/GITHUB_PAGES.md                (docs. subdomain, not the apex)
modified: docs/BACKLOG.md                     (domain entry)
modified: docs/documentation.html             (index entry for the new page)
modified: docs/DECISIONS.md                   (D-047 in the index)
modified: project-memory/DECISIONS.md         (D-047)
added:    project-memory/sessions/2026-09-12-05-.../
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Site links | `check_site_links.py` | **0 problems — 35 routes** (was 34) |
| Project memory | `session.py check` | **Passed** — 26 sessions |
| Site build | `jekyll build` in Docker | **Passed** — 34 pages (was 33) |
| The new route exists | `ls /git-ssh/` in the built output | `index.html` present |
| Its content survived Liquid | grep the built page | `ssh.github.com` twice, as written |
| The index links it | grep `/docs/` in the built output | 1 link |
| Privacy sweep of the new page | grep for identifiers, private ranges, key material | **Only GitHub's own public hostname** |

No code was touched, so neither test suite was re-run.

## What remains

**Nothing is committed** — this session's work sits in the tree alongside no
other uncommitted change.

**`README.md`, `DEVELOPMENT.md` and the landing page still clone over HTTPS.**
Correct for the public repository that will exist later; today a private clone
needs SSH, which the callout above Requirements now points at. Left deliberately
rather than churned twice.

**The `docs/development/` directory holds one file.** That is the intended shape
(D-047), not an oversight — but if no second setup guide ever joins it, folding
the page up into `docs/` flat would be the tidier end state.

## Exact next step

Review the diff and commit it. Nothing here has been committed, and the
maintainer controls pushes.
