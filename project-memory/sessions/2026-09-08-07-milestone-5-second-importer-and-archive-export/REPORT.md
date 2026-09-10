# Report — 2026-09-08-07-milestone-5-second-importer-and-archive-export

## The bug only a second provider could find

The `Importer` interface has existed since Milestone 2 with a single
implementation, and its `detect()` looked like this:

```python
if path.suffix.lower() == ".zip":
    with inspect(path) as archive:
        return find_member(archive, CONVERSATIONS_FILE) is not None
```

That is: *"is there a file called `conversations.json` in this zip?"*

**Claude's export is also a zip containing a file called
`conversations.json`.** So the ChatGPT importer would have accepted a Claude
export, found no `mapping` in any conversation, and told the user their export
contained nothing readable — which is both wrong and impossible to debug from
the outside.

No amount of testing the ChatGPT importer could have found this. It needed a
second real provider to exist. That is the entire argument for generalising an
interface against a genuine second case rather than a guessed one, and it is
the reason D-002 said adapters from the start but D-027 only got written now.

Detection now inspects the *shape*: `mapping` is ChatGPT's, `chat_messages` is
Claude's, and each rules out the other's key.

## Two formats that share almost nothing

| | ChatGPT | Claude |
|---|---|---|
| Messages | a `mapping` tree plus `current_node` | a flat `chat_messages` list |
| Title | `title` | `name` |
| Identifier | `conversation_id` | `uuid` |
| Timestamps | Unix epoch floats | ISO 8601 strings |
| Speaker | `author.role`, `"user"` | `sender`, `"human"` |
| Text | `content.parts[]` | `text`, plus `content[]` blocks |

Claude's flat list is a considerable mercy after ChatGPT's branching tree: the
export is already in the order the conversation happened, with no abandoned
edits to walk past.

What the two *do* share — pulling a JSON member out of a zip, coercing untrusted
values, refusing to raise on one bad field — moved into
`importers/reading.py`. That extraction happened now, with two real callers,
rather than in Milestone 2 when there was one and a hypothesis.

## A regression the tests caught immediately

Making detection strict broke two existing tests, and they were right to break.

An **empty** export (`[]`) and a **corrupt** one now matched no importer, so
instead of *"that export contains no conversations"* or *"not valid JSON on
line 4"*, the user got *"that file was not recognised"* — a vague complaint
about a file that is very nearly right.

Fixed by making ChatGPT the fallback when the shape says nothing, and by adding
`has_member` so an importer can tell *"not our kind of file"* apart from *"our
kind of file, and broken"*. The second deserves a real explanation.

The mis-claiming bug stays fixed, because a real Claude export has
`chat_messages` and ChatGPT explicitly declines it.

## Getting everything back out

`GET /api/export` zips the archive folder. The important property is what it is
*not*: not a bundle in a format of ours, not a database dump, not anything
needing Mind Archive to open. It is the folder from disk — same Markdown, same
JSON, same layout — plus a `README.txt` for whoever opens it in five years
without us.

There is a test asserting no `.db` file is in there. The index is derived and
belongs to the application; the conversations belong to the user.

Built to a temporary file rather than streamed. A personal archive is megabytes,
the code is far simpler, and a stream that fails halfway would hand somebody a
corrupt archive of their own conversations.

## What was deliberately not built

Milestone 5 specified a `StorageProvider` interface with `LocalStorageProvider`
as its only implementation. It was not built (D-028).

The reasoning is this milestone's own lesson. An interface with one
implementation is a guess about the second, and the `Importer` interface only
revealed its real defect when a genuine second case arrived. Writing
`StorageProvider` now — with cloud storage still a milestone away — would repeat
exactly the mistake this milestone corrected.

It would also be inconsistent: projects were deferred in Milestone 4 for the
same reason (D-026), and *"do not build speculative structure"* cannot be a rule
that applies only when it is convenient.

## Documentation drift, found by a failed edit

Adding D-027 and D-028 to the summary table in `docs/DECISIONS.md` failed
because **D-025 and D-026 were never added either** — Milestone 4 updated the
decision log but not its index.

Small, and exactly the kind of thing the project's own rules forbid. Both are in
now. Worth noting that it was caught by an edit failing rather than by anyone
checking, which suggests the index is due to be generated from the log rather
than maintained beside it.

## Still true

**No real export from either provider has been imported.** The Claude importer
was written from Anthropic's documented format and third-party parsers, and
carries the same honest caveat the ChatGPT one did:
`scripts/inspect_export.py` reports the structure of a real export safely, and
both importers should be checked against one.
