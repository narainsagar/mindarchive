# Contributing to Mind Archive

Thank you for considering it. Mind Archive is meant to be a project one person
can understand and many people can improve.

You should be able to clone, install, run, understand, modify and test it
without any private credentials. If you cannot, that is a bug — please tell us.

## Before anything else: outside code is not being accepted yet

Mind Archive is **source-available, not open source** — free for noncommercial
use under [PolyForm Noncommercial 1.0.0](LICENSE), with commercial licences sold
separately. See [LICENSING.md](LICENSING.md).

That means contributed code has to be includable in commercially licensed
releases, which requires a **Contributor Licence Agreement**. The CLA does not
exist yet, so pull requests from outside the project cannot be merged at this
stage. Opening one before then risks wasting your time, which we would rather
avoid.

**What is very welcome right now:** bug reports, feature ideas, documentation
corrections, questions that reveal unclear docs, and testing on platforms we
cannot reach. Open an issue.

The rest of this document describes how contribution will work once the CLA is
in place, and applies today to anyone working on the project directly.

## Before you start

Read [AGENTS.md](AGENTS.md). It is the canonical working guide for this
repository and it applies to humans and AI coding agents alike — the read
order, the working method, and the definition of done.

Then get it running: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## What we are looking for

Good contributions are small, focused and finished. A pull request that fixes
one thing completely — with a test and updated documentation — is worth far
more than a large one that touches everything.

Especially welcome:

- Importers for AI providers we do not support yet
- Bugs, particularly around malformed or hostile import files
- Accessibility improvements
- Documentation that was wrong, unclear, or out of date
- Platform fixes for Windows, WSL2, Linux and macOS

Please open an issue before starting anything large, so nobody duplicates work.

## The principles your change has to respect

These are not negotiable, because they are the product:

- **Local first.** Nothing may require a network connection to work.
- **Privacy first.** Nothing leaves the user's machine without explicit,
  deliberate configuration. No telemetry, ever.
- **The user owns their data.** Content stays human-readable on the filesystem.
  SQLite indexes it; SQLite never owns it.
- **No provider lock-in.** Provider-specific code lives behind an adapter. Core
  code never imports it.
- **Simple over clever.** If a reviewer has to work hard to follow it,
  simplify it.
- **Light mode is the default; dark mode must keep working.**
- **Write for humans.** "Import archive", not "Initialize ingestion pipeline".

## Making a change

1. **Open an issue first** for anything non-trivial, so nobody duplicates work
   and the approach can be agreed before you spend time on it.
2. Fork and branch from `main`. One topic per branch.
3. Make the smallest coherent change that fully solves the problem.
4. Add or update tests.
5. **Iterate however suits you.** Nothing forces you to run checks while you
   work — no pre-commit hook, no watcher. Run what is useful when it is useful:

   ```bash
   python scripts/dev.py test backend
   python scripts/dev.py lint
   python scripts/dev.py format --fix
   ```

6. Update the documentation your change affects. Documentation is part of the
   implementation, not a follow-up.
7. If you changed architecture, add a numbered entry to
   [project-memory/DECISIONS.md](project-memory/DECISIONS.md).
8. **Before you push, run the full gate and fix what it finds:**

   ```bash
   python scripts/dev.py verify
   ```

9. Review your own diff. Then open the pull request.

CI runs the same checks `verify` does, so a green local run should mean a green
pull request.

## Commit messages

```
feat:     a new capability
fix:      a bug fix
docs:     documentation only
refactor: no behaviour change
test:     tests only
chore:    tooling, config, housekeeping
```

For example:

```
feat: add ChatGPT archive importer
fix: handle malformed conversation metadata
docs: update WSL development guide
```

## Pull requests

Describe what changed and why. Mention anything a reviewer should look at
carefully — especially path handling, file parsing, or a new dependency.

Confirm before opening it:

- [ ] Tests and checks pass locally
- [ ] Documentation updated
- [ ] No secret, `.env`, database file or personal archive in the diff
- [ ] Any new dependency justified in one sentence
- [ ] Scope limited to the problem described

CI runs the same checks on every pull request.

## Writing a blog post

The blog lives on the documentation site, in `docs/_posts/`. Jekyll builds it —
there is no separate blog application, and nothing to install.

Start by copying the template:

```bash
cp docs/_drafts/TEMPLATE.md docs/_posts/2026-01-31-a-short-slug.md
```

The template covers front matter, house style and the rules about checkable
claims. Two things it is worth repeating here:

- **Front matter is not optional.** Jekyll copies Markdown without it straight
  through, and the post silently never appears. This has already broken this
  site once (decision D-033).
- **Preview by building the site**, not with `python -m http.server`, which runs
  no Jekyll and cannot tell a correct site from a broken one. The command is in
  [docs/GITHUB_PAGES.md](docs/GITHUB_PAGES.md).

### A post is not required with a pull request

Write one when a change is worth explaining to someone outside the project — a
new importer, a decision that changed direction, something that will surprise
people. Most changes do not need one, and a blog filling up with routine notes
is worse than a blog that stays quiet.

### On drafting posts with AI

Draft a post however you like, including with an AI assistant, and including
from the session records in `project-memory/sessions/`, which already
capture what changed and why.

**Nothing is published without a person approving it.** No automation posts to
this blog. Generated text produces volume rather than value, and a product whose
whole argument is that it can be inspected and trusted cannot have its public
writing appear unread. If an assistant drafted it, you are still the author, and
the accuracy of every claim in it is yours.

> As with the rest of this document, this applies today to anyone working on the
> project directly, and to outside contributors once the CLA is in place.

## Adding a dependency

Every dependency is a long-term maintenance cost and a security surface. Before
adding one, ask whether twenty lines of ordinary code would do instead.

If you still need it, say in the pull request what it does, why the standard
library or existing dependencies are not enough, and how actively it is
maintained.

## Licensing of contributions

Once the CLA exists, contributors will be asked to sign it before their first
merge. It grants the rights needed to include contributed work in commercially
licensed releases, while leaving contributors their own copyright.

This is the standard arrangement for a project that sells commercial licences.
Without it, contributed code could not legally be included in what is sold.

## Security

If you have found a vulnerability, please do not open a public issue. See
[docs/SECURITY.md](docs/SECURITY.md).

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions

Open an issue. A question that needed asking usually means the documentation
could be better, and that is useful to know.
