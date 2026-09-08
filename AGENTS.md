# AGENTS.md

Instructions for anyone working on Mind Archive — AI coding agents and humans
alike. This is the canonical file. `CLAUDE.md`, `GEMINI.md` and `QWEN.md` point
here; they do not repeat it.

---

## The project

**Mind Archive — Your Personal AI Mind Archive.**
*Own your AI memory. Simple, private, and yours.*

A local-first, source-available application for preserving, organising,
searching, importing and exporting your AI conversations, memories, knowledge
and files. It must remain useful after you change AI provider.

Licensed under [PolyForm Noncommercial 1.0.0](LICENSE) — free for noncommercial
use, commercial use requires a separate licence. See [LICENSING.md](LICENSING.md).
Source-available, not open source: keep the code readable and inspectable, and
do not describe the project as open source.

## The rule behind every other rule

**The repository is the permanent source of truth. AI chat history is
temporary.**

Never depend on a conversation as the only record of a decision. If it matters,
write it into the repository before the session ends.

## Read this first, and stop

Do not read the whole repository. Read in this order:

1. This file
2. `docs/project-memory/PROJECT_STATE.md` — what actually exists right now
3. `docs/project-memory/MILESTONES.md` — what is in scope
4. `docs/project-memory/DECISIONS.md` — what is already decided
5. `git status`, recent `git log`

Then locate only the files your task touches.

Read as needed: `docs/ARCHITECTURE.md`, `docs/PRODUCT.md`,
`docs/DEVELOPMENT.md`, `docs/SECURITY.md`.

`MASTER.md` is the founding specification, kept for historical intent. Where it
and `docs/` disagree, `docs/` is current — and the disagreement should be fixed.

The full working method is in
[`docs/project-memory/AI_AGENT_PROTOCOL.md`](docs/project-memory/AI_AGENT_PROTOCOL.md).

## Principles

Local first · Privacy first · User owns their data · AI-provider agnostic ·
Source available · Human readable · Simple UX · Event driven · Portable ·
Extensible · Contributor friendly

## Architecture

```
Web UI (React + TypeScript + Vite)
        |
        v
API layer (Python + FastAPI)
        |
        +-- Importers (adapters, one per provider)
        +-- Archive
        +-- Search
        +-- Events (in-process bus)
        +-- Storage adapters
        +-- Configuration
        |
        v
Local filesystem + SQLite
```

- The local filesystem is the default storage. Cloud is optional and off by
  default.
- Every AI provider lives behind an importer adapter. Core code never imports
  provider-specific modules.
- User content is Markdown, JSON and plain text. SQLite holds metadata and
  indexes only, and must be rebuildable from the files on disk.

Do not couple the core to OpenAI, Anthropic, Google, Qwen or any other provider.

## UX

Light mode is the default. Dark mode must keep working. Prefer a single primary
workspace with minimal top navigation.

Avoid: permanent sidebars, dashboards, heavy navigation, unnecessary animation,
visual clutter, and interfaces that look AI-generated.

Write for humans. "Import archive", not "Initialize ingestion pipeline". "Your
archive is stored locally", not "Local persistence subsystem operational".

Accessibility is required, not optional.

## Working method

**Before editing:** inspect the repository, read the relevant documentation,
understand the existing architecture, and identify the smallest correct change.

**After editing:** run the tests and checks, review the diff, update the
documentation, record any architectural decision, update the roadmap or backlog
if scope changed, and review `git status`.

**Never claim a command passed unless you actually ran it.** Code inspection is
not verification. If something failed, say so and show the output.

Do not blindly rewrite working code. Do not refactor beyond your task. Do not
create a fake implementation to make a task look complete. Do not silently
change an architectural decision — explain it, implement it if appropriate, then
document it.

Work on the current milestone only.

## Engineering philosophy

```
simple      >  clever
readable    >  abstract
portable    >  vendor-specific
tested      >  impressive
maintainable>  fashionable
```

Do not introduce microservices, Kubernetes, Redis, Kafka, Elasticsearch or
cloud infrastructure without a documented reason grounded in a real requirement.

Do not add a dependency you cannot justify in one sentence.

## Security

Never commit secrets, API keys, passwords, tokens, private keys or personal
archives. Never expose API keys to the frontend.

Treat every imported file as untrusted input. Check filesystem paths for
traversal. Do not log private conversation content unnecessarily. Keep cloud
functionality disabled by default and never enable it silently.

Details in `docs/SECURITY.md` and `.claude/rules/security.md`.

## Documentation is part of the implementation

If behaviour changes, update the documentation. If architecture changes, update
`docs/ARCHITECTURE.md` and `docs/project-memory/DECISIONS.md`. If development
commands change, update `docs/DEVELOPMENT.md` and `README.md`.

Never let documentation and code drift apart. If two documents conflict, name
the conflict, resolve it deliberately, and update both.

## Definition of done

A change is not complete until:

1. Code is implemented.
2. Tests and checks have been run.
3. Configuration is documented.
4. Relevant documentation is updated.
5. Architectural decisions are recorded where applicable.
6. Roadmap, backlog and project state are updated where applicable.
7. `git status` has been reviewed.

## Git

Small, meaningful commits:

```
feat: add ChatGPT archive importer
fix: handle malformed conversation metadata
docs: update WSL development guide
refactor: simplify storage provider interface
chore: establish project foundation
```

## Quick commands

```bash
# Everything, the supported way
cp .env.example .env
docker compose up --build      # web on :5173, API on :8000

# Backend, natively (needs Python 3.11+)
cd apps/api && python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]" && pytest && uvicorn mind_archive.main:app --reload

# Frontend, natively (needs Node 20+)
cd apps/web && npm install && npm run dev && npm test
```
