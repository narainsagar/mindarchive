# Session: Publish the canonical documents as site pages, and check every link

**ID:** 2026-09-11-02-publish-the-canonical-documents-as-site-pages-and
**Started:** 2026-09-11
**Ended:** 2026-09-11 06:59
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Fix the links that leave the site. The maintainer reported four
`github.com/RootedGlobal/mindarchive/blob/main/...` links that go nowhere on
`localhost:4000`, and asked for every page to be checked for the same problem.

## Starting state

Branch `main`, last commit `840ac36` (D-042, the sharded importer). Clean tree.

## What was done

**The reported four were fifteen**, across ten pages: `LICENSING.md` (×4),
`project-memory/MILESTONES.md` (×3), `project-memory/DECISIONS.md` (×2),
`AGENTS.md` (×2), `CONTRIBUTING.md`, `project-memory/RESEARCH.md`,
`project-memory/SESSION_PROTOCOL.md` and `.env.example`.

**None of those targets was a page on the site**, so rewriting URLs was not
enough — the destinations had to be made to exist. Jekyll is rooted at `docs/`
and cannot read above it (D-039 made that explicit), and the Pages build runs in
safe mode so a symlink out of the source folder is not followed either.

**`scripts/sync_site_pages.py`** generates eleven pages from the canonical
files. Output is git-ignored in `docs/reference/`, regenerated before every
build, so there is no committed copy to drift — D-010 forbade a second decision
log, and a committed copy would have been one.

`LICENSE`, `CODE_OF_CONDUCT.md` and `AI_AGENT_PROTOCOL.md` were added to the
list, unrequested: the documents that *were* requested link to them 22 times
between them, and publishing pages whose own links dead-end just moves the
problem one click deeper.

**`scripts/check_site_links.py`** walks every internal link. This is the more
useful half. D-036 has required it since the day it was written — *"a check that
only looks where you just worked cannot find what you broke elsewhere"* — **and
nothing did it.** It had run by hand, once. Now in `dev.py verify`.

**`python scripts/dev.py docs`** generates, checks and serves on :4000. Bare
`jekyll serve` now shows an incomplete site, so the documented command changed.

**A 404 page** at `docs/404.html`. A safety net, not a fix: the checker is what
stops a broken link shipping.

## Decisions made

**D-043** — the repository's canonical documents are generated as site pages.
It **amends D-036**, whose closing clause read *"Links to `project-memory/` now
point at GitHub, since that directory is deliberately excluded from the site."*
That clause is why the links were written that way; it is no longer true. D-036
is annotated in place rather than quietly contradicted.

## Bugs found while doing it

1. **Liquid inside backticks is still executed.** Liquid runs over the whole
   file before Kramdown sees Markdown, so D-036's own entry — which *explains*
   the `relative_url` convention by quoting it — would have rendered the
   evaluated URL instead of the syntax. Pre-existing Liquid is now wrapped in
   `{% raw %}`.
2. **A link label containing backticks is still a link.** My first version
   skipped every code span, which split ``[`docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md)``
   apart and left three real links unconverted. Only a *whole* link in backticks
   is an example. The checker caught this, which is the argument for the checker.
3. **Three stale `docs/project-memory/` paths** survived the D-039 move, in
   `apps/api/Dockerfile` and `apps/web/src/styles.css` — same root cause D-039
   recorded, the path split across lines so the search missed it.
4. **The Pages workflow would not have rebuilt.** Its path filter was `docs/**`;
   editing `LICENSING.md` now changes the published site. The sources are listed.
5. **The site footer had the contact address written out by hand**, a second
   copy beside `_data/support.yml`. It now reads from the data file.

## Files changed

```
added:    scripts/sync_site_pages.py
added:    scripts/check_site_links.py
added:    docs/404.html
modified: scripts/dev.py                     (docs command; two new gate steps)
modified: .github/workflows/docs-pages.yml   (generate + check; path filter)
modified: .gitignore                         (docs/reference/)
modified: docs/_layouts/default.html         (contact address from data)
modified: docs/documentation.html            (Reference + working-record sections)
modified: docs/GITHUB_PAGES.md               (generation, the checker, dev.py docs)
modified: docs/{ARCHITECTURE,BACKLOG,DECISIONS,DEVELOPMENT,PRODUCT,ROADMAP}.md
modified: docs/{support,contribute}.md
modified: docs/_posts/2026-09-10-what-local-first-actually-means.md
modified: apps/api/Dockerfile                (stale docs/project-memory path)
modified: apps/web/src/styles.css            (stale docs/project-memory paths)
modified: project-memory/DECISIONS.md        (D-043; D-036 amended in place)
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Full gate | `python scripts/dev.py verify` | **All checks passed** |
| Tests | `python scripts/dev.py test` | **310 backend, 107 frontend** |
| Link check, source | `scripts/check_site_links.py` | 15 problems found, then **0 — 34 routes** |
| Site build | `jekyll build` in Docker | done in 1.79s; all 11 pages plus `/404.html` present |
| Link walk, built output | one-off over `/tmp/ma_site` | **987 internal links across 33 pages, all resolve** (two apparent hits were URL text inside code blocks, confirmed not anchors) |
| Third-party scripts | grep over built HTML | none |
| `project-memory/` leak | built output | no such directory |

## What remains

**The contact address is unchanged.** The maintainer chose "a project address"
to replace `kishor3947@gmail.com` but did not name one, and `mindarchive.app`
has no DNS yet (backlog), so an address there would bounce. It is now defined in
**one** place for the site — `contact_email` in `docs/_data/support.yml` — plus
`contactEmail` in `apps/web/src/support.ts` for the application, and
`project.json` for author identity. Changing it is a one-line edit in each once
a mailbox exists. `apps/web/src/App.test.tsx` asserts on it and will need the
same value.

**Not published, deliberately:** `PROJECT_STATE.md`, `SESSION_LOG.md`,
`MEMORY_INDEX.md` and the session records. Working scratch; nothing links to
them.

**The link checker reads source, not built output.** It catches the class of
mistake that has actually happened here and costs a second. Building and walking
the output is still the last word before a release, and was done by hand this
session.

**Uncommitted and not mine:** the donation tiers in `LICENSING.md` and
`docs/_data/support.yml` were changed from $20/$25 to $15/$20 during this
session by the maintainer. Left out of this commit deliberately.

## Exact next step

Decide the project contact address and whether its mailbox exists, then change
`contact_email` in `docs/_data/support.yml`, `contactEmail` in
`apps/web/src/support.ts`, the assertion in `apps/web/src/App.test.tsx`, and
`project.json`.
