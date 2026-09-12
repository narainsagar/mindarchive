# Session: Proprietary licence, and the public/private boundary

**ID:** 2026-09-12-03-proprietary-licence-and-the-public-private
**Started:** 2026-09-12
**Ended:** 2026-09-12
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Act on decisions the maintainer confirmed after the boundary audit: replace the
PolyForm licence with All Rights Reserved, make current product-facing wording
agree with it, add a high-level AI-assistance disclosure, record the decision,
and describe — without building — the future publication mechanism.

Working-tree changes only. **Nothing committed, nothing pushed**, by instruction.

## Starting state

Branch `main`, commit `a613016`, clean but for the untracked
`docs/development/GIT_SSH_SETUP.md`. 33 tracked files carried PolyForm or
source-available claims.

## What was done

**The licence is now All Rights Reserved.** `LICENSE` is a copyright notice
rather than a licence text: no permission granted, access for reference only.
`LICENSING.md` was rewritten from a four-tier pricing page into a short
proprietary statement.

**No replacement commercial system was invented**, deliberately and on
instruction. The $49 seat price, the $39 volume tier and the checkout path are
**withdrawn, not repriced** — including the `licence` block in
`docs/_data/support.yml`, which is now empty with a comment saying why. A price
nobody has approved is worse than no price.

**Twenty files were split into three groups**, which was the actual work:

1. **Current and product-facing → changed.** Manifests, README, the site, the
   application's own panels and footer.
2. **Historical → left alone.** `CHANGELOG.md`'s 0.1.0 entry, `MILESTONES.md`,
   `prompts/`, the session records and the superseded decisions. They were true
   on their dates; rewriting them would be falsifying the record to make it look
   as though the project always said this.
3. **Superseded but still useful → annotated, not deleted.** D-016 and D-032
   carry dated forward-links in the project's existing convention, and
   `docs/BACKLOG.md`'s commercial section keeps its merchant-of-record research
   under a note saying the plan above it is void.

**D-016's own argument is what made this possible.** It chose PolyForm partly
because *"a licence can be relaxed but never tightened"* — and the software has
never been published or distributed, so there is no recipient of that grant to
take anything away from. That is recorded in D-046 rather than left as a
coincidence; it is also the reason this had to happen **now** rather than after
the first public release.

**The AI disclosure is one sentence in `README.md`**, under a new "How it is
built" heading. Nothing about prompts, agent rules, project memory or session
records — the disclosure is a fact about how the work is done, not an invitation
to read the workshop.

**One test caught a mistake as it was written.** The Support panel's new wording
said there was "no checkout to send you to" — and `App.test.tsx` scans the whole
rendered interface for payment-provider words including `checkout`, which would
have failed. Reworded to "nowhere to send you". The guard from D-038 is still
doing its job a month later.

## Decisions made

**D-046 — proprietary, and published from an allowlist into a separate
repository.** Supersedes D-016 (the licence) and the publication half of D-032.
It records: All Rights Reserved; this repository stays private permanently; a
separate clean-history public repository later; AI assistance disclosed at a high
level while the machinery stays private; and the publication mechanism —
allowlist out, never denylist in — with the four couplings that will break a
naive split.

## Files changed

```
licence:      LICENSE · LICENSING.md
manifests:    project.json · apps/web/package.json · apps/api/pyproject.toml
root docs:    README.md (+ AI disclosure) · CONTRIBUTING.md · AGENTS.md
site:         docs/index.html · docs/PRODUCT.md · docs/contribute.md ·
              docs/support.md · docs/documentation.html · docs/_layouts/default.html ·
              docs/_data/support.yml · docs/_drafts/TEMPLATE.md ·
              docs/_posts/2026-09-10-introducing-mind-archive.md ·
              docs/DEPLOYMENT.md · docs/BACKLOG.md · docs/DECISIONS.md (index)
application:  components/SupportPanel.tsx · components/ContributePanel.tsx ·
              components/SiteFooter.tsx · support.ts (comment) · App.test.tsx
memory:       project-memory/DECISIONS.md (D-046; D-016 and D-032 annotated) ·
              project-memory/PROJECT_STATE.md
added:        project-memory/sessions/2026-09-12-03-.../
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Project memory | `scripts/session.py check` | see below |
| Remaining licence claims | `grep` over all tracked files | Only negations, the historical `CHANGELOG` entry, and deliberate footnotes |
| Working tree | `git diff --stat`, `git status` | Reviewed; nothing committed |

**Not run: both test suites and `dev.py verify`.** They need containers, which
this session was told not to start. **Three assertions in `App.test.tsx` were
edited to match the new wording and have not been executed.** That is the first
thing to run next session.

## What remains

**Run the frontend suite.** Three changed assertions are unverified: the "never
nags" lede, the "nothing is for sale yet" line, and the footer's "all rights
reserved". The payment-provider guard also needs to pass against the new text.

**`CHANGELOG.md` has no entry for the licence change**, deliberately — changelog
work was out of scope this session. It should record it when that work happens.

**`ContributePanel` still offers a "Read the source" button** when
`repositoryUrl` is set, which now points at a private repository and says "read
the source" beside "not source-available". Left alone: it is configuration and
changing the component's behaviour was out of scope.

**`prompts/MASTER.md` and `prompts/AI-CODING.md` still say "open source"** —
private founding documents, left accurate to their date.

## Exact next step

Run `python scripts/dev.py test frontend` and fix whatever the three edited
assertions reveal.
