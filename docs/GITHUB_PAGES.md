---
title: GitHub Pages
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
`PRODUCT.md` would stay `PRODUCT.md` and every link to `PRODUCT.html` would
404. That is exactly what happened the first time this site was built, and it is
the one thing to remember when adding a page:

```markdown
---
title: Product
---

# Product
```

`_config.yml` supplies `layout: default` to every page through `defaults`, so
the front matter only needs the title.

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
├── _config.yml         Jekyll settings (layout defaults, permalinks, exclusions)
├── PRODUCT.md          These render on the site and in GitHub alike
├── ARCHITECTURE.md
├── DEVELOPMENT.md
├── SECURITY.md
├── ROADMAP.md
├── BACKLOG.md
├── DECISIONS.md
├── project-memory/     Excluded from the published site
└── archive/            Excluded from the published site
```

`project-memory/` and `archive/` are excluded in `_config.yml`. They are
internal working memory, useful to contributors reading the repository but noise
on a public documentation site.

## Enabling it

Once the repository is on GitHub:

1. **Settings → Pages**
2. **Source:** GitHub Actions
3. Push to `main`

The site appears at <https://rootedglobal.github.io/mindarchive/>.

The workflow needs `pages: write` and `id-token: write` permissions, which are
already declared in `docs-pages.yml`.

## Working on the site locally

**`python -m http.server` is not enough, and will mislead you.** It serves files
as they are on disk. It does not run Jekyll, so no `.md` becomes `.html` and
every documentation link 404s — which looks exactly like a broken site when the
site is fine. Use it only to check the landing page's own layout.

To see what GitHub will actually publish, build it with Jekyll. Docker needs
nothing installed:

```bash
docker run --rm -v "$PWD/docs:/srv/jekyll" -v /tmp/ma_site:/out \
  jekyll/jekyll:4 jekyll build --destination /out

python -m http.server 8080 --directory /tmp/ma_site
```

Or serve it directly, with live reload:

```bash
docker run --rm -p 4000:4000 -v "$PWD/docs:/srv/jekyll" \
  jekyll/jekyll:4 jekyll serve --host 0.0.0.0
```

If you have Ruby and the gems locally, `cd docs && bundle exec jekyll serve`
does the same thing.

**What to check in the built output**, not the source folder:

- `PRODUCT.html`, `ARCHITECTURE.html` and the rest exist. If one is missing, its
  `.md` is missing front matter.
- `blog/index.html` exists and every post has its own `blog/<slug>/index.html`.
- `_drafts/TEMPLATE.md` did **not** get published.
- `feed.xml` is present and parses.
- `project-memory/` is absent.
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
section of [CONTRIBUTING.md](../CONTRIBUTING.md).

## Writing for the documentation site

Same rule as everywhere else in this project: **write for humans.** Short
sentences, plain words, concrete examples. The documentation is part of the
product, not an afterthought.

Keep it accurate. If behaviour changes, the documentation changes in the same
pull request.

## A note on the custom domain

`mindarchive.rootedglobal.co` is the intended eventual home — it is set as
`site.domain` in `project.json`, with `useCustomDomain` still `false`. To turn
it on, add a `CNAME` file containing the domain to `docs/`, and point a `CNAME`
DNS record at `rootedglobal.github.io`. Full steps, including the apex-versus-
subdomain distinction, are in [DEPLOYMENT.md](DEPLOYMENT.md).
