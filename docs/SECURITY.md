---
title: Security and Privacy
permalink: /security/
---

# Security and Privacy

Mind Archive exists to keep personal material private. Security is a product
requirement here, not a checklist.

## The privacy model in one paragraph

Your archive lives on your computer. Mind Archive has no account system, no
hosted service, and no telemetry. It makes no outbound network request as part
of its normal operation. Nothing is uploaded anywhere unless you explicitly
configure cloud storage, which is off by default and cannot be enabled
silently.

## What we guarantee

**No silent uploads.** `MIND_ARCHIVE_CLOUD_ENABLED` defaults to `false`. No
cloud adapter exists yet, and when one does it will require explicit
configuration. The API reports cloud status so the interface can tell you
plainly where your data is.

**No telemetry.** No analytics, no crash reporting, no usage statistics.

**No secret ever reaches the browser.** The frontend receives only non-sensitive
configuration. API keys, when future features need them, stay server-side.

**Your content stays readable and yours.** Markdown and JSON on your filesystem.
No proprietary format, no encryption you cannot undo, no lock-in.

**Conversation content is not logged.** Application logs record what happened —
"imported 412 conversations" — never what was said.

## Imported files are untrusted input

This is the most important attack surface in the project. A provider export is
a file from outside, and from Milestone 2 onward we parse them.

Every importer must:

- **Validate structure before trusting it.** Never assume a field exists, has
  the expected type, or is the expected size.
- **Guard against path traversal.** Filenames inside an archive are attacker
  controlled. Resolve every path and confirm it is inside the archive root
  before writing. This is centralised in `mind_archive/paths.py` — use it.
- **Guard against zip-slip and zip bombs.** Check entry names and uncompressed
  sizes before extracting.
- **Cap resource use.** Bound file sizes, entry counts and nesting depth.
- **Fail clearly.** A malformed archive produces a plain-language error, not a
  stack trace and not a partial, corrupted import.

Treat every imported archive as if it were written by someone hostile, because
you cannot prove it was not.

## Secrets

Never commit API keys, passwords, tokens, private keys, credentials or personal
archives.

`.env` is git-ignored; `.env.example` holds placeholders only and is the file
that gets committed. If a secret is ever committed, rotate it — removing it from
history is not enough.

`.gitignore` also excludes `data/`, `*.db`, `*.sqlite` and `*.zip` so that your
archive and any provider export you are working with cannot be committed by
accident.

## Network exposure

By default the API binds to localhost. Do not expose it to a network you do not
control: there is no authentication, because it is a single-user local
application.

CORS is restricted to the local frontend origin and is configurable through
`MIND_ARCHIVE_CORS_ORIGINS`. Widen it only if you understand the consequence.

If you ever want to reach Mind Archive from another machine, put it behind a
reverse proxy with authentication that you control. That is out of scope for
the project itself until Milestone 7.

## Dependencies

Dependencies are kept deliberately few, which is itself a security measure. Each
one must be justifiable in a sentence. CI runs on every push and pull request.

## For contributors

Before opening a pull request:

- Run `git diff --cached` and read it. Confirm no secret, no `.env`, no personal
  archive and no database file is included.
- If you touched anything that handles a path or an imported file, say so in the
  pull request description.
- If you added a dependency, explain why.

## Reporting a vulnerability

Please do not open a public issue for a security vulnerability.

Use GitHub's private vulnerability reporting on the repository
(**Security → Report a vulnerability**), or contact the maintainers directly.

Include what you found, how to reproduce it, and what an attacker could achieve.
We will confirm receipt, agree a disclosure timeline with you, and credit you
unless you would rather we did not.
