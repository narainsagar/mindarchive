# Session: a blog on the Jekyll site

**ID:** 2026-09-10-01-a-blog-on-the-jekyll-site
**Started:** 2026-09-10
**Ended:** 2026-09-10 04:59
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Add a blog to Mind Archive, with an opening set of posts, and decide how posts
get written from here on.

## Starting state

Branch `main`, clean at `e4c901f`. Identity set to the **RootedGlobal**
organisation as **`mindarchive`**; `origin` configured but nothing pushed, and
the repository is currently **private**.

## What was done

**The blog is part of the Jekyll site, not the application.**

Serving `/blog` and `/docs` from `localhost:5173` was asked for and argued
against. Port 5173 is the Vite dev server — it exists only on a developer's
machine during `dev.py up`, and the application is local-first, running on each
user's own computer over their own files. Bundling the public site into it would
contradict D-008 and D-032 and would need `react-router` plus a proxy to do
worse what Jekyll already does. Agreed: `:5173` the application, `:4000` the
site.

Infrastructure: `docs/_posts/`, `docs/blog.html` at `/blog/`,
`docs/_layouts/post.html` on top of the shared default layout, `docs/feed.xml`,
a `Blog` link in the site nav, and blog styles in `assets/site.css` using only
existing tokens — so posts follow the reader's palette and theme like everything
else.

**Four short posts**, all dated 2026-09-10: *Introducing Mind Archive*,
*What "local-first" actually means*, *How Mind Archive is built*, and
*Decisions worth stealing*.

The requested tone was marketing-forward. Followed as benefit-led and
accessible; not followed into invention. No download counts, no testimonials, no
screenshots of things that do not exist, and the project is never described as
open source. Every technical claim points at something in the repository.

**No plugins.** `jekyll-feed` works on GitHub Pages but is absent from the
`jekyll/jekyll:4` image used for local preview, so it would make the local and
published builds differ — the drift D-033 exists to prevent. `feed.xml` is
hand-written Liquid instead.

**A verification step found a real subtlety.** The built feed carried *relative*
item links, and RSS requires absolute ones. The cause is that `url` and
`baseurl` are unset in `_config.yml`. They were deliberately left unset:
`actions/configure-pages@v5` (already at `docs-pages.yml:34`) injects the
correct values for a project site at build time, and hardcoding them would break
local preview, where `localhost:4000` serves from the root. Documented in
`_config.yml` and D-035 rather than "fixed" wrongly.

**How posts get written.** `docs/_drafts/TEMPLATE.md` carries the house style
and is never published. `CONTRIBUTING.md` gained a *Writing a blog post*
section, explicitly marked as taking effect once the CLA exists — writing it as
current policy would have contradicted that file's own opening line that outside
code is not yet accepted. A post may be drafted from anything, including an AI
assistant or a session record, but **a person approves before merge and nothing
auto-publishes**.

## Decisions made

**D-035 — The blog is part of the Jekyll site, and nothing publishes itself.**

## Files changed

```
Added:
  docs/blog.html
  docs/feed.xml
  docs/_layouts/post.html
  docs/_drafts/TEMPLATE.md
  docs/_posts/2026-09-10-introducing-mind-archive.md
  docs/_posts/2026-09-10-what-local-first-actually-means.md
  docs/_posts/2026-09-10-how-mind-archive-is-built.md
  docs/_posts/2026-09-10-decisions-worth-stealing.md

Modified:
  docs/_config.yml                  post layout default, permalink, url/baseurl note
  docs/_layouts/default.html        Blog nav link
  docs/assets/site.css              blog index and post styles
  docs/GITHUB_PAGES.md              blog structure, how to write a post
  CONTRIBUTING.md                   Writing a blog post
  docs/DECISIONS.md                 D-035
  docs/project-memory/DECISIONS.md  D-035
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Site build | `jekyll/jekyll:4 jekyll build` | Passed |
| Blog index | built output | `blog/index.html` present, all four posts linked |
| Posts | built output | all four at `blog/<slug>/index.html` |
| Drafts | built output | `TEMPLATE.md` **not** published |
| Feed | `xml.dom.minidom` parse | valid XML, 4 items |
| Shared layout | built output | palette and theme controls present on a post |
| Memory excluded | built output | `project-memory/` absent |
| Unrendered Liquid | built output | 0 files |
| Full gate | `dev.py verify` | Passed |

## What remains

- **Nothing is pushed, and the repository is private.** GitHub Pages does not
  publish from a private repository on a free plan, so the blog is local-only
  until the repository is made public.
- **The feed's absolute URLs are unverified.** They only materialise in the
  published build, where `configure-pages` supplies `url` and `baseurl`. Check
  the live `feed.xml` after the first deploy.
- No `CNAME`; `mindarchive.rootedglobal.co` remains unconfigured with
  `useCustomDomain: false`.
- The posts have been built and structurally verified but not read on a rendered
  page in every palette.

## Exact next step

Make the repository public, push, enable **Settings → Pages → Source: GitHub
Actions**, then check the live site's `/blog/` and `feed.xml`.
