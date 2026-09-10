# Report — 2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting

## The question, and the honest answer

*"It takes 24 hours for ChatGPT to email the export — how do we improve or
automate this?"*

**The wait cannot be automated.** The export job runs on OpenAI's
infrastructure. The Platform API's `conversation` objects hold conversations
created *through the API*; there is no endpoint for ChatGPT consumer history and
there never has been.

What research did find is that the premise was wrong in an interesting way, and
that our own code was repeating the error.

## Two clocks, and everyone confuses them

OpenAI's confirmation email, quoted verbatim by the user:

> We have started preparing your data export, this process may take a few days.

Yet "24 hours" is what everyone believes, including me when I wrote the import
panel in Milestone 2. The number is real — it is **how long the download link
lasts once the email arrives**. It is a deadline, not a wait.

Add a third fact: **only the most recent export request is fulfilled.** Asking
again because the first felt slow silently cancels it.

Put together, that is a trap with teeth. Request an export, miss the email for a
day, find a dead link, request again impatiently, cancel your own job. Our
interface said nothing about any of it and got the one number it did show
exactly backwards.

Fixing the copy is a smaller change than anything else in this session and
probably the most useful.

## Automating ingestion instead

**The inbox.** Save an export into a folder and it imports itself — on startup,
on demand, and when the interface regains focus. No upload, no browser.

The interesting decisions were about restraint:

- **No filesystem watcher.** Three scan triggers cover every case a personal
  archive has. `watchdog` would be a dependency earning nothing.
- **Two shapes, not one.** The default folder is one Mind Archive owns, and
  there it tidies: imported files to `imported/`, failures to `failed/` with a
  note. But pointing the inbox at a folder you already keep exports in must not
  move your files — a program that reorganises your Downloads folder is a
  program you uninstall. So a folder you chose is read, never rearranged, and a
  small ledger remembers what has been done.
- **A folder you chose is never created for you.** Silently making directories
  somewhere a person picked is not our business.
- Everything in the inbox is untrusted, exactly like an upload: same importers,
  same zip-safety checks, same caps, and only `.zip` and `.json` are ever
  opened.

## Re-importing is the normal case

Every ChatGPT export is a *full* export. The second one contains everything the
first did. So "Imported 412 conversations" is true, useless, and slightly
insulting the second time.

Now: **"12 new, 8 updated, 392 already in your archive."** And an unchanged
conversation is not merely reported differently — it is **not written at all**.
A file's modification time should mean "this changed", and it stops meaning that
if every import rewrites everything.

There is a test asserting the mtime does not move on a re-import.

## The fast path, and where the line is

ChatGPT's web app uses undocumented `/backend-api/` endpoints. Getting your
conversations through them takes minutes, not days.

Two shapes of the same idea, with completely different risk:

1. **Paste your session token into an application.** Several third-party tools
   ask for this. That token grants full account access — reading everything and
   sending messages as you.
2. **Run a script in your own logged-in tab.** It reuses the session the browser
   already holds. Nothing is pasted, and the token never leaves the tab.

We ship the second, as `scripts/browser/chatgpt-export.js`, clearly marked as
**not part of the application**. Mind Archive makes no request to OpenAI and
never handles a credential; it reads a file you put in a folder, like any other
export. That is D-024, and it is what lets the privacy claim stay trivially
true rather than carefully worded.

The warnings are honest rather than reassuring: the endpoints are undocumented
and may break, using them may violate OpenAI's Terms of Use, and it cannot fetch
attachments. The counter-argument — your own data, GDPR Article 20 — is
presented as the user's to weigh, not settled on their behalf.

**Rejected outright:** Mind Archive calling those endpoints itself, in any form.

## Testing without anyone's real data

The recurring problem for three milestones: the importer had never seen a real
export, and a real export cannot be shared.

`scripts/inspect_export.py` reports the **structure** of an export and none of
its content — conversation counts, which content types appear, branch depths,
null fields, unknown keys. Safe to paste into an issue.

Writing it produced a small lesson. The first version printed the archive's file
list, which seemed harmless until it wasn't: a ChatGPT export names attachments
after what they are, so `file-abc-passport-scan.png` would have leaked exactly
what the script exists to protect. It now reports extensions and counts. A tool
built to avoid leaking content leaked content on its first draft, which is worth
remembering.

`scripts/make_fixture_export.py` generates large, deliberately messy synthetic
exports — every content type including invented ones, abandoned branches,
unicode, hostile titles, nulls everywhere.

## Measuring instead of guessing

The first 2,000-conversation import took **194 seconds**, which felt bad enough
to optimise. Before doing that, the same import was run against the container's
own filesystem:

| Archive written to | Write | Index | Total |
|---|---|---|---|
| Container filesystem | 1.9s | 2.8s | **4.7s** |
| Windows bind mount | 48.2s | 79.2s | **127.4s** |

**27× slower**, same code, same data. The bottleneck is Docker Desktop's
Windows filesystem, not anything we wrote. Batching writes or pooling SQLite
connections would have won almost nothing, and the twenty minutes spent
measuring saved a day spent optimising the wrong thing. Recorded as R-005.

It did justify one change: the startup scan now runs on a **background thread**.
Inline, a large import left the server refusing connections for minutes — the
application looked broken at exactly the moment it was being most useful. Found
by trying it, not by reading it.

## Other things found by running it

- **`Settings(alias=...)` broke construction by field name** until
  `populate_by_name=True` was added — caught immediately by a settings check.
- Two pieces of an aborted edit script never landed (`Literal`, `_unchanged`),
  and the container failed to start with a bare `NameError`. Cheap to find,
  and a reminder that a partially-applied refactor is worse than none.
- The inbox status endpoint initially reported `/data/inbox` — the container's
  path — repeating the exact bug fixed in Milestone 2 for the archive folder.
  Same fix, `inbox_location`.

## What is still not done

- **No real ChatGPT export has been imported.** Three milestones running. This
  session makes that moment cheap rather than replacing it.
- No progress reporting during a long import. It no longer blocks anything, but
  the interface says nothing while it works.
- The browser script's output shape is *believed* identical to the official
  export's. Unverified until both can be compared with `inspect_export.py`.
