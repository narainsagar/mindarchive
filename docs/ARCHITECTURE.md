# Architecture

How Mind Archive is put together, and why.

The decisions behind this document are recorded in
[project-memory/DECISIONS.md](project-memory/DECISIONS.md).

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
    (now)     (now)   (later)   (now)  adapters
      |        |        |       |       |
      +----------------+----------------+
                       |
            Local filesystem + SQLite
```

Two applications, one repository. They talk over plain HTTP with JSON. There is
no shared runtime, no build-time coupling, and no reason for either to know how
the other is implemented.

Items marked *(later)* are extension points with a defined place in the design;
they are not implemented yet. See
[project-memory/MILESTONES.md](project-memory/MILESTONES.md).

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
│   ├── zip_safety.py  Reading archives someone else produced
│   └── chatgpt.py     The ChatGPT adapter
├── archive/
│   └── writer.py      Conversations to Markdown and JSON on disk
└── routes/
    ├── health.py      GET /api/health
    ├── config.py      GET /api/config
    └── import_.py     GET /api/importers, POST /api/import
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
writing an adapter and adding it to one list. ChatGPT is the first
implementation and carries no special privileges in the design.

The interface will be generalised against a genuine second implementation in
Milestone 5, not guessed at in advance.

### Untrusted input

An export is a file from outside the application, so importers treat it as
hostile. `zip_safety.py` refuses path traversal, zip bombs and oversized
archives; every JSON field is checked before use; conversation titles become
folder names only through `paths.py`. One unreadable conversation is skipped
and reported rather than failing the whole import. See
[SECURITY.md](SECURITY.md).

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

Native development is supported and documented in [DEVELOPMENT.md](DEVELOPMENT.md),
and requires Python 3.11+ and Node 20+.

## What is deliberately absent

No microservices. No Kubernetes. No Redis, Kafka or Celery. No Elasticsearch —
SQLite full-text search is the plan, and is sufficient for a personal archive.
No authentication, because the application is single-user and local. No GraphQL.
No ORM yet.

Each of these can be added when a real requirement appears. Adding them before
that would make the project harder to understand for no benefit.
