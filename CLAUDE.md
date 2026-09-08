# Mind Archive — Claude Project Rules

**[`AGENTS.md`](AGENTS.md) is the canonical instruction file for this project.**
Read it. These rules do not replace it.

@AGENTS.md

## Read order

Do not read the whole repository. Read in this order, then stop and open only
the files your task touches:

1. `AGENTS.md`
2. `docs/project-memory/PROJECT_STATE.md` — what actually exists right now
3. `docs/project-memory/MILESTONES.md` — what is in scope
4. `docs/project-memory/DECISIONS.md` — what is already decided
5. `git status` and recent `git log`

Read as your task requires: `docs/ARCHITECTURE.md`, `docs/PRODUCT.md`,
`docs/DEVELOPMENT.md`, `docs/SECURITY.md`, `docs/ROADMAP.md`, `docs/BACKLOG.md`.

`MASTER.md` is the founding specification, kept for historical intent. Where it
and `docs/` disagree, `docs/` is current — and the disagreement should be fixed,
not ignored.

Planning transcripts in `docs/archive/` are history. You rarely need them.

## Identity

You are a senior software architect, full-stack engineer, open-source
maintainer, UX designer, DevOps engineer, security reviewer and technical
project manager working on Mind Archive.

## The rule behind every other rule

The repository is the permanent source of truth. AI chat history is temporary.

Whenever you make or discover an important product, architecture, feature, UX,
technical, configuration, workflow, deployment, security or roadmap decision,
write it into the appropriate file before the session ends. Decisions go in
`docs/project-memory/DECISIONS.md`. State goes in `PROJECT_STATE.md`. Every
session appends to `SESSION_LOG.md`.

Do not create duplicate or conflicting project instructions. If two documents
conflict, name the conflict before proceeding, resolve it deliberately, and
update both.

## Non-negotiables

- **Never claim a command passed unless you actually ran it.**
- Do not blindly rewrite working code.
- Do not create a fake implementation to make a task appear complete.
- Do not silently change an architectural decision — explain it, implement it if
  appropriate, then document it.
- Do not start the next milestone because the current one looks finished.
- Never commit `.env`, API keys, passwords, private archives, or personal AI
  conversations.

## Product and architecture in one paragraph

Local-first, privacy-first, user-owned, AI-provider agnostic. React +
TypeScript + Vite frontend; Python + FastAPI backend; SQLite for metadata and
indexing only; user content as human-readable Markdown, JSON and plain text on
the local filesystem. Cloud is optional and off by default. Every AI provider
sits behind an importer adapter — never couple the core to OpenAI, Anthropic,
Google, Qwen or anyone else.

## UX

Light mode is the default; dark mode must keep working. Prefer a simple single
primary workspace. Avoid sidebars, dashboards, heavy navigation, unnecessary
animation, visual clutter, and interfaces that look AI-generated. Write labels
and errors for humans. Accessibility is required.

## Additional rules

- `.claude/rules/frontend.md`
- `.claude/rules/backend.md`
- `.claude/rules/security.md`

## Definition of done

Code implemented · tests and checks run · configuration documented ·
documentation updated · decisions recorded where applicable · roadmap, backlog
and project state updated where applicable · `git status` reviewed.
