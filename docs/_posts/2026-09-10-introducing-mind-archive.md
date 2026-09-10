---
title: Introducing Mind Archive
summary: Your AI conversations are some of the most useful writing you have done. They are also locked inside products you do not control. Mind Archive gets them back.
author: Mind Archive
tags: [product]
---

You have had hundreds of conversations with an AI. Somewhere in them is the
explanation that finally made a thing click, the plan you talked yourself into,
the shape of a problem you had been circling for weeks.

Now try to find one from March.

## The problem is not search. It is ownership.

Your conversations live inside a product you do not control. If you switch
providers, they do not come with you. If the service changes its retention
policy, that is not your decision. If it shuts down, that is that.

Every provider will hand you an export — a `.zip` or a `.json` that is technically
your data and practically unreadable. It sits in your downloads folder, and the
part of your thinking that lives in it stays out of reach.

**Mind Archive turns that export into something you can actually use, on your own
computer.**

## What it does

Three things, done properly.

**Import.** Drop an export into a folder and it imports itself. ChatGPT and
Claude are supported today, as `.zip` or raw `.json`. Each provider sits behind
its own adapter, so support for one never destabilises another.

**Search.** Full-text search across everything, with the matching line shown in
place so you can tell which result is the one you want without opening it. Tag
what matters.

**Keep.** This is the part that makes the rest worth doing. Your archive is
Markdown and JSON in an ordinary folder. Every conversation becomes one file,
dated and titled:

```
data/archive/2026/chatgpt/2026-03-11-postgres-index-strategy.md
```

Open it in any editor. Grep it. Sync it. Put it in git. Delete Mind Archive
tomorrow and every one of those files still opens, because they were never in a
format that needed us.

## It runs on your machine

No account. No sync. No telemetry. The interface runs at `localhost:5173` and
the API at `localhost:8000`, and neither is reachable from outside your
computer.

Optional cloud backup exists, is off by default, and cannot be switched on
without you doing it deliberately.

This is not a promise we are asking you to take on faith. It is a property of
how the thing is built, and you can read the code to check.

## Try it

```bash
git clone https://github.com/RootedGlobal/mindarchive.git
cd mindarchive
cp .env.example .env
python scripts/dev.py up --build
```

Then open <http://localhost:5173>. Getting your export out of ChatGPT is the
slow part — it can take a few days, and the download link expires 24 hours after
the email arrives, so ask once and wait.

## Free, and staying free

Mind Archive is free for personal use, and for schools, charities, public
research bodies and government — under the
[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/)
licence. No feature limits, no accounts, no nagging.

Company use needs a commercial licence, which is a short email rather than a
sales process.

The code is **source-available**: readable and inspectable, but not open source,
and we are not going to describe it as open source because that word means
something specific.

A privacy product you cannot read the source of is a promise. One you can read
is a fact. Start with
[what "local-first" actually means]({{ '/blog/what-local-first-actually-means/' | relative_url }}).
