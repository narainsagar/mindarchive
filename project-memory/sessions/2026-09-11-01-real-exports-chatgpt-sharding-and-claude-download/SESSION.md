# Session: Real exports: ChatGPT sharding and Claude download manifest

**ID:** 2026-09-11-01-real-exports-chatgpt-sharding-and-claude-download
**Started:** 2026-09-11 04:08
**Ended:** 2026-09-11 04:48
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Make the importers work against **real** provider exports. Until this session
both had only ever been run on synthetic fixtures, and the two real files the
maintainer had — a ChatGPT export and a Claude `manifest-*.json` — both failed.

## Starting state

Branch `main`, last commit `c9bd5a3` (site build fix). Nothing broken. Both
importers passing their tests, and both wrong about what a current export
actually contains.

## What was done

**Inspected the real exports by shape only.** Key names, types and counts — no
message text, titles or identifiers were read or printed. `tmp/` is git-ignored
(`.gitignore:103`) and nothing from it is committed.

**ChatGPT: the file it looked for no longer exists.** `CONVERSATIONS_FILE =
"conversations.json"` is hardcoded, and the real export does not contain that
file. OpenAI shards it — `conversations-000.json` (100),
`conversations-001.json` (100), `conversations-002.json` (4) — and declares the
mapping in `export_manifest.json` under `logical_files`. `detect()` found
nothing and returned `False`, so **204 conversations were reported as "not
recognised"**.

Resolution was added in `importers/reading.py`, not in the adapter, because it
is not provider knowledge:

- `conversation_members(path, filename)` — the manifest's `files` list when
  `sharded` is true, else `stem-NNN.json` matched by name and sorted by numeric
  index, else `[filename]` for the plain single-file form.
- `load_conversations(...)` — reads every member and concatenates, in the
  manifest's order.
- `peek_conversations` uses the same resolution, so `detect()` sees exactly what
  the import will.

**Claude: that file is not conversations at all.** The `manifest-*.json` is a
989-byte **download manifest** — three single-use `claude.ai` links and no
conversation data. It now fails with an explanation naming the file to fetch,
instead of a generic shrug. **No network access**: Mind Archive never follows
those links, which keeps the no-phone-home promise intact.

**Two latent bugs surfaced along the way.**

1. Mapping nodes in a current export carry only `['id', 'message', 'parent']` —
   **`children` is gone**. The main walk follows `current_node` upward and was
   fine; the fallback walk descends through `children` from the root and could
   no longer work at all. It is the only thing between a missing `current_node`
   and an empty import, so `_children_by_parent()` now rebuilds the child lists
   from `parent` links.
2. `ChatGPT.detect()` returned `True` for the Claude manifest. The registry
   lists ChatGPT first, so it would have answered with the worse message. Fixed
   by putting `looks_like_download_manifest` in `reading.py` — **not** in
   `claude.py`, because an adapter must never import another adapter — and
   having ChatGPT decline.

**A regression I caused and caught.** `conversation_members` initially returned
`[filename]` for *any* non-zip path, which made ChatGPT claim `notes.txt`. The
registry test for unknown files failed. It now returns `[]` for anything that is
not `.json` or `.zip`.

**Attachments were left out of scope**, deliberately. A real export carries 50+
`file-*.dat` plus `conversation_asset_file_names.json`. Backlogged with what it
would actually need.

## Decisions made

**D-042** — Exports are sharded; resolve them from the export's own manifest.
Recorded in `project-memory/DECISIONS.md` with the two latent bugs, the reason
shard resolution lives in `reading.py` rather than an adapter, and the honest
note that the Claude path is unverified against real data.

## Files changed

```
modified: apps/api/src/mind_archive/importers/reading.py
modified: apps/api/src/mind_archive/importers/chatgpt.py
modified: apps/api/src/mind_archive/importers/claude.py
modified: apps/api/tests/conftest.py
modified: apps/api/tests/test_chatgpt_importer.py
modified: apps/api/tests/test_claude_importer.py
modified: apps/web/src/components/ImportPanel.tsx
modified: docs/ARCHITECTURE.md
modified: docs/BACKLOG.md
modified: docs/DECISIONS.md
modified: project-memory/DECISIONS.md
added:    project-memory/sessions/2026-09-11-01-.../
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Real ChatGPT export | in-container, against `tmp/` | **204 conversations, 0 problems, 2866 messages** (1427 user / 1439 assistant); shards resolved `-000/-001/-002`; no conversation missing title, date or messages |
| Real Claude manifest | in-container, against `tmp/` | `Claude.detect()` **True**, `ChatGPT.detect()` **False**, advice names `conversations-000.zip` |
| Full gate | `python scripts/dev.py verify` | **passed** — 310 backend tests, 107 frontend tests, lint, format, types, build, project memory, CSS band guard |
| Formatting | `python scripts/dev.py format --fix` | 1 file reformatted; `verify` green afterwards |
| Nothing leaked | `git status --short` | no path under `tmp/` |

The first `verify` attempt failed on `Backend formatting` only; `format --fix`
then `verify` again was green. Recorded because a check that failed once is part
of the record.

## What remains

**Claude is unverified against a real export.** Only the download manifest was
available and its links are single-use. The importer is still written from
documentation and covered by synthetic fixtures only. It may shard too — the
first real Claude export should be checked against it. This is stated in the
backlog rather than glossed.

**The browser script's output is now more doubtful**, not less: it produces one
`conversations.json` while the official export shards. Both shapes are handled,
but the script's output has still never been compared against a real export.

**Attachments** are backlogged, not built.

## Exact next step

Remove `kishor3947@gmail.com` from the "Say thanks" message, and replace the
`github.com/RootedGlobal/mindarchive/blob/main/...` links with in-site links
that work on `localhost:4000` — starting with `LICENSING.md`,
`project-memory/DECISIONS.md` and `project-memory/RESEARCH.md`. Audit every page
for the same problem, and decide whether a 404 page is the right answer for
targets that are not published.
