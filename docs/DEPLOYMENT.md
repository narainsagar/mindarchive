---
title: Deployment
permalink: /deployment/
---

# Deployment

How Mind Archive gets published, and what deliberately is not published.

**What ships where:**

| | Where | Why |
|---|---|---|
| This repository | **Stays private, permanently** | It is the development workspace: project memory, session records, prompts (D-046). |
| Approved source and docs | A **separate** public repository, created later with clean history | Nothing from this history is published. Proprietary, all rights reserved. |
| Documentation site | GitHub Pages, from the public repository's `docs/` | Static. No backend needed. |
| The application | **Nowhere.** People run it themselves | It is local-first. A hosted copy would defeat the point. |
| A public demo | **Not yet — see below** | The API has no authentication. |

---

## Before the first push

### 1. Identity — already done

`project.json` is the single source of truth for who owns this repository, and
it now holds real values:

```json
"github":    { "username": "narainsagar", "repository": "mindarchive" },
"site":      { "domain": "mindarchive.narainsagar.com", "useCustomDomain": false }
```

`scripts/set_identity.py` propagated them into `LICENSE`, `README.md`,
`CHANGELOG.md`, the docs and the workflows. Re-run it after any change here:

```bash
python scripts/set_identity.py --check   # show what would change
python scripts/set_identity.py           # apply it
```

**What it actually replaces**, so you know what it cannot do for you: the literal
`YOUR-USERNAME` placeholder, the two URL forms built from it
(`github.com/YOUR-USERNAME/mindarchive` and
`YOUR-USERNAME.github.io/mindarchive`), and the `Copyright (c) YEAR HOLDER` line
— in the 16 files listed in `TARGETS` at the top of the script, and nowhere else.

**It does not rename anything.** Changing `repository` in `project.json` from one
real name to another rewrites no existing URL, because the script matches the
placeholder rather than the current value. A rename is a manual pass, and these
are the places it has to reach:

```
apps/web/package.json        homepage
apps/web/src/support.ts      repositoryUrl — the Source link inside the app
docs/_data/support.yml       contact_email
docs/documentation.html      and docs/index.html
docs/_posts/                 the launch post's git clone line
docs/DEPLOYMENT.md           this file — it is not in TARGETS either
```

Read the diff of any run rather than committing it unseen.

### 2. Confirm your git identity and authentication

Identity is set per repository, not globally, so it does not leak into your
other projects (decision D-015):

```bash
git config user.name && git config user.email
```

Authentication is SSH, because the repository is private.
[Git and SSH setup]({{ '/git-ssh/' | relative_url }}) has the whole of it —
keys, the agent, the remote, and what to do on a network that blocks port 22.

### 3. Run the gate

Never push red:

```bash
python scripts/dev.py verify
python scripts/session.py check
```

### 4. Check nothing private is going out

This is a public repository. Once pushed, it is public permanently — assume
anything committed has been copied by someone.

```bash
# Must return nothing.
git ls-files | grep -Ei "\.env$|\.pem$|\.key$|secret|credential|conversations\.json|\.zip$"

# Confirm your data and scratch folders really are ignored.
git check-ignore -v data/ tmp/ .env

# Read what is actually about to be published.
git status --short
```

Two things worth knowing before you push:

- **`project-memory/` is never published.** Session records, decisions, research
  and the prompts that produced them stay in this private repository (D-046).
  Publishing happens from an explicit allowlist into a separate repository, so
  nothing here reaches the public one by default.
- **Your email address is public on the site.** `contact_email` in
  `docs/_data/support.yml` and `contactEmail` in `apps/web/src/support.ts` are
  printed on every page and in the application (D-044).
- **Commit authorship is permanent.** Every commit in this repository carries the
  author identity in `project.json`; it is one reason this history is not the
  history that gets published.

---

## Creating the repository

**Name it `mindarchive`** — that matches `project.json` and the URLs already
written into the documentation. If you name it something else, change
`project.json` and re-run `set_identity.py`.

### With the web interface

1. <https://github.com/new>
2. **Repository name:** `mindarchive`
3. **Visibility:** Public
4. **Do not** add a README, `.gitignore` or licence — they already exist here,
   and adding them creates a conflicting first commit.
5. Create repository.

### Or with the `gh` CLI

`gh` is not currently installed on this machine. If you install it
(`sudo apt install gh`, then `gh auth login`):

```bash
gh repo create mindarchive --public --source=. --remote=origin --push
```

That does the creation, the remote and the first push in one step — skip the
next section if you use it.

---

## The first push

```bash
git remote add origin git@github.com:narainsagar/mindarchive.git
git branch -M main
git push -u origin main
```

Check it took, and that the remote agrees with `project.json`:

```bash
git remote -v
git log --oneline -5
```

SSH rather than HTTPS because the repository is private; keys, the agent and the
port-443 route are in
[Git and SSH setup]({{ '/git-ssh/' | relative_url }}).

---

## Turning on GitHub Pages

The workflow is already written and committed — `.github/workflows/docs-pages.yml`.
It has simply never run, because there was no remote.

1. **Settings → Pages**
2. **Source: GitHub Actions**

   Not "Deploy from a branch". The workflow uses the Actions deployment path
   and declares the `pages: write` and `id-token: write` permissions it needs.
   Choosing the branch option will fight it.
3. **Actions → Documentation site → Run workflow**

   The first run usually needs this. The workflow only triggers on pushes that
   touch `docs/**`, so if your first push happens to contain no `docs/` change
   it will sit idle. It also has `workflow_dispatch` for exactly this reason.

The site appears at:

```
https://YOUR-USERNAME.github.io/mindarchive/
```

Give it a minute or two. **Settings → Pages** shows the live URL and the last
deployment once it succeeds.

### What to expect on that first push

- **CI** (`ci.yml`) runs backend lint, format, types and tests; frontend lint,
  types, tests and build; the project-memory check; and a committed-secrets
  check. It has never run on GitHub before — a first-run failure is more likely
  to be a runner difference than a real regression, so read the log before
  assuming the worst.
- **Documentation site** (`docs-pages.yml`) builds `docs/` with Jekyll and
  deploys it.

### Checking it worked

- The landing page loads, and the palette and theme controls in the header work
  — the same three palettes as the application, and Light / Dark / System.
- **The documentation links resolve.** Jekyll renders `PRODUCT.md` at
  `/product/`, but only because it has YAML front matter *and* an explicit
  `permalink`. A page missing either will 404. See
  [the documentation-site notes]({{ '/github-pages/' | relative_url }}).
- A documentation page has the same header and footer as the landing page.
- `project-memory/` is **not** reachable on the site. It lives outside `docs/`,
  so Jekyll never sees it — the site cannot publish what it cannot reach.

> **Do not check any of this with `python -m http.server`.** It runs no Jekyll,
> so no `.md` becomes `.html` and every documentation link 404s whether the site
> is correct or not. `GITHUB_PAGES.md` has a Docker one-liner that builds the
> real thing.

---

## The domain names

Four names, three of them subdomains of one apex nobody has to buy again
(**D-047**). **None of this is configured yet** — no DNS record exists, and no
certificate has been issued.

| Name | Serves | Where it runs |
|---|---|---|
| `mindarchive.narainsagar.com` | The application | A private VPS instance |
| `api.mindarchive.narainsagar.com` | The API | The same VPS, behind the same proxy |
| `docs.mindarchive.narainsagar.com` | The documentation site | GitHub Pages, custom domain |
| `narainsagar.github.io/mindarchive/` | The same site, unbranded | GitHub Pages, default URL |

The last two are one deployment with two addresses; the Pages URL keeps working
whatever happens to DNS, which is why `_config.yml` leaves `baseurl` unset and
lets the Pages build inject it.

**When the documentation site gets its custom domain:**

1. `docs/CNAME`, one line: `docs.mindarchive.narainsagar.com`
2. A `CNAME` record at the registrar pointing that name at
   `narainsagar.github.io` — a subdomain, so no apex `A` records are needed.
3. **Settings → Pages → Custom domain**, then tick **Enforce HTTPS** once the
   certificate is issued, which can take up to an hour.
4. Set `site.useCustomDomain` to `true` in `project.json`.

The application's two names are a VPS and reverse-proxy matter, not a Pages one.
See [Hosting the application on a VPS](#hosting-the-application-on-a-vps) below,
and note what it says before you point a public name at anything.

---

## Hosting the application on a VPS

**Do not put the current application on a public address.**

This is not caution for its own sake. From `docs/SECURITY.md`:

> By default the API binds to localhost. Do not expose it to a network you do
> not control: there is no authentication, because it is a single-user local
> application.

A publicly reachable instance today would mean:

- **No authentication.** Every endpoint is open — import, read, tag, delete,
  export.
- **One shared archive.** Whatever any visitor imports, every other visitor can
  read and download. If someone uploads a real ChatGPT export, their private
  conversations become public.
- **Your legal problem.** Strangers' personal conversations sitting on your
  server carries real obligations.

For a product whose entire premise is that your conversations stay yours, that
is the exact failure it exists to prevent.

### What would have to exist first

A public demo is real work, not a deployment step. It is in
[BACKLOG.md]({{ '/backlog/' | relative_url }}):

1. **A read-only demo mode** — `MIND_ARCHIVE_DEMO=true` seeds a synthetic
   archive and refuses every write. Visitors search and read; nobody uploads.
2. **Authentication at the proxy**, even in demo mode, so the API is never
   directly reachable.
3. **TLS**, a real reverse proxy, and a production frontend image. The current
   web image runs the Vite dev server and is not suitable for anything public.
4. **A decision record** covering all of it, since it changes the security model
   the product is built on.

### If you host it for yourself only

Perfectly reasonable — a private instance on your own VPS, reachable only by
you:

- Keep `MIND_ARCHIVE_API_HOST` bound to localhost inside the box and reach it
  over an **SSH tunnel** or a private network (Tailscale, WireGuard). This is
  the safest option by a wide margin and needs no new code.
- If you must expose a port, put **HTTP basic auth and TLS** in front of it in
  nginx or Caddy, and set `MIND_ARCHIVE_CORS_ORIGINS` to your real origin —
  never `*`.
- Back up the archive folder. It is a bind mount of ordinary files, so any
  normal backup tool works.

---

## Releasing a version

Not automated yet — Milestone 7. For now:

1. Update `CHANGELOG.md`.
2. Bump `version` in `project.json` and run `python scripts/set_identity.py`.
3. `python scripts/dev.py verify`.
4. Tag: `git tag -a v0.1.0 -m "..."` and `git push --tags`.
5. Draft a GitHub release from the tag.
