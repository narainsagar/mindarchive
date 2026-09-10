# Report — 2026-09-08-03-milestone-2-chatgpt-importer

## Reading a ChatGPT export: what the format actually requires

Notes for anyone writing the next importer, and for whoever revisits this one.

### `mapping` is a tree, not a list

The single thing that makes this format harder than it looks. A conversation's
messages are stored as a node graph:

```json
"mapping": {
  "root":   {"message": null,  "parent": null,   "children": ["node-0"]},
  "node-0": {"message": {...}, "parent": "root", "children": ["node-1", "node-7"]}
}
```

Branches exist because **editing a message or regenerating a reply does not
replace anything** — it forks. A conversation you edited three times has four
branches, and only one of them is what you would see if you opened it today.

`current_node` points at the leaf of that branch. Walking up through `parent`
and reversing gives the conversation as the person last saw it.

Naively iterating `mapping.values()` produces a conversation that never
happened: superseded drafts interleaved with their replacements.

**Decision: abandoned branches are not imported.** They are drafts the person
moved on from, and including them makes the archive harder to read rather than
more complete. Worth revisiting only if someone actually wants them.

### Fallbacks matter

`current_node` can be missing or point at a node that is not in `mapping`. The
parser falls back to following first children from the root, and then to file
order. Something readable always comes out.

A cycle (`parent` pointing at a descendant) must not loop forever — there is a
`seen` set and a node cap. Tested.

### Content types

`content_type` varies and new ones appear over time:

| Type | Where the text is |
|---|---|
| `text` | `parts`, a list of strings |
| `multimodal_text` | `parts`, mixing strings and asset dicts |
| `code`, `execution_output`, `system_error` | `text` |
| `tether_browsing_display` | `result`, falling back to `text` |
| `tether_quote` | `title` + `text`, rendered as a blockquote |

Anything unrecognised falls back to `parts`, then `text`. A content type
invented after this was written degrades to "imported, possibly plainly" rather
than "silently lost". Tested with a made-up type.

### Messages that should not appear

- ChatGPT's own system prompt — skipped.
- **A user-written system message is kept**: those are custom instructions, the
  person's own words, and they belong in the archive.
- `metadata.is_visually_hidden_from_conversation` — skipped.
- Empty or whitespace-only text — skipped.

### Everything is optional

Real exports contain null titles, missing `create_time`, timestamps that do not
convert, `parts` containing `null` or numbers, and conversations whose
`mapping` is not a dict.

Two rules that fell out of this:

1. **A missing timestamp stays missing.** An archive people will read in ten
   years is better with a gap than with an invented date.
2. **One bad conversation never fails the import.** It is skipped, counted, and
   described by shape — "Conversation 12 could not be read (KeyError)" — never
   by content.

## Security

An export is a file from outside the application, so it is treated as hostile.

**Zip slip.** Entry names are checked for `..`, absolute paths, null bytes and
Windows drive letters. Nothing is ever extracted to a path derived from an entry
name — named members are read into memory and nothing else. One hostile entry
poisons the whole archive: it is refused entirely.

**Zip bombs.** Declared sizes are checked before reading, reads are capped, and
a member expanding more than 200× is refused. Ordinary JSON compresses 10–20×,
so this does not catch real exports — tested both ways.

**Bounds.** 50,000 entries, 500 MB per member, 2 GB uncompressed, 1 GB upload.

**Titles become folder names.** A conversation titled `../../escaped` must not
write outside the archive. Every segment goes through `paths.py`. Tested with
traversal, nesting, Windows reserved names, empty and whitespace titles.

**Logging.** Size and counts, never content. There is an explicit test that a
message containing a fake password does not appear in the event payload.

## A design flaw worth remembering

`Importer.detect()` deliberately never raises, so an unsafe archive matched no
importer and the user was told the file was **"not recognised"** — untrue, and
a dead end. It was recognised and refused.

Fixed with `safety_problem()`, which the route consults when nothing matches.
Caught by a test that was written expecting the right behaviour rather than the
implemented one.

## What is not done

- Attachments and images: recorded as `_[image — not imported yet]_`
  placeholders. The message is preserved; the file is not.
- `chat.html`, `user.json`, `message_feedback.json`: ignored.
- **Only synthetic exports so far.** A real export is the outstanding
  verification, and the reason `local/` exists.
