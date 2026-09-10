# Session: audit and Milestone 1

**ID:** 2026-09-08-01-audit-and-milestone-1
**Started:** 2026-09-08
**Ended:** 2026-09-08
**Agent:** Claude Opus 5 (Claude Code, VS Code extension)

---

## Goal

Audit the repository read-only, get approval, then implement Milestone 1 in
full: a clean, runnable, documented foundation. Stop before Milestone 2.

## Starting state

Branch `master`, no commits, no remote, no git identity configured. 26 files,
~93 KB, **zero source code**.

`MASTER.md` held a strong specification. Everything else was either empty or a
chat transcript: all ten `docs/*.md` files, `AGENTS.md` and `README.md` were
0 bytes, and `project-memory/` did not exist despite the prompt stating
that it did. There was no `.gitignore` — the highest-priority risk for a
privacy-first project. `CLAUDE.md` directed agents to read five empty files as
the source of truth and never mentioned `MASTER.md`.

The full audit is in [REPORT.md](REPORT.md).

## What was done

**M1.0 — safety and memory.** `.gitignore` first. Then the project-memory
system: `MEMORY_INDEX`, `PROJECT_STATE`, `MILESTONES`, `DECISIONS`, `RESEARCH`,
`DISCUSSION_SUMMARY`, `AI_AGENT_PROTOCOL`, `SESSION_LOG`, `SESSION_PROTOCOL`.
`AGENTS.md` written as the canonical cross-agent file; `QWEN.md` added;
`CLAUDE.md` and `GEMINI.md` rewritten as pointers.

**M1.1 — documentation.** All ten empty docs filled. `README`, `CONTRIBUTING`,
`CODE_OF_CONDUCT`, `CHANGELOG`, `.env.example`, `.gitattributes`.

**M1.2 — backend.** FastAPI with typed settings, health and config endpoints, an
in-process event bus, and traversal-safe path handling. 33 tests.

**M1.3 — frontend.** React + TypeScript + Vite single-page workspace. Light
default, dark toggle, system preference honoured, choice persisted. Plain CSS
custom properties. 19 tests.

**M1.4 — Docker.** Both Dockerfiles and `docker-compose.yml`, API published on
localhost only.

**M1.5 — CI and Pages.** Four CI jobs, a Pages workflow, issue and PR templates,
`docs/index.html` and `_config.yml`.

**M1.6 — cleanup.** Durable knowledge extracted from the transcripts into
project memory; transcripts moved to `docs/archive/`; scratch fragments deleted.

**Added mid-session, on request:** the session memory system
(`SESSION_PROTOCOL.md`, `sessions/`, `scripts/session.py`) and project identity
configuration (`project.json`, `scripts/set_identity.py`).

## Decisions made

D-006 Docker as the primary backend path · D-007 Python 3.11 floor · D-008 plain
CSS over a UI framework · D-009 in-process event bus · D-010
`project-memory/` as the single memory system · D-015 `main` branch with
per-repository identity · **D-016 PolyForm Noncommercial 1.0.0, superseding
D-012 (MIT)** · D-017 repository stays local for now.

D-016 was a mid-session reversal. The licence changed from MIT to
source-available before anything was published — deliberately, because the
direction is one-way: a licence can be relaxed later but never tightened.

## Files changed

```
Added:    .gitignore .gitattributes .env.example project.json LICENSE
          LICENSING.md README.md CONTRIBUTING.md CODE_OF_CONDUCT.md
          CHANGELOG.md AGENTS.md QWEN.md docker-compose.yml
          apps/api/**  (9 source files, 3 test files, Dockerfile, pyproject)
          apps/web/**  (11 source files, 2 test files, Dockerfile, configs)
          docs/*.md    (8 files, previously empty)
          docs/index.html docs/_config.yml
          project-memory/**  (9 files + sessions/)
          .github/workflows/{ci,docs-pages}.yml + templates
          scripts/{session,set_identity}.py

Modified: CLAUDE.md GEMINI.md  (were pointing at empty files)

Moved:    start.txt SETUP.md structure.md pc_specs.* prompts/first_time.md
          prompts/local_claude.md .claude/code.md  ->  docs/archive/

Deleted:  sreps.md NEXT_TBR.txt tbd.txt  (knowledge extracted first)
```

## Checks run

Every check below was executed, inside Docker, not inspected.

| Check | Command | Result |
|---|---|---|
| Backend tests | `pytest` | **33 passed** |
| Backend lint | `ruff check .` | **passed** |
| Backend format | `ruff format --check .` | **passed** |
| Backend types | `mypy src` (strict) | **passed**, 8 files |
| Frontend tests | `vitest run` | **19 passed** |
| Frontend types | `tsc --noEmit` | **passed** |
| Frontend lint | `eslint .` | **passed** |
| Frontend build | `vite build` | **passed**, 147.84 kB / 47.73 kB gzip |
| Docker build | `docker compose build` | both images built |
| Stack | `docker compose up -d` | both up, API healthy |
| API | `GET /api/health`, `/api/config` | 200, correct payloads |
| Interface | `GET localhost:5173` | 200, correct title |
| Ignore rules | `git check-ignore data/ .env` | both ignored |
| Project memory | `scripts/session.py check` | passed |

**Three real bugs were found by running things, not reading them:**

1. `config.py` used `Path(__file__).parents[4]`, which raised `IndexError`
   inside the container where the package sits at `/app/src/mind_archive/`.
   Replaced with an upward search for a project marker.
2. `vite.config.ts` referenced `process` without `@types/node`, and its `test`
   block was untyped because `defineConfig` came from `vite` rather than
   `vitest/config`.
3. Vitest 2 pulled in its own nested Vite 5 alongside Vite 6, producing two
   incompatible `Plugin` types and breaking `tsc`. Upgraded to Vitest 3.

Ruff also auto-fixed three formatting issues and a `datetime.UTC` modernisation.

## What remains

- `project.json` holds placeholder identity values.
- No git remote; CI and Pages have never run against a live repository.
- No `package-lock.json` committed.
- The frontend image runs the dev server, not a production build.
- No CLA, so outside contributions cannot be accepted.

## Exact next step

**Milestone 2 — the ChatGPT importer.** Build the `Importer` interface against
the real ChatGPT export format, treating every imported file as hostile input
and routing anything that becomes a filename through `paths.py`.
