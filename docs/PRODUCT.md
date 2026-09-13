---
title: Product
permalink: /product/
---

# Product

**Mind Archive — Your Personal AI Mind Archive.**
*Own your AI memory. Simple, private, and yours.*

## The problem

People are accumulating a large and growing amount of genuinely valuable
thinking inside AI chat products: research, decisions, drafts, explanations,
plans, code, personal reflection.

That material has three problems.

1. **It lives on someone else's server.** You can usually export it, but you
   cannot really *use* it where it is.
2. **It is trapped per provider.** Move from ChatGPT to Claude and you leave
   your history behind.
3. **It is not readable on its own terms.** A provider export is a large JSON
   file, not something a person can browse, search or keep.

## What Mind Archive does

Mind Archive gives you a personal archive of your AI conversations and related
knowledge that lives on your own computer, in formats you can read, and that
survives any change of provider.

It lets you:

- **Import** exports from AI providers, starting with ChatGPT
- **Preserve** them as human-readable Markdown and JSON on your filesystem
- **Organise** them with projects, tags and metadata
- **Search** across everything
- **Export** the whole archive at any time
- **Optionally synchronise** to storage you choose — never by default

## Who it is for

People who use AI assistants seriously and want to keep what comes out of them:
researchers, writers, engineers, students, consultants, and anyone who has ever
thought "I know I worked this out with an AI six months ago."

The first version targets desktop and laptop use. Mobile is not a Milestone 1
target, though the interface is built responsively where practical.

## Principles

**Local first.** The application works fully with no network, no account and no
third-party service. This is not a degraded offline mode; it is the normal mode.

**Privacy first.** Nothing leaves your machine unless you explicitly configure
it. Cloud features are off by default and cannot be enabled silently.

**You own your data.** Your content is stored as ordinary files you can read,
grep, back up and move. The database indexes your archive; it never owns it.
If Mind Archive disappeared tomorrow, your archive would still be readable.

**AI-provider agnostic.** No provider sits at the architectural centre. ChatGPT
is the first importer target and nothing more.

**Human readable.** The interface, the documentation and the stored data are
written for people. "Import archive", not "Initialize ingestion pipeline".

**Simple.** A single primary workspace with minimal navigation. No dashboards,
no permanent sidebars, no unnecessary animation. It should feel like a calm,
modern document archive.

**Proprietary, and honest about it.** Mind Archive is **All Rights Reserved**:
not open source, not source-available, no licence granted. What that does not
change is the promise underneath — your archive is ordinary readable files on
your own disk, exportable at any time, whatever happens to the software. See
[LICENSING.md]({{ '/licensing/' | relative_url }}).

## What Mind Archive is not

- Not a chat interface. It archives conversations; it does not host them.
- Not a cloud service. There is no hosted product and no account.
- Not an AI provider client. It does not need an API key to do its core job.
- Not a note-taking app competitor. It is an archive first.

## Interface direction

Two appearance choices sit in the header, and both are remembered. A palette —
Light minimal (the default), Warm paper, or Ink & violet — and a theme: Light,
Dark, or System, which follows the computer. All six combinations must look
good. See DECISIONS.md D-029.

Each is a menu button rather than a row of options, which is what lets the
header be a single row: brand, navigation, then actions and appearance. Below
1024px the navigation folds into a menu; the appearance buttons never do, and
lose only their text label. **Nothing on either surface scrolls sideways** —
wide content scrolls inside its own container instead. See D-037.

The interface should read as something a thoughtful person designed: calm,
clean, obvious, lightweight, professional. It should specifically *not* look
AI-generated — no gradient-heavy card grids, no decorative dashboards, no
jargon.

Settings must be simple, and only settings that genuinely work may exist. No
placeholder toggles.

## Milestones

Milestone 1 delivers a runnable foundation. Milestone 2 delivers the ChatGPT
importer — the first point at which Mind Archive becomes useful. Later
milestones add browsing and search, organisation, more importers, and finally
optional cloud synchronisation.

The full plan is in [ROADMAP.md]({{ '/roadmap/' | relative_url }}){% if site.data.private_pages %}, with the
authoritative scope in [MILESTONES.md]({{ '/milestones/' | relative_url }}){% endif %}.
