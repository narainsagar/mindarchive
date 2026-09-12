---
title: Contribute
permalink: /contribute/
description: What is genuinely useful right now, and why outside code cannot be accepted yet.
---

# Contribute

The most valuable contributions to Mind Archive are not code.

## Outside code is not being accepted yet

Mind Archive is **proprietary software, all rights reserved** — not open source,
not source-available, and no licence is granted to use or modify it.

Accepting outside code would need a licensing arrangement that does not exist
yet, so pull requests from outside the project cannot be merged. Opening one
risks wasting your time, which we would rather avoid.

This is stated plainly rather than left for you to discover after doing the
work.

## What is genuinely useful right now

**Tell us about an export that will not import.** Every provider changes its
format eventually, and one real broken export is worth more than any amount of
guessing. Say which service, when you exported, and what happened.

**Never send the file itself.** It is a copy of your private conversations. A
description of the shape — the top-level keys, roughly how many conversations —
is what is actually needed.

**Say what confused you.** Wording that made you hesitate is a bug. So is a
documentation page that assumed something you did not know.

**Test it somewhere we cannot.** Other operating systems, other shells, other
Docker setups, unusual filesystems. "It worked" is useful; "it worked except
this" is more useful.

**Ask a question.** A question that reveals unclear documentation improves the
documentation.

## When the CLA exists

The work that will be most welcome:

**A new importer.** Every provider sits behind its own adapter, and the core
imports none of them — so a new one is genuinely self-contained. Detection is by
the *shape* of a file rather than its name, because ChatGPT and Claude both
export something called `conversations.json`. See
[the architecture]({{ '/architecture/' | relative_url }}).

**Test fixtures must be synthetic.** Test files are committed, and a real export
is a copy of someone's private conversations. Hand-write a small sample that
exercises the format's shape, and keep any real export you are working against
in `tmp/`, which is git-ignored.

**Documentation corrections**, at any time.

## The principles a change has to respect

- Local first. It works with no network and no account.
- Nothing leaves the machine unless explicitly configured.
- User content stays human-readable on disk. SQLite indexes the archive; it
  never owns it.
- No provider sits at the centre.
- No dependency that cannot be justified in one sentence.

## Writing a blog post

The [blog]({{ '/blog/' | relative_url }}) is part of this site, in
`docs/_posts/`. `docs/_drafts/TEMPLATE.md` carries the house style.

Draft a post however you like — including with an AI assistant. **Nothing is
published without a person approving it.** No automation posts here. If an
assistant drafted it, you are still the author, and the accuracy of every claim
in it is yours.

A post is not expected with every change. Write one when something is worth
explaining to someone outside the project.

## The full guide

Everything above is the summary for a site visitor. The canonical document is
[CONTRIBUTING.md]({{ '/contributing/' | relative_url }}),
alongside
[AGENTS.md]({{ '/agents/' | relative_url }}) —
which applies whether you are a human or an AI coding agent.

Security issues should not go in a public issue. See
[the security notes]({{ '/security/' | relative_url }}).
