# Session: Build the private-to-public publication mechanism

**ID:** 2026-09-12-06-build-the-private-to-public-publication-mechanism
**Started:** 2026-09-12
**Ended:** 2026-09-12
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Build the allowlist-based publisher D-046 described: generate a clean public-safe
tree from this private repository, without ever copying everything and deleting
the private parts.

## Starting state

Branch `main` at `ae57849`, clean tree.

## What was done

**`scripts/publish_public.py`**, standard library only, three modes: `--list`,
`--check`, `--build DIR`. It is not in its own allowlist — a private
repository's publication tool stays private.

**It never runs `git`.** No `init`, no `commit`, no `remote`, no `push`, no
GitHub call. It writes files to a named directory and stops, because publishing
is a deliberate human act and a tool that could do it by accident is the wrong
tool.

**Files are listed individually; directories are recursive.** The trade-off is
argued in D-048: an allowlist naming every module under `apps/api/src` would be
stale within a day, and the safety comes not from enumeration but from every
file passing three gates before it is copied.

**The allowlist is a series of judgements, not an inventory.** `AGENTS.md` is
withheld — it is instructions for working inside a private repository, not
documentation of a product. So are `docs/BACKLOG.md` (withdrawn pricing and
internal reasoning), `docs/DECISIONS.md` (a pointer that would dangle),
`scripts/session.py` and `scripts/sync_site_pages.py`.

### Running it found three things

**Two were bugs in my own scanner, not in the repository.** It refused four test
fixtures containing `/home/someone/mindarchive/data/archive` — a deliberate
placeholder — and my home-path rule had its polarity backwards, exempting the
maintainer's real path while flagging invented ones. Both fixed; placeholder
users are now allowed and real account names are not.

**The third is the finding that matters.** Generating the tree and running **the
public tree's own link checker against it** produces **38 broken links**. That
is not a defect in the publisher; it is the coupling D-046 predicted, now
measured rather than argued. Five routes break only because the page generator is
withheld; eight are generated from private sources and can never exist publicly,
so the published documents have to stop linking to them.

**Usability came from running it, not from designing it.** The first version
printed forty-two reference lines on every invocation and sent refusals to
stderr, where they scrolled past unread behind the report. References are now
summarised unless `--verbose`, and every refusal prints to both streams. The
`.git` guard also moved ahead of `--force`, so `--force` cannot destroy a
repository — it previously only checked when forced.

## Decisions made

**D-048 — the publication allowlist, and what it refuses to publish.** Records
the allowlist model and its trade-off, the three gates, the scanner's deliberate
smallness and its limits, the withheld list with a reason for each, and the
38-link finding with the fix for both halves.

## Files changed

```
added:    scripts/publish_public.py
modified: project-memory/DECISIONS.md       (D-048)
modified: docs/DECISIONS.md                 (D-048 in the index)
modified: project-memory/PROJECT_STATE.md   (the publisher exists; the site does not build yet)
added:    project-memory/sessions/2026-09-12-06-.../
```

Nothing in the working tree was modified by the tool itself, by construction.

## Checks run

| Check | Result |
|---|---|
| `publish_public.py --check` | **Passes** — 134 files, no secret, no denied path; 42 references reported |
| Build to `/home/narain/ma_public` | **134 files written** |
| Private material in the output | **None** — searched for `project-memory`, `AUDIT`, `CLAUDE.md`, `GEMINI.md`, `QWEN.md`, `AGENTS.md`, `session.py`, `sync_site_pages.py`, `.env`, `.git`, `*.db`, `*.zip` |
| Refuses a destination inside the repository | **Refused**, with the reason |
| Refuses an existing destination without `--force` | **Refused** |
| Refuses a destination containing `.git`, even with `--force` | **Refused**, and the directory was untouched afterwards |
| Reproducible | Two builds to different destinations, `diff -r` — **identical** |
| Public tree's own link checker | **38 broken links** — see D-048 |
| Private repository unchanged | `git status` — only the files listed above |
| `session.py check`, `check_site_links.py` | Both pass |

## What remains

**Nothing is committed**, by instruction.

**The public site does not build.** Two fixes, both described in D-048: teach
`sync_site_pages.py` which sources are private-only so a trimmed generator can
be published, and stop the published documents linking to eight routes that will
never exist publicly. The second is a content decision about what the public site
says, and belongs to whoever decides that.

**The generated tree is at `/home/narain/ma_public`**, outside the repository,
safe to delete and regenerate.

**The scanner will not catch a secret that reads like ordinary prose.**
`.gitignore` and the CI secrets job remain the primary defence; this is a second
lock, not the first.

## Exact next step

Review `scripts/publish_public.py` and the allowlist in it — particularly the
withheld list — then decide whether to fix the 38 links before or after the
public repository is created.
