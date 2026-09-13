---
title: Coming next
permalink: /coming-next/
description: What works today, what is being built next, and what has been deliberately deferred.
---

# Coming next

What works today, what is being worked on, and what has been deliberately put
off. Nothing here is a promise of a date.

## What works today

- **Import** from ChatGPT and Claude, as `.zip` or raw `.json`. Drop a file in
  the inbox folder and it imports itself.
- **Search** across everything, with the matching line shown in place.
- **Tags**, to narrow a search.
- **Read** any conversation as rendered Markdown.
- **Export** the whole archive as a zip of ordinary files.
- **Three palettes** and a Light / Dark / System theme.

## Being built next

**More importers.** Gemini, Cursor, Copilot, Perplexity, local runners. Each is
one adapter and one test — the constraint is not the code, it is getting a real
export of each format to write the adapter against. If you have one, please
[say so]({{ '/contribute/' | relative_url }}).

**Import several exports at once, in the background.** Choose multiple files and
start them together, with the work surviving the dialog being closed, and
progress reported outside it.

**Progress during a long import.** A large archive on a slow filesystem takes
minutes. The import already runs on a background thread so nothing blocks; what
is missing is a way to ask how it is going.

**Projects**, to group conversations more coarsely than tags do.

**Optional backup to storage you choose.** Off by default, and it will never be
enabled silently.

## Deliberately deferred

**A public demo.** The obvious ask, and the answer is no for now. The API has no
authentication, by design, because it is a single-user application on your own
machine. A public instance would be one shared archive with no access control:
whatever any visitor imported, every other visitor could read and export. For a
product whose premise is that your conversations stay yours, that is precisely
the failure it exists to prevent.

A demo needs a read-only mode that seeds synthetic data and refuses every write,
authentication at a reverse proxy, and TLS. That is a piece of engineering, not
a deployment step. Until it exists, the honest answer to "can I see it live" is
`docker compose up`.

**A storage abstraction.** An interface with one implementation is not an
abstraction — it is a guess about the second one, written down in a shape that
is expensive to change. It waits for a real second case.

**A mobile interface.** Desktop and laptop first. The interface is built
responsively where practical, but small screens are not a current target.

## Where the detail lives

- [Roadmap]({{ '/roadmap/' | relative_url }}) — the milestone plan
- [Architecture]({{ '/architecture/' | relative_url }}) — how it is put
  together, and why
{% if site.data.private_pages %}- [Backlog]({{ '/backlog/' | relative_url }}) — ideas and known gaps, including
  what was rejected and why
- [Decisions]({{ '/decisions/' | relative_url }}) — every architectural
  decision, with its reasoning
{% endif %}

If one of these matters to you, saying so is the clearest signal about what to
build next.
