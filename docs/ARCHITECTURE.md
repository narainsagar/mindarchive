---
title: Architecture
permalink: /architecture/
---

# Architecture

How Mind Archive is put together, and why.

The decisions behind this document are recorded in
[project-memory/DECISIONS.md](https://github.com/RootedGlobal/mindarchive/blob/main/project-memory/DECISIONS.md).

## Shape of the system

```
                    Browser
                       |
        React + TypeScript + Vite  (apps/web)
                       |
                    HTTP / JSON
                       |
          Python + FastAPI  (apps/api)
                       |
      +----------------+----------------+
      |        |        |       |       |
  Importers  Archive  Search  Events  Storage
    (now)     (now)    (now)    (now)  adapters
      |        |        |       |       |
      +----------------+----------------+
                       |
            Local filesystem + SQLite
```

Two applications, one repository. They talk over plain HTTP with JSON. There is
no shared runtime, no build-time coupling, and no reason for either to know how
the other is implemented.

Storage adapters are the one piece still to come: local storage is currently
direct filesystem access, and the interface is introduced in Milestone 5 against
a real second implementation rather than guessed at now. See
[project-memory/MILESTONES.md](https://github.com/RootedGlobal/mindarchive/blob/main/project-memory/MILESTONES.md).

## Backend — `apps/api`

```
apps/api/src/mind_archive/
├── main.py            FastAPI application, CORS, router wiring
├── config.py          Typed settings from environment variables
├── events.py          Small in-process event bus
├── paths.py           Safe resolution of filesystem paths
├── models.py          Conversation and Message, the archive's own model
├── importers/
│   ├── __init__.py    The registry: which importer can read this file
│   ├── base.py        The Importer protocol every provider satisfies
│   ├── reading.py     Reading untrusted JSON, shared by every importer
│   ├── zip_safety.py  Reading archives someone else produced
│   ├── chatgpt.py     The ChatGPT adapter
│   └── claude.py      The Claude adapter
├── archive/
│   ├── writer.py      Conversations to Markdown and JSON on disk
│   └── reader.py      ... and back off disk again
├── index/
│   ├── schema.py      The SQLite schema. Derived, droppable, rebuildable
│   ├── indexer.py     Building the index by reading the archive
│   └── search.py      FTS5 queries, and rewriting what people type
└── routes/
    ├── health.py      GET /api/health
    ├── config.py      GET /api/config
    ├── import_.py     GET /api/importers, POST /api/import, the inbox
    ├── conversations.py  GET /api/conversations, tags, POST /api/index/rebuild
    └── export.py      GET /api/export — the whole archive as a zip
```

**Configuration** is typed and read from the environment through
`pydantic-settings`. Nothing reads `os.environ` directly, and no secret is ever
returned by an API endpoint.

**The event bus** is a synchronous, in-process publish/subscribe helper. Event
names are `noun.verb` — `archive.imported`, `conversation.created`,
`document.indexed`, `sync.completed`. It exists now so that later milestones
have a real extension point rather than an aspiration. It is deliberately not a
message broker; see decision D-009.

**Path safety** is centralised in `paths.py`. Every path that originates outside
the application — a configured archive location, a filename inside an imported
export — is resolved and checked to be inside the archive root before use. This
matters most in Milestone 2, when untrusted archives start arriving.

**Storage** will sit behind a `StorageProvider` interface with
`LocalStorageProvider` as the only implementation for the foreseeable future.
Synchronisation, when it arrives, is a separate `SyncProvider` concern — storing
a file and replicating it elsewhere are different problems and should not share
an interface.

## Frontend — `apps/web`

```
apps/web/src/
├── main.tsx           Entry point
├── App.tsx            The single workspace
├── api.ts             Typed calls to the backend
├── theme.ts           Light/dark handling
├── styles.css         CSS custom properties for both themes
└── components/
    ├── Header.tsx
    ├── ThemeToggle.tsx
    ├── ImportPanel.tsx
    ├── ArchivePanel.tsx      Browse and search
    ├── ConversationView.tsx  Read one
    ├── Snippet.tsx           A search match, marked
    └── StatusPanel.tsx
```

One page, one workspace, a minimal header. No router yet, because there is one
view. No state management library, because component state is sufficient. No UI
framework — theming is CSS custom properties on `:root`, which is both smaller
and less likely to produce a generic, AI-generated look (decision D-008).

Light is the default theme. With no stored preference the system setting is
honoured, falling back to light. The choice persists in `localStorage`, wrapped
in `try`/`catch` because storage can be unavailable.

## Data

Two kinds of data, deliberately separated.

**Your content** — conversations, documents, attachments — is written to the
filesystem as Markdown, JSON and plain text under the archive directory. It is
readable, greppable and portable with ordinary tools.

**Application metadata** — indexes, search tables, import records — lives in
SQLite.

The rule that keeps these honest: **deleting the SQLite database must never
destroy your content.** It must be rebuildable by re-reading the files on disk.
This is what prevents the archive from becoming another proprietary silo.

That rule is enforced by a test — `test_deleting_the_database_loses_nothing`
deletes the database, rebuilds it, and checks the results are identical. If it
ever fails, something has started living only in SQLite, and that is a bug.

The index is rebuilt automatically at startup when the archive has content but
the index does not, which is what makes copying the archive folder to another
machine enough. `POST /api/index/rebuild` does the same on demand.

```
data/
├── archive/              Your conversations and documents
│   └── <source>/<conversation>/
│       ├── conversation.md
│       └── metadata.json
└── mind_archive.db       Index only. Rebuildable. Disposable.
```

## Providers are adapters

Every AI provider is an importer adapter behind one interface:

```python
class Importer(Protocol):
    name: str                      # "chatgpt"
    display_name: str              # "ChatGPT"
    supported_formats: list[str]   # [".zip", ".json"]

    def detect(self, path: Path) -> bool: ...
    def validate(self, path: Path) -> ValidationResult: ...
    def parse(self, path: Path) -> ImportResult: ...
```

`parse` returns `Conversation` objects and writes nothing. Storing them is the
archive's job, which keeps parsing testable without touching the filesystem.

Core code never imports a provider-specific module — it asks the registry in
`importers/__init__.py` which adapter can read a file. Adding a provider means
writing an adapter and adding it to one list.

**Detection inspects the file's shape, not its name** (D-027). ChatGPT and
Claude both ship a file called `conversations.json`, so matching on the filename
had the ChatGPT importer confidently claiming Claude exports. That defect had
existed since Milestone 2, and only a second real provider could expose it —
which is precisely why the interface was generalised against a genuine second
case rather than a guessed one.

The two formats share almost nothing:

| | ChatGPT | Claude |
|---|---|---|
| Messages | a `mapping` tree plus `current_node` | a flat `chat_messages` list |
| Title / id | `title` / `conversation_id` | `name` / `uuid` |
| Timestamps | Unix epoch floats | ISO 8601 strings |
| Speaker | `author.role`, `"user"` | `sender`, `"human"` |

What they *do* share — reading a JSON member out of a zip, coercing untrusted
values, refusing to raise on a bad field — moved into `importers/reading.py`
once two real callers wanted it, rather than when one might.

### Untrusted input

An export is a file from outside the application, so importers treat it as
hostile. `zip_safety.py` refuses path traversal, zip bombs and oversized
archives; every JSON field is checked before use; conversation titles become
folder names only through `paths.py`. One unreadable conversation is skipped
and reported rather than failing the whole import. See
[SECURITY.md]({{ '/security/' | relative_url }}).

## Search

SQLite FTS5, with the porter tokenizer so "bake" finds "baking". No
Elasticsearch: a personal archive is thousands of conversations, and adding a
search server would be infrastructure without a requirement.

`MATCH` takes a query *language*, not a string, so what someone types is
rewritten before it gets there. `C++`, a lone `"`, or `NEAR(` are all syntax
errors in FTS5 and none of them should be an error in a search box. The input is
split into words, each is quoted, and they are joined with `AND`; the last word
gets a prefix wildcard so results narrow as you type. A query with nothing
searchable in it means "no filter", not "no results".

This is about correctness rather than security — the query was always a bound
parameter.

## Taking it all with you

`GET /api/export` zips the archive folder and hands it over. What comes out is
not a bundle in some format of ours — it is exactly the folder from disk: same
Markdown, same JSON, same layout, plus a `README.txt` explaining how to read it
without Mind Archive.

This is what makes "your data is yours" a property rather than a claim.

**Storage adapters are still direct filesystem access.** A `StorageProvider`
interface with a single implementation would be a guess about the second, so it
waits for Milestone 6, where a real cloud adapter can shape it (D-028).

## Cloud

Not implemented, and off by default when it is. `MIND_ARCHIVE_CLOUD_ENABLED`
defaults to `false`, the API reports cloud status so the interface can state
plainly where your data lives, and no code path uploads anything without
explicit configuration. See decision D-011.

## Running it

Docker Compose is the primary supported path, because it gives every contributor
an identical, current runtime (decision D-006).

```
docker compose up --build
    web  → localhost:5173  (Vite dev server)
    api  → localhost:8000  (Uvicorn)
    data → ./data          (bind mount, git-ignored)
```

Native development is supported and documented in [DEVELOPMENT.md]({{ '/development/' | relative_url }}),
and requires Python 3.11+ and Node 20+.

## What is deliberately absent

No microservices. No Kubernetes. No Redis, Kafka or Celery. No Elasticsearch —
SQLite full-text search is the plan, and is sufficient for a personal archive.
No authentication, because the application is single-user and local. No GraphQL.
No ORM yet.

Each of these can be added when a real requirement appears. Adding them before
that would make the project harder to understand for no benefit.
