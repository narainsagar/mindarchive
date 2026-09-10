---
title: The post's title, as a sentence
summary: One or two sentences. Shown on the blog index, in the RSS feed, and under the title on the post itself. Write it last.
author: Mind Archive
tags: [product]
---

<!--
  A blog post template.

  This lives in _drafts/, which Jekyll ignores unless you build with --drafts,
  so nothing here is ever published.

  To write a post:

    1. Copy this file to _posts/YYYY-MM-DD-a-short-slug.md
    2. The date in the filename is what orders the blog. The URL becomes
       /blog/a-short-slug/ — no date in it, so the post does not look stale
       next year.
    3. Front matter is not optional. Jekyll copies Markdown without it
       verbatim, and the post silently never appears. See D-033.
    4. Delete these comments.

  Tags in use so far: product, privacy, engineering, process.
  Add a new one only when none of those fit.
-->

Open with the reader's problem, not with the project. Someone who has never
heard of Mind Archive should recognise the situation in the first two
sentences.

## Use headings that say something

"How search works" beats "Implementation". A reader skimming the headings should
come away with the argument.

Keep paragraphs short. Prefer concrete nouns to abstract ones: "your archive is
a folder of Markdown files" rather than "content is persisted in a
human-readable format".

## Make claims checkable

Every technical claim should point at something a reader can verify — a file in
the repository, a decision record, a command they can run.

```bash
python scripts/dev.py up --build
```

Do not invent numbers. No download counts, no benchmarks that were not measured,
no testimonials, no screenshots of things that do not exist. A privacy-first
product that oversells is a privacy-first product nobody trusts.

## House style

- British spelling, matching the rest of the documentation.
- Write for humans: "Import your archive", not "Initialise the ingestion
  pipeline".
- The project is **source-available**, never "open source". The licence is
  PolyForm Noncommercial 1.0.0 and the distinction is deliberate.
- Link related posts and docs with `relative_url`, so they work at
  `/mindarchive/` as well as at a custom domain:
  `[the decision log]({{ '/DECISIONS.html' | relative_url }})`

## Close with somewhere to go

A link to the docs, the source, or another post. Not a call to action —
just the next useful thing.
