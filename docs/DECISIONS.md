# Decisions

**The decision log lives in
[project-memory/DECISIONS.md](project-memory/DECISIONS.md).**

This file is a pointer, deliberately. Keeping two decision logs guarantees they
will disagree, and a decision log that cannot be trusted is worse than none.
See decision D-010.

Record new architectural and product decisions there, numbered and dated.

## Decisions at a glance

| # | Decision |
|---|---|
| D-001 | Local-first and privacy-first |
| D-002 | AI-provider agnostic; providers are importer adapters |
| D-003 | React + TypeScript + Vite, Python + FastAPI, SQLite |
| D-004 | Human-readable user data; SQLite holds metadata only |
| D-005 | Monorepo: `apps/web` and `apps/api` |
| D-006 | Docker is the primary supported backend path |
| D-007 | Python 3.11 minimum |
| D-008 | Plain CSS with custom properties; no UI framework |
| D-009 | In-process event bus in V1; no message broker |
| D-010 | `docs/project-memory/` is the single project-memory system |
| D-011 | Cloud disabled by default, never silently enabled |
| D-012 | ~~MIT License~~ — superseded by D-016 |
| D-013 | `AGENTS.md` is the canonical cross-agent instruction file |
| D-014 | ~~Light mode default; dark mode toggle~~ — superseded by D-029 |
| D-015 | Default branch `main`; per-repository git identity |
| D-016 | PolyForm Noncommercial 1.0.0; commercial licences sold separately |
| D-017 | ~~Repository stays local until there is a product worth showing~~ — superseded by D-032 |
| D-018 | Verification is developer-controlled; required at milestone boundaries |
| D-019 | Docker containers are disposable and never left running |
| D-020 | A conversation is served and rendered as one Markdown file |
| D-021 | Markdown rendered with `react-markdown`; raw HTML stays off |
| D-022 | Search matches all words, last word as a prefix |
| D-023 | A watched inbox folder, owned by default and configurable |
| D-024 | The fast path is a user-run script; no credential enters the app |
| D-025 | Tags live in `metadata.json`; an import never removes them |
| D-026 | Projects deferred; tags first |
| D-027 | Importers detect by shape, not by filename |
| D-028 | `StorageProvider` waits for Milestone 6 |
| D-029 | Appearance is two choices: a palette, and light / dark / system |
| D-030 | Import is a dialog; the header navigates within the one page |
| D-031 | The page carries Support, Contribute and a real footer |
| D-032 | Published publicly on GitHub; Pages for docs; no hosted application |
