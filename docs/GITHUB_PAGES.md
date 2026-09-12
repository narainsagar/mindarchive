---
title: GitHub Pages
permalink: /github-pages/
---

# GitHub Pages

The project documentation is published as a small static site from the `docs/`
folder in this repository.

**The application does not depend on GitHub Pages.** Pages hosts the project
website and documentation only. Mind Archive itself is local-first and runs
entirely on your own machine.

## How it works

`.github/workflows/docs-pages.yml` builds and deploys the site with Jekyll
whenever `docs/` changes on `main`. The Markdown files stay readable both on the
site and directly in the repository.

**Every Markdown file needs YAML front matter.** Jekyll only converts files that
have it; a file without front matter is copied through verbatim, so
`PRODUCT.md` would stay `PRODUCT.md` and every link to it would 404. That is
exactly what happened the first time this site was built.

**Every page also needs an explicit `permalink`.** Pages live at clean lowercase
routes — `/product/`, not `/PRODUCT.html` — and Jekyll will not invent one for
you:

```markdown
---
title: Product
permalink: /product/
---

# Product
```

`_config.yml` supplies `layout: default` to every page through `defaults`, so
the front matter needs only the title and the route.

> **Do not add a top-level `permalink:` key to `_config.yml`.** A global
> permalink applies to pages as well as posts. Setting `/blog/:title/` at the
> top level once rewrote every documentation page from `PRODUCT.html` to
> `PRODUCT/index.html` and broke the whole nav. The blog's permalink is scoped
> to `type: posts` inside `defaults` for exactly that reason. See D-036.

```
docs/
├── index.html          The landing page
├── blog.html           The blog index, at /blog/
├── feed.xml            RSS, hand-written — no plugin (D-035)
├── _posts/             Published posts. YYYY-MM-DD-slug.md
├── _drafts/
│   └── TEMPLATE.md     House style. Never published
├── _layouts/
│   ├── default.html    Header, appearance controls, footer — every page
│   └── post.html       Date, tags and summary on top of that
├── assets/
│   └── site.css        The same colour tokens the application uses
├── _config.yml         Jekyll settings (layout defaults, permalinks)
├── _data/
│   └── support.yml     Donation and licence URLs (D-038)
├── PRODUCT.md          These render on the site and in GitHub alike
├── ARCHITECTURE.md
├── DEVELOPMENT.md
├── SECURITY.md
├── ROADMAP.md
├── BACKLOG.md
└── DECISIONS.md
```

**The working memory is not in here.** `project-memory/` sits at the repository
root, one level up and outside this folder entirely, so Jekyll never sees it and
no exclusion rule is needed — the site cannot publish what it cannot reach
(D-039). It is useful to anyone reading the repository and noise on a public
documentation site, which is exactly the split.

## Enabling it

Once the repository is on GitHub:

1. **Settings → Pages**
2. **Source:** GitHub Actions
3. Push to `main`

The site appears at <https://narainsagar.github.io/mindarchive/>.

The workflow needs `pages: write` and `id-token: write` permissions, which are
already declared in `docs-pages.yml`.

## Working on the site locally

**`python -m http.server` is not enough, and will mislead you.** It serves files
as they are on disk. It does not run Jekyll, so no `.md` becomes `.html` and
every documentation link 404s — which looks exactly like a broken site when the
site is fine. Use it only to check the landing page's own layout.

To see what GitHub will actually publish:

```bash
python scripts/dev.py docs        # http://localhost:4000
```

**Use this rather than `jekyll serve` directly.** Eleven pages are generated
before the build — `/licensing/`, `/agents/`, `/decisions/log/` and the rest —
and they are git-ignored, so a bare `jekyll serve` shows a site that is missing
them and full of dead links (D-043). `dev.py docs` generates them, checks every
internal link, and then serves.

If you would rather drive it yourself, generate first and then build:

```bash
python scripts/sync_site_pages.py

docker run --rm -v "$PWD/docs:/srv/jekyll" -v /tmp/ma_site:/out \
  jekyll/jekyll:4 jekyll build --destination /out

python -m http.server 8080 --directory /tmp/ma_site
```

If you have Ruby and the gems locally, `cd docs && bundle exec jekyll serve`
does the same thing — again, after generating.

## Pages generated from the repository's own documents

Jekyll is rooted at `docs/` and cannot read above it, and the Pages build runs
in safe mode so it will not follow a symlink out of the source folder either.
`LICENSING.md`, `AGENTS.md` and everything under `project-memory/` are therefore
**generated** into `docs/reference/` by `scripts/sync_site_pages.py`.

```bash
python scripts/sync_site_pages.py --list    # what is published, and where
```

- **`docs/reference/` is git-ignored. Never edit a file in it** — edit the
  canonical document at the repository root. The page is regenerated from it,
  so the two cannot drift.
- **Adding a page** means adding a row to `PAGES` in that script. Linking to a
  document that has no page is a build failure, not a silent 404.
- **Links inside the generated content are rewritten** to
  `{% raw %}{{ '/permalink/' | relative_url }}{% endraw %}`, because Kramdown
  leaves `.md` links alone and they 404.
- **Liquid already in the document is escaped**, because Liquid runs over the
  whole file before Kramdown sees any Markdown — backticks do not protect it. A
  raw block the author wrote is left alone rather than wrapped again, and a lone
  `raw` or `endraw` tag written as prose is printed instead. Getting this wrong
  produces a page Jekyll will not parse, so the generator checks each page and
  refuses to write one that would fail (D-043).
- **Writing about Liquid in a document that gets published is awkward on
  purpose.** If you need to show a `raw` tag, name it without its braces. Only
  one form survives being escaped and it is not worth memorising.

**What to check in the built output**, not the source folder:

- `product/index.html`, `architecture/index.html` and the rest exist. If one is
  missing, its `.md` is missing front matter or a `permalink`.
- **Every internal link resolves.** A permalink change can silently 404 a whole
  section, so check the links rather than a handful of files.

  ```bash
  python scripts/check_site_links.py
  ```

  This ran by hand exactly once between D-036 and D-043 — which is to say it did
  not run. It is now part of `dev.py verify`. It reads the source rather than a
  built site, so it needs no Ruby and takes under a second. `verify` also builds
  the site itself, which is what catches a page Liquid cannot parse; walking the
  built output by hand is still worth doing before a release.
- `blog/index.html` exists and every post has its own `blog/<slug>/index.html`.
- `_drafts/TEMPLATE.md` did **not** get published.
- `feed.xml` is present and parses.
- No `project-memory/` directory in the output. Four of its documents are
  published, but as generated pages at `/decisions/log/`, `/milestones/`,
  `/research/` and `/session-protocol/` (D-043) — the directory itself is still
  outside anything Jekyll can reach. `PROJECT_STATE.md`, `SESSION_LOG.md` and
  the session records are not published at all.
- **No band rule uses the `padding` shorthand.** The band gives every page its
  side gutter with `padding-inline: var(--gutter)`. Any rule on the *same
  element* that uses the `padding` shorthand silently resets that to zero and
  the content goes flush to the window edge — which is precisely what
  `.doc { padding: 48px 0 72px }` did to all twenty document pages (D-041).

  Elements that carry a band: `<main class="wrap doc">`,
  `<main class="wrap home">`, `.site-header__in`, `.site-header__panel-in`,
  `.site-footer__in`. On any of those, and on any class sharing the element,
  write `padding-block`. Never `padding`.

  Worth knowing why it went unnoticed: **no other check reads CSS.** The link
  checker, the band checker and the privacy checker all passed the entire time
  the padding was broken.
- **No third-party script or frame anywhere.** This is a promise, not a
  preference — a privacy-first product cannot load a script that fingerprints
  every visitor, and the donate page is exactly where that temptation appears
  (D-038). The check:

  ```bash
  # Must return nothing.
  grep -rEo '<(script|iframe)[^>]+src="https?://[^"]+"' /tmp/ma_site --include='*.html'
  ```

  Every script on this site is inline and first-party. If that command ever
  prints something, someone has embedded a payment widget, an analytics tag or
  a font host, and it needs removing rather than allowing.
- The header, the palette and theme controls and the footer appear on a
  documentation page and a blog post, not just on the landing page.

## Writing a post

`docs/_drafts/TEMPLATE.md` is the starting point and carries the house style:

```bash
cp docs/_drafts/TEMPLATE.md docs/_posts/2026-01-31-a-short-slug.md
```

The date in the filename orders the blog; the URL is `/blog/a-short-slug/` with
no date in it, so a post does not look stale a year later. `_drafts` is ignored
unless you build with `--drafts`, so work in progress never ships.

Nothing publishes itself — see decision D-035 and the *Writing a blog post*
section of [CONTRIBUTING.md]({{ '/contribute/' | relative_url }}).

## Writing for the documentation site

Same rule as everywhere else in this project: **write for humans.** Short
sentences, plain words, concrete examples. The documentation is part of the
product, not an afterthought.

Keep it accurate. If behaviour changes, the documentation changes in the same
pull request.

## A note on the custom domain

**This site's eventual home is `docs.mindarchive.narainsagar.com`** — a
subdomain, so one `CNAME` record pointing at `narainsagar.github.io` is all the
DNS it needs, and no apex `A` records are involved. The application takes
`mindarchive.narainsagar.com` and its API takes
`api.mindarchive.narainsagar.com`; neither is a Pages concern (**D-047**).

`project.json` holds `site.domain` with `useCustomDomain` still `false`, and
nothing is configured. Full steps are in
[DEPLOYMENT.md]({{ '/deployment/' | relative_url }}#the-domain-names).
