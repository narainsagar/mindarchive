# Session: Milestone 4 — tags

**ID:** 2026-09-08-06-milestone-4-tags-and-organisation
**Started:** 2026-09-08
**Ended:** 2026-09-08
**Agent:** Claude Opus 5 (Claude Code, VS Code extension)

---

## Goal

Milestone 4: organising the archive. Scoped to tags — see D-026 for why the
rest of the originally specified model list was left out.

## Starting state

`main` at `09950ad`, clean. Milestone 3.5 complete. The user was still unable to
run the stack in WSL (a Docker credential-helper problem, documented but not yet
applied on their machine) and asked to proceed with milestones regardless.

## What was done

**The design decision that shaped everything.** Tags are the first thing in the
archive a person *makes* rather than imports. Storing them in SQLite would have
made a rebuildable cache load-bearing and broken D-004 in the one place it would
destroy original work. They live in each conversation's `metadata.json`; SQLite
indexes them and holds nothing else (**D-025**).

**The bug that design would otherwise have caused.** Every ChatGPT export is a
full export, so re-importing rewrites every `metadata.json` — and an export
contains no tags. Naively, importing next month's download would have erased
months of a person's filing, silently. `ArchiveWriter.write` now merges existing
tags forward, with a test named after exactly that failure.

**Backend.** `Conversation.tags`, `clean_tags` (trim, collapse, dedupe
case-insensitively keeping the first spelling, cap length and count),
`read_tags`/`write_tags` that touch only the `tags` key, a `tags` table at
schema version 2, tag filtering that combines with search rather than replacing
it, and tag counts.

**API.** `PUT /api/conversations/{path}/tags`, a `tag` filter on the listing,
and every tag in use returned with counts. The path goes through `safe_join`
like every other conversation path.

**Interface.** A `TagEditor` on each conversation — a list of labels and a text
box, no autocomplete or colour picker; tagging should take about as long as
writing the word. A filter bar of tags with counts above the list, and tags
shown on each row.

**Scope.** Projects, and the rest of the originally specified archive model,
deliberately deferred (**D-026**).

## Problems found and fixed

**A crash that blanked the interface.** `Object.entries(undefined)` throws, so a
response without `tags` took out the whole archive panel. Found because the old
test fixtures lacked the field — a fair stand-in for a cached frontend meeting a
newer backend. Now defensive.

**A type that lied.** mypy found an unreachable `isinstance` guard in
`clean_tags`: the signature claimed `list[str]` while the function genuinely
reads untrusted JSON. Signature corrected to `Sequence[object]`.

**Six SQL-injection warnings** on f-string query assembly. Checked rather than
suppressed: the tag is a bound parameter, only our own literals are
interpolated. Each suppression carries its reason and the module docstring
explains the property.

**Two escaping bugs of my own** — `\n` in a bash heredoc became a literal
newline, breaking `dev.py` and then `writer.py`. Both caught immediately.

## Decisions made

- **D-025** — tags live in `metadata.json`; an import never removes them.
- **D-026** — projects deferred; tags first.

## Files changed

```
Added:    apps/api/tests/test_tags.py
          apps/web/src/components/TagEditor.tsx (+ .test.tsx)

Modified: apps/api/src/mind_archive/models.py
          apps/api/src/mind_archive/archive/{writer,reader}.py
          apps/api/src/mind_archive/index/{schema,indexer,search}.py
          apps/api/src/mind_archive/routes/conversations.py
          apps/api/tests/test_conversations_api.py
          apps/web/src/{api.ts,styles.css}
          apps/web/src/components/{ArchivePanel,ConversationView}.tsx
          apps/web/src/components/ArchivePanel.test.tsx
          project-memory/DECISIONS.md, docs/DECISIONS.md
```

## Checks run

`python scripts/dev.py verify`

| Check | Result |
|---|---|
| Backend lint (ruff) | **passed** |
| Backend formatting | **passed**, 37 files |
| Backend types (mypy strict) | **passed**, 23 files |
| Backend tests | **254 passed** (was 217) |
| Frontend lint | **passed** |
| Frontend types | **passed** |
| Frontend tests | **64 passed** (was 54) |
| Frontend build | **passed** |
| Project memory | **passed** |

Not yet exercised end to end against the running stack — the user's environment
is the blocker, not the code. Worth doing at the next opportunity.

## What remains

- **No real ChatGPT export has been imported.** Four milestones now.
- **Tags not yet tried in a browser.** Unit and component tests pass; the
  interface has not been clicked through.
- Projects deferred (D-026).
- Unchanged: placeholder GitHub identity, no git remote, no committed
  `package-lock.json`, frontend image runs the dev server.

## Exact next step

Milestone 5 — a second importer (Claude or Gemini), which is what finally
generalises the `Importer` interface against a real second case rather than a
guess.
