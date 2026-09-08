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

## Milestone 2 — ChatGPT importer ⬜

**Goal:** import a ChatGPT export and store it as human-readable files.

- `Importer` adapter interface: `name`, `supported_formats`, `detect()`,
  `validate()`, `import()`, `normalize()`
- ChatGPT export parser (`conversations.json` inside the export archive)
- Normalisation into the internal conversation model
- Write conversations to disk as Markdown with JSON metadata
- Treat every imported file as untrusted: validate structure, guard against
  path traversal, cap sizes
- Emit `archive.imported` and `conversation.created`
- Import UI: choose a file, see progress, see a plain-language result
- Tests covering malformed, truncated and hostile inputs

**Do not** generalise the adapter interface to other providers yet. One real
importer first; generalise against a second real case in Milestone 5.

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
