# Prompts

The instruction given during this session. Abridged — it was a structured brief.

---

**1.** *("Reconcile Development / Git / SSH Documentation".)* Reconcile the
project's development and setup documentation, covering Windows + WSL2, the
VS Code + WSL workflow, Git and GitHub setup, SSH authentication, **GitHub SSH
over port 443**, remote configuration, the normal Git workflow, troubleshooting,
and the then-untracked `docs/development/GIT_SSH_SETUP.md`.

Inspect before changing. Avoid duplicating instructions that already exist. Use a
practical structure rather than many tiny documents, and **preserve existing
canonical documents where they already serve the purpose well** — do not rename
or split files merely to match a suggested tree.

On the Git/SSH document: incorporate it if technically useful; generalise
anything user-specific while keeping the port-443 solution; and keep it free of
personal network details, private addresses, credentials, keys or anything
specific to one developer's environment.

Preserve the approved domain architecture — `mindarchive.narainsagar.com` for the
application, `api.` for the API, `docs.` for the documentation site, and the
GitHub Pages URL — **without configuring DNS, Pages, hosting or deployment.**

Boundaries: no commit, no push, no public repository, no GitHub settings, no
visibility change, no deploy, no VPS, no DNS or TLS, no history rewriting, and no
exposure of project memory.
