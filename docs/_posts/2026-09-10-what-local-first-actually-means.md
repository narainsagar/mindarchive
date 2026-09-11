---
title: What "local-first" actually means
summary: Plenty of products say "your data stays private". Here is what that phrase is worth only when you can check it — and how to check ours in about five minutes.
author: Mind Archive
tags: [privacy]
---

"Local-first" and "privacy-first" appear on a lot of landing pages. They are
easy to write and hard to verify, which is a bad combination.

So here is what they mean in Mind Archive, stated as things you can go and
check rather than things you are asked to believe.

## There is no account

There is no sign-up, no login, no identity, no password reset. There is no
server holding a row about you, because there is no server.

Not "we don't sell your data". There is no mechanism by which anyone else has
it.

## The API is bound to localhost

The backend listens on `127.0.0.1:8000`. It is not reachable from your network,
let alone the internet.

It also has **no authentication**, and that is deliberate: it is a single-user
application running on your own machine, where the operating system has already
decided who you are. Adding a login to a program that only you can reach would
be theatre.

The consequence is written into
[the security notes]({{ '/security/' | relative_url }}): do not expose it to
a network you do not control. We hold ourselves to that too — there is no public
demo of Mind Archive, because a public instance would be one shared archive that
any visitor could read and download. For a product built on your conversations
staying yours, that is the one thing we will not ship.

## Your archive is files, in a folder you chose

```
data/
├── archive/
│   ├── 2026/
│   │   ├── chatgpt/
│   │   │   └── 2026-03-11-postgres-index-strategy.md
│   │   └── claude/
│   │       └── 2026-04-02-mindarchive-naming.md
│   └── index.sqlite
└── inbox/
```

Markdown and JSON. Not a proprietary container, not a database you would have to
escape from. `cat` one. Open it in any editor. Put the folder in git, or on a
drive in a drawer.

**The SQLite file is only an index.** It holds metadata so search is fast. Delete
it and it rebuilds from the files. The files are the truth; the database is a
convenience, and it is designed so that losing it costs you nothing.

That is the test of whether a local-first claim is real: **what happens when you
delete the application?** Here, you keep everything, in a format that predates
us and will outlast us.

## Cloud is off, and cannot switch itself on

Optional backup to storage you choose exists as a future feature. It is off by
default, and enabling it takes a deliberate configuration change. It will never
be turned on by an update, and it will never be turned on quietly.

## Nothing is uploaded during an import

When you import a multi-gigabyte export, it can take a few minutes. Nothing is
being sent anywhere during that time — it is your machine reading your files.
The interface says so while it works, because "this is taking a while" is
exactly the moment people wonder.

## How to check all of this in five minutes

You do not have to take any of it on trust.

1. **Watch the network.** Run the app, import something, search it. Open your
   browser's network tab, or point `tcpdump` at it. Nothing leaves.
2. **Read the config.** [`.env.example`]({{ '/env-example/' | relative_url }})
   documents every setting and its default, in one file.
3. **Read the security notes.** [The threat model]({{ '/security/' | relative_url }})
   states the threat model plainly, including what Mind Archive does *not*
   protect you from.
4. **Delete the index.** Remove `index.sqlite`, restart, watch it rebuild. Your
   conversations were never in it.

A privacy claim you cannot verify is marketing. One you can is a property of the
software. We would rather ship the second kind.
