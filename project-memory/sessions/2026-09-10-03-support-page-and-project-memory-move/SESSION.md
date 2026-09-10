# Session: support page and project-memory move

**ID:** 2026-09-10-03-support-page-and-project-memory-move
**Started:** 2026-09-10
**Ended:** 2026-09-10 18:16
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Two things. Take money on the website — donations and the $49 commercial
licence — without breaking the promise that the application never contains
payment code. Then move project memory out of `docs/` to the repository root.

## Starting state

Branch `main`, clean at `651ea60`, 106 tests. `LICENSING.md` already published
$49 per seat and the ☕/🍺/🍕 donation tiers. `docs/project-memory/` was kept off
the website only by an `exclude:` rule.

## What was done

### Payment, on the website only (D-038)

The maintainer asked whether the promise in `LICENSING.md:72-74` blocked this.
It does not: *"Donations will be handled on the project website, not inside the
application"* permits exactly this. The constraint is on `apps/`, and it is now
kept **and tested** — the Support panel holds one link to the website, and a
test asserts no payment provider name appears anywhere in the rendered
interface.

**A merchant of record, not raw Stripe.** Selling a digital licence to an EU
consumer creates a VAT obligation on the first sale; there is no threshold. Raw
Stripe would leave registration, quarterly filing and ten years of records with
the maintainer. `BACKLOG.md` had flagged this as "evaluate before taking the
first payment" — this is that evaluation.

**Hosted checkout, plain links.** No Stripe.js, no PayPal SDK, no iframe. A
product whose argument is that nothing tracks you cannot load a script that
fingerprints every visitor to its donate page. **Enforced by a build check**, now
documented in `GITHUB_PAGES.md`: no third-party `<script src>` or `<iframe src>`
anywhere in the built site.

`/support/` is driven entirely by `docs/_data/support.yml`. Every URL is blank,
so the page currently says so and points at the contact address.

### Project memory moved to the root (D-039)

It was never documentation. `docs/` is what the website publishes; project
memory is the internal record of how the project got here. At the root the
exclusion is **structural rather than configured** — the site cannot publish
what it cannot reach — so `_config.yml` no longer needs the rule that was the
only thing keeping it private.

50 files repointed. Paths are pointers rather than historical claims, so past
session records were updated too; nothing describing what was once true was
altered.

## Two things found by running checks rather than reading

**A dead link shipped into the built page.** The "Any amount" button rendered
with `href=""` — precisely what the blank-means-hidden pattern exists to
prevent. Cause: **Liquid's `assign` does not evaluate a comparison**, so
`assign has_custom = url != ""` was never a boolean. Comparisons moved into
`if`, where they work. A `no empty href` check now guards it.

**`scripts/session.py` builds its path from separate segments** —
`REPO_ROOT / "docs" / "project-memory"` — so a text search for
`docs/project-memory` did not match it. It is the single place that would have
broken CI, because `session.py check` is a required job.

Also fixed: a `react-hooks/exhaustive-deps` warning introduced by the new
`onTotalChange` callback, and a palette label that had drifted to "Ink &
violet" on the site after being renamed to "Ink & Violet" in `theme.ts`.

Two documents claimed project memory was "excluded in `docs/_config.yml`". That
is no longer why it is absent, so both were corrected — a true statement for the
wrong reason is still wrong.

## Decisions made

**D-038** — money is taken by a merchant of record, through plain links.
**D-039** — project memory lives at the repository root.

## Files changed

```
Added:
  docs/_data/support.yml
  docs/support.md

Renamed:
  docs/project-memory/ -> project-memory/          (git-recorded rename)

Modified (selected):
  docs/assets/site.css          tier and wallet styles
  docs/_layouts/default.html    Support in nav and footer
  docs/_config.yml              exclusion rule removed, and why
  docs/documentation.html       Support listed
  docs/GITHUB_PAGES.md          third-party-script check; new structure
  docs/DEPLOYMENT.md            two corrected claims
  docs/BACKLOG.md               commercial section resolved
  LICENSING.md                  🍽️$25 tier; how the promise is kept
  apps/web/src/support.ts       links to the website, never a provider
  apps/web/src/App.test.tsx     provider-absence test
  apps/web/src/components/ArchivePanel.tsx   dependency fix
  scripts/session.py            MEMORY_DIR path
  + 47 files repointed to project-memory/
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Full gate | `dev.py verify` | **Passed — 107 tests** |
| Lint | `dev.py lint` | Passed, 0 warnings after the dependency fix |
| Project memory | `session.py check` | Consistent, 13 sessions, at the new path |
| Site build | `jekyll/jekyll:4` | Passed |
| Links | built output | 618/618 resolve |
| Third-party embeds | built output | none — every script inline and first-party |
| Provider domains in `apps/` | grep | none |
| Empty `href` | built output | none |
| `project-memory/` published? | built output | absent |

## What remains

- **No payment has been tested, and cannot be from here.** No account exists and
  every URL in `docs/_data/support.yml` is blank. A real purchase on both paths,
  and the refund path, is required before either is announced.
- **What a licence buyer actually receives** is undecided — with a merchant of
  record it is a file attached to the receipt, and that file does not exist.
- Neither surface has been looked at since the header rework; the support page
  has been built and checked but not seen.
- The repository is still private, so Pages does not publish.

## Exact next step

Open an account with Polar, Paddle or Lemon Squeezy, create the products, and
paste the URLs into `docs/_data/support.yml` — nothing else needs touching.
