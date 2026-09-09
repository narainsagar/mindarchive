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

## D-032 — Published publicly on GitHub; Pages for docs; no hosted application
**Date:** 2026-09-09 · **Status:** Accepted

Mind Archive is published as a **public** GitHub repository named
`mind-archive`. GitHub Pages serves `docs/` as the project website. **The
application itself is not hosted anywhere**, and there is **no public demo**.

**Why public.** The licence is PolyForm Noncommercial 1.0.0 — source-available.
A privacy-first product asking people to trust it with their conversations has
to let them read what they are running. A private repository would contradict
the claim.

**Why `docs/` only on Pages.** Pages serves static files. The application needs
the FastAPI backend, and hosting a copy would contradict local-first: people run
it themselves, on their own machine, over their own files. The site exists to
explain and to hand over the code.

**Everything is published, including `docs/project-memory/`.** A separate branch
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
- Full instructions live in [`docs/DEPLOYMENT.md`](../DEPLOYMENT.md).

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
mind-archive-palette   minimal | warm | violet     default: minimal
mind-archive-theme     light   | dark | system     default: system
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
