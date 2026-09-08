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

## Milestone 3 — Archive browser, Markdown and search ✅

| Item | Status |
|---|---|
| Browse imported conversations | ✅ |
| Render Markdown for reading | ✅ |
| SQLite schema for metadata and indexing | ✅ |
| Full-text search using SQLite FTS5 | ✅ |
| The database is rebuildable from the files on disk | ✅ enforced by a test |
| Rebuild on startup, and on demand | ✅ |

No Elasticsearch or external search infrastructure, as planned.

**Deliberately excluded:** editing or deleting conversations from the
interface, tags, projects, and any per-message structure — the whole Markdown
file is rendered rather than parsed back into messages.

---

## Milestone 3.5 — Import ergonomics ✅

Slotted in after Milestone 3 because getting an export out of ChatGPT turned out
to be the real obstacle to using the product, not anything in the code. OpenAI's
own email says the export "may take a few days" — see [RESEARCH.md](RESEARCH.md)
R-004.

| Item | Status |
|---|---|
| Watched inbox folder — drop an export in and it imports itself | ✅ |
| Configurable to a folder you already keep exports in, files left in place | ✅ |
| Honest re-import reporting: new, updated, already there | ✅ |
| Unchanged conversations are not rewritten at all | ✅ |
| Correct guidance: days to prepare, 24h link expiry, one request at a time | ✅ |
| `scripts/inspect_export.py` — structure only, safe to share | ✅ |
| `scripts/make_fixture_export.py` — large messy synthetic exports | ✅ |
| `scripts/browser/chatgpt-export.js` — optional fast path, run by the user | ✅ |

**Deliberately excluded:** a filesystem watcher (scanning covers it), progress
reporting during a long import, and anything that puts a session token inside
Mind Archive (D-024).

---

## Milestone 4 — Tags ✅

| Item | Status |
|---|---|
| Tags stored in `metadata.json`, indexed in SQLite | ✅ |
| An import never removes a tag | ✅ enforced by a test |
| Add and remove tags on a conversation | ✅ |
| Filter by tag, combined with search | ✅ |
| Tag counts | ✅ |
| `conversation.tagged` event | ✅ |

**Deliberately excluded** (D-026): Projects, and the `Memory` / `Document` /
`Attachment` model types originally listed here. Tags plus full-text search
already answer the question people actually have. A schema with no feature
behind it is one nobody has tested against a real need.

Projects are in `docs/BACKLOG.md`, most likely as a reserved tag namespace
rather than a parallel hierarchy.

---

## Milestone 5 — A second provider, and getting everything back out ✅

| Item | Status |
|---|---|
| A second real importer (Claude) | ✅ |
| The `Importer` interface generalised against it | ✅ |
| Shared JSON reading extracted once two callers wanted it | ✅ |
| Export the whole archive as ordinary files | ✅ |
| `StorageProvider` interface | ⬜ **deferred to Milestone 6** (D-028) |

**What the second provider revealed.** ChatGPT and Claude both ship a file
called `conversations.json`, and detection matched on the filename — so the
ChatGPT importer would have claimed a Claude export and reported it empty. A
latent bug from Milestone 2 that no amount of testing one importer could find.
Detection now inspects shape (D-027).

**Why `StorageProvider` waits.** An interface with one implementation is a guess
about the second, and this milestone is the evidence: the `Importer` interface
only revealed its defect when a real second case arrived. Building
`StorageProvider` now — with cloud still a milestone away — would repeat the
mistake this milestone just corrected (D-028).

---

## Milestone 6 — Optional cloud storage and synchronisation ⬜

- `SyncProvider`, kept separate from `StorageProvider`
- `storage.mode` = `local` · `cloud` · `both`
- Disabled by default; never silently enabled (see DECISIONS.md D-011)
- Candidate adapters: S3-compatible, WebDAV, self-hosted. Not all at once.

---

## Milestone 7 — Production hardening and public release ⬜

- Security review, packaging, release process, public documentation site
