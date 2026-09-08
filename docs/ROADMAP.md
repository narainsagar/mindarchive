# Roadmap

Where Mind Archive is going. The detailed, authoritative version — including
what is finished — is
[project-memory/MILESTONES.md](project-memory/MILESTONES.md).

The repository must remain runnable after every milestone.

---

## Milestone 1 — Runnable foundation ✅

A clean, documented, runnable foundation with no product features yet.

React + TypeScript + Vite frontend with light and dark modes. Python + FastAPI
backend with typed settings, health and configuration endpoints, and a small
in-process event bus. Docker and Docker Compose. GitHub Actions CI. A GitHub
Pages documentation foundation. Tests on both sides. Complete documentation and
project memory.

---

## Milestone 2 — ChatGPT importer ✅

The point at which Mind Archive becomes useful.

Import a ChatGPT export and store it as human-readable Markdown with JSON
metadata. Establish the `Importer` adapter interface that every later provider
will use. Treat imported files as untrusted throughout. A simple import screen
that reports what happened in plain language.

---

## Milestone 3 — Archive browser and search ✅

Browse and read imported conversations. Markdown rendering. A SQLite schema for
metadata and indexing, with full-text search through SQLite FTS. The database
stays rebuildable from the files on disk.

---

## Milestone 4 — Organisation 🎯 next

Projects, tags and metadata. The fuller archive model — Conversation, Message,
Document, Memory, Tag, Attachment, Source. Broader use of the event system.

---

## Milestone 5 — More providers, and export

A second real importer, most likely Claude or Gemini, used to generalise the
adapter interface against a genuine second case rather than a guess. The
`StorageProvider` interface. Full archive export.

---

## Milestone 6 — Optional cloud

Opt-in synchronisation to storage you choose. Disabled by default, never
enabled silently. `SyncProvider` kept separate from `StorageProvider`.
Candidate adapters — S3-compatible, WebDAV, self-hosted — added one at a time.

---

## Milestone 7 — Production hardening and public release

Security review, packaging, a release process, and the public documentation
site.

---

## Not planned

A hosted service. An account system. A chat interface. Telemetry. Anything that
requires a network connection for the core product to work.

Ideas that are not yet milestones live in [BACKLOG.md](BACKLOG.md).
