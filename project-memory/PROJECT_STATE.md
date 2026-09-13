# Project State

**What actually exists right now.** Read this before starting any work.

If this file and the code disagree, the code is right and this file needs
updating. Keep it honest — it is the file people trust to know where things
stand.

**Last updated:** 2026-09-08 · **Milestone 5 complete** · Version 0.1.0

> **Workflow note.** Checks do not run on every change. Verification is
> developer-controlled and required at milestone boundaries, pull requests and
> releases — run `python scripts/dev.py verify` (decision D-018). Containers are
> disposable; `python scripts/dev.py down` when finished (D-019).

---

## In one paragraph

Mind Archive imports a ChatGPT export, stores it as readable Markdown and JSON
on your own disk, and lets you browse, search and read it. That is a whole
useful loop: the product does its core job.

Getting an export out of ChatGPT takes days, so importing one takes no effort:
drop it into `data/inbox/` and it imports itself. Re-importing reports what is
genuinely new and rewrites nothing else.

You can tag conversations and filter by tag. Tags are stored in your archive
files, not the database, so they survive anything happening to the index and
travel with the folder.

It imports from ChatGPT and Claude, and exports the whole archive as a zip of
ordinary files that need nothing to read them.

What it cannot do yet: edit or delete conversations from the interface, import
attachments, or store anything anywhere but your own disk. Cloud is Milestone 6
and is off by default when it arrives.

Underneath: a FastAPI backend, a React + TypeScript + Vite frontend, SQLite with
FTS5 as a rebuildable index, Docker Compose, CI, and complete project memory.

Appearance is two remembered choices in the header (D-029): a palette — Light
minimal by default, Warm paper, or Ink & violet — and a theme of Light, Dark or
System, which keeps following the computer for as long as it is selected.

The workspace is still one page and one view. Import opens in a dialog rather
than sitting below the archive, and the sticky header links to five sections —
Archive, Coming next, Status, Support, Contribute — with a Back to top link in
the footer. In-page anchors, not routes (D-030, D-031).

There are three ways back to the top and they all go to `#top` (D-045): the
brand in the sticky header, the footer link, and a floating link that appears
once you have scrolled a screen and hides again at the top. The brand was a
link that did nothing at all until 2026-09-11 — it cancelled its own click.

Support and Contribute explain donations and commercial licensing. **Donation
links are not configured yet**: every URL in `apps/web/src/support.ts` ships
blank on purpose and unset ones are not rendered, so nothing shows a dead link.
Fill that file in to turn them on.

## Publication

Decided but **not yet done** (D-032): a public GitHub repository named
`mindarchive`, with Pages serving `docs/`. The application is not hosted
anywhere and there is no public demo — the API has no authentication by design,
so a public instance would expose one shared archive to every visitor.

Everything is prepared and committed. Identity is set — the project belongs to
the **narainsagar** organisation as **`mindarchive`**, with
`mindarchive.narainsagar.com` reserved as a future custom domain
(`useCustomDomain` is still `false`, so URLs use
`narainsagar.github.io/mindarchive`).

Still outstanding:

- **Nothing is pushed.** The repository name is **`mindarchive`**, without a
  hyphen — that is what `project.json` says and what all 20 published URLs use.
  On 2026-09-12 `origin` was still `git@github.com:narainsagar/mind-archive.git`;
  the maintainer is renaming the GitHub repository and pointing the remote at
  `narainsagar/mindarchive` to match. **Check `git remote -v` against
  `project.json` before the first push** — if the two ever disagree again, the
  clone command in the launch post and the Source link inside the application
  are the first things to break.
- `narainsagar` is an organisation, so whoever pushes needs membership with write
  access. GitHub password authentication was removed in 2021; a personal access
  token or an SSH key is required.
- The CI and Pages workflows have still never run against a live repository.
- `scripts/set_identity.py` **replaces the `narainsagar` placeholder and the
  copyright line, in the 16 files in its `TARGETS` list — nothing else.** It
  cannot rename one real name to another, because it matches the placeholder
  rather than the current value. `homepage` in `apps/web/package.json`,
  `repositoryUrl` in `apps/web/src/support.ts`, `contact_email` in
  `docs/_data/support.yml`, `docs/documentation.html`, `docs/_posts/` and
  `docs/DEPLOYMENT.md` are all maintained by hand. The list is in
  [`docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).

Steps are in [`docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).

## The documentation site

34 routes, all of them working on `localhost:4000` before anything is pushed —
987 internal links across 33 built pages resolve (D-043).

**Eleven of those pages are generated, not written.** `LICENSING.md`, `LICENSE`,
`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `AGENTS.md`, `.env.example` and four
documents from `project-memory/` become pages via
`scripts/sync_site_pages.py`. The output lands in `docs/reference/` and is
**git-ignored** — never edit it, edit the canonical file.

```bash
python scripts/dev.py docs              # generate, check links, serve on :4000
python scripts/sync_site_pages.py --list
```

Bare `jekyll serve` now shows an incomplete site, because the generated pages are
not in the repository. `dev.py verify` runs the generator and
`scripts/check_site_links.py`, which walks every internal link — a standard
D-036 required and nothing had automated. **It also builds the site with
Jekyll**, because a page that will not parse passes every other check and fails
in the Pages workflow instead, where the failure is a failed deployment (D-043).

Still not published: `PROJECT_STATE.md`, `SESSION_LOG.md`, `MEMORY_INDEX.md` and
the session records.

**The contact address is `mindarchive@narainsagar.com`**, on a domain that already
exists — the earlier plan of an address at `mindarchive.app` would have bounced,
since that domain has no DNS. It reaches the project for commercial licensing
and everything else.

It is defined **twice, unavoidably**: `contact_email` in
`docs/_data/support.yml` for the site, and `contactEmail` in
`apps/web/src/support.ts` for the application, because Jekyll cannot read a
TypeScript file. Change both. Nothing else hardcodes it — the site pages and the
footer read the data file, and `App.test.tsx` asserts against the configured
value rather than a copy of it.

`project.json` is **not** one of those places, despite an earlier note saying so:
its `author.email` is the git commit identity that `scripts/set_identity.py`
writes into the local git config, not a published contact address.

## What runs

```bash
cp .env.example .env
docker compose up --build
```

- Interface — http://localhost:5173
- API — http://localhost:8000, docs at `/docs`
- Archive folder — `./data/archive`, git-ignored

Verified working on 2026-09-09: both containers start, the API reports healthy,
the interface loads and displays live backend status. The Compose project name
is pinned to `mindarchive`, so renaming the checkout directory no longer breaks
`up` with a container name conflict.

## What is implemented

**Backend** — `apps/api`

| | |
|---|---|
| `main.py` | FastAPI app, lifespan, CORS restricted to the local frontend |
| `config.py` | Typed settings via pydantic-settings; finds the repo root by marker, not by counting parents |
| `events.py` | In-process event bus; a failing handler cannot break the publisher |
| `paths.py` | Traversal-safe path joining and filename cleaning. Now genuinely exercised: conversation titles become folder names through it |
| `models.py` | `Conversation` and `Message` — the archive's own model, shaped like no provider's export |
| `importers/__init__.py` | The registry. Core code asks it which adapter can read a file |
| `importers/base.py` | The `Importer` protocol: `detect()`, `validate()`, `parse()` |
| `importers/zip_safety.py` | Reading archives someone else produced: zip slip, zip bombs, size caps |
| `importers/chatgpt.py` | The ChatGPT adapter, including the branching `mapping` tree |
| `importers/claude.py` | The Claude adapter: a flat message list, ISO timestamps, content blocks |
| `importers/reading.py` | Untrusted-JSON coercion, zip member loading, and shard resolution from `export_manifest.json`, shared by both |
| `routes/export.py` | `GET /api/export` — the archive folder, zipped, plus a README |
| `archive/writer.py` | Conversations to `conversation.md` + `metadata.json`, one folder each |
| `archive/reader.py` | ... and back off disk, tolerating folders that are not conversations |
| `index/schema.py` | The SQLite schema. Derived, droppable, rebuildable |
| `index/indexer.py` | Building the index by reading the archive |
| `index/search.py` | FTS5 queries, and rewriting whatever someone types |
| `routes/health.py` | `GET /api/health` |
| `routes/config.py` | `GET /api/config` — non-sensitive config only, with a test enforcing that |
| `routes/import_.py` | `GET /api/importers`, `POST /api/import` |
| `routes/conversations.py` | `GET /api/conversations`, `GET /api/conversations/{path}`, `POST /api/index/rebuild` |
| `inbox.py` | The watched folder. Owned and tidied by default; a folder you chose is read but never rearranged |
| `models.py` `clean_tags` | Tidies what people type: trims, collapses, dedupes case-insensitively keeping the first spelling |

**Frontend** — `apps/web`

Single-page workspace, minimal header, no router and no sidebar. Light default,
dark toggle, system preference honoured, choice persisted to `localStorage` with
every access wrapped in try/catch.

An archive panel with a debounced search box, results with marked snippets, and
paging; opening a conversation renders its Markdown in place. An import panel
that explains where to find a ChatGPT export and reports what could not be read.
A status panel showing backend health, archive location and cloud state.

Plain CSS custom properties, no UI framework. One rendering dependency,
`react-markdown`, chosen because it builds React elements rather than setting
HTML (D-021).

**Project**

Docker + Compose · GitHub Actions CI (backend matrix on 3.11/3.12, frontend,
project-memory check, committed-secrets check) · GitHub Pages foundation ·
`.gitignore` · `.gitattributes` · `.env.example` · issue and PR templates ·
`project.json` + `scripts/set_identity.py` · session memory via
`scripts/session.py`.

## What is deliberately absent

No tags, projects or organisation. No editing or deleting conversations from
the interface. No cloud or sync code of any kind. No authentication. No settings
beyond the theme toggle and read-only configuration display.

Within the importer, deliberately not done: attachments and images (recorded as
placeholders in the Markdown, not copied), and abandoned conversation branches
from edits and regenerations.

Within search: no phrase search, `OR` or negation — a deliberate trade so that
nothing typed into the box can produce a syntax error (D-022). No per-message
structure in the reading view, because the whole file is rendered (D-020).

Each belongs to a later milestone. See [MILESTONES.md](MILESTONES.md).

## Verified on 2026-09-08

Everything below was actually run, not inspected.

| Check | Result |
|---|---|
| Backend tests (`pytest`) | **295 passed** |
| Backend lint (`ruff check`) | **passed** |
| Backend formatting (`ruff format --check`) | **passed**, 34 files |
| Backend types (`mypy src`, strict) | **passed**, 22 files, no issues |
| Frontend tests (`vitest`) | **66 passed** |
| Frontend types (`tsc --noEmit`) | **passed** |
| Frontend lint (`eslint`) | **passed** |
| Frontend build (`vite build`) | **passed** — 147.84 kB JS, 47.73 kB gzipped |
| Docker images | both build |
| `docker compose up` | both containers start, API healthy |
| `GET /api/health` | 200, correct payload |
| `GET /api/config` | 200, cloud disabled, local storage |
| Web interface | HTTP 200, correct title |
| `git check-ignore data/ .env local/` | all correctly ignored |
| `scripts/session.py check` | passes |
| **End-to-end import** | a synthetic export with a normal, an awkward and a broken conversation uploaded through `POST /api/import`: 2 imported, 1 skipped and reported, correct files on disk |
| **End-to-end browse** | list, search, prefix search, read one, rebuild the index — all against the running stack |
| **End-to-end hostile input** | `C++`, `NEAR(`, `"`, `a AND OR b` all return results rather than errors; URL-encoded traversal returns 404 |

Bugs found by running things rather than reading them, and fixed. In Milestone 1:
`parents[4]` failed inside the container, `vite.config.ts` had no `node` types,
and Vitest 2 pulled a second copy of Vite. In Milestone 2: a hostile archive was
reported as merely "not recognised", the interface showed the container's path
rather than the user's, and an unwritable archive folder produced a raw 500.

## Environment reality

The development machine has **Python 3.7.9 on Windows and 3.8.10 in WSL2** —
both end-of-life and unsuitable for the backend. Docker is therefore the primary
supported path (decision D-006). Node 24 in WSL2 is fine for frontend work.

All verification above was run inside Docker for this reason.

## Known gaps

- **`project.json` still holds placeholders.** `github.username` and
  `copyright.holder` are unset. Run `python scripts/set_identity.py --git`
  after filling them in.
- **No git remote** — deliberate, decision D-017. CI and Pages workflows are
  committed but have never run against a live GitHub repository.
- **No `package-lock.json`.** The Dockerfile falls back to `npm install`. CI
  expects a lockfile for caching; commit one on the first native `npm install`.
- **The frontend Docker image runs the dev server**, not a production build.
  Fine locally; a production image is Milestone 7.
- **The index is rebuilt only when it is empty**, not when the archive has
  changed underneath it. Editing files by hand needs
  `POST /api/index/rebuild`, though reading a conversation always comes from
  disk so edits are visible immediately.
- **Paging is Previous/Next, not virtualised.** Fine for thousands of
  conversations; revisit if anyone has hundreds of thousands.
- **Import speed is bounded by the filesystem, not the code.** 2,000
  conversations take 4.7s on a native filesystem and 127s across a Windows
  Docker bind mount (R-005). Do not optimise the importer against the second
  number.
- **The Claude importer has never seen a real Claude export.** Written from
  Anthropic's documented format and third-party parsers. The only real Claude
  file available was the download manifest, whose links are single-use, so the
  conversation path is still covered by synthetic fixtures alone (D-042). It may
  well shard the way ChatGPT's does — check the first real one against it.
- **Nothing since Milestone 3 has been clicked through in a browser.** 254 backend and
  64 frontend tests pass, but the tag interface has never been used by a
  person. The blocker is the development environment, not the code.
- **No progress reporting during a long import.** It runs on a background
  thread so nothing blocks, but the interface says nothing while it works.
- **The ChatGPT importer has now been run against a real export** — 204
  conversations, 2,866 messages, no problems reported (D-042). That export
  turned out not to contain `conversations.json` at all; it shards it, which the
  importer had no idea about until it was tried. Two providers remain the
  limit: everything else is still synthetic.
- **The browser script's output has still never been compared** against an
  official export, and is now more doubtful rather than less: it produces one
  `conversations.json` while the official export shards. Both shapes are
  handled; only one has been seen.
- **Attachments are not imported** — images and files appear as placeholders in
  the Markdown.

## Licence and repository visibility

**Proprietary — all rights reserved** (D-046, 2026-09-12). Not open source, not
source-available, no licence granted to anyone, and nothing for sale. `LICENSE`
is a copyright notice; `LICENSING.md` is the plain-language version. The
withdrawn PolyForm licence is recorded in D-016, which is kept for its reasoning.

**This repository is private and stays private.** A separate public repository
will be created later, with clean history, populated from an explicit allowlist —
never by copying this one and deleting things. `project-memory/`, `prompts/`,
`.claude/`, the session records and this file are never published.

**The publisher exists**: `scripts/publish_public.py --check | --list | --build DIR`
(D-048). It copies an allowlist of 135 files, screens every one for secrets and
denied paths, never runs `git`, and refuses to write inside this repository or
over anything containing `.git`.

**The generated tree is internally coherent.** It generates its own five pages,
resolves 27 routes with no broken links, and builds. The private tree generates
eleven and resolves 35. One `docs/` serves both: the page list is split between
the script and `project-memory/site_pages.json`, and links to private-only
routes are wrapped in `{% raw %}{% if site.data.private_pages %}{% endraw %}`,
whose data file is not published. Nothing is edited on its way out.

**AI-assisted development is disclosed at a high level**, in `README.md`, and the
machinery behind it is not: no prompts, no agent rules, no project memory, no
session records, no internal research.

Outside contributions cannot be accepted while no licensing arrangement exists.

## Next step

**Run it and click through it.** Two milestones have now shipped without anyone
using them. `docs/TRY_IT.md` is the walkthrough; PowerShell avoids the WSL
problems that have blocked it so far.

**Verify against a real ChatGPT export** placed in `local/`, and fix whatever
genuine data reveals. Synthetic fixtures are thorough, but they were written by
the same mind that wrote the parser, so they cannot find an assumption that is
simply wrong. This has been outstanding since Milestone 2 and is now the highest
value check available.

Then **Milestone 4 — projects, tags and metadata**: organising the archive once
there is enough in it to need organising.
