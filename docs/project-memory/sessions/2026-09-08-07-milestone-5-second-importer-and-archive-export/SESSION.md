# Session: Milestone 5 — a second provider, and getting everything back out

**ID:** 2026-09-08-07-milestone-5-second-importer-and-archive-export
**Started:** 2026-09-08
**Ended:** 2026-09-08
**Agent:** Claude Opus 5 (Claude Code, VS Code extension)

---

## Goal

Milestone 5: a second real importer to generalise the adapter interface against
a genuine case, and whole-archive export.

## Starting state

`main` at `cc0ea2e`, clean. Milestone 4 complete. The user's WSL environment was
still unresolved, so nothing has been clicked through in a browser since
Milestone 3.

## What was done

**Researched Claude's export format** rather than trusting memory — Anthropic's
documented structure plus third-party parsers. It shares almost nothing with
ChatGPT's: a flat `chat_messages` list instead of a `mapping` tree, `name`
instead of `title`, `uuid` instead of `conversation_id`, ISO 8601 instead of
epoch, `sender: "human"` instead of `author.role: "user"`.

**The bug a second provider exposed.** Both providers ship a file called
`conversations.json`, and `detect()` matched on that filename — so the ChatGPT
importer would have claimed a Claude export and reported it empty. A latent
defect from Milestone 2 that no amount of testing one importer could find.
Detection now inspects shape (**D-027**).

**Shared what two callers actually wanted.** `importers/reading.py` now holds
the untrusted-JSON coercion, timestamp parsing for both formats, zip member
loading, and the shape-peeking used by detection. Extracted now, with two real
callers, rather than in Milestone 2 with one and a hypothesis.

**Whole-archive export.** `GET /api/export` zips the archive folder — exactly
the folder, same files, same layout, plus a `README.txt` for whoever opens it
without Mind Archive. A test asserts no `.db` is included: the index belongs to
the application, the conversations belong to the user.

**`StorageProvider` deliberately not built** (**D-028**) — see below.

## Problems found and fixed

**Strict detection broke two tests, correctly.** An empty or corrupt export
matched no importer, so the user would get "not recognised" instead of "that
export contains no conversations" or "not valid JSON on line 4". Fixed with
`has_member`, so an importer can tell "not our file" from "our file, broken",
and by making ChatGPT the documented fallback for an ambiguous shape.

**Documentation drift, caught by a failed edit.** Adding D-027/D-028 to the
index in `docs/DECISIONS.md` failed because D-025 and D-026 had never been added
there either — Milestone 4 updated the log but not its summary. Both added.

## Decisions made

- **D-027** — importers detect by shape, not by filename.
- **D-028** — `StorageProvider` waits for Milestone 6, because an interface with
  one implementation is a guess about the second. This milestone is the
  evidence.

## Files changed

```
Added:    apps/api/src/mind_archive/importers/{claude,reading}.py
          apps/api/src/mind_archive/routes/export.py
          apps/api/tests/test_claude_importer.py

Modified: apps/api/src/mind_archive/importers/{__init__,chatgpt}.py
          apps/api/src/mind_archive/main.py
          apps/api/tests/test_conversations_api.py
          apps/web/src/{api.ts,styles.css}
          apps/web/src/components/ArchivePanel.tsx (+ .test.tsx)
          docs/{ARCHITECTURE,ROADMAP,BACKLOG,DECISIONS}.md
          docs/project-memory/{DECISIONS,MILESTONES,PROJECT_STATE,SESSION_LOG}.md
          CHANGELOG.md
```

## Checks run

| Check | Result |
|---|---|
| Backend lint (ruff) | **passed** |
| Backend formatting | **passed** |
| Backend types (mypy strict) | **passed**, 25 source files |
| Backend tests | **295 passed** (was 254) |
| Frontend lint | **passed** |
| Frontend types | **passed** |
| Frontend tests | **66 passed** (was 64) |
| Frontend build | **passed** |
| Project memory | **passed** |

## What remains

- **No real export from either provider has been imported.** Five milestones.
  The Claude importer especially is written from documentation, not from data.
- **Nothing since Milestone 3 has been used in a browser.** Tags and the export
  button have tests but no human has clicked them.
- Attachments still placeholders; Gemini and others not supported.
- `StorageProvider` deferred to Milestone 6 by design.

## Exact next step

Milestone 6 — optional cloud storage and synchronisation, which is also where
`StorageProvider` gets designed against a real second implementation. But it is
worth saying plainly that shipping a cloud feature before anyone has used the
local one is the wrong order, and the honest next step is running it.
