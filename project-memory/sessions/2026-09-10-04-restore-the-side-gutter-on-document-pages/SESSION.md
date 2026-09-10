# Session: restore the side gutter on document pages

**ID:** 2026-09-10-04-restore-the-side-gutter-on-document-pages
**Started:** 2026-09-10
**Ended:** 2026-09-10 21:25
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Body content on the site sat flush against the window edge while the header and
footer kept their gutter. Fix it, without changing anything else.

## Starting state

Branch `main`, clean at `f078620`, 107 tests. The maintainer reported it with a
screenshot of `/support/` at ~920px: the brand inset ~32px, the heading at 0.

## What was done

**One declaration**, `docs/assets/site.css`:

```css
.doc {
-  padding: 48px 0 72px;
+  padding-block: 48px 72px;
}
```

`<main>` carries `wrap doc`. The band rule sets
`padding-inline: var(--gutter)`; `.doc` has the same specificity and comes
later, so its **shorthand** reset `padding-inline` to zero.

**The scope was wrong at first, and the maintainer caught it.** I checked
`/support/` and generalised from one page. Enumerating every built page instead:
**20 pages carry `wrap doc` and were all broken**; only the home page
(`wrap home`) escaped, because no `.home` rule exists to override the band. That
matched exactly what had been reported — "all pages except home".

**This shipped when the site layout was first built.** `--content-max` was
`1280px` with `margin-inline: auto`, so above that width the auto margins made
side space that looked like the gutter. D-040 set `--content-max: none`, removed
the centring, and exposed it. The later change revealed the defect; it did not
cause it.

The comment three sections above the broken rule already said *"padding-block,
never the padding shorthand, which would reset the band's padding-inline to
zero."* Prose is not a check.

**A preview was published before touching the repository**, showing before and
after at 920px and 375px from the real tokens, and approved.

## Ruled out rather than assumed

Only a rule on `<main>` itself can remove its padding, and exactly two target
it: `.wrap` and `.doc`. Scanning the whole stylesheet also confirmed no negative
inline margins (only `margin: -1px` in `.visually-hidden`), no `100vw`, and no
bare `.post` rule. The three other zero-horizontal-padding rules —
`.doc blockquote`, `.post-list__item`, `.site-footer` — are all on non-band
elements and correct. **Nothing under `apps/` was touched**: its `.workspace`
band uses `padding-top` / `padding-bottom` longhands.

## The guard, and why it was needed

Every existing check passed for as long as this was broken, because **none of
them reads CSS**. `scripts/check_css_bands.py` now fails if any class landing on
a layout band uses the `padding` shorthand, and it **runs inside
`dev.py verify`** rather than sitting unused.

**It was proven by reintroducing the bug**: passes on the fix, fails on
`padding: 48px 0 72px` with file, line and selector. A guard that cannot fail is
worth nothing.

It avoids `list[str]` annotations — WSL's Python here is 3.8, which is the whole
reason Docker is the supported path for the application (D-006, D-007). The
first version crashed on exactly that.

## Decisions made

**D-041 — Band elements use `padding-block`, never the `padding` shorthand.**

## Files changed

```
Added:
  scripts/check_css_bands.py
  project-memory/sessions/2026-09-10-04-restore-the-side-gutter-on-document-pages/

Modified:
  docs/assets/site.css       .doc -> padding-block (the fix)
  scripts/dev.py             the guard wired into verify
  docs/GITHUB_PAGES.md       the rule, and why no other check catches it
  docs/DEVELOPMENT.md        the command
  docs/DECISIONS.md          D-041
  project-memory/DECISIONS.md
```

## Checks run

| Check | Result |
|---|---|
| `dev.py verify` | **Passed — 107 tests**, lint clean, CSS guard included |
| CSS guard, against the fix | Passed |
| CSS guard, bug reintroduced | **Failed as designed** — file, line, selector |
| Site build | Passed |
| Links | 618/618 resolve |
| Bands | all 21 pages correct |
| Third-party embeds / empty href | none |

## What remains

- **The visual result is unverified by me.** I have no browser. The markup and
  every check are right, but whether the gutter looks correct across the pages
  is the maintainer's check, at `localhost:4000`.
- Neither surface has been looked at by me since the header rework.
- Payment URLs are still blank; no purchase has been tested.
- The repository is private, so Pages does not publish.

## Exact next step

Reload `localhost:4000` and click through `/support/`, `/blog/`, a post and
`/docs/` — the text should be inset exactly like the header.
