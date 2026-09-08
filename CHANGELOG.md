# Changelog

All notable changes to Mind Archive are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

**Milestone 3 — the archive browser and search.** You can now read what you
imported.

- Browse your archive, newest first, with paging
- Full-text search across every conversation, using SQLite FTS5
- Search matches all your words and treats the last as a prefix, so results
  narrow as you type
- Read a conversation with its Markdown rendered
- `GET /api/conversations`, `GET /api/conversations/{path}`,
  `POST /api/index/rebuild`
- The index rebuilds itself when the archive has content but the database does
  not — so copying your archive folder to another computer is enough

**Milestone 2 — the ChatGPT importer.** Mind Archive can now actually archive
something.

- Import a ChatGPT export (`.zip`, or a bare `conversations.json`) and store it
  as readable Markdown with JSON metadata, one folder per conversation
- `Importer` adapter interface and a registry, so core code never imports a
  provider-specific module
- ChatGPT parser that follows the branch you last saw, since edits and
  regenerations make the export a tree rather than a list
- Hostile-input handling for zip slip, zip bombs, oversized members and
  traversal via conversation titles
- `GET /api/importers` and `POST /api/import`
- An import panel in the interface, reporting what was imported and what could
  not be read
- `MIND_ARCHIVE_DISPLAY_DATA_DIR`, so the interface shows a path that exists on
  your machine rather than one inside the container

- `scripts/dev.py` — one entry point for running checks and managing Docker.
  Nothing runs automatically; the developer decides when.

### Fixed

- An unusable archive folder no longer stops the application starting. It logs
  the problem and carries on, so the interface can explain it.
- The handler that indexes an imported conversation now uses the configuration
  the application was started with, rather than re-reading a cached copy.
- An unwritable archive folder — an unplugged drive, a permissions problem —
  now produces a clear explanation instead of a 500 error.

### Changed

- **Tests are no longer expected on every change.** Verification is developer-
  controlled during development and required at milestone boundaries and on
  pull requests. See decision D-018.

### Removed

- `docs/archive/`. The durable content was merged into `docs/project-memory/`
  and the transcripts removed; they remain in git history at commit `fcf1f5c`.

Next up: the ChatGPT importer (Milestone 2).

---

## [0.1.0] — 2026-09-08

Milestone 1. A runnable, documented foundation. No product features yet — you
cannot import or browse conversations. That is deliberate.

### Added

**Backend** (`apps/api`)

- FastAPI application with typed settings read from the environment
- `GET /api/health` — liveness and version
- `GET /api/config` — non-sensitive configuration, including where the archive
  is stored and whether cloud is enabled
- A small in-process event bus, so later milestones have a real extension point
- Centralised, traversal-safe filesystem path resolution
- Tests with pytest; linting with ruff; type checking with mypy

**Frontend** (`apps/web`)

- React + TypeScript + Vite single-page workspace
- Light mode by default, dark mode toggle, system preference honoured, choice
  persisted locally
- Status panel showing backend health and where the archive lives
- Tests with Vitest and Testing Library

**Project**

- Docker and Docker Compose for the whole stack
- GitHub Actions CI: backend and frontend checks, plus a project-memory check
- GitHub Pages documentation foundation
- `.gitignore` protecting secrets, databases and personal archives
- `.env.example` with safe placeholders and an explanation of every setting
- `LICENSE` (PolyForm Noncommercial 1.0.0) and `LICENSING.md` explaining the
  free noncommercial tier and paid commercial licensing
- `project.json` as the single source of truth for project identity, applied
  across the repository by `scripts/set_identity.py`
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
- Issue and pull request templates

**Documentation and project memory**

- `README.md`, and `docs/` covering product, architecture, development,
  security, roadmap, backlog, decisions and GitHub Pages
- `docs/project-memory/` — the permanent project memory: state, milestones,
  numbered decisions, research, discussion summary, agent protocol, session log
- Session memory: every working session is recorded in the repository, with the
  prompts and reports that produced it (`scripts/session.py`)
- `AGENTS.md` as the canonical cross-agent instruction file, with `CLAUDE.md`,
  `GEMINI.md` and `QWEN.md` as thin pointers

### Changed

- `CLAUDE.md` rewritten — it previously directed agents to five empty files as
  the project's source of truth
- Licence changed from MIT to PolyForm Noncommercial 1.0.0 before any code was
  published. Mind Archive is source-available, not open source: free for
  noncommercial use, commercial use requires a licence. See decision D-016.
- Planning transcripts moved to `docs/archive/`, with the durable knowledge in
  them extracted into project memory

[Unreleased]: https://github.com/YOUR-USERNAME/mind-archive/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YOUR-USERNAME/mind-archive/releases/tag/v0.1.0
