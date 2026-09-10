---
title: Deployment
---

# Deployment

How Mind Archive gets published, and what deliberately is not published.

**What ships where:**

| | Where | Why |
|---|---|---|
| Source code | A public GitHub repository | Source-available. People should be able to read what they run. |
| Documentation site | GitHub Pages, from `docs/` | Static. No backend needed. |
| The application | **Nowhere.** People run it themselves | It is local-first. A hosted copy would defeat the point. |
| A public demo | **Not yet — see below** | The API has no authentication. |

---

## Before the first push

### 1. Identity — already done

`project.json` is the single source of truth for who owns this repository, and
it now holds real values:

```json
"github":    { "username": "RootedGlobal", "repository": "mindarchive" },
"site":      { "domain": "mindarchive.rootedglobal.co", "useCustomDomain": false }
```

`scripts/set_identity.py` propagated them into `LICENSE`, `README.md`,
`CHANGELOG.md`, the docs and the workflows. Re-run it after any change here:

```bash
python scripts/set_identity.py --check   # show what would change
python scripts/set_identity.py           # apply it
```

**Check its work.** It rewrites `mind-archive` to `mindarchive` across the whole
repository, which reaches further than URLs — the first run also renamed the
inbox ledger file, the export filename prefix, temporary directory prefixes and
both `container_name` values. All harmless here, but read the diff rather than
committing it unseen.

It does **not** manage `homepage` in `apps/web/package.json` or `repositoryUrl`
in `apps/web/src/support.ts`. Both are set by hand and are currently:

```
homepage       https://rootedglobal.github.io/mindarchive
repositoryUrl  https://github.com/RootedGlobal/mindarchive
```

### 2. Confirm your git identity is set

Set per-repository, not globally, so it does not leak into your other projects
(decision D-015):

```bash
git config user.name  "Your Name"
git config user.email "you@example.com"
```

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

- **`docs/project-memory/` will be public.** Session records, decisions and the
  prompts that produced them. It is excluded from the published *website* by
  `docs/_config.yml`, but anyone browsing the repository can read it. This was a
  deliberate choice — for a source-available project the reasoning is the
  interesting part.
- **Your email address will be public.** It is in `project.json` and in
  `apps/web/src/support.ts`, where it is the contact for commercial licences.

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
git remote add origin https://github.com/RootedGlobal/mindarchive.git
git branch -M main
git push -u origin main
```

If you use SSH instead:

```bash
git remote add origin git@github.com:YOUR-USERNAME/mindarchive.git
```

Check it took:

```bash
git remote -v
git log --oneline -5
```

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
- **The documentation links resolve.** Jekyll renders `PRODUCT.md` as
  `PRODUCT.html`, but only because every `.md` in `docs/` has YAML front matter.
  If you add a page without it, its link will 404. See
  [GITHUB_PAGES.md](GITHUB_PAGES.html).
- A documentation page has the same header and footer as the landing page.
- `docs/project-memory/` is **not** reachable on the site. It is excluded in
  `docs/_config.yml`.

> **Do not check any of this with `python -m http.server`.** It runs no Jekyll,
> so no `.md` becomes `.html` and every documentation link 404s whether the site
> is correct or not. `GITHUB_PAGES.md` has a Docker one-liner that builds the
> real thing.

---

## A custom domain

`mindarchive.app` is the intended home. Not configured yet.

1. Create `docs/CNAME` containing exactly one line:

   ```
   mindarchive.app
   ```

2. DNS, at your registrar:

   **Apex domain** (`mindarchive.app`) — four `A` records:

   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```

   **Subdomain** (`www.mindarchive.app`) — one `CNAME` record pointing at
   `YOUR-USERNAME.github.io`.

   Use the apex or the subdomain as the primary, not both as equals — pick one
   and redirect the other.

3. **Settings → Pages → Custom domain**, enter it, and tick **Enforce HTTPS**
   once the certificate is issued. That can take up to an hour.

4. Set `site.useCustomDomain` to `true` in `project.json`.

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
[BACKLOG.md](BACKLOG.md):

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
