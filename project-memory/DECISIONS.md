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

## D-010 — `project-memory/` is the single project-memory system
**Date:** 2026-09-08 · **Status:** Accepted

**Why:** Two competing layouts were proposed during planning — a flat `docs/`
and a dedicated `project-memory/`. Two memory systems means neither is
trusted. The dedicated folder separates *living product documentation* from
*decision history and project state*, which are different things with different
readers.

**Consequences:** `docs/DECISIONS.md` is a pointer to this file, not a second
log. `docs/` describes the product as it is; `project-memory/` records how
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
**Date:** 2026-09-08 · **Status:** Superseded by D-046

> **Superseded 2026-09-12 by [D-046](#d-046--proprietary-and-published-from-an-allowlist-into-a-separate-repository).**
> Mind Archive is now proprietary, all rights reserved. Everything below was true
> on 2026-09-08 and is kept because its central argument — that a licence travels
> one way — is precisely what made this reversal possible while the software was
> still unpublished, and impossible afterwards. The pricing described here is
> withdrawn, not repriced.

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

## D-027 — Importers detect by shape, not by filename
**Date:** 2026-09-08 · **Status:** Accepted

`Importer.detect()` inspects the structure of the file's contents. It does not
match on the filename, and the order importers are registered in does not
matter.

**Why:** ChatGPT and Claude both ship a file called `conversations.json`. The
original ChatGPT importer returned `True` for any zip containing that name, so
it would have confidently accepted a Claude export, found no `mapping` in
anything, and reported that the user's export contained nothing readable.

This was a latent bug from Milestone 2 that no amount of testing the ChatGPT
importer could have found. It took a second real provider to expose it, which
is the whole argument for generalising an interface against a genuine second
case rather than a guessed one.

**Consequences:** `looks_like_chatgpt` and `looks_like_claude` check for
`mapping` and `chat_messages` respectively, and each rules out the other's key.
A new importer must add its own shape check, not just a filename.

**ChatGPT is the fallback when the shape says nothing** — an empty export, or
one whose JSON cannot be parsed. Without that, a corrupt or empty export would
match nothing and the user would be told the file was "not recognised" instead
of "conversations.json is not valid JSON on line 4". A specific complaint about
a nearly-right file beats a vague one.

---

## D-028 — `StorageProvider` waits for Milestone 6
**Date:** 2026-09-08 · **Status:** Accepted

Milestone 5 specified a `StorageProvider` interface with `LocalStorageProvider`
as its only implementation. Not built.

**Why:** An interface with one implementation is a guess about the second. This
milestone is itself the evidence: the `Importer` interface only revealed its
real defect — filename-based detection (D-027) — when a genuine second provider
arrived. Writing `StorageProvider` now, with cloud storage still a milestone
away, would repeat exactly the mistake that milestone just corrected.

It would also be inconsistent. Projects were deferred in Milestone 4 for the
same reason (D-026), and "do not build speculative structure" cannot be a rule
that applies only when convenient.

**Consequences:** Filesystem access stays direct until Milestone 6, where the
interface gets designed against a real cloud adapter and a real local one at
the same time. Recorded in `docs/BACKLOG.md` so it is deferred rather than
forgotten.

---

## D-025 — Tags live in `metadata.json`, and an import never removes them
**Date:** 2026-09-08 · **Status:** Accepted

Tags are stored in each conversation's `metadata.json`, on disk, beside the
conversation they belong to. SQLite indexes them for filtering and counting and
holds nothing else.

**Why:** Everything else in the archive is *derived* from a provider export, so
losing the index costs nothing but time. Tags are different: **you make them**.
They exist nowhere else in the world. Storing them only in `mind_archive.db`
would mean deleting a rebuildable cache destroyed original work, which breaks
D-004 in the one place it would actually hurt.

Putting them in `metadata.json` also means they travel with the archive: copy
the folder to another machine and your organisation comes with it, because it
was never separate from it.

**The consequence that needed the most care:** an export contains no tags, and
re-importing rewrites `metadata.json`. Done naively, importing your monthly
export would silently erase every tag you had ever applied. So the writer
**reads the existing metadata and merges tags forward** before writing. There is
a test for exactly this, because it is the kind of data loss nobody notices
until months later.

**Consequences:**

- `Conversation.tags` is part of the model; importers never set it.
- Tags are trimmed, collapsed, deduplicated case-insensitively, and capped in
  length and number. A tag is a label, not a document.
- The schema gains a `tags` table and `SCHEMA_VERSION` becomes 2. The index
  rebuilds itself, which costs nothing precisely because it is derived.
- Editing `metadata.json` by hand is a supported way to tag things.

---

## D-026 — Projects are deferred; tags first
**Date:** 2026-09-08 · **Status:** Accepted

Milestone 4 was specified as "Project, Conversation, Message, Document, Memory,
Tag, Attachment, Source, Metadata, Event". Only tags are being built.

**Why:** Tags plus the existing full-text search already answer the question
people actually have — *"where is that conversation about X?"*. Projects add a
second, hierarchical way to organise the same things, and building both at once
means guessing at how they interact before anyone has used either.

Building the whole model list now would also be the kind of speculative
structure this project has avoided since Milestone 1. A `Memory` or `Document`
type with no feature behind it is a schema nobody has tested against a real
need.

**Consequences:** If projects are still wanted after living with tags, they are
straightforward to add — likely as a reserved tag namespace rather than a
parallel hierarchy. Recorded in `docs/BACKLOG.md` rather than dropped.

---

## D-023 — A watched inbox folder, owned by default and configurable
**Date:** 2026-09-08 · **Status:** Accepted

Mind Archive watches one folder for provider exports. Anything dropped in is
imported. `MIND_ARCHIVE_INBOX_DIR` defaults to `data/inbox`.

**Why:** Getting an export out of ChatGPT takes days (see RESEARCH R-004). When
it finally arrives, the least the application can do is pick it up without being
asked. Saving a file into a folder is a smaller act than opening an application
and finding an upload button.

**Why one folder and not a filesystem watcher:** scanning on startup, on demand,
and when the interface regains focus covers every case that matters for a
personal archive, and costs no dependency. `watchdog` can be added if it ever
earns its place.

**Consequences and the boundary that matters:**

- The default folder is one Mind Archive owns. There it tidies up: imported
  files move to `imported/`, unreadable ones to `failed/` with a note. An empty
  inbox means everything is in.
- Pointing the setting at a folder of your own is supported, and then **files
  are left exactly where they are** — moving things out of somebody's Downloads
  folder would be presumptuous. A small ledger records what has been imported.
- A folder the user chose is never created for them.
- **Everything in the inbox is untrusted**, exactly like an upload: same
  importers, same zip-safety checks, same size caps. Only `.zip` and `.json`
  are ever opened.
- The startup scan runs on a **background thread**. On a slow filesystem a
  large import takes minutes, and doing it inline left the server refusing
  connections throughout — the application looked broken at exactly the moment
  it was being most useful. Found by measurement, see R-005.

---

## D-024 — The fast path is a script the user runs; no credential enters Mind Archive
**Date:** 2026-09-08 · **Status:** Accepted

ChatGPT's undocumented `/backend-api/` endpoints can return your conversations
in minutes rather than days. Mind Archive will **never** call them, and will
never ask for a session token.

The supported fast path is `scripts/browser/chatgpt-export.js`: a script the
user pastes into the console of their own logged-in tab. It reuses the session
the browser already holds, downloads a `conversations.json`, and that file goes
into the inbox like any other export.

**Why this shape and not the obvious one:** a ChatGPT session token grants full
account access — reading every conversation and sending messages as the user.
Several third-party tools ask people to paste that token into a text box. For a
product whose entire pitch is that your data stays yours, asking for that
credential would be self-defeating regardless of how carefully it was handled.

Keeping the script outside the application means Mind Archive's privacy claim
stays trivially true: it makes no outbound request, and only ever reads a file
you put in a folder.

**Consequences:** The script is documented as **not part of the application**,
with honest warnings — the endpoints are undocumented and may break, using them
may violate OpenAI's Terms of Use, and it cannot fetch attachments. The
counter-argument (it is the user's own data, GDPR Article 20) is presented as
theirs to weigh rather than settled for them. The official export stays the
default and the recommendation.

**Explicitly rejected:** Mind Archive storing a session token and calling
OpenAI itself, in any form, opt-in or otherwise.

---

## D-020 — A conversation is served and rendered as one Markdown file
**Date:** 2026-09-08 · **Status:** Accepted

The API returns `conversation.md` as Markdown, front matter removed, and the
interface renders the whole file. It does not parse the file back into
individual messages.

**Why:** Round-tripping our own rendering would be fragile — a message whose
text contains `## You` would break it — and it would gain nothing. The file on
disk *is* the readable artefact; that is the entire point of storing Markdown
(D-004). Rendering it whole means what you see in the interface is exactly what
you see if you open the file in any editor.

**Consequences:** No per-message structure in the interface: no speaker bubbles,
no per-message actions, no reply-level anchors. Speaker headings render as
headings, which reads correctly for a document archive. If per-message
behaviour is ever genuinely needed, the honest fix is to store structure in
`metadata.json` rather than to parse prose.

The conversation is read from disk rather than from the index, so editing a
file by hand shows immediately without waiting for a re-index.

---

## D-021 — Markdown is rendered with `react-markdown`, and raw HTML stays off
**Date:** 2026-09-08 · **Status:** Accepted

The one frontend dependency added in Milestone 3.

**Why:** Conversation text comes from a provider export — untrusted content that
must never become markup in the page. `react-markdown` builds React elements
instead of setting HTML, and does not render embedded HTML unless explicitly
enabled, which it is not. The alternative, a Markdown-to-HTML library plus a
sanitiser and `dangerouslySetInnerHTML`, is two dependencies and one mistake
away from an injection.

**Consequences:** Raw HTML inside a conversation appears as characters, which is
the correct and safe behaviour. Search snippets take the same approach from the
other direction: the backend marks matches with `<<` and `>>` rather than
sending HTML, and the interface splits on those markers. Both are covered by
tests that assert an `<img onerror=...>` in content never becomes an element.

---

## D-022 — Search matches all words, and the last word as a prefix
**Date:** 2026-09-08 · **Status:** Accepted

Typed words are combined with `AND`. The final word also matches as a prefix,
so "sourd" finds "sourdough". Anything unsearchable means "no filter", not "no
results".

**Why:** This is what a search box is expected to do. `AND` because a personal
archive is searched to find one remembered thing, not to browse loosely.
Prefix-matching the last word makes search-as-you-type feel responsive rather
than empty until the final keystroke.

**Consequences:** Phrase search, `OR` and negation are not available — typing
them searches for those words literally. That is a deliberate trade for never
showing someone a syntax error. Revisit if anyone actually asks for operators.

---

## D-018 — Verification is developer-controlled during development, and required at milestone boundaries
**Date:** 2026-09-08 · **Status:** Accepted

Tests and checks are **not** expected to run on every change. There is no
pre-commit hook, no file watcher, and nothing wired into saving a file.

The developer decides when to verify. Checks are **required** at three points:

1. Before a milestone is called complete.
2. Before opening a pull request.
3. Before a release or deployment.

CI enforces the second and third; the first is a working discipline.

**Why:** Running a full suite after every edit is slow, and slow feedback gets
skipped or worked around, which is worse than an explicit gate. Exploratory
work — trying an approach, throwing it away — is where most development time
goes, and the code is *expected* to be broken during it. Verifying constantly
during that phase costs time and buys nothing.

This mirrors how open-source projects actually work: contributors iterate
locally however they like, then run the full suite before pushing, and CI is the
backstop.

**Consequences:** `scripts/dev.py` gives granular commands (`test`, `lint`,
`types`, `format`, `build`) plus `verify`, which runs everything and is the
milestone gate. `AGENTS.md` and `AI_AGENT_PROTOCOL.md` were updated: agents must
no longer run the full suite after every edit, but must run `verify` before
declaring a milestone done — and must still never claim a check passed without
running it.

**What does not change:** honesty about verification. "I did not run the tests"
is a fine thing to say. "The tests pass" without having run them is not.

---

## D-019 — Docker containers are disposable and never left running
**Date:** 2026-09-08 · **Status:** Accepted

Every check runs in a one-shot container (`docker compose run --rm`). Nothing
lingers. `scripts/dev.py verify` tears the stack down when it finishes, and
`dev.py clean` removes this project's containers, volumes and built images.

**Why:** Development machines accumulate stopped containers, orphaned volumes
and stale images until Docker quietly consumes tens of gigabytes. Making
teardown explicit and easy prevents that, and guarantees checks run against a
clean environment rather than a container that has drifted.

**Consequences:** `./data` is a bind mount, not a Docker volume, so no cleanup
command can delete the user's archive — including `down --volumes`. That
separation is deliberate and must be preserved.

---

## D-048 — The publication allowlist, and what it refuses to publish
**Date:** 2026-09-12 · **Status:** Accepted

**Implements the mechanism D-046 described.** `scripts/publish_public.py` copies
an explicit allowlist into a clean tree. It is not published itself — a private
repository's publication tool belongs in the private repository.

```
python3 scripts/publish_public.py --list              what would be published
python3 scripts/publish_public.py --check             screen it, say what is wrong
python3 scripts/publish_public.py --build DIR         write the tree
```

**It never runs `git`.** No `init`, no `commit`, no `remote`, no `push`, and no
GitHub call of any kind. It writes files to a named directory and stops.
Publishing is a deliberate human act; a tool that could do it by accident is the
wrong tool. It refuses a destination inside this repository, refuses an existing
destination without `--force`, and **refuses any destination containing `.git`
even with `--force`** — a repository's history is not this script's to destroy.

### Files are listed; directories are recursive

`PUBLIC_FILES` names individual files. `PUBLIC_TREES` names directories that are
published whole, so a new file under `apps/api/src` is published automatically.

**That is the deliberate half of the trade-off.** An allowlist naming every
module would be stale within a day, and a stale allowlist is one people learn to
bypass. The safety is not in enumerating files; it is in every file — new or old
— passing three gates before it is copied, and in `--check` printing the whole
resolved list so additions are visible. Nothing outside the allowlist is read at
all, so it cannot leak by being forgotten, only by being added on purpose.

**The three gates:** denied path segments and file types (`.env`, keys,
databases, archives, `project-memory`, `sessions`, `prompts`, `.claude`, `data`,
`tmp`, symlinks); a content scan for private keys, provider tokens, AWS keys,
private IP ranges and absolute home paths; and a report of references to
unpublished material. **The first two stop a build. The third does not** — a
comment citing `project-memory/DECISIONS.md D-009` leaks nothing, but a public
reader cannot follow it, so it is reported for a human to judge.

**The scanner is deliberately small.** Placeholder paths (`/home/someone/`) are
allowed, because a scanner that cries wolf is one people pass with `--force`.
It will not catch a secret that looks like ordinary prose; `.gitignore` and the
CI secrets job remain the primary defences.

### Withheld, and why

| Withheld | Reason |
|---|---|
| `project-memory/`, `prompts/`, `.claude/` | The internal record and the development process itself |
| `CLAUDE.md`, `GEMINI.md`, `QWEN.md` | Agent entry points into that record |
| **`AGENTS.md`** | Read order, session protocol and the public/private boundary — instructions for working inside a private repository, not documentation of a product |
| `AUDIT-REPORT.md` | An internal punch list of current weaknesses |
| `docs/DECISIONS.md` | A pointer to the private log; it would dangle |
| `docs/BACKLOG.md` | Withdrawn pricing, merchant-of-record research, internal reasoning |
| `scripts/session.py` | The private session-memory tool, useless without `project-memory/` |
| `scripts/publish_public.py` | This script |
| `project-memory/site_pages.json` | The private half of the site's page list |
| `docs/_data/private_pages.yml` | The signal that switches the private links on |

### One `docs/`, two builds — added 2026-09-12

The first generated tree contained a site with **38 broken links**: five routes
whose sources *were* published but whose generator was not, and eight generated
from documents that can never be public. Both are now resolved, and the
mechanism is the same idea twice — **a private file whose absence changes the
build, rather than a publication step that edits files on their way out.**

Editing files during publication was rejected outright: the published output
would then differ from anything reviewable here, and a publication step that
rewrites code is one nobody can check.

**The page list is split.** `sync_site_pages.py` holds the five public entries
and loads the rest from `project-memory/site_pages.json` **if it is there**. The
private repository generates 11 pages; the published tree has no such file and
generates 5. The script itself is now publishable — it names no private
document — and there is one implementation, not two that drift.

**The links are conditional.** Anything pointing at a private-only route is
wrapped in `{% raw %}{% if site.data.private_pages %}{% endraw %}`, and
`docs/_data/private_pages.yml` is not published. The private site keeps every
link; the public site renders the same documents without them. Several passages
carry an `{% raw %}{% else %}{% endraw %}` branch so the public wording stands on
its own rather than reading like something went missing.

**`check_site_links.py` had to learn the same condition**, because it reads
source rather than built output and would otherwise report links the build it is
checking would never render — a checker that cries wolf. It strips the private
blocks when the data file is absent.

**Two tools also stand aside where their inputs are absent:** `dev.py verify`
skips the project-memory step when `session.py` is not present, and the CI
`project-memory` job does the same. Conditional rather than removed, so the gate
keeps checking them in the repository where they mean something.

**Prose was rewritten, not just links.** Four published documents described a
`project-memory/` directory that will not exist for a public reader — a layout
diagram, the Pages explanation, two research citations. A public reader should
not be told about a folder they cannot see.

**Result:** the public tree generates its own 5 pages, resolves **27 routes with
zero broken links**, and builds. The private tree still generates 11 and resolves
35. The eight private route families do not exist in the public build, and the
word `project-memory` appears nowhere in its rendered HTML.

**Consequences:**

- Adding a file to `PUBLIC_FILES` means reading it first. The allowlist is a
  series of judgements, not an inventory.
- A new top-level directory is invisible to the publisher until someone adds it,
  which is the intended default.
- `--check` should pass before any publication, and its reference report should
  be read rather than skimmed.

---

## D-047 — Four names on one apex, and one page for Git and SSH
**Date:** 2026-09-12 · **Status:** Accepted

### The domain architecture

| Name | Serves | Runs on |
|---|---|---|
| `mindarchive.narainsagar.com` | The application | A private VPS instance |
| `api.mindarchive.narainsagar.com` | The API | The same VPS, same proxy |
| `docs.mindarchive.narainsagar.com` | The documentation site | GitHub Pages |
| `narainsagar.github.io/mindarchive/` | The same site, unbranded | GitHub Pages |

**Nothing is configured.** No DNS record exists, no certificate has been issued,
and this decision authorises none of that — it records the shape so that
documentation stops contradicting itself.

**Why subdomains of an existing apex** rather than `mindarchive.app`, which the
documentation named until today: the apex is already owned, a subdomain needs one
`CNAME` record instead of four apex `A` records, and no renewal is at stake. The
`mindarchive.app` plan predated the identity being settled and was never acted on.

**Why the API gets its own name** rather than a path on the application's: it is
a separate process behind the same proxy, and a name can be moved, firewalled or
taken down without touching the other. Note that the API has **no
authentication** (D-032, `docs/SECURITY.md`) — giving it a public name does not
make it safe to expose, and nothing here says it should be.

**Why the site keeps both addresses.** The Pages URL works whatever happens to
DNS, which is why `_config.yml` deliberately leaves `baseurl` unset and lets the
Pages build inject it. A custom domain is an addition, never a replacement.

### Git and SSH get one page, not a section and not a tree

`docs/development/GIT_SSH_SETUP.md` — published at `/git-ssh/`.

**Why a page.** Authentication is a one-time task consulted in a crisis, usually
when a push has just hung. `DEVELOPMENT.md` is 340 lines about running and
changing the software; burying "your network blocks port 22" inside it means
nobody finds it at the moment they need it.

**Why not a `docs/development/` + `docs/deployment/` tree.** Twelve documents sit
flat in `docs/` with explicit permalinks, and the routes are already clean —
`/development/`, `/deployment/`, `/security/`. Restructuring twelve files to
match a diagram would change every internal link and every published URL to gain
nothing a reader can perceive. The subdirectory holds setup guides because that
is where this one already was; future setup guides join it.

**The rule that matters is no duplication.** The page owns keys, the agent, the
remote and the port-443 route. `DEVELOPMENT.md` owns installing, running and
committing conventions. `DEPLOYMENT.md` owns publication. Each links to the
others; none restates them.

**The port-443 route is the durable technical content.** Some networks drop
outbound port 22, and GitHub serves SSH on 443 for exactly that reason. It is
written generically — no hostname, address, network name or key material — so it
is safe to publish, which matters because this page is intended to become public.

**Consequences:**

- `project.json` holds `site.domain` and `useCustomDomain: false`. Turning the
  custom domain on is four steps in `DEPLOYMENT.md`, none of them taken.
- A second setup guide belongs in `docs/development/`, not in `DEVELOPMENT.md`.
- If the application ever answers on a public name, the authentication problem
  has to be solved first. The name is not the missing piece.

---

## D-046 — Proprietary, and published from an allowlist into a separate repository
**Date:** 2026-09-12 · **Status:** Accepted

**Supersedes [D-016](#d-016--polyform-noncommercial-100-with-commercial-licences-sold-separately)
(the licence) and the publication half of
[D-032](#d-032--published-publicly-on-github-pages-for-docs-no-hosted-application).**
Both are annotated in place rather than rewritten; they were correct decisions on
their dates and the reasoning in them is still worth reading.

### The licence is All Rights Reserved

Mind Archive is **proprietary software**. Not open source, not source-available,
no licence granted to anyone. `LICENSE` is a copyright notice rather than a
licence text, and `LICENSING.md` says so in plain language.

**Why now.** D-016 chose PolyForm Noncommercial specifically because *"licence
changes only travel one way"* — a permissive grant, once published, is permanent.
That reasoning is exactly what makes this change possible today and impossible
later: **the software has never been published or distributed to anyone.** The
repository has been private since its first commit and the documentation site has
never been deployed. There is no recipient of the PolyForm grant, so withdrawing
it takes nothing away from anybody.

**No commercial licensing system replaces it.** D-016's $49 seat price, the $39
volume tier and the merchant-of-record plan in D-038 belonged to a model that no
longer exists. They are removed rather than repriced: **nothing is for sale, and
inventing a price nobody has approved would be worse than saying so.** The
donation configuration stays as it is — blank, therefore invisible — because
donations are not a licence.

D-038's substantive promise survives unchanged: **the application will never
contain payment code, phone home, or ask for money while it is running.** A test
still fails if any payment provider's name appears in the interface.

### This repository stays private, permanently

It is the development workspace, and a third of it by file count is working
memory: 45 decisions, 23 session records, verbatim prompts, internal research
including a profile of the development machine, and agent instructions.

**A separate public repository will be created later, with clean history.** Not a
fork, not a mirror, not a history rewrite of this one. The audit on 2026-09-11
established why: no secret was ever committed — `.gitignore` has covered secrets,
`data/`, `local/`, databases and provider exports since the first commit, and CI
enforces it — but the history contains the raw planning transcripts deleted in
`14159dc`, a probe of the development machine, 534 lines of verbatim prompts in
the first session record alone, and a personal email address in all 39 commit
author fields. **Flipping this repository to public would publish all of it.**

### AI-assisted development is disclosed, at a high level

Mind Archive may state publicly that it is built with AI assistance. `README.md`
carries one sentence to that effect. **What stays private is the machinery**:
prompts, agent rules, `project-memory/`, session records, internal research and
development transcripts. The disclosure is a fact about how the work is done, not
an invitation to read the workshop.

### The publication mechanism: allowlist out, never denylist in

**Publishing copies approved files into a clean tree. It must never copy the
repository and then delete the private parts.** The difference is not stylistic:
a denylist fails open — anything new is public until someone remembers to exclude
it — while an allowlist fails closed, which is the only acceptable direction for
a repository whose private material is the majority.

```
private repository (source of truth)
        │
        ▼
explicit allowlist  ──► sanitised public tree (built fresh, never a copy)
        │
        ▼
new public repository, clean history, own initial commit
```

**Recommended home when it is built:** `scripts/publish_public.py`, beside
`sync_site_pages.py` and `check_site_links.py` — the same shape as the existing
scripts, standard library only, and with a `--check` mode that lists what would
be published without writing anything. It is deliberately **not** in `dev.py`:
publishing is not a development command and should not sit one typo away from
`verify`.

Four things it has to handle, all of them established by inspection rather than
guessed:

1. **`project-memory/` is referenced from 22 tracked files**, about 40 times.
   Most are prose citations in comments (*"see D-009"*); those are harmless but
   dangling once the target is not published.
2. **`sync_site_pages.py` would fail outright.** Five of its eleven `PAGES`
   sources live in `project-memory/`; a missing source is a hard error by design.
   The public copy needs a trimmed list.
3. **`session.py check` would fail**, and it runs both in `dev.py verify` and as
   its own CI job. Neither belongs in the public repository.
4. **Three navigation links** in `docs/documentation.html` point at pages
   generated from private files, and `check_site_links.py` correctly refuses to
   ship dead links.

**Consequences:**

- Every published page, manifest and UI string must now say proprietary. The
  application's Support and Contribute panels, the site footer, the landing page,
  `README.md`, `CONTRIBUTING.md` and both package manifests were changed with
  this decision.
- **Historical records are not rewritten.** `CHANGELOG.md`'s 0.1.0 entry,
  `MILESTONES.md`, the session records and the superseded decisions still say
  PolyForm, because on their dates that was true. Only current-state documents
  were changed.
- The public repository's name is expected to be `mindarchive`; this one is
  expected to be renamed to something like `mindarchive-private` later. Neither
  has been done.
- Nothing here changes the product, the architecture or the privacy model.

---

## D-045 — The brand goes back to the top, and so does a floating link
**Date:** 2026-09-11 · **Status:** Accepted

**The brand in the header was a link that did nothing.** `href="/"` with an
`onClick` that called `preventDefault()` and stopped there — it cancelled the
navigation and never replaced it. Introduced with the one-row header (D-037,
commit `651ea60`) and inert from its first line: it looked like a link, took
focus like a link, and answered a click with nothing at all.

`preventDefault()` was right; what was missing was the rest. There is no router
(D-008, D-030), so a real navigation to `/` reloads the page and throws away the
current search and any open conversation.

**The brand now does what the nav's Home entry already did.** The guard clause
is copied from `SectionNav` deliberately, so the two read the same: a plain left
click scrolls `#top` into view, and a click with Ctrl, Cmd, Shift or Alt, or a
non-primary button, is handed back to the browser so "open in new tab" and "copy
link address" keep working. The header is sticky, so this is a way back to the
top from any scroll position.

**A floating `Back to top` appears after one screen of scrolling**, bottom
right, and hides again at the top. It is a plain `<a href="#top">` — the same
destination the footer link and the header use — so it works before React has
hydrated and with JavaScript off. The only thing the component decides is
whether the link is worth showing.

**Two links with the same name is deliberate.** The footer keeps its Back to top
(D-031); the floating one exists because the footer is a long scroll away from
the middle of a large archive. Renaming one to avoid the duplicate would make it
describe itself less accurately, which is the worse trade.

**Against the clutter rule, on purpose.** AGENTS.md rules out visual clutter, and
a control pinned over the page is exactly that if it is always there. So it is
hidden at the top of the page; hidden by `visibility` rather than unmounted, so
it stays out of the tab order and away from screen readers until it is offered;
and it sits below the dialog backdrop, because with a dialog open there is
nothing behind it worth scrolling to.

**No JavaScript animation.** `html` already carries `scroll-behavior: smooth`,
which the existing reduced-motion block turns off. The only transition is the
link's own 120ms fade, which that same block already reduces to nothing.

**Consequences:**

- `#top` is now load-bearing for three controls. It is rendered unconditionally,
  including when the backend is unreachable — which is why the brand works in
  the error state, where the section nav is not rendered at all.
- A test asserting on "Back to top" must say *which* one. The footer's is scoped
  to `contentinfo`.
- The brand's click path had never been tested, and nothing clicked Home either.
  It is tested now in both directions: a plain click scrolls, a Ctrl-click does
  not. jsdom implements no scrolling, so the target's `scrollIntoView` is stubbed
  per element rather than on the prototype.

---

## D-044 — The published contact address is `info@narainsagar.com`
**Date:** 2026-09-11 · **Status:** Accepted

Commercial licensing enquiries, support and everything else the site and the
application offer to answer go to **`info@narainsagar.com`**.

**Why not an address at `mindarchive.app`.** That was the earlier intention, and
the domain has no DNS. Publishing an address that bounces is worse than
publishing a personal one, and a licensing enquiry is exactly the mail nobody
sends twice. `narainsagar.com` exists and receives mail today.

**Why not `kishor3947@gmail.com`.** It was a personal address printed on a page
that asks strangers to write in. The project can change hands, or gain a second
maintainer, without reissuing every published document.

**It is configured in two places, and that is not an oversight:**

| Where | Key | Read by |
|---|---|---|
| `docs/_data/support.yml` | `contact_email` | the Jekyll site — the footer, `/support/`, every generated page |
| `apps/web/src/support.ts` | `contactEmail` | the application — the footer and the Support panel |

Jekyll cannot read a TypeScript file and Vite cannot read Jekyll's data files, so
one of them has to hold a copy. **Change both.** Nothing else hardcodes it, and
`App.test.tsx` now asserts against the configured value rather than a copy of
it — the test previously named the address and would have failed on this change
for no reason.

**`project.json` is not a third place.** Its `author.email` is the *git commit
identity* that `scripts/set_identity.py` writes into the local git config
(D-015). An earlier note listed it as one of the contact-address locations; it
never was. It stays `kishor3947@gmail.com` **deliberately**: the existing history
is authored by that address, and changing it now would attribute one person's
commits to two identities to no benefit. Commit authorship and a published
contact address are different things and are allowed to differ.

**Consequences:**

- The two values must be changed together. There is no check that compares them;
  the honest fix if they ever drift is to notice it here.
- The address is published on every page of the site, so it will be scraped.
  That is the cost of a contact address on a public site, and the reason it is
  not a personal mailbox.

---

## D-043 — The repository's canonical documents are generated as site pages
**Date:** 2026-09-11 · **Status:** Accepted

**Supersedes the closing clause of [D-036](#d-036--clean-lowercase-routes-for-every-page-set-per-page):**
*"Links to `project-memory/` now point at GitHub, since that directory is
deliberately excluded from the site."* That is no longer true, and the reason it
changed is worth keeping.

**The problem.** Fifteen links across ten pages pointed at
`github.com/narainsagar/mindarchive/blob/main/...` — `LICENSING.md`,
`CONTRIBUTING.md`, `AGENTS.md`, `.env.example` and four files under
`project-memory/`. On `localhost:4000` they leave the site entirely, and until
the repository is published they go nowhere at all. A reader who clicks
"the full terms are in LICENSING.md" on the donation page gets a 404 from
GitHub.

Those links were not careless. Jekyll is rooted at `docs/` and **cannot read
above it**, which D-039 made explicit on purpose — *"the site cannot publish
what it cannot reach."* There was no local page to point at. A symlink does not
help either: the Pages build runs Jekyll in safe mode and will not follow one
out of the source folder.

**The decision.** `scripts/sync_site_pages.py` generates a page for each
canonical document — eleven of them, at `/licensing/`, `/license/`,
`/contributing/`, `/code-of-conduct/`, `/agents/`, `/env-example/`,
`/decisions/log/`, `/milestones/`, `/research/`, `/session-protocol/` and
`/agent-protocol/`.

`LICENSE`, `CODE_OF_CONDUCT.md` and `AI_AGENT_PROTOCOL.md` were not on the
original list. They are here because the documents that *were* link to them 22
times between them, and publishing a page whose own links dead-end just moves
the problem one click deeper.

**The output is git-ignored, not committed.** Generated into `docs/reference/`
before every build — by `dev.py verify`, by `dev.py docs`, and by the Pages
workflow. Committing copies would mean a second version of every decision in the
repository and a check to notice when the two disagree; generating them means
the two *cannot* disagree. D-010 forbade a second decision log for exactly this
reason, and a committed copy would have been one.

**Links inside the generated content are rewritten**, because Kramdown does not
touch `.md` links and they would 404: `[RESEARCH.md](RESEARCH.md)` becomes
`[RESEARCH.md]({% raw %}{{ '/research/' | relative_url }}{% endraw %})`, per the
convention D-036 set. **A link to a document with no page fails the build.**

**Three things this surfaced that were already broken:**

1. **Liquid inside backticks is still executed.** Liquid runs over the whole
   file before Kramdown sees any Markdown, so D-036's own entry — which
   *explains* the `relative_url` convention by quoting it — would have rendered
   the evaluated URL instead of the syntax. Pre-existing Liquid is now wrapped
   in `{% raw %}`. **Wrapping everything was wrong, twice** — see below.
2. **A link label containing backticks is still a link.** The first version
   skipped every code span, which split ``[`docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md)``
   apart and left three real links unconverted. Only a whole link wrapped in
   backticks is an example rather than a link.
3. **Three stale `docs/project-memory/` paths** survived the D-039 move, in
   `apps/api/Dockerfile` and `apps/web/src/styles.css`. Same root cause D-039
   recorded: the path was split across lines, so the search for it missed.

**Escaping Liquid has three cases, and only the first is obvious.** Wrapping
every tag in a raw block broke the site build twice before the rule was right.

*The tags are named without their braces below — `raw`, `endraw` — because a
document that prints them literally is exactly the document that breaks. That is
case 3.*

1. An ordinary tag or output — wrap it, so it is shown rather than run.
2. **A raw block the author already wrote — leave it completely alone.**
   Wrapping one produced `raw raw … endraw endraw`, and Jekyll refused to build:
   *Unknown tag 'endraw'*. Liquid does not nest raw blocks: the first `endraw`
   closes the block, so the last one has nothing to close.
3. **A lone `raw` or `endraw` tag, written as prose about escaping.** It cannot
   go inside a raw block — `endraw` is exactly what closes one. The obvious
   alternative, printing the whole tag from a string literal, **also fails**:
   Liquid ends an output at the first `}`, so the `%}` inside the quotes closes
   it early and the parse dies on an unterminated variable. Only the opening
   brace is printed, and the rest of the tag stays ordinary text.

`project-memory/DECISIONS.md` contains all three, so this is not hypothetical —
this entry is one of them.

**`check_liquid()` in the generator refuses to write a page Liquid cannot
parse**, reading it with the same tokenising rule Liquid uses — an output ends
at the first `}`, and a raw block ends at the first `endraw`.

It exists because nothing else would have caught this. The generator was happy,
the link checker reads source rather than Liquid, and **`dev.py verify` did not
build the site**: the Pages workflow was the first thing that ran Liquid at all,
by which point the failure is a failed deployment. **`verify` now builds the
site** in a throwaway container, discarding the output — the check is whether
Jekyll can render every page, not what it rendered.

**`scripts/check_site_links.py` is the other half**, and arguably the more
important one. D-036 has required since the day it was written that every
internal link be walked and resolved — **and nothing did it.** It was done by
hand, once. Its own post-mortem is the argument: *"a check that only looks where
you just worked cannot find what you broke elsewhere."* The checker reads the
source rather than a built site, so it needs no Ruby, Docker or Jekyll and runs
in under a second inside `verify`. It also refuses a GitHub link to a document
that now has a page — this exact regression.

**A 404 page exists** at `docs/404.html`, in the site's layout. It is a safety
net, not a fix: a link that lands on a styled 404 is still a broken link, and
the checker is what stops one shipping.

**What is still not published:** `PROJECT_STATE.md`, `SESSION_LOG.md`,
`MEMORY_INDEX.md` and the per-session records. Those are working scratch, and
nothing links to them from a page.

**Consequences:**

- A new canonical document that a page links to must be added to `PAGES` in
  `sync_site_pages.py`, or the build fails. That is the intended failure.
- `docs/reference/` is git-ignored. Never edit a file there; edit the source.
- Bare `jekyll serve` now shows an incomplete site. Use `python scripts/dev.py
  docs`, which generates first.
- `dev.py verify` now ends with a Jekyll build, so the gate needs the
  `jekyll/jekyll:4` image as well as the project's own. It is the same image
  `dev.py docs` already used, and the build takes about a second.
- Writing *about* Liquid in a document that is published is awkward, and the
  workaround is to name a tag without its braces rather than to fight the
  escaper. This entry does exactly that.
- The Pages workflow's path filter had to grow. Without it, editing
  `LICENSING.md` would change the published site and trigger no rebuild.

---

## D-042 — Exports are sharded; resolve them from the export's own manifest
**Date:** 2026-09-11 · **Status:** Accepted

Both importers had only ever been run against synthetic fixtures. Given real
exports, neither worked — for entirely different reasons.

**ChatGPT no longer ships `conversations.json`.** A real export contains
`conversations-000.json`, `-001`, `-002` and declares the mapping in
`export_manifest.json`:

```json
"logical_files": { "conversations.json":
  { "files": [...], "shard_count": 3, "sharded": true } }
```

`chatgpt.py` looked only for the plain name, found nothing, and `detect()`
returned `False` — **204 conversations reported as "not recognised"**.

`reading.py` now resolves a logical filename to its members and concatenates
them. **The manifest is preferred over guessing filenames**, for the same
reason detection reads shape rather than name (D-027): the export is telling us
the answer. A `stem-NNN.json` fallback covers an export that declares nothing,
and the plain single-file form still works untouched.

**Claude's file is not an export.** It is a download manifest — a 989-byte JSON
of three single-use links. It carries no conversations, so importing it can
never succeed. It is now detected **only to refuse it usefully**, naming the
file to download rather than saying "not recognised".

**Mind Archive does not fetch those URLs.** Downloading them would be the
application's first network request, against the promise in `LICENSING.md` and
D-038. The refusal tells you what to do; you do it.

**Two bugs found while doing this, both latent:**

- **`children` is gone from mapping nodes** — they are now `{id, message,
  parent}`. The main walk follows `current_node` upward and was fine, but the
  fallback walked *down* via `children` and had become dead code. It rebuilds
  the child map from parent links now.
- **`detect()` claimed files it should not.** The ChatGPT fallback accepted any
  bare `.json`, so it answered for Claude's manifest — and the registry lists
  ChatGPT first, so it would have won with a worse message. The manifest check
  lives in `reading.py`, not `claude.py`, because **an adapter must never
  import another adapter**.

**Consequences:**

- Verified against the maintainer's real export: **204 conversations, 2866
  messages, 0 problems**, counts matching the shards exactly (100 + 100 + 4).
- **The Claude path is not verified against real data.** Only the manifest was
  available, and its links are single-use. Claude keeps synthetic fixtures.
- Test fixtures are hand-written and always will be. A real export is a copy of
  somebody's private conversations; test files are committed.
- Attachments (`file-*.dat`, 50+ in a real export) remain out of scope and stay
  in `BACKLOG.md`.

---

## D-041 — Band elements use `padding-block`, never the `padding` shorthand
**Date:** 2026-09-10 · **Status:** Accepted

`.doc` used the `padding` shorthand:

```css
.doc { padding: 48px 0 72px; }        /* resets padding-inline to 0 */
```

`<main>` carries `wrap doc`. The band rule sets
`padding-inline: var(--gutter)`; `.doc` has the same specificity and comes
later, so it won, and **all twenty document pages rendered with their content
flush against the window edge**. Only the home page escaped, because `.home`
has no rule at all.

Fixed by one declaration: `padding-block: 48px 72px`.

**How it hid for so long.** `--content-max` was `1280px` with
`margin-inline: auto`, so above that width the auto margins produced side space
that looked like the gutter. D-040 set `--content-max: none`, which removed the
centring and exposed a defect that had shipped when the site layout was first
built. The later change revealed it; it did not cause it.

**The rule, stated so it is checkable:** on any element that carries a layout
band — `<main class="wrap doc">`, `<main class="wrap home">`,
`.site-header__in`, `.site-header__panel-in`, `.site-footer__in`, and the
application's `.header__inner`, `.header__panel-inner`, `.workspace` — vertical
spacing is written with `padding-block`. The `padding` shorthand is forbidden
there, including on any other class sharing the element.

**Consequences:**

- `scripts/check_css_bands.py` enforces exactly this and **runs inside
  `dev.py verify`**, so it is part of the gate rather than a script nobody
  invokes. Documented in `docs/GITHUB_PAGES.md`.
- **It was proven by reintroducing the bug**: it passes on the fix and fails on
  `padding: 48px 0 72px`, reporting the file, line and selector. A guard that
  cannot fail is worth nothing.
- It avoids `list[str]` annotations, because these scripts run on the
  developer's own Python and this machine's is 3.8 — the reason Docker is the
  supported path for the application (D-006, D-007).
- **No other check reads CSS.** The link checker, band checker and privacy
  checker all passed throughout — which is why this survived several rounds of
  verification and needed a human to see it.
- The comment above the band rule had already stated this rule in prose. Prose
  is not a check.

---

## D-040 — Full-width bands, a centred footer, and a site URL that works locally
**Date:** 2026-09-10 · **Status:** Accepted

Three corrections after looking at the running pages.

**`--content-max` is now `none`.** The bands use the full screen on both
surfaces. `--gutter` still holds content off the edges and `--measure` still
caps running text, so nothing that should be readable sprawls — the cap was
solving a problem the measure already solves, at the cost of a layout that did
not match the rest of the interface.

**The footer is one line of text and one centred row of links.** It was two
stacked paragraphs on the left and a link row pushed right by
`justify-content: space-between`, which left a visible hole across the middle
of a full-width footer. The slogan and the licence are the same sentence's
worth of information, so they are now one paragraph, and everything is centred.
Identical on both surfaces.

**`VITE_SITE_URL` makes the Support link usable while developing.** This is the
one that mattered: the application's Support panel had the production URL
hardcoded, so clicking it on a developer's machine jumped to the published
site — which meant **the application could not be checked locally at all**.

It now follows the `VITE_API_BASE_URL` pattern that was already there, and
defaults to `http://localhost:4000`, the local Jekyll server. `dev.py up` plus
the Jekyll one-liner gives a working link with no configuration.

**Consequences:**

- Documented in `.env.example` and set in `docker-compose.yml`.
- The test asserts the **path** (`/support/`), not the host. Pinning the
  production URL would fail locally for a reason unrelated to the behaviour.
- Verified rather than assumed: `VITE_SITE_URL` reaches the container, the
  served module carries `localhost:4000` rather than the published host, and
  `localhost:4000/support/` answers 200.
- The token comments describing `--content-max` as "an outer bound" were
  corrected. A comment that contradicts its value is worse than no comment.

---

## D-039 — Project memory lives at the repository root, not under `docs/`
**Date:** 2026-09-10 · **Status:** Accepted

The working memory moved from `docs/project-memory/` to **`project-memory/`** at
the repository root.

**Why.** It was never documentation. `docs/` is what the website publishes;
project memory is the internal record of how the project got here — session
notes, decisions, research, the prompts that produced them. Keeping it inside
`docs/` meant it was *only* kept off the website by an `exclude:` rule in
`docs/_config.yml`, which is a rule someone could delete without realising what
it was for.

At the root it is outside the published folder entirely. **The site cannot
publish what it cannot reach**, so the exclusion is now structural rather than
configured, and `_config.yml` no longer needs the rule. The read order in
`AGENTS.md` also gets shorter, which matters for the file every agent reads
first.

**Consequences:**

- 50 files were repointed. Paths are pointers, not historical claims, so past
  session records were updated too — a dead path helps nobody, and nothing that
  *describes* what was once true was altered.
- **`scripts/session.py` builds the path from separate segments**
  (`REPO_ROOT / "docs" / "project-memory"`), so a text search for
  `docs/project-memory` missed it. It is the one place that would have broken
  CI, since `session.py check` is a required job. Found by running the check
  rather than by reading the diff.
- Two documents claimed project memory was "excluded in `docs/_config.yml`".
  That is no longer why it is absent, so both were corrected — a true statement
  for the wrong reason is still wrong.
- `docs/archive/` no longer exists and its exclusion went with the rest.

---

## D-038 — Money is taken by a merchant of record, through plain links
**Date:** 2026-09-10 · **Status:** Accepted

Donations (☕$5 · 🍺$10 · 🍕$20 · 🍽️$25 · any amount) and the $49-per-seat
commercial licence are sold from `/support/` on the website. Every URL lives in
`docs/_data/support.yml`; a blank entry renders nothing.

**A merchant of record, not raw Stripe or PayPal.** Polar, Paddle and Lemon
Squeezy become the *legal seller* and remit tax in every jurisdiction. Selling a
digital licence to a consumer in the EU creates a VAT obligation on the **first
sale** — there is no threshold — and raw Stripe would leave registration,
collection, quarterly filing and ten years of record-keeping with the
maintainer. The extra ~2% is the cheapest part of this decision. `BACKLOG.md`
had flagged it as "evaluate before taking the first payment"; this is the
evaluation.

**Hosted checkout, reached by plain `<a href>`.** No Stripe.js, no PayPal SDK,
no embedded frame. A product whose entire argument is that nothing tracks you
cannot load a third-party script that fingerprints every visitor to its donate
page. **This is enforced by a build check** in `GITHUB_PAGES.md`: no
`<script src="http…">` or `<iframe src="http…">` may appear anywhere in the
built site. Every script on the site is inline and first-party.

It is also forced by the host. GitHub Pages is static — no server, no secrets,
no webhooks — so nothing here could process, verify or fulfil a payment even if
it wanted to.

**The application stays clean, and it is tested.** `LICENSING.md` promises Mind
Archive "will never contain payment code, phone home, or ask you for money while
you are using it". The Support panel therefore holds **one link to the website**
— no provider, no amounts, no checkout — and a test asserts that none of
`stripe`, `paypal`, `paddle`, `lemonsqueezy`, `polar.sh` or `checkout` appears
anywhere in the rendered interface. Changing payment provider never touches
`apps/`.

**Crypto is for gifts, never licences.** A published address costs nothing and
is the most private option on the page. A licence needs a buyer you can
identify and a receipt you can produce, so it goes through checkout.

**Consequences:**

- `LICENSING.md` gained the 🍽️$25 tier so the published tiers and the page
  agree — they would otherwise have contradicted each other on day one.
- Volume pricing ($39/seat at 10+) is provider configuration, not code.
- **Nothing about payment can be verified from this repository.** No account
  exists, every URL is blank, and a real end-to-end purchase on both paths —
  plus the refund path — is required before either is announced anywhere.

---

## D-037 — One header row; appearance is two menus; navigation folds
**Date:** 2026-09-10 · **Status:** Accepted

Both surfaces now carry a **single header row**: brand, navigation, then
actions and appearance. The two segmented radio groups became two menu buttons.
Below 1024px the navigation folds into a panel behind a hamburger; the
appearance buttons never fold.

**What forced it.** Six visible radio options is a wide control, and it was the
reason the header needed a second row at all. That second row did not collapse
when it ran out of space — it **scrolled sideways**, from
`.site-nav__in { overflow-x: auto }` and `.sectionnav__list { overflow-x: auto }`.
Both are gone. The links fold now instead of overflowing.

**`overflow-x` on `pre` and `table` deliberately stays.** That is a scroll
container doing its job so the *page* never scrolls — the opposite problem, and
removing it would break wide code blocks.

**Why a hand-built menu rather than `<select>`.** A native select is free,
bulletproof and gives a phone its own picker. It cannot show colour. Seeing the
three palettes is the entire job of a palette picker, so the menu is
hand-written and owns its keyboard and focus behaviour:
`role="menu"` with `menuitemradio` children — the pair that describes choosing
one of a few options from a menu button, and it lets each option stay a real
`<button>`. Arrow keys, `Home`/`End`, `Enter`, `Escape` with focus returned,
`Tab` to close, click-outside, one menu open at a time.

**The theme button shows the icon of the current choice** — sun, moon, or a
monitor for System. That is what lets it drop its text label under 640px and
still read, which is what keeps brand plus three controls inside 320px.

**Consequences:**

- `SegmentedControl.tsx` is deleted; `Menu.tsx` and `icons.tsx` replace it.
  Icons are inline SVG, not a library — six small paths.
- **The tagline left the header.** It still opens the landing page. The `<h1>`
  stays: dropping the tagline must not drop the page's one top-level heading,
  and it briefly did during implementation.
- Import and Export moved from the archive panel to the header, so they are
  reachable wherever you have scrolled to. `ArchivePanel` now reports its count
  upward (`onTotalChange`) because the export dialog needs it.
- Written twice — React and vanilla JS — like the pre-paint script before it
  (D-033). Same roles, same class names, same 1024px breakpoint.
- About ten test assertions moved from `radio` to `menuitemradio`, plus new
  tests for opening, arrow keys, Escape-restores-focus, and one-menu-at-a-time.
- The site's menus are **built by script rather than written into the markup**.
  Without JavaScript they cannot work, and a dead control is worse than none;
  `.no-js .appearance` hides them either way.
- Palette swatch colours are duplicated in `theme.ts` and the site's script. A
  swatch has to be a literal, because a custom property cannot be read from a
  palette that is not currently applied.

**Not verified here, and stated as such.** That the page never scrolls sideways
cannot be proven in this repository's tests: jsdom has no layout, so
`scrollWidth` is always zero, and there is no headless browser in the
environment. The rules that caused it are gone and the breakpoints are correct,
but the final check is dragging a real window from 320px upward — a manual step.

---

## D-036 — Clean lowercase routes for every page, set per page
**Date:** 2026-09-10 · **Status:** Accepted

Every page on the site has an explicit lowercase `permalink` in its front
matter: `/product/`, `/architecture/`, `/decisions/`, and so on. No `.html` URLs
remain. The site also gained `/docs/` (a documentation index), `/contribute/`
and `/coming-next/`.

**The bug that forced this.** D-035 added `permalink: /blog/:title/` as a
top-level key in `_config.yml`. **A global permalink applies to pages as well as
posts.** Every documentation page moved from `PRODUCT.html` to
`PRODUCT/index.html`, so every link in the navigation 404ed — the whole site
except Home and Blog. The blog's permalink is now scoped to `type: posts` inside
`defaults`, where it belongs.

**Why it was not caught.** The verification script written for D-035 checked
blog output only: the index, the four posts, the draft template, the feed. It
confirmed everything it was asked about and missed that it had broken
everything it was not. A check that only looks where you just worked cannot find
what you broke elsewhere.

The replacement walks the built output and resolves **every** `href` that is not
an external URL — 371 links across 21 pages. That is now the documented standard
in `GITHUB_PAGES.md`.

**Cross-document links were also broken, and always had been.** Kramdown does
not rewrite `.md` links, so `[BACKLOG.md](BACKLOG.md)` inside a published page
pointed at a file that is not in the output. Those now use
`{{ '/backlog/' | relative_url }}`.

**The trade-off, stated plainly:** Liquid is required rather than a bare
`/backlog/`, because this is a project site served from `/mindarchive/` and only
`relative_url` supplies the base. The cost is that these links render as literal
Liquid when the same file is read in GitHub's file browser. The published site
is the primary artefact, so site correctness wins — but it is a real cost, not a
free choice.

Links to `project-memory/` now point at GitHub, since that directory is
deliberately excluded from the site.

> **Amended 2026-09-11 by [D-043](#d-043--the-repositorys-canonical-documents-are-generated-as-site-pages).**
> That last paragraph no longer holds. Pointing at GitHub meant every such link
> left the site on `localhost:4000` and went nowhere at all before the
> repository was public. The documents are now generated as pages and linked
> with `relative_url` like everything else. The rest of this decision stands.

**Consequences:**

- A new page needs front matter **and** a `permalink`. Jekyll invents neither.
- Never add a top-level `permalink:` to `_config.yml` again. The comment there
  says so.
- `/docs/` is a hand-written index rather than a generated one — the ordering
  and the one-line descriptions are editorial and worth writing by hand.
- `/contribute/` summarises `CONTRIBUTING.md` for a site visitor and links to
  the canonical file rather than restating its rules, so the two cannot drift
  into conflict.

---

## D-035 — The blog is part of the Jekyll site, and nothing publishes itself
**Date:** 2026-09-10 · **Status:** Accepted

The blog lives in `docs/_posts/`, served at `/blog/` by the same Jekyll site as
the documentation. It uses `_layouts/post.html` on top of the shared
`_layouts/default.html`, so posts inherit the header, the three palettes, the
theme switcher and the footer with no extra work.

**Why not inside the application.** Serving `/blog` and `/docs` from
`localhost:5173` was requested and rejected. Port 5173 is the Vite dev server:
it exists only on a developer's machine during `dev.py up`, and the application
is local-first — it runs on each user's own computer over their own files.
Bundling the public marketing site into it would contradict D-008 (one page, no
router) and D-032 (the application is not hosted; Pages serves docs only), and
would need `react-router` plus a proxy to do worse what Jekyll does natively.
The two things stay on two ports: **:5173 the application, :4000 the site**.

**No plugins.** `jekyll-feed` is supported by GitHub Pages but is absent from
the `jekyll/jekyll:4` image used for local preview, so the local build and the
published build would differ — the exact drift D-033 exists to prevent.
`docs/feed.xml` is a few lines of hand-written Liquid and behaves identically in
both.

**`url` and `baseurl` stay unset in `_config.yml`.** This is a project site
served from `/mindarchive/`; `actions/configure-pages@v5` injects the right
values at build time. Hardcoding them would break local preview, where
`localhost:4000` serves from the root. The visible consequence is that
`feed.xml` carries relative links locally and absolute ones once published —
confirm the published feed after the first deploy.

**Nothing auto-publishes.** A post may be *drafted* from anything, including an
AI assistant and including the session records in
`project-memory/sessions/`, which already capture what changed and why. A
person approves before merge. Generated text published unread produces volume
rather than value, and a product whose whole argument is that it can be
inspected and trusted cannot have its public writing appear without a human
behind it.

**Consequences:**

- `docs/_drafts/TEMPLATE.md` holds the house style. Jekyll ignores `_drafts`
  unless built with `--drafts`, so it is never published — verified.
- `CONTRIBUTING.md` gained a *Writing a blog post* section, marked as applying
  once the CLA exists, so it does not contradict that file's own opening
  statement that outside code is not yet accepted.
- Posts need YAML front matter like every other page, for the reason in D-033.
- A post is not expected with every pull request. A blog filling with routine
  notes is worse than one that stays quiet.
- Verified by building with `jekyll/jekyll:4`: index and all four posts present,
  all four linked, template absent, `feed.xml` valid XML with four items, a post
  carrying the shared layout, `project-memory/` still excluded, no unrendered
  Liquid.

---

## D-034 — The appearance controls carry no visible group labels
**Date:** 2026-09-10 · **Status:** Superseded by [D-037](#d-037--one-header-row-appearance-is-two-menus-navigation-folds)

**Superseded the same day.** The segmented controls this describes were
replaced by two menu buttons. Its principle survived and was applied to the new
control: the group name is still carried in the accessible name — now on the
trigger, as "Palette: Light minimal" — while nothing redundant is printed on
screen.

The words "Palette" and "Theme" no longer appear above the segmented controls,
in the application or on the website. The `<legend>` elements remain in the
markup and are hidden with the standard visually-hidden pattern.

**Why:** Six option labels already say plainly what they are — "Light minimal /
Warm paper / Ink & violet" and "Light / Dark / System". Two uppercase headings
restating that in a header this small is clutter, and the project's UX rule is
to avoid exactly that.

**Why they are hidden rather than deleted.** A `<fieldset>` without a `<legend>`
gives a screen reader six loose radio buttons and no way to tell which three
belong together — "Light" would be announced with no indication it means the
theme rather than the palette. Accessibility is required here, not optional, so
the accessible name stays and only the pixels go.

**Consequences:**

- `.segmented__legend` is the visually-hidden rule in both
  `apps/web/src/styles.css` and `docs/assets/site.css`. Deleting a legend from
  the markup because it "does nothing" would be a regression; the comment above
  each rule says so.
- The column gap in `.appearance` widened from 20px to 24px. With no headings,
  that gap is the only thing stopping two controls reading as one row of six.
- A test asserts both groups still have accessible names. **It deliberately does
  not assert they are invisible** — jsdom does not load the stylesheet, so every
  element reports as visible there and such a test would be theatre. The visual
  half is verified by looking at the page.

---

## D-033 — The website shares the application's palettes, through one Jekyll layout
**Date:** 2026-09-09 · **Status:** Accepted

The documentation site carries the same appearance controls as the application:
the three palettes (Light minimal, Warm paper, Ink & violet) and a Light / Dark
/ System theme choice, in the same header position, storing the same
`localStorage` keys.

Delivered through `docs/_layouts/default.html` and `docs/assets/site.css`, which
use **the same token names** as `apps/web/src/styles.css`. The gem theme
(`jekyll-theme-primer`) is gone — it could not carry the controls, and a second
visual system would have guaranteed drift.

**Why a layout rather than styling the landing page alone.** The site is one
HTML page plus eleven Markdown documents rendered by Jekyll. Theming only
`index.html` would have given a themed front door opening onto unstyled pages.
The layout applies to everything, and `_config.yml` supplies it through
`defaults` so a new page needs only a title.

**The bug this fixed, which had already shipped.** The rebuilt landing page
linked to `PRODUCT.html`, `SECURITY.html` and so on. **Jekyll only converts
Markdown that has YAML front matter**; a file without it is copied verbatim. No
document in `docs/` had any, so none of those `.html` files would have existed
and every documentation link on the published site would have 404ed. It was
caught because the maintainer previewed the site and reported the 404s.

Two lessons, both written into `docs/GITHUB_PAGES.md`:

- Every Markdown file in `docs/` needs front matter. It is now the first thing
  that section says.
- **`python -m http.server` cannot validate this site.** It serves files as they
  are and runs no Jekyll, so `.md` never becomes `.html` — a correct site looks
  broken and a broken one cannot be told apart. The guide now gives a Docker
  one-liner that builds the real thing.

**Consequences:**

- Verified by building with `jekyll/jekyll:4` and checking the output: all nine
  linked pages present, no unrendered Liquid, every internal link resolving,
  `project-memory/` absent, and the controls present on a documentation page.
- The pre-paint script is duplicated in three places now — `apps/web/index.html`,
  `apps/web/src/theme.ts` and `docs/_layouts/default.html`. Deliberate: each has
  to run before its own first paint, and sharing code across two independent
  deployables would cost more than it saves. They must be kept in step.
- Without JavaScript the controls cannot work, so `.no-js` hides them rather
  than showing dead radios. The site still renders in Light minimal.
- Token values are duplicated between `styles.css` and `site.css`. The names are
  identical so a mismatch is obvious, but a change must be made in both.

---

## D-032 — Published publicly on GitHub; Pages for docs; no hosted application
**Date:** 2026-09-09 · **Status:** Partly superseded by D-046

> **Amended 2026-09-12 by [D-046](#d-046--proprietary-and-published-from-an-allowlist-into-a-separate-repository).**
> The publication half no longer holds: **this** repository stays private, and a
> separate public repository will be created later with clean history, populated
> from an allowlist. The reasoning below — *"a privacy-first product has to let
> people read what they are running"* — is why a public repository still exists
> in the plan at all; it is the **history** that is not published, not the idea.
> One clause is now simply wrong, and was argued against at the time by this very
> decision: it says `project-memory/` being public is acceptable. It is not.
> **The rest of this decision stands**, including the refusal to host the
> application and the refusal of a public demo.

Mind Archive is published as a **public** GitHub repository named
`mindarchive`. GitHub Pages serves `docs/` as the project website. **The
application itself is not hosted anywhere**, and there is **no public demo**.

**Why public.** The licence is PolyForm Noncommercial 1.0.0 — source-available.
A privacy-first product asking people to trust it with their conversations has
to let them read what they are running. A private repository would contradict
the claim.

**Why `docs/` only on Pages.** Pages serves static files. The application needs
the FastAPI backend, and hosting a copy would contradict local-first: people run
it themselves, on their own machine, over their own files. The site exists to
explain and to hand over the code.

**Everything is published, including `project-memory/`.** A separate branch
for a "clean" public version was considered and rejected: branches share
history, so it does not hide anything the moment the full history is pushed, and
maintaining two divergent branches means cherry-picking every change forever.
The real mechanism would have been two repositories, which was judged not worth
the standing risk of pushing to the wrong one. project-memory is already
excluded from the published *site* by `docs/_config.yml`, so only people reading
the repository see it — and for a source-available project the decision record
is arguably the most useful thing in it.

**Why there is no demo — the important part.** A public instance was requested
and refused, because `docs/SECURITY.md` is unambiguous: there is no
authentication, by design, because this is a single-user local application. A
publicly reachable instance today means one shared archive that anyone can read,
write to, and export. Whatever one visitor imports, every other visitor can
download. For a product whose premise is that your conversations stay yours,
that is precisely the failure it exists to prevent — and it would put strangers'
personal data on the maintainer's server.

A demo therefore needs a `MIND_ARCHIVE_DEMO` read-only mode that seeds synthetic
data and refuses every write, authentication at the proxy, TLS, and a production
frontend image. That is a milestone, not a deployment step. Recorded in
`docs/BACKLOG.md`.

**Consequences:**

- `docs/index.html` was rebuilt on the same token names as
  `apps/web/src/styles.css`, so the site and the application cannot drift apart
  unnoticed.
- The maintainer's email address becomes public. It was already committed in
  `project.json` and is the contact for commercial licences, so this is
  intended rather than incidental.
- `project.json` must carry the real GitHub username before the first push;
  `scripts/set_identity.py` propagates it. Until then, `YOUR-USERNAME` appears
  in the clone URL on the landing page.
- The current web Docker image runs the Vite dev server and is unsuitable for
  any public host. Milestone 7.
- Full instructions live in [`docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).

---

## D-031 — The page carries Support, Contribute and a real footer
**Date:** 2026-09-09 · **Status:** Accepted

Five sections now, each reachable from the header nav: Archive, Coming next,
Status, Support, Contribute — plus a footer carrying the copyright line, the
licence, contact and Back to top.

**"Coming next" is its own section again**, reversing point 4 of D-030 on the
same day. Folding it into Status was tidier on the page but wrong once it needed
a nav entry: a thing worth navigating to is a section, not a footnote inside
another one.

**Why Support and Contribute live in the application** rather than only on the
public site: someone deciding whether to fund a tool is using it at that moment,
and the licensing question — is my use commercial? — occurs to people while
working, not while browsing a marketing page.

**Nothing asks twice.** No modal, no banner, no dismissible nag, no counter. The
sections sit at the bottom of the page and are reached deliberately. Mind
Archive is free for noncommercial use and that is not a trial (D-016).

**Consequences:**

- `apps/web/src/support.ts` is the single place donation links, wallet addresses
  and the contact address are configured. **Every donation URL ships blank**,
  and `configuredDonations()` filters out anything unset, so the interface shows
  no dead links and no invented handles. Until they are filled in, the panel
  says so rather than pretending.
- `contactEmail` is taken from the `author` block already committed in
  `project.json`. It is public by design; if licensing mail should go elsewhere,
  change both.
- `mailto()` percent-encodes the subject. Without it, mail clients truncate at
  the first space — caught by a test, not by reading.
- The Contribute panel explicitly asks people **not** to send their export
  files when reporting an importer bug. A broken export is a copy of someone's
  private conversations, and inviting people to attach one would be a
  privacy-first product teaching the opposite habit.
- Five nav entries is the ceiling. AGENTS.md rules out heavy navigation, and a
  sixth would need something else to leave.

---

## D-030 — Import is a dialog; the header navigates within the one page
**Date:** 2026-09-09 · **Status:** Accepted

The workspace had grown long enough that importing meant scrolling past the
whole archive to reach it. Four changes, together:

1. **Import opens in a dialog**, from a button in the archive panel's header and
   a second one in the header nav. It closes on Escape, on a click outside it,
   and on its close button, and returns focus to whatever opened it.
2. **The export instructions sit behind a disclosure** inside that dialog. They
   matter enormously the first time and never again.
3. **The header carries in-page anchor links** to Your archive and Status, with
   the current section highlighted as you scroll. The header is sticky, and the
   footer has a Back to top link.
4. ~~**"What is coming next" moved inside the Status panel.**~~ **Reversed the
   same day by [D-031](#d-031--the-page-carries-support-contribute-and-a-real-footer)**,
   which gives it its own section and its own place in the nav. The other three
   parts of this decision stand.

**Why:** Importing is rare and searching is constant, so the archive earns the
top of the page and import earns a button rather than a permanent block. A
dialog was chosen over expanding the panel in place because it does not move the
archive underneath the reader.

**On D-008.** That decision says one page, no router, no sidebar — "there is one
view, so there is nothing to navigate between". That still holds. These are
in-page anchors, not routes: no route table, no history entries beyond the
fragment, no router dependency, and one view. D-008 is extended here, not
reversed. Had this needed real routes, it would have needed a separate decision
and an argument for the dependency.

**Consequences:**

- Inbox state moved out of `ImportPanel` into `useInbox`, because two places now
  need the waiting count: the panel, and the Import button that shows it while
  the panel is closed. One fetch, one answer.
- `Modal` is the project's first dialog primitive. Hand-written rather than the
  native `<dialog>` element, whose `showModal()` is not implemented everywhere
  the tests run — and rather than a dependency.
- `ArchivePanel` gained `id` and `action` props so App can put the Import button
  in its header without the two components knowing about each other. The header
  action row now renders even on an empty archive, which is exactly when Import
  matters most.
- `StatusPanel`'s heading changed from "Your archive" to "Status", which also
  ends a genuine duplication — `ArchivePanel` uses the same words.
- Smooth scrolling is CSS, and turns itself off under `prefers-reduced-motion`.
  The anchors are plain `<a href="#...">`, so they work without JavaScript.

---

## D-029 — Appearance is two choices: a palette, and light / dark / system
**Date:** 2026-09-09 · **Status:** Accepted

Mind Archive ships three palettes — **Light minimal** (the default), **Warm
paper** (the original) and **Ink & violet** — each drawn in light and dark. The
theme is a three-way choice: Light, Dark, or System. Both live in the header and
both persist:

```
mindarchive-palette   minimal | warm | violet     default: minimal
mindarchive-theme     light   | dark | system     default: system
```

**Why:** Two separate questions were being answered by one control. Which
colours the product uses is a matter of taste and should be the reader's to set;
whether the screen is light or dark usually belongs to the operating system.
Collapsing them into one toggle forced a choice on both.

The old two-way toggle also had a real defect: `getInitialTheme` resolved the
system preference into a concrete `light` or `dark` and `applyTheme` immediately
wrote it to storage, so a first visit permanently pinned the reader to whatever
their computer happened to say at that moment. There was no way to say "follow
the system". `system` is now a stored choice in its own right, and
`watchSystemTheme` keeps following it for as long as it is selected.

**Consequences:**

- The stylesheet never sees `system`. `resolveTheme` turns the choice into
  `light` or `dark` and `applyTheme` stamps that on `<html>`, so colours are
  selected by `[data-palette][data-theme]` alone. This removed the duplicated
  dark token block — the same values previously appeared in both
  `@media (prefers-color-scheme: dark)` and `:root[data-theme="dark"]`.
- The inline pre-paint script in `apps/web/index.html` now stamps both
  attributes and must stay in step with `apps/web/src/theme.ts`. It is the one
  deliberate duplication, and it exists so no one sees a flash of the wrong
  colours.
- Controls are real radio inputs in a `fieldset` (`SegmentedControl`), so
  keyboard and screen-reader behaviour is the browser's, not ours.
- `ThemeToggle.tsx` is removed; `AppearanceControls.tsx` replaces it.

**This supersedes the default stated in D-014, and keeps its principle.** Light
is still what a reader gets when nothing else is known: `system` falls back to
light whenever the browser cannot answer, and the default palette is a light
one. What changed is that a reader who wants to follow their computer can now
say so.

---

## D-017 — The repository stays local until there is something worth showing
**Date:** 2026-09-08 · **Status:** Superseded by [D-032](#d-032--published-publicly-on-github-pages-for-docs-no-hosted-application)

No git remote is configured. The project is developed locally, with CI and Pages
workflows in place but dormant until a remote exists.

**Why:** At Milestone 1 there is a foundation and no product. Publishing now
would put scaffolding in front of the first visitors and spend the launch on
nothing. The workflows are written and committed so that adding a remote is the
only step required later.

**Consequences:** `.github/workflows/` and the Pages setup are untested against
a live GitHub repository. The `YOUR-USERNAME` placeholders in URLs are resolved
by `project.json` and `scripts/set_identity.py` when a remote is chosen.

**Superseded 2026-09-09.** The condition it set has been met — five milestones,
a working product, a green gate. It did its job: the workflows were ready and
publishing needed no new infrastructure.

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
**Date:** 2026-09-08 · **Status:** Superseded by [D-029](#d-029--appearance-is-two-choices-a-palette-and-light--dark--system)

**Why:** Stated product requirement. The application should feel like a calm
document archive, and light is the appropriate default for a reading surface.

**Consequences:** The theme choice persists in `localStorage`. With no stored
choice, the system preference is honoured, falling back to light.

**Superseded 2026-09-09.** The principle stands — light is still what a reader
gets when nothing else is known. D-020 replaces the two-way toggle with a
palette choice and a three-way Light / Dark / System theme choice. D-029
supersedes only the shape of the control, not the principle.

---

## D-015 — Default branch is `main`; git identity is set per-repository
**Date:** 2026-09-08 · **Status:** Accepted

**Why:** `main` matches GitHub's default and avoids a rename after the first
push. The audit found no `user.name` or `user.email` configured locally or
globally, which would have made committing impossible; it is set locally so the
setting does not leak into the developer's other projects.
