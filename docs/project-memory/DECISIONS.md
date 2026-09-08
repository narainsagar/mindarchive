# Decisions

Numbered, dated architectural and product decisions. This is the authoritative
decision log for Mind Archive. `docs/DECISIONS.md` points here; do not keep two
lists.

Add a new decision rather than rewriting an old one. If a decision is reversed,
mark the original **Superseded** and link forward.

Status values: **Accepted** · **Superseded** · **Proposed**

---

## D-001 — Mind Archive is local-first and privacy-first
**Date:** 2026-09-08 · **Status:** Accepted

The application must be fully usable with no cloud account, no network access,
and no third-party service. All data lives on the user's own machine by default.

**Why:** This is the product's reason to exist. A personal AI archive that
depends on someone else's server reproduces the problem it is meant to solve.

**Consequences:** No feature may require the network to function. Cloud is an
optional adapter added later (Milestone 6), never a dependency.

---

## D-002 — Mind Archive is AI-provider agnostic
**Date:** 2026-09-08 · **Status:** Accepted

No AI provider may sit at the architectural centre. ChatGPT is the first
importer target only. Claude, Gemini, Qwen, OpenAI, Google AI Studio and local
models are all equal, later, pluggable targets.

**Why:** The archive must stay useful when the user changes providers. Vendor
lock-in is the failure mode we are designing against.

**Consequences:** Every provider-specific concern lives behind an `Importer`
adapter interface. Core code never imports provider-specific modules.

---

## D-003 — Stack: React + TypeScript + Vite, Python + FastAPI, SQLite
**Date:** 2026-09-08 · **Status:** Accepted

**Why:** All four are mainstream, well documented, easy for a single developer
to run locally, and easy for contributors to recognise. No exotic choices.

**Consequences:** Frontend and backend are separate applications under `apps/`.
Database access stays behind an interface so SQLite can be replaced later.

---

## D-004 — User data stays human-readable; SQLite holds only metadata
**Date:** 2026-09-08 · **Status:** Accepted

Archive content is stored as Markdown, JSON and plain text on the filesystem.
SQLite is used for indexing, search and application metadata — never as the only
home of the user's knowledge.

**Why:** Data portability. The user must be able to read, grep, back up and move
their archive with ordinary tools, even if Mind Archive disappears.

**Consequences:** Deleting the SQLite database must never destroy user content.
It must be rebuildable from the files on disk.

---

## D-005 — Monorepo layout: `apps/web` and `apps/api`
**Date:** 2026-09-08 · **Status:** Accepted

**Why:** One clone, one `docker compose up`, one CI workflow. A single developer
should not manage two repositories for a V1.

**Consequences:** Shared tooling at the root; each app owns its own dependency
manifest.

---

## D-006 — Docker is the primary supported path for the backend
**Date:** 2026-09-08 · **Status:** Accepted

Docker Compose is the documented, supported way to run Mind Archive. Native
development is supported but secondary.

**Why:** Discovered during the 2026-09-08 audit: the development machine has
Python 3.7.9 on Windows and Python 3.8.10 in WSL2. Both reached end-of-life
(3.8 in October 2024) and neither is a good host for a current FastAPI +
Pydantic v2 stack. Docker gives every contributor an identical, current runtime
regardless of what their host happens to have installed.

**Consequences:** `docker compose up --build` is the first-run instruction in
the README. Native setup is documented in `docs/DEVELOPMENT.md` with an explicit
Python 3.11+ prerequisite. See [RESEARCH.md](RESEARCH.md).

---

## D-007 — Python 3.11 is the minimum supported version
**Date:** 2026-09-08 · **Status:** Accepted

**Why:** 3.8 and 3.9 are end-of-life or near it. 3.11 is widely available, is a
significant performance step, and is comfortably supported by FastAPI and
Pydantic v2. Containers pin 3.12.

**Consequences:** `requires-python = ">=3.11"` in `pyproject.toml`. CI tests
against 3.11 and 3.12.

---

## D-008 — Plain CSS with custom properties; no UI framework
**Date:** 2026-09-08 · **Status:** Accepted

No Tailwind, Material UI, Chakra, Bootstrap or component library in V1. Theming
uses CSS custom properties on `:root`.

**Why:** The product rule is "must not look AI-generated" and "human readability
over visual novelty". Component libraries push interfaces toward a recognisable
generic look and add a large dependency for a UI that is currently one page.
Light/dark theming is four lines of CSS variables.

**Consequences:** Revisit only if the UI grows enough that hand-written CSS
becomes the bottleneck. Record a new decision if so.

---

## D-009 — Events are an in-process bus in V1
**Date:** 2026-09-08 · **Status:** Accepted

Event-driven design is a stated principle, so the extension point ships in
Milestone 1 — as a small synchronous in-process publish/subscribe helper, not a
message broker.

**Why:** The principle needs to be real in code so later milestones have
something to build on, but Redis, Kafka, Celery or RabbitMQ would be
infrastructure with no current requirement.

**Consequences:** Event names follow `noun.verb` (`archive.imported`,
`conversation.created`). Upgrade the transport only when an actual requirement
appears, and record a new decision then.

---

## D-010 — `docs/project-memory/` is the single project-memory system
**Date:** 2026-09-08 · **Status:** Accepted

**Why:** Two competing layouts were proposed during planning — a flat `docs/`
and a dedicated `docs/project-memory/`. Two memory systems means neither is
trusted. The dedicated folder separates *living product documentation* from
*decision history and project state*, which are different things with different
readers.

**Consequences:** `docs/DECISIONS.md` is a pointer to this file, not a second
log. `docs/` describes the product as it is; `docs/project-memory/` records how
it got that way and what is next.

---

## D-011 — Cloud is disabled by default and can never be silently enabled
**Date:** 2026-09-08 · **Status:** Accepted

Cloud storage and synchronisation are opt-in, configuration-driven, and off
unless the user explicitly turns them on.

**Why:** Privacy-first means no surprise uploads, ever.

**Consequences:** `MIND_ARCHIVE_CLOUD_ENABLED` defaults to `false`. The API
reports cloud status so the UI can state plainly where the user's data lives.
No cloud adapter is implemented before Milestone 6.

---

## D-012 — MIT License
**Date:** 2026-09-08 · **Status:** Superseded by D-016

Originally chosen for maximum permissiveness and minimal friction. Reversed the
same day, before any code was published, in favour of a source-available
licence. See D-016.

---

## D-016 — PolyForm Noncommercial 1.0.0, with commercial licences sold separately
**Date:** 2026-09-08 · **Status:** Accepted

Mind Archive is **source-available, not open source**. Free for any
noncommercial use under PolyForm Noncommercial 1.0.0. Commercial use requires a
separate paid licence.

**Why:** The project needs to be readable, inspectable and forkable — users are
trusting it with private conversations and should be able to verify what it does
with them. Source-available provides all of that. What it withholds is the right
for someone else to resell the work, which a permissive licence would grant.

**Why not both PolyForm and FSL, as originally requested:** the two cannot
coexist as alternatives. FSL permits commercial use except for building a
competing product, so it is strictly more permissive than PolyForm
Noncommercial. Offering a choice would mean every commercial user chose FSL and
the noncommercial terms never applied to anyone. What was actually wanted —
free noncommercial, paid commercial, negotiable beyond that — is PolyForm
Noncommercial plus a separate commercial licence, which is the pattern PolyForm
was designed for.

**Direction is one-way.** A licence can be relaxed later but never tightened:
any version published permissively stays permissive forever. Starting here keeps
both futures open. FSL, which auto-converts to MIT or Apache after two years,
is the most likely route if the project later moves toward open source.

**Consequences:** `LICENSE` holds the PolyForm text; `LICENSING.md` explains it
in plain language. `package.json` and `pyproject.toml` declare the licence as
`LicenseRef-PolyForm-Noncommercial-1.0.0` rather than an SPDX open-source
identifier. A Contributor Licence Agreement is required before accepting outside
contributions, because contributed code must be includable in commercially
licensed releases. Planned pricing is $49 per seat perpetual with one year of
updates; see `LICENSING.md` and `docs/BACKLOG.md`.

---

## D-017 — The repository stays local until there is something worth showing
**Date:** 2026-09-08 · **Status:** Accepted

No git remote is configured. The project is developed locally, with CI and Pages
workflows in place but dormant until a remote exists.

**Why:** At Milestone 1 there is a foundation and no product. Publishing now
would put scaffolding in front of the first visitors and spend the launch on
nothing. The workflows are written and committed so that adding a remote is the
only step required later.

**Consequences:** `.github/workflows/` and the Pages setup are untested against
a live GitHub repository. The `YOUR-USERNAME` placeholders in URLs are resolved
by `project.json` and `scripts/set_identity.py` when a remote is chosen.

---

## D-013 — `AGENTS.md` is the canonical cross-agent instruction file
**Date:** 2026-09-08 · **Status:** Accepted

`AGENTS.md` holds the instructions every AI agent and human contributor should
follow. `CLAUDE.md`, `GEMINI.md` and `QWEN.md` are thin pointers to it plus any
tool-specific notes.

**Why:** The repository must be handed to any agent — Claude, Gemini, Qwen,
Cursor, Copilot, Aider, OpenCode — or to a human, and each should understand the
project from the repository alone. Duplicating instructions per tool guarantees
drift.

**Consequences:** Substantive instruction changes go in `AGENTS.md`. Tool files
stay short.

---

## D-014 — Light mode is the default; dark mode is a simple toggle
**Date:** 2026-09-08 · **Status:** Accepted

**Why:** Stated product requirement. The application should feel like a calm
document archive, and light is the appropriate default for a reading surface.

**Consequences:** The theme choice persists in `localStorage`. With no stored
choice, the system preference is honoured, falling back to light.

---

## D-015 — Default branch is `main`; git identity is set per-repository
**Date:** 2026-09-08 · **Status:** Accepted

**Why:** `main` matches GitHub's default and avoids a rename after the first
push. The audit found no `user.name` or `user.email` configured locally or
globally, which would have made committing impossible; it is set locally so the
setting does not leak into the developer's other projects.
