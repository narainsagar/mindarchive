# Session: import ergonomics — the inbox and honest re-import reporting

**ID:** 2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting
**Started:** 2026-09-08
**Ended:** 2026-09-08
**Agent:** Claude Opus 5 (Claude Code, VS Code extension)

---

## Goal

The importer had gone three milestones without seeing a real ChatGPT export.
The reason was a product problem, not an oversight: getting an export is slow
and its rules are not obvious. Make the wait less painful and the arrival
effortless.

## Starting state

`main` at `24d6be5`, clean. Milestone 3 complete. `local/` held only synthetic
fixtures.

## What was done

**Research first** (RESEARCH R-004). OpenAI's confirmation email says an export
"may take a few days" — the widely believed "24 hours" is how long the download
link lasts, and only the most recent request is fulfilled. Our own import panel
had the number exactly backwards. There is no official API for ChatGPT history,
so the wait cannot be automated; ingestion can.

**The inbox** (D-023). Save an export into `data/inbox/` and it imports itself —
on startup, on demand, and when the interface regains focus. No filesystem
watcher. Configurable to a folder you already keep exports in, and **that folder
is read, never rearranged** — a small ledger remembers what has been imported
instead. A folder you chose is never created for you.

**Honest re-import reporting.** Every provider export is a full export, so
re-importing now says "12 new, 8 updated, 392 already in your archive" — and an
unchanged conversation is not rewritten at all, so file timestamps keep meaning
something.

**Correct guidance** in the panel, the README and `local/README.md`: days to
prepare, 24-hour link expiry, one outstanding request.

**Testing without real data.** `inspect_export.py` reports structure and never
content; `make_fixture_export.py` generates large messy synthetic exports.

**The fast path** (D-024). `scripts/browser/chatgpt-export.js` plus
[FASTER_IMPORT.md](../../FASTER_IMPORT.md): a script the user runs in their own
logged-in tab. No token is pasted anywhere and Mind Archive never contacts
OpenAI. Mind Archive calling those endpoints itself is rejected outright.

**`docs/TRY_IT.md`** — a clean fifteen-minute walkthrough, on request.

## Problems found and fixed

**The startup scan blocked the server.** A large import left the API refusing
connections for minutes. Now on a background thread. Found by trying it.

**194s for 2,000 conversations looked like a code problem.** Measuring first
showed the same import takes 4.7s on the container filesystem and 127s on the
Windows bind mount — **27× slower**, same code. No optimisation was needed;
R-005 records it so nobody optimises the wrong thing later.

**`inspect_export.py` leaked content in its first draft** by listing archive
filenames. ChatGPT names attachments after what they are. Now reports extensions
and counts.

**The inbox reported the container's path**, repeating the Milestone 2 bug.
Fixed with `inbox_location`.

**Two pieces of an aborted edit script never landed**, and the container failed
to start with a `NameError`.

## Decisions made

- **D-023** — a watched inbox folder; owned and tidied by default, configurable,
  and never rearranging a folder the user chose.
- **D-024** — the fast path is a script the user runs; no credential ever enters
  Mind Archive.

## Files changed

```
Added:    apps/api/src/mind_archive/inbox.py
          apps/api/tests/test_inbox.py
          scripts/inspect_export.py
          scripts/make_fixture_export.py
          scripts/browser/chatgpt-export.js
          docs/FASTER_IMPORT.md
          docs/TRY_IT.md

Modified: apps/api/src/mind_archive/{config,main}.py
          apps/api/src/mind_archive/archive/writer.py
          apps/api/src/mind_archive/routes/import_.py
          apps/api/tests/test_archive_writer.py
          apps/web/src/{api.ts,styles.css}
          apps/web/src/components/ImportPanel.tsx (+ .test.tsx)
          .env.example .gitignore docker-compose.yml README.md CHANGELOG.md
          local/README.md docs/{ROADMAP,BACKLOG,DECISIONS}.md
          project-memory/{RESEARCH,DECISIONS,MILESTONES,PROJECT_STATE,
            SESSION_LOG}.md
```

## Checks run

`python scripts/dev.py verify`

| Check | Result |
|---|---|
| Backend lint (ruff) | **passed** |
| Backend formatting | **passed**, 36 files |
| Backend types (mypy strict) | **passed**, 23 files |
| Backend tests | **217 passed** (was 197) |
| Frontend lint | **passed** |
| Frontend types | **passed** |
| Frontend tests | **54 passed** (was 45) |
| Frontend build | **passed** |
| Project memory | **passed** |

**End to end against the running stack:** 2,000 synthetic conversations dropped
into `data/inbox/` and imported in the background while the API stayed
responsive (`/api/health` answered immediately throughout); 1,938 indexed and
searchable; the file tidied into `imported/`.

## What remains

- **Still no real ChatGPT export.** Now cheap to do: drop it in the inbox, run
  `inspect_export.py`, paste the safe structural output.
- No progress reporting during a long import.
- The browser script's output shape is believed identical to the official
  export's, unverified.
- Unchanged from Milestone 1: placeholder GitHub identity, no git remote, no
  committed `package-lock.json`, frontend image runs the dev server.

## Exact next step

Walk `docs/TRY_IT.md` end to end on a clean checkout. Then Milestone 4 —
projects, tags and metadata.
