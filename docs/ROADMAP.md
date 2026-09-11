---
title: Roadmap
permalink: /roadmap/
---

# Roadmap

Where Mind Archive is going. The detailed, authoritative version — including
what is finished — is
[MILESTONES.md]({{ '/milestones/' | relative_url }}).

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

## Milestone 3.5 — Import ergonomics ✅

Getting an export out of ChatGPT takes days, so importing one should take no
effort at all. A watched inbox folder imports anything you drop into it.
Re-importing reports what is genuinely new rather than counting everything
again, and rewrites nothing that has not changed. Correct guidance about the
export's real timings. An optional [faster route]({{ '/faster-import/' | relative_url }}) you run
yourself in your own browser.

---

## Milestone 4 — Organisation ✅

Tag your conversations, filter by tag, and combine that with search. Tags are
stored in your archive files, not in the database, so they travel with it and
survive anything happening to the index.

Projects were deliberately deferred — see decision D-026.

---

## Milestone 5 — More providers, and export ✅

Import from Claude as well as ChatGPT, and download your whole archive as a zip
of ordinary Markdown and JSON files that need nothing to read them.

The second importer did its real job: it exposed a bug in how exports were
recognised that only a second provider could have found.

---

## Milestone 6 — Optional cloud 🎯 next

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

Ideas that are not yet milestones live in [BACKLOG.md]({{ '/backlog/' | relative_url }}).
