# Session: prepare for publication on GitHub and Pages

**ID:** 2026-09-09-04-prepare-for-publication-on-github-and-pages
**Started:** 2026-09-09
**Ended:** 2026-09-09 11:49
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Make the repository ready to publish on GitHub with Pages, commit three
sessions of outstanding work, and produce a deployment guide.

## Starting state

Branch `main` at `310cbb2`, 40 files uncommitted across D-029, D-030 and D-031.
No git remote. CI and Pages workflows written at Milestone 1 and never run.

## What was done

**Two requests were refused as asked and redirected, both for good reason.**

*A separate branch for a "clean" public version.* It does not do what was
wanted. project-memory is already excluded from the published **site** by
`docs/_config.yml` — visitors never see it; only people browsing the repository
do. And branches share history, so a second branch hides nothing once the
history is pushed, while costing a cherry-pick on every future change. The real
mechanism would have been two repositories. Presented as such, and the choice
became: one public repository with everything in it.

*A public live demo on a VPS.* `docs/SECURITY.md:68` states there is no
authentication because this is a single-user local application, and that
exposing it is out of scope. A public instance means one shared archive that any
visitor can read, write and export — whatever one person imports, everyone else
downloads. For a privacy-first product that is the exact failure it exists to
prevent, and it would put strangers' conversations on the maintainer's server.
Deferred, with the four things a real demo needs written into the backlog.

**Publication prepared:**

- `docs/index.html` rebuilt on the same token names as `apps/web/src/styles.css`
  — Light minimal with a `prefers-color-scheme` dark variant, no palette
  switcher. The old page carried its own duplicated tokens and had already
  drifted from the application.
- `docs/DEPLOYMENT.md` written: identity, pre-push safety checks, repository
  creation (web UI and `gh`), first push, enabling Pages, the manual first
  workflow run, custom domain DNS, and a VPS section that says plainly what
  would have to exist before anything is exposed.
- D-017 superseded by **D-032**. `docs/BACKLOG.md` Deployment section resolved
  and the demo scoped as real work.

**Verified safe to publish before committing.** `git ls-files` matched nothing
against `.env`, `*.pem`, `*.key`, `secret`, `credential`, `conversations.json`
or `*.zip`. `git check-ignore` confirmed `data/`, `tmp/` and `.env` are ignored.

**Git identity was not configured** — `user.name` and `user.email` were both
empty despite existing commits carrying an author. Set per-repository (D-015)
before committing rather than discovering it mid-commit.

**Committed in three pieces, not five.** Splitting file-by-file was considered
and rejected: `App.tsx` and `styles.css` are touched by all three feature
sessions, so a finer split would have produced commits that do not compile. Each
of the three builds.

## Decisions made

**D-032 — Published publicly on GitHub; Pages for docs; no hosted application.**
Supersedes D-017. Added to `docs/DECISIONS.md` index.

## Files changed

```
Added:
  docs/DEPLOYMENT.md

Modified:
  docs/index.html                     rebuilt on the app's tokens
  docs/BACKLOG.md                     deployment resolved; demo scoped
  docs/DECISIONS.md                   D-032; D-017 struck
  docs/project-memory/DECISIONS.md    D-032; D-017 superseded
  docs/project-memory/PROJECT_STATE.md

Commits:
  761553a chore: keep agent instruction files at the repo root
  c42d37d feat: appearance controls, import dialog and page navigation
  fee8dce docs: prepare for publication on GitHub and Pages
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Secrets scan | `git ls-files \| grep -Ei ...` | Passed — nothing matched |
| Ignore rules | `git check-ignore -v data tmp .env` | Passed — all three ignored |
| Full gate | `dev.py verify` | **Passed — 98 tests, all checks passed** |
| Working tree | `git status --short` | Clean after three commits |

## What remains

- **Nothing is pushed.** No remote exists. `gh` is not installed on this
  machine and the GitHub username is unknown, so repository creation and the
  first push are the maintainer's steps, from `docs/DEPLOYMENT.md`.
- **`project.json` still holds `github.username: "YOUR-USERNAME"`.** This is the
  one value only the maintainer can supply. `scripts/set_identity.py`
  propagates it — including into the clone URL now shown on the landing page.
- **The workflows have still never run.** A first-run CI failure on GitHub is
  more likely a runner difference than a regression; read the log before
  assuming otherwise.
- **Still no visual check** of the application or the rebuilt landing page.
  Everything across four sessions is verified by tests and the build only.
- The web Docker image runs the Vite dev server and is unsuitable for any
  public host. Milestone 7.

## Exact next step

Put the real GitHub username in `project.json`, run
`python scripts/set_identity.py`, then follow `docs/DEPLOYMENT.md` from
"Creating the repository".
