# Session: archive cleanup and developer-controlled workflow

**ID:** 2026-09-08-02-archive-cleanup-and-dev-workflow
**Started:** 2026-09-08
**Ended:** 2026-09-08
**Agent:** Claude Opus 5 (Claude Code, VS Code extension)

---

## Goal

Three pieces of groundwork before Milestone 2: audit and clean up
`docs/archive/`, replace run-tests-on-every-change with developer-controlled
verification, and make Docker containers disposable.

## Starting state

`main` at `5048c37`, working tree clean. Milestone 1 complete and verified.
`docs/archive/` held 9 files and 2,565 lines of planning transcript.

## What was done

**Archive audit and removal.** Every file assessed — see [REPORT.md](REPORT.md).
Only `SETUP.md` held unextracted durable content; it was merged into
`RESEARCH.md` R-002 along with the `pc_specs` probe commands. The folder was
then deleted, which is safe because all nine files are committed in `fcf1f5c`.
Eight files carrying dangling references were updated to point at that commit.

Found and recorded a Milestone 1 error: `agent-tooling-research.md` was
misnamed during that session — it was a prompt, not research.

**Developer-controlled verification (D-018).** Tests are no longer expected on
every change. Required before a milestone completes, before a pull request, and
before a release. Documented in `AGENTS.md`, `CLAUDE.md`,
`AI_AGENT_PROTOCOL.md`, `DEVELOPMENT.md`, `CONTRIBUTING.md` and the PR
template.

**Disposable Docker (D-019).** Every check runs in a `--rm` container, `verify`
tears the stack down, and `clean` removes this project's containers, volumes and
images. `./data` is a bind mount, so no cleanup command can delete the archive.

**`scripts/dev.py`.** One entry point for both: `up`, `down`, `stop`, `restart`,
`status`, `logs`, `clean` for the stack; `test`, `lint`, `types`, `format`,
`build`, `verify` for checks.

**Two small fixes.** `session.py slugify` truncated mid-word, producing folder
names like `...-testing-docke`; it now cuts at a word boundary, and this
session's folder was renamed. `dev.py` now suppresses ANSI colour when stdout
is not a capable terminal, which was filling PowerShell output with escape
codes.

## Decisions made

- **D-018** — verification is developer-controlled during development, required
  at milestone boundaries.
- **D-019** — Docker containers are disposable and never left running.

## Files changed

```
Added:    scripts/dev.py
          project-memory/sessions/2026-09-08-02-.../{SESSION,PROMPTS,REPORT}.md

Modified: AGENTS.md CLAUDE.md GEMINI.md QWEN.md README.md CONTRIBUTING.md
          CHANGELOG.md .github/pull_request_template.md
          docs/DEVELOPMENT.md docs/DECISIONS.md
          project-memory/{DECISIONS,RESEARCH,MEMORY_INDEX,
            DISCUSSION_SUMMARY,AI_AGENT_PROTOCOL,SESSION_LOG}.md
          project-memory/sessions/2026-09-08-01-.../PROMPTS.md
          scripts/session.py

Deleted:  docs/archive/  (9 files, recoverable from fcf1f5c)
```

## Checks run

`python scripts/dev.py verify` — the new gate, exercising itself.

| Check | Result |
|---|---|
| Backend lint | **passed** |
| Backend formatting | **passed**, 12 files |
| Backend types (mypy strict) | **passed**, 8 files |
| Backend tests | **33 passed** |
| Frontend lint | **passed** |
| Frontend types | **passed** |
| Frontend tests | **19 passed** |
| Frontend build | **passed**, 32 modules |
| Project memory | **failed on first run** — correctly, because this session's record was unwritten. Passed once completed. |
| Teardown | stack stopped automatically |

The memory check failing before the session record existed is the system
working as intended, not a defect.

## What remains

Unchanged from Milestone 1: `project.json` still holds placeholder identity
values, there is no git remote, no `package-lock.json` is committed, the
frontend image runs the dev server rather than a production build, and no CLA
exists.

## Exact next step

**Milestone 2 — the ChatGPT importer.** Build the `Importer` interface against
the real ChatGPT export format, treating every imported file as hostile input
and routing anything that becomes a filename through `paths.py`.
