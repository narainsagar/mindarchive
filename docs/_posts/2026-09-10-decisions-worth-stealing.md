---
title: Decisions worth stealing
summary: Mind Archive keeps a written record of every architectural decision and why it was made. Four of them are useful well beyond this project.
author: Mind Archive
tags: [engineering, process]
---

Mind Archive keeps a decision log — every architectural decision, dated, with
the reasoning that produced it and the consequences that followed{% if site.data.private_pages %}, and it is
[published with the code]({{ '/decisions/' | relative_url }}){% endif %}. A decision nobody
wrote down is indistinguishable from an accident six months later.

Four of them generalise.

## Detect by shape, not by name

**D-027.** The ChatGPT importer originally recognised an export by its filename:
`conversations.json`. Reasonable, until you notice that Claude exports a file
with exactly the same name and a completely different structure — a flat
`chat_messages` list against a `mapping` tree, `name` against `title`, ISO 8601
against epoch floats.

The importer would have accepted a Claude export and reported it empty.

**The general lesson:** a name is a claim someone else controls. The content is
the thing you actually have. Where the two disagree, the content wins.

This bug was invisible while there was one importer. It appeared the moment there
were two — which leads directly to the next one.

## Do not build an interface against one implementation

**D-028.** A `StorageProvider` abstraction was scheduled, to sit between the
application and wherever files live, so cloud storage could slot in later.

It was deliberately not built.

An interface with one implementation is not an abstraction — it is a guess about
the second one, written down in a shape that is expensive to change. With the
cloud work a milestone away, building it early would have meant designing
against an imagined caller.

The importer interface earned its shape by meeting a real second provider and
being wrong about it first. Storage will get the same treatment when there is a
second real case.

**The general lesson:** generalise on the second concrete case, not on the first
plus imagination.

## Refuse the thing that would embarrass you

**D-032.** The obvious ask for a project like this is a live demo. Click a link,
see it work.

It is not going to happen, and the reason is written down so it does not get
quietly revisited. The API has no authentication, by design, because it is a
single-user application on your own machine. A public instance would therefore be
**one shared archive with no access control** — whatever any visitor imported,
every other visitor could read and export. Someone would upload a real export,
and their private conversations would be public.

For a product whose entire premise is that your conversations stay yours, that is
precisely the failure it exists to prevent.

A demo is still possible, but it is a piece of engineering rather than a
deployment: a read-only mode that seeds synthetic data and refuses every write.
Until that exists, the honest answer to "can I see it live" is a screenshot and
`docker compose up`.

**The general lesson:** the feature that would best market your product is
sometimes the one that would most undermine it. Write down why you said no, or
you will have the argument again in six months and lose it.

## Decide when to run the tests

**D-018.** Verification is developer-controlled during development and required
at three points: before a milestone is called complete, before a pull request,
and before a release.

Not after every change. Broken code mid-task is expected and fine.

The rule that matters is not about frequency — it is this:

> Never claim a command passed unless you actually ran it. "I have not run the
> tests" is a perfectly good thing to say. Claiming they pass when you did not is
> not.

**The general lesson:** the cost of a check is not just the time it takes; it is
the pressure to skip it, and then the temptation to say it passed. Make it
required where it matters and optional everywhere else, and the temptation never
arises.

---

None of this is unusual practice. What is slightly unusual is writing it down at
the time, in the repository, where the reasoning survives the conversation that
produced it. Six months later, the value is not the decision — you can see that
in the code. The value is knowing what you already thought about and rejected.

{% if site.data.private_pages %}The whole log is [here]({{ '/decisions/' | relative_url }}).{% else %}Four decisions, four arguments you can borrow whether or not you ever run this
particular application.{% endif %}
