# Project State

**What actually exists right now.** Read this before starting any work.

If this file and the code disagree, the code is right and this file needs
updating. Keep it honest — it is the file people trust to know where things
stand.

**Last updated:** 2026-09-08 · **Milestone 3 complete** · Version 0.1.0

> **Workflow note.** Checks do not run on every change. Verification is
> developer-controlled and required at milestone boundaries, pull requests and
> releases — run `python scripts/dev.py verify` (decision D-018). Containers are
> disposable; `python scripts/dev.py down` when finished (D-019).

---

## In one paragraph

Mind Archive imports a ChatGPT export, stores it as readable Markdown and JSON
on your own disk, and lets you browse, search and read it. That is a whole
useful loop: the product does its core job.

What it cannot do yet is **organise** — no tags, no projects, no editing or
deleting from the interface. That is Milestone 4.

Underneath: a FastAPI backend, a React + TypeScript + Vite frontend with light
and dark modes, SQLite with FTS5 as a rebuildable index, Docker Compose, CI, and
complete project memory.

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
| `paths.py` | Traversal-safe path joining and filename cleaning. Now genuinely exercised: conversation titles become folder names through it |
| `models.py` | `Conversation` and `Message` — the archive's own model, shaped like no provider's export |
| `importers/__init__.py` | The registry. Core code asks it which adapter can read a file |
| `importers/base.py` | The `Importer` protocol: `detect()`, `validate()`, `parse()` |
| `importers/zip_safety.py` | Reading archives someone else produced: zip slip, zip bombs, size caps |
| `importers/chatgpt.py` | The ChatGPT adapter, including the branching `mapping` tree |
| `archive/writer.py` | Conversations to `conversation.md` + `metadata.json`, one folder each |
| `archive/reader.py` | ... and back off disk, tolerating folders that are not conversations |
| `index/schema.py` | The SQLite schema. Derived, droppable, rebuildable |
| `index/indexer.py` | Building the index by reading the archive |
| `index/search.py` | FTS5 queries, and rewriting whatever someone types |
| `routes/health.py` | `GET /api/health` |
| `routes/config.py` | `GET /api/config` — non-sensitive config only, with a test enforcing that |
| `routes/import_.py` | `GET /api/importers`, `POST /api/import` |
| `routes/conversations.py` | `GET /api/conversations`, `GET /api/conversations/{path}`, `POST /api/index/rebuild` |

**Frontend** — `apps/web`

Single-page workspace, minimal header, no router and no sidebar. Light default,
dark toggle, system preference honoured, choice persisted to `localStorage` with
every access wrapped in try/catch.

An archive panel with a debounced search box, results with marked snippets, and
paging; opening a conversation renders its Markdown in place. An import panel
that explains where to find a ChatGPT export and reports what could not be read.
A status panel showing backend health, archive location and cloud state.

Plain CSS custom properties, no UI framework. One rendering dependency,
`react-markdown`, chosen because it builds React elements rather than setting
HTML (D-021).

**Project**

Docker + Compose · GitHub Actions CI (backend matrix on 3.11/3.12, frontend,
project-memory check, committed-secrets check) · GitHub Pages foundation ·
`.gitignore` · `.gitattributes` · `.env.example` · issue and PR templates ·
`project.json` + `scripts/set_identity.py` · session memory via
`scripts/session.py`.

## What is deliberately absent

No tags, projects or organisation. No editing or deleting conversations from
the interface. No cloud or sync code of any kind. No authentication. No settings
beyond the theme toggle and read-only configuration display.

Within the importer, deliberately not done: attachments and images (recorded as
placeholders in the Markdown, not copied), and abandoned conversation branches
from edits and regenerations.

Within search: no phrase search, `OR` or negation — a deliberate trade so that
nothing typed into the box can produce a syntax error (D-022). No per-message
structure in the reading view, because the whole file is rendered (D-020).

Each belongs to a later milestone. See [MILESTONES.md](MILESTONES.md).

## Verified on 2026-09-08

Everything below was actually run, not inspected.

| Check | Result |
|---|---|
| Backend tests (`pytest`) | **197 passed** |
| Backend lint (`ruff check`) | **passed** |
| Backend formatting (`ruff format --check`) | **passed**, 34 files |
| Backend types (`mypy src`, strict) | **passed**, 22 files, no issues |
| Frontend tests (`vitest`) | **45 passed** |
| Frontend types (`tsc --noEmit`) | **passed** |
| Frontend lint (`eslint`) | **passed** |
| Frontend build (`vite build`) | **passed** — 147.84 kB JS, 47.73 kB gzipped |
| Docker images | both build |
| `docker compose up` | both containers start, API healthy |
| `GET /api/health` | 200, correct payload |
| `GET /api/config` | 200, cloud disabled, local storage |
| Web interface | HTTP 200, correct title |
| `git check-ignore data/ .env local/` | all correctly ignored |
| `scripts/session.py check` | passes |
| **End-to-end import** | a synthetic export with a normal, an awkward and a broken conversation uploaded through `POST /api/import`: 2 imported, 1 skipped and reported, correct files on disk |
| **End-to-end browse** | list, search, prefix search, read one, rebuild the index — all against the running stack |
| **End-to-end hostile input** | `C++`, `NEAR(`, `"`, `a AND OR b` all return results rather than errors; URL-encoded traversal returns 404 |

Bugs found by running things rather than reading them, and fixed. In Milestone 1:
`parents[4]` failed inside the container, `vite.config.ts` had no `node` types,
and Vitest 2 pulled a second copy of Vite. In Milestone 2: a hostile archive was
reported as merely "not recognised", the interface showed the container's path
rather than the user's, and an unwritable archive folder produced a raw 500.

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
- **The index is rebuilt only when it is empty**, not when the archive has
  changed underneath it. Editing files by hand needs
  `POST /api/index/rebuild`, though reading a conversation always comes from
  disk so edits are visible immediately.
- **Paging is Previous/Next, not virtualised.** Fine for thousands of
  conversations; revisit if anyone has hundreds of thousands.
- **The importer has only seen synthetic exports.** Tests cover malformed and
  hostile input thoroughly, but no real ChatGPT export has been imported yet.
  `local/` exists (git-ignored) for exactly this. **This is the outstanding
  verification for Milestone 2.**
- **Attachments are not imported** — images and files appear as placeholders in
  the Markdown.

## Licence

**Source-available, not open source.** Free for noncommercial use under PolyForm
Noncommercial 1.0.0; commercial use requires a separate licence. See
`LICENSING.md` and decisions D-016 and D-012.

A Contributor Licence Agreement must exist before outside contributions can be
accepted. It does not exist yet.

## Next step

**Verify against a real ChatGPT export** placed in `local/`, and fix whatever
genuine data reveals. Synthetic fixtures are thorough, but they were written by
the same mind that wrote the parser, so they cannot find an assumption that is
simply wrong. This has been outstanding since Milestone 2 and is now the highest
value check available.

Then **Milestone 4 — projects, tags and metadata**: organising the archive once
there is enough in it to need organising.
