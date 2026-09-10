---
title: How Mind Archive is built
summary: React, FastAPI, SQLite and a folder of Markdown. A short tour of the architecture, and the two constraints that decided most of it.
author: Mind Archive
tags: [engineering]
---

Mind Archive is a small application, and staying small is a design goal rather
than an accident. Here is the shape of it.

```
Web UI  (React + TypeScript + Vite)
   |
API     (Python + FastAPI)
   |
   +-- Importers   one adapter per provider
   +-- Archive     reads and writes the files
   +-- Search      full-text, over SQLite FTS5
   +-- Events      an in-process bus
   |
Local filesystem + SQLite
```

Two constraints decided almost everything else.

## Constraint one: the files are the truth

User content is Markdown, JSON and plain text on disk. SQLite holds metadata and
search indexes **only**, and must be rebuildable from the files at any time.

This sounds like a storage detail. It is actually the product. It means:

- You can read your archive without us.
- A corrupted index is an inconvenience, not a loss.
- Backup is "copy a folder" — every tool you already own works.
- Migrating away is a no-op, because you were never locked in.

The moment the database becomes the source of truth, all four of those go away.
So it does not get to be.

## Constraint two: no provider is special

Every AI provider lives behind an importer adapter, and core code never imports
a provider-specific module. Adding Gemini means adding one adapter and one test;
it does not mean touching the archive, the search, or the ChatGPT importer.

This paid off faster than expected. ChatGPT and Claude both export a file called
`conversations.json`, and the original importer matched on that filename — so it
would have confidently claimed a Claude export and reported it empty. Detection
now inspects the *shape* of the file instead. It was a latent bug that no amount
of testing one importer could have found, and the fix stayed inside the adapter
layer where it belonged.

## The interface is one page

No router. No sidebar. No dashboard.

There is one view — your archive — with search, import and status on it. A
conversation opens in place rather than navigating somewhere. When the page grew
long enough to need it, we added in-page anchors in the header, which is
navigation *within* one view rather than between several.

It is styled with plain CSS and custom properties. No component framework,
because a framework is a large dependency that pulls an interface toward looking
like every other interface built with it. There are three palettes and a Light /
Dark / System theme, all driven by two attributes on `<html>` and one set of
tokens.

## Events, without the infrastructure

There is an in-process event bus — about forty lines. `archive.imported` fires,
things listen.

There is no message broker, no queue, no Redis. For a single-user application
running on one machine, those would be operational weight bought against a
requirement nobody has. The extension point is real; the infrastructure behind it
is a function call.

## Docker is the supported path

Not because containers are fashionable, but because of a specific problem: the
machine this project started on had Python 3.7 on Windows and 3.8 in WSL2, both
end-of-life and neither able to run a modern FastAPI stack. That is a common
situation, and Docker removes it as a question:

```bash
python scripts/dev.py up --build
```

Native setup is documented and fully supported for anyone who prefers it.

## The stack, and why each piece

| Piece | Why |
|---|---|
| React + TypeScript + Vite | Types catch the class of bug that ruins a data tool; Vite is fast and unopinionated |
| Python + FastAPI | Typed request models, and the ecosystem for reading messy archive formats |
| SQLite + FTS5 | Real full-text search in a file. No service to run, no port to secure |
| Plain CSS | No framework, no generated look |
| Docker Compose | One command, identical everywhere |

Nothing here is exotic, and that is the point. The interesting decisions are
about what was left out — which is
[its own post]({{ '/blog/decisions-worth-stealing/' | relative_url }}).
