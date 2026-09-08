# Report — 2026-09-08-04-milestone-3-archive-browser-and-search

## Keeping the index honest

The rule from D-004 is that SQLite indexes the archive and never owns it. That
is easy to write down and easy to erode: one convenient column that is not on
disk, and the archive stops being portable.

So it is enforced by a test rather than by intention.
`test_deleting_the_database_loses_nothing` writes conversations, indexes them,
searches, deletes `mind_archive.db`, rebuilds, and searches again. The results
must be identical. If that test ever fails, something has started living only in
SQLite.

Three ways the index gets built, all from the same code path:

1. **On startup**, if the archive has content but the index does not. This is
   what makes copying the archive folder to another machine sufficient.
2. **On import**, through the `conversation.created` event. Importing does not
   know that an index exists — which is what the event bus was for (D-009).
3. **On demand**, `POST /api/index/rebuild`, for after editing files by hand.

Schema changes drop and rebuild rather than migrate. Migration would be work
spent protecting data that is already safe somewhere else.

## What people type into a search box

FTS5's `MATCH` takes a query language. A search box takes whatever someone
types. Those are not the same thing, and the gap is where the bugs are:

| Typed | Raw FTS5 behaviour |
|---|---|
| `C++` | syntax error |
| `"` | syntax error |
| `NEAR(` | syntax error |
| `a AND b` | silently becomes a boolean query |

So input is rewritten: split into words on anything non-alphanumeric, each word
quoted, joined with `AND`, and the final word given a prefix wildcard. Operators
survive as literal text because they are inside quotes.

Deliberate consequences:

- **All words must match.** A personal archive is searched to find one
  remembered thing, not to browse.
- **The last word is a prefix**, so "sourd" finds "sourdough" and search feels
  responsive rather than empty until the final keystroke.
- **Nothing searchable means no filter, not no results.** Typing `!!!` shows the
  archive rather than an empty page.
- **No phrase search, `OR` or negation.** A deliberate trade against ever
  showing someone a syntax error. Recorded as D-022.

There is a parametrised test for eleven awkward queries, and the same ones were
tried against the running server.

Note this was never an injection risk — the query has always been a bound
parameter. Rewriting is about correctness.

## Untrusted content reaching the page

Two paths where conversation text could have become markup, both closed:

**The conversation body.** Rendered with `react-markdown`, which builds React
elements rather than setting HTML, with raw HTML not enabled. A conversation
containing `<script>alert(1)</script>` renders those characters. The
alternative — a Markdown-to-HTML library plus a sanitiser plus
`dangerouslySetInnerHTML` — is more dependencies and one mistake away from an
injection. Recorded as D-021.

**Search snippets.** The backend marks matches with `<<` and `>>`, not `<mark>`.
No markup crosses the wire; the interface splits on those delimiters and builds
elements. Approached from the opposite direction, same guarantee.

Both have tests asserting that an `<img onerror=...>` in content never becomes
an element.

**The path in the URL.** `/api/conversations/{path:path}` is a request anyone
can make, so it goes through `safe_join`. A refusal and a genuine miss both
return the same 404 and neither describes the filesystem.

## Reading conversations as whole files

The API returns `conversation.md` as Markdown, front matter stripped, and the
interface renders the file. It does not parse the file back into messages.

Round-tripping our own rendering would be fragile: a message whose text contains
`## You` would break it. And it would gain nothing, because the file *is* the
readable artefact — that is the whole point of storing Markdown.

The cost is no per-message structure in the interface: no speaker bubbles, no
per-message actions. Speaker headings render as headings, which reads correctly
for a document archive. If per-message behaviour is ever genuinely needed, the
honest fix is to store structure in `metadata.json`, not to parse prose.
Recorded as D-020.

One consequence worth having: the conversation is read from **disk**, not from
the index, so editing a file by hand shows immediately.

## A design flaw found by a failing test

`test_an_imported_conversation_becomes_searchable` failed, and the cause was
worth more than the test.

The event handler that indexes a new conversation called `get_settings()`
directly. That function is cached, so it ignored `dependency_overrides` — the
import route wrote to the test's temporary archive while the handler indexed the
real one. In production it happened to work; in a test it silently used the
wrong folder, and it would have surprised anyone reconfiguring the app.

Fixed by binding settings when the handler is built, at startup, rather than
looking them up inside it. A handler should act on the configuration its
application was started with.

The same problem existed one layer up: `lifespan` also called `get_settings()`
directly, so startup and routes could be configured differently. `_settings_for`
now consults the same override, with a comment explaining why.

## Other problems found by running it

**An unusable archive folder crashed startup.** `ensure_directories()` was
unguarded in `lifespan`, so a data directory that was a file — or an unplugged
drive — stopped the application booting. It now logs clearly and starts anyway,
so the interface can explain the problem and the user can fix the setting.

**Three test-fixture bugs of my own.** Two conversations shared message text, so
"this search matched one conversation" assertions were meaningless. And a date
assertion assumed a British format when the component correctly uses the
viewer's locale.

## What is not done

- No editing or deleting conversations from the interface.
- No tags, projects or filtering by source, though the counts are returned.
- Attachments are still placeholders, from Milestone 2.
- Pagination is Previous/Next, not virtualised. Fine for thousands of
  conversations; revisit if anyone has hundreds of thousands.
- **Still only synthetic data.** A real ChatGPT export remains the outstanding
  verification.
