# GitHub Pages

The project documentation is published as a small static site from the `docs/`
folder in this repository.

**The application does not depend on GitHub Pages.** Pages hosts the project
website and documentation only. Mind Archive itself is local-first and runs
entirely on your own machine.

## How it works

`.github/workflows/docs-pages.yml` builds and deploys the site whenever `docs/`
changes on `main`. There is no static site generator and no build step — it
publishes plain HTML and Markdown, which keeps the documentation readable both
on the site and directly in the repository.

```
docs/
├── index.html          The landing page
├── _config.yml         Jekyll settings (theme, exclusions)
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

The site appears at `https://YOUR-USERNAME.github.io/mind-archive/`.

The workflow needs `pages: write` and `id-token: write` permissions, which are
already declared in `docs-pages.yml`.

## Working on the site locally

The plain HTML page opens directly in a browser:

```bash
# any static server will do
python -m http.server 8080 --directory docs
```

To preview exactly what GitHub renders, including the Markdown pages, run
Jekyll:

```bash
cd docs
bundle exec jekyll serve
```

Jekyll is not required to contribute. If you are only editing Markdown, the
GitHub preview is close enough.

## Writing for the documentation site

Same rule as everywhere else in this project: **write for humans.** Short
sentences, plain words, concrete examples. The documentation is part of the
product, not an afterthought.

Keep it accurate. If behaviour changes, the documentation changes in the same
pull request.

## A note on the custom domain

`mindarchive.app` is the intended eventual home. To use it, add a `CNAME` file
containing the domain to `docs/`, and point a `CNAME` DNS record at
`YOUR-USERNAME.github.io`. Not configured yet.
