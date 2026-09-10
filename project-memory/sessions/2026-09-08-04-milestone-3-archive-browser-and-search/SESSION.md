# Session: Milestone 3 — archive browser and search

**ID:** 2026-09-08-04-milestone-3-archive-browser-and-search
**Started:** 2026-09-08
**Ended:** 2026-09-08
**Agent:** Claude Opus 5 (Claude Code, VS Code extension)

---

## Goal

Milestone 3: read and search what has been imported. Until now you could import
a ChatGPT export and then had to open the files yourself.

## Starting state

`main` at `1670ad3`, working tree clean. Milestone 2 complete and verified.
`local/` held only the synthetic export from the previous session — the real
one had not arrived, so the outstanding real-data verification stayed
outstanding. Proceeded because this milestone reads the archive on disk rather
than exports, so a parser bug could not invalidate it.

## What was done

**The index.** SQLite with FTS5, built three ways from the same code path: at
startup when the archive has content but the index does not, on import through
the `conversation.created` event, and on demand via `POST /api/index/rebuild`.
Schema changes drop and rebuild rather than migrate, which is free because
nothing in the database is original.

**Reading back off disk.** `archive/reader.py` turns a conversation folder into
something the API can serve, tolerating folders that are not conversations —
people put things in folders.

**Search.** What someone types is rewritten into a safe FTS5 query: words
quoted, joined with `AND`, last word prefixed. Details and the reasoning are in
[REPORT.md](REPORT.md).

**API.** `GET /api/conversations` lists or searches with paging and per-source
counts; `GET /api/conversations/{path}` reads one from disk; `POST
/api/index/rebuild`.

**Interface.** An archive panel with a debounced search box, a result list with
marked snippets, and paging. Opening a conversation renders the Markdown in
place — still one page, still no router.

**Untrusted content.** Two paths where conversation text could have become
markup, both closed: `react-markdown` without raw HTML for bodies, and
`<<`/`>>` delimiters rather than HTML for snippets. Both have tests asserting an
`<img onerror=...>` never becomes an element. The path in the URL goes through
`safe_join`.

## Problems found and fixed

**A real design flaw, caught by a failing test.** The event handler that indexes
a new conversation called `get_settings()` directly. That function is cached, so
it ignored `dependency_overrides`: the import route wrote to the test's archive
while the handler indexed the real one. Settings are now bound when the handler
is built. `lifespan` had the same problem and now consults the same override.

**An unusable archive folder crashed startup.** `ensure_directories()` was
unguarded, so a data directory that was actually a file stopped the application
booting. It now logs and starts anyway.

**Three test-fixture bugs of mine.** Two fixtures shared message text, making
"matched one conversation" assertions meaningless; and a date assertion assumed
a British format when the component correctly uses the viewer's locale.

**One invented import.** `strip_front_matter_path` did not exist; and
`PathOutsideRoot` was really `UnsafePathError`. Both caught immediately by the
type checker and the test run.

## Decisions made

- **D-020** — a conversation is served and rendered as one Markdown file, not
  parsed back into messages.
- **D-021** — `react-markdown`, raw HTML off. The one new frontend dependency.
- **D-022** — search matches all words, last word as a prefix; no operators.

## Files changed

```
Added:    apps/api/src/mind_archive/index/{__init__,schema,indexer,search}.py
          apps/api/src/mind_archive/archive/reader.py
          apps/api/src/mind_archive/routes/conversations.py
          apps/api/tests/{test_index,test_conversations_api}.py
          apps/web/src/components/{ArchivePanel,ConversationView,Snippet}.tsx
          apps/web/src/components/ArchivePanel.test.tsx

Modified: apps/api/src/mind_archive/main.py  (startup index, event wiring)
          apps/api/src/mind_archive/archive/{__init__,writer}.py
          apps/web/src/{App.tsx,api.ts,styles.css}
          apps/web/package.json  (react-markdown)
          docs/{ARCHITECTURE,ROADMAP,DECISIONS}.md
          project-memory/{DECISIONS,MILESTONES,PROJECT_STATE,SESSION_LOG}.md
          CHANGELOG.md
```

## Checks run

`python scripts/dev.py verify`

| Check | Result |
|---|---|
| Backend lint (ruff) | **passed** |
| Backend formatting | **passed**, 34 files |
| Backend types (mypy strict) | **passed**, 22 files |
| Backend tests | **197 passed** (was 137) |
| Frontend lint | **passed** |
| Frontend types | **passed** |
| Frontend tests | **45 passed** (was 29) |
| Frontend build | **passed** |
| Project memory | **passed** |

**End-to-end against the running stack**, not just unit tests: imported a
synthetic export, then listed, searched, prefix-searched, read a conversation,
and rebuilt the index. Confirmed `C++`, `NEAR(`, `"` and `a AND OR b` all
return results rather than errors, that URL-encoded traversal returns 404, and
that the web interface serves.

## What remains

- **Still no real ChatGPT export has been imported.** Unchanged from Milestone
  2, and still the most valuable next check.
- No editing or deleting from the interface; no tags or projects; attachments
  still placeholders.
- Paging is Previous/Next rather than virtualised — fine for thousands.
- Unchanged from Milestone 1: placeholder GitHub identity, no git remote, no
  committed `package-lock.json`, frontend image runs the dev server.

## Exact next step

Import a real ChatGPT export from `local/` and fix what genuine data reveals.
Then Milestone 4 — projects, tags and metadata.
