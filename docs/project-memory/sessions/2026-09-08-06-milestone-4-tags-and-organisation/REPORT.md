# Report — 2026-09-08-06-milestone-4-tags-and-organisation

## One question decided the whole design

Everything in the archive so far is **derived**. Conversations come from an
export, the Markdown is rendered from them, and the SQLite index is rebuilt from
the Markdown. Losing any of it costs time, not information — which is what makes
"delete `mind_archive.db` and everything comes back" a safe promise rather than
a brave one.

Tags are the first thing that breaks that pattern. **You make them.** They exist
nowhere else in the world, and no amount of re-reading an export will reproduce
them.

So the obvious implementation — a `tags` table in SQLite — would have quietly
made the database load-bearing. Deleting a rebuildable cache would have
destroyed original work, and D-004 would have become a slogan rather than a
property.

Tags live in each conversation's `metadata.json` instead. SQLite indexes them
for filtering and counting and holds nothing that is not on disk. There is a
test that deletes the database, rebuilds, and requires the tags to come back
(D-025).

## The bug this design would have caused, if unnoticed

Every ChatGPT export is a **full** export. Importing next month's download
rewrites `metadata.json` for every conversation you already have — and an export
contains no tags.

Done naively, importing would have set `"tags": []` on everything, silently
erasing months of a person's own filing. Nobody would notice at the time. They
would notice much later, with no idea what happened or when.

So `ArchiveWriter.write` reads the existing metadata and **merges tags forward**
before writing. `test_importing_again_does_not_erase_tags` exists specifically
for this, and is the most valuable test added this session.

The same care applies in the other direction: writing tags rewrites only the
`tags` key, so relabelling a conversation cannot disturb anything derived from
the export.

## What tidying tags actually requires

People type `"Bread"`, `" bread "` and `"BREAD"` and mean one label. Storing
those as three tags would split someone's own filing without them noticing, so
`clean_tags` deduplicates case-insensitively and keeps the first spelling — the
one they chose. It also trims, collapses internal whitespace, drops empties, and
caps both tag length and count.

Filtering matches case-insensitively for the same reason: filtering for
`recipes` should find what you tagged `Recipes`.

## What was left out, and why

Milestone 4 was originally specified as "Project, Conversation, Message,
Document, Memory, Tag, Attachment, Source, Metadata, Event". Only tags were
built (D-026).

Tags plus the existing full-text search already answer the question people
actually have — *"where is that conversation about X?"*. Projects add a second,
hierarchical way to organise the same things, and building both at once means
guessing how they interact before anyone has used either. A `Memory` or
`Document` type with no feature behind it is a schema nobody has tested against
a real need.

If projects are still wanted after living with tags, they are likely a reserved
tag namespace rather than a parallel hierarchy. Recorded in the backlog.

## Problems found by the tooling

**A crash that would have blanked the interface.** `Object.entries(undefined)`
throws, so a response without a `tags` field took out the whole archive panel
rather than merely hiding the filter bar. Only found because the existing test
fixtures did not have the new field — which is a reasonable stand-in for a
cached frontend meeting an older backend. Now defensive.

**A type that lied.** mypy reported an unreachable branch in `clean_tags`: the
signature said `list[str]`, so the `isinstance(tag, str)` guard could never
fire. The guard is right — tags come from JSON on someone's disk — so the
signature was wrong. It takes `Sequence[object]` now, which says what is
actually accepted rather than what we hope for.

**Six SQL-injection warnings**, all on f-string query assembly. Worth taking
seriously rather than suppressing blindly: the tag is a bound `?` parameter and
the only interpolated values are our own literals and a run of `?` characters.
Nothing from a request reaches the SQL text. Each suppression carries its reason
and the module docstring explains the property in full, so the next person can
re-check it rather than trust it.

**Two self-inflicted escaping bugs.** `\n` inside a bash heredoc passed to
Python became a literal newline twice, once breaking `dev.py` and once breaking
`writer.py` with an unterminated string. Both caught immediately. The lesson is
already learned twice: use the editing tool for anything containing escapes.

## Still true

No real ChatGPT export has been imported. Four milestones now.
