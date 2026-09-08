# Gemini — Mind Archive

Read [`AGENTS.md`](AGENTS.md) first. It is the canonical instruction file for
every agent working on this project, and it is not repeated here.

Then read, in order:

1. `docs/project-memory/PROJECT_STATE.md` — what actually exists right now
2. `docs/project-memory/MILESTONES.md` — what is in scope
3. `docs/project-memory/DECISIONS.md` — what is already decided

Then open only the files your task touches.

## The short version

Mind Archive is local-first, privacy-first, user-owned and AI-provider
agnostic. React + TypeScript + Vite frontend, Python + FastAPI backend, SQLite
for metadata only, user content as human-readable files on the local
filesystem. Cloud is optional and off by default.

Light mode is the default; dark mode must keep working. Keep the UI simple and
written for humans.

Never claim a command passed unless you ran it. Never commit secrets or
personal archives. Work on the current milestone only.

## Note specific to this tool

Google Gemini and Google AI Studio are, for this project, one possible
development assistant and one possible future *import source*. Neither may
become an architectural dependency of the product.

Planning transcripts live in `docs/archive/`. They are history.
