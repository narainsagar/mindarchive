# Project State

**What actually exists right now.** Read this before starting any work.

If this file and the code disagree, the code is right and this file needs
updating. Keep it honest — it is the file people trust to know where things
stand.

**Last updated:** 2026-09-08 · **Milestone 1 complete** · Version 0.1.0

---

## In one paragraph

Mind Archive has a runnable, tested, documented foundation: a FastAPI backend, a
React + TypeScript + Vite frontend with light and dark modes, Docker Compose
wiring them together, CI, and complete project memory. **It cannot import or
browse conversations yet** — that is Milestone 2, and it is the entire reason
the product exists. What is here is scaffolding: correct, verified scaffolding,
but scaffolding.

## What runs

```bash
cp .env.example .env
docker compose up --build
```

- Interface — http://localhost:5173
- API — http://localhost:8000, docs at `/docs`
- Archive folder — `./data/archive`, git-ignored

Verified working on 2026-09-08: both containers start, the API reports healthy,
the interface loads and displays live backend status.

## What is implemented

**Backend** — `apps/api`

| | |
|---|---|
| `main.py` | FastAPI app, lifespan, CORS restricted to the local frontend |
| `config.py` | Typed settings via pydantic-settings; finds the repo root by marker, not by counting parents |
| `events.py` | In-process event bus; a failing handler cannot break the publisher |
| `paths.py` | Traversal-safe path joining and filename cleaning. Unused so far — it exists for Milestone 2 |
| `routes/health.py` | `GET /api/health` |
| `routes/config.py` | `GET /api/config` — non-sensitive config only, with a test enforcing that |

**Frontend** — `apps/web`

Single-page workspace, minimal header, no router and no sidebar. Light default,
dark toggle, system preference honoured, choice persisted to `localStorage` with
every access wrapped in try/catch. Status panel showing backend health, archive
location and cloud state. Plain CSS custom properties, no UI framework.

**Project**

Docker + Compose · GitHub Actions CI (backend matrix on 3.11/3.12, frontend,
project-memory check, committed-secrets check) · GitHub Pages foundation ·
`.gitignore` · `.gitattributes` · `.env.example` · issue and PR templates ·
`project.json` + `scripts/set_identity.py` · session memory via
`scripts/session.py`.

## What is deliberately absent

No importer. No archive browsing. No search. No SQLite schema — only a path
where the database will live. No cloud or sync code of any kind. No
authentication. No settings beyond the theme toggle and read-only configuration
display.

Each belongs to a later milestone. See [MILESTONES.md](MILESTONES.md).

## Verified on 2026-09-08

Everything below was actually run, not inspected.

| Check | Result |
|---|---|
| Backend tests (`pytest`) | **33 passed** |
| Backend lint (`ruff check`) | **passed** |
| Backend formatting (`ruff format --check`) | **passed**, 12 files |
| Backend types (`mypy src`, strict) | **passed**, 8 files, no issues |
| Frontend tests (`vitest`) | **19 passed** |
| Frontend types (`tsc --noEmit`) | **passed** |
| Frontend lint (`eslint`) | **passed** |
| Frontend build (`vite build`) | **passed** — 147.84 kB JS, 47.73 kB gzipped |
| Docker images | both build |
| `docker compose up` | both containers start, API healthy |
| `GET /api/health` | 200, correct payload |
| `GET /api/config` | 200, cloud disabled, local storage |
| Web interface | HTTP 200, correct title |
| `git check-ignore data/ .env` | both correctly ignored |
| `scripts/session.py check` | passes |

Three real bugs were found by running things rather than reading them, and
fixed: `parents[4]` failed inside the container, `vite.config.ts` had no `node`
types and an untyped `test` block, and Vitest 2 pulled a second copy of Vite
that broke type checking.

## Environment reality

The development machine has **Python 3.7.9 on Windows and 3.8.10 in WSL2** —
both end-of-life and unsuitable for the backend. Docker is therefore the primary
supported path (decision D-006). Node 24 in WSL2 is fine for frontend work.

All verification above was run inside Docker for this reason.

## Known gaps

- **`project.json` still holds placeholders.** `github.username` and
  `copyright.holder` are unset. Run `python scripts/set_identity.py --git`
  after filling them in.
- **No git remote** — deliberate, decision D-017. CI and Pages workflows are
  committed but have never run against a live GitHub repository.
- **No `package-lock.json`.** The Dockerfile falls back to `npm install`. CI
  expects a lockfile for caching; commit one on the first native `npm install`.
- **The frontend Docker image runs the dev server**, not a production build.
  Fine locally; a production image is Milestone 7.
- **`paths.py` is untested against real archives** because no importer exists.
  Its unit tests pass, but Milestone 2 is where it earns its place.

## Licence

**Source-available, not open source.** Free for noncommercial use under PolyForm
Noncommercial 1.0.0; commercial use requires a separate licence. See
`LICENSING.md` and decisions D-016 and D-012.

A Contributor Licence Agreement must exist before outside contributions can be
accepted. It does not exist yet.

## Next step

**Milestone 2 — the ChatGPT importer.** Start by reading
[MILESTONES.md](MILESTONES.md), then build the `Importer` interface against the
real ChatGPT export format. Treat every imported file as hostile input and use
`paths.py` for anything that becomes a filename.
