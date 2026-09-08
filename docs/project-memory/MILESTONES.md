# Milestones

The plan, and what is actually finished. Update the status here whenever
milestone progress changes.

Status: ✅ done · 🚧 in progress · ⬜ not started

---

## Milestone 1 — Runnable foundation ✅

**Goal:** a clean, runnable, documented foundation. No product features.

| Item | Status |
|---|---|
| `.gitignore` protecting secrets and user data | ✅ |
| Project memory (`docs/project-memory/`) | ✅ |
| Cross-agent instructions (`AGENTS.md`, per-tool pointers) | ✅ |
| Documentation (`README.md`, `docs/*.md`) | ✅ |
| `LICENSE` (PolyForm Noncommercial), `LICENSING.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md` | ✅ |
| `project.json` + `scripts/set_identity.py` for project identity | ✅ |
| Session memory (`SESSION_PROTOCOL.md`, `sessions/`, `scripts/session.py`) | ✅ |
| `.env.example` with safe placeholders | ✅ |
| Backend: FastAPI, health + config endpoints, settings, event bus | ✅ |
| Backend tests (pytest) | ✅ |
| Frontend: React + TypeScript + Vite single-page workspace | ✅ |
| Light mode default, dark mode toggle | ✅ |
| Frontend tests (Vitest) | ✅ |
| Docker + Docker Compose | ✅ |
| GitHub Actions CI | ✅ |
| GitHub Pages documentation foundation | ✅ |
| Clean initial commit | ✅ |

**Deliberately excluded:** any importer, any archive browsing, any search, any
cloud or sync code, authentication, multi-user support.

---

## Milestone 2 — ChatGPT importer ✅

**Goal:** import a ChatGPT export and store it as human-readable files.

| Item | Status |
|---|---|
| `Importer` protocol: `detect()`, `validate()`, `parse()` | ✅ |
| Registry so core code never imports a provider module | ✅ |
| ChatGPT parser, including the branching `mapping` tree | ✅ |
| Normalisation into `Conversation` / `Message` | ✅ |
| Markdown + JSON metadata on disk, one folder per conversation | ✅ |
| Hostile-input handling: zip slip, zip bombs, size caps, path traversal | ✅ |
| `archive.imported` and `conversation.created` events | ✅ |
| Import UI: choose a file, see progress, plain-language result | ✅ |
| Tests for malformed, truncated and hostile input | ✅ |

**Deliberately excluded:** browsing or reading imported conversations, search,
the SQLite schema, attachments and images (recorded as placeholders in the
Markdown), abandoned conversation branches.

**Not generalised.** The adapter interface stays shaped by one real importer.
It gets generalised in Milestone 5 against a genuine second case.

---

## Milestone 3 — Archive browser, Markdown and search ⬜

- Browse imported conversations
- Render Markdown for reading
- SQLite schema for metadata and indexing
- Full-text search using SQLite FTS
- The database must be rebuildable from the files on disk

No Elasticsearch or external search infrastructure.

---

## Milestone 4 — Projects, tags, metadata and events ⬜

- Archive model: Project, Conversation, Message, Document, Memory, Tag,
  Attachment, Source, Metadata, Event
- Tagging and organisation
- Broader use of the event system

---

## Milestone 5 — Importer and plugin architecture expansion ⬜

- A second real importer (Claude or Gemini export), generalising the interface
  against a genuine second case
- Storage provider interface: `StorageProvider`, with `LocalStorageProvider` as
  the only implementation
- Export the whole archive

---

## Milestone 6 — Optional cloud storage and synchronisation ⬜

- `SyncProvider`, kept separate from `StorageProvider`
- `storage.mode` = `local` · `cloud` · `both`
- Disabled by default; never silently enabled (see DECISIONS.md D-011)
- Candidate adapters: S3-compatible, WebDAV, self-hosted. Not all at once.

---

## Milestone 7 — Production hardening and public release ⬜

- Security review, packaging, release process, public documentation site
