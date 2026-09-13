# Session: Make the generated public tree internally publishable

**ID:** 2026-09-12-07-make-the-public-tree-internally-publishable
**Started:** 2026-09-12
**Ended:** 2026-09-12
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Close the 38 broken links in the generated public tree without publishing any of
the eight private route families, and without making the public repository
depend on private files.

## Starting state

Branch `main` at `ae57849`, with the previous session's publisher uncommitted in
the tree. A generated public tree contained a site that 404d in 38 places.

## The idea both halves share

**A private file whose absence changes the build — never a publication step that
edits files on their way out.** Editing during publication was rejected in D-048
and stayed rejected: the published output would differ from anything reviewable
here, and a publication step that rewrites code is one nobody can check.

**The page list is split.** `sync_site_pages.py` holds the five public entries
and loads the rest from `project-memory/site_pages.json` if that file exists.
Private repository: 11 pages. Published tree: 5. The script itself is now
publishable — it names no private document — and there is one implementation
rather than two that drift.

**The links are conditional.** Anything pointing at a private-only route is
wrapped in an `if site.data.private_pages` block, and the data file behind it is
not published. The private site keeps every link; the public site renders the
same documents without them. Where a sentence would read oddly with a clause
removed, an `else` branch carries public wording instead.

## What that required

**`check_site_links.py` had to learn the same condition.** It reads source rather
than built output, so it was reporting links that the build it was checking would
never render. A checker that cries wolf is one people stop reading.

**Two tools now stand aside where their inputs are absent.** `dev.py verify`
skips the project-memory step when `session.py` is not present, and the CI
`project-memory` job does the same. Conditional rather than deleted, so the gate
keeps checking them where they mean something.

**`CONTRIBUTING.md` could not use the trick.** It is a root canonical document,
and `escape_liquid()` deliberately wraps author Liquid in `raw` so a document
about Liquid renders its examples — which means a conditional there would print
as text. Its two links to `AGENTS.md` and the decision log became prose instead,
and the guidance survived: *"record it as a numbered decision — what was chosen,
why, and what it costs."*

**Prose was rewritten, not just links.** Four published documents described a
`project-memory/` directory a public reader will never find: a layout diagram,
the Pages explanation, two research citations in `TRY_IT.md`. Fixed, because the
test is whether the documentation reads naturally to someone who has never seen
this repository.

## A defect found on the way

**Page generation was broken, and had been since `e0c6c34`.** The licence
rewrite gave `LICENSING.md` a link to `docs/_data/support.yml`, which has no
page, so `sync_site_pages.py` exited 1. It went unnoticed because
`check_site_links.py` was reading the *stale* generated output from the previous
run. `dev.py verify` runs the generator before the link checker and would have
caught it — it was not run after that edit, because containers were out of scope
that session. The link now points at the support page.

## Decisions made

**D-048 updated, not duplicated.** The new section — "One `docs/`, two builds" —
records the split page list, the conditional links, the checker's matching
condition, the two tools that stand aside, and the measured result. The withheld
table changed: `sync_site_pages.py` is now published; `site_pages.json` and
`private_pages.yml` are withheld in its place.

## Files changed

```
added:    project-memory/site_pages.json          (the private half of the page list)
added:    docs/_data/private_pages.yml            (the signal; never published)
modified: scripts/sync_site_pages.py              (split page list)
modified: scripts/check_site_links.py             (honours the same condition)
modified: scripts/publish_public.py               (allowlist; _data no longer recursive)
modified: scripts/dev.py                          (project-memory step is conditional)
modified: .github/workflows/ci.yml                (same, in CI)
modified: CONTRIBUTING.md                         (prose instead of private links)
modified: LICENSING.md                            (the link that broke generation)
modified: docs/404.html · blog.html · documentation.html · index.html
modified: docs/_layouts/default.html
modified: docs/ARCHITECTURE.md · DEPLOYMENT.md · DEVELOPMENT.md · GITHUB_PAGES.md
modified: docs/PRODUCT.md · ROADMAP.md · TRY_IT.md · coming-next.md · contribute.md
modified: docs/_posts/2026-09-10-decisions-worth-stealing.md
modified: project-memory/DECISIONS.md             (D-048 updated)
modified: project-memory/PROJECT_STATE.md
added:    project-memory/sessions/2026-09-12-07-.../
```

## Checks run

| Check | Result |
|---|---|
| `publish_public.py --check` | **Passes** — 135 files, no secret, no denied path |
| Public tree: `sync_site_pages.py` | **5 pages** |
| Public tree: `check_site_links.py` | **0 broken links — 27 routes** (was 38 broken) |
| Public tree: `check_css_bands.py` | **Passes** |
| Public site: `jekyll build` | **Passes** |
| Private routes in the public build | **None** — no `/decisions/`, `/decisions/log/`, `/milestones/`, `/research/`, `/agent-protocol/`, `/session-protocol/`, `/agents/`, `/backlog/` |
| `project-memory` in the public build's HTML | **No occurrences** |
| Private material in the tree | **None** — searched every withheld name |
| Reproducible | Two builds, `diff -r` identical but for a `__pycache__` created by running the scripts |
| Private tree: generator and links | **11 pages, 35 routes, all resolve** |
| Private gate: `dev.py verify` | **All checks passed** |

## What remains

**Nothing is committed**, by instruction — this session and the publisher from
the previous one are both in the working tree.

**The conditional blocks are a real cost.** Twenty-odd `if site.data.private_pages`
fences now sit in the documentation source. They are invisible in both outputs,
but they make the source busier to read and they are easy to forget when adding
a link to a private route. `check_site_links.py` catches the mistake in the
private repository only if the data file is removed, which nobody does day to
day — **the publisher's own run is what catches it**, and it should be run before
any publication rather than only before the first one.

**`AGENTS.md` remains withheld**, so the public repository has no single "how to
work here" document. `CONTRIBUTING.md` now carries the working method instead.
Whether that is enough is a judgement for whoever reads the public tree first.

## Exact next step

Review the generated tree at `/home/narain/ma_public` and the diff, then decide
whether to commit this and the publisher together or separately.
