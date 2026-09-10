---
title: Backlog
permalink: /backlog/
---

# Backlog

Ideas, known gaps and deferred work that are not yet part of a milestone.

Adding something here is how you avoid doing unrelated work mid-task. Nothing
here is a commitment.

---

## Known gaps from Milestone 1

- **Project identity is a placeholder.** `github.username` and
  `copyright.holder` in `project.json` still hold placeholder values. Fill them
  in and run `python scripts/set_identity.py --git` to propagate them.
- **No `git remote`.** Deliberate for now — see decision D-017. CI and Pages
  workflows are committed but dormant until a remote exists, so neither has been
  exercised against a live GitHub repository.
- **Frontend Docker image is a dev server.** Fine for local use; a production
  image would build static assets and serve them behind nginx or similar.
  Milestone 7.
- **No `.gitattributes` line-ending policy verified on Windows.** Added, but
  only exercised on one machine so far.
- **CI does not yet run the Docker build.** Compose config is validated; a full
  image build in CI would be slower but catch more.

## Deployment

**Decided (D-032):** public GitHub repository, Pages for the documentation site,
no hosted application, no public demo. Steps are in
[DEPLOYMENT.md]({{ '/deployment/' | relative_url }}).

Still open:

- **The first push has not happened.** `project.json` needs the real GitHub
  username; the workflows have still never run against a live repository.
- **Production frontend image.** The current web image runs the Vite dev server.
  Anything hosted needs a static build behind nginx or similar. Milestone 7.
- **Release process, versioning and packaging.** Milestone 7. `DEPLOYMENT.md`
  has the manual steps in the meantime.
- **Custom domain `mindarchive.app`.** DNS and `docs/CNAME` documented, not set
  up.

### A public demo — what it would actually take

Requested and deliberately deferred (D-032). Hosting the application as it
stands would mean one shared archive with no authentication: whatever any
visitor imports, every other visitor can read and export. That is the failure
this product exists to prevent, and it would put strangers' private
conversations on the maintainer's server.

Not a deployment step. The work:

- **`MIND_ARCHIVE_DEMO` read-only mode.** Seeds a synthetic archive at startup
  and refuses every write — import, tag, delete, inbox scan — at the API layer,
  not by hiding buttons. The interface should say plainly that it is a demo and
  that uploads are disabled, rather than failing silently.
- **Synthetic seed data** that shows search and tags working without being
  anyone's real conversations.
- **Authentication and TLS at a reverse proxy**, so the API is never directly
  reachable even read-only.
- **A decision record**, because this changes the security model the product is
  built on.

Until all four exist, the honest answer to "can I see it live" is a screenshot
and `docker compose up`.

## Commercial and licensing

None of this is application work — it belongs on the project website, not in
this repository. Recorded here so the plan is not lost. See
[LICENSING.md](https://github.com/RootedGlobal/mindarchive/blob/main/LICENSING.md) and decision D-016.

**Decided (D-038):** a **merchant of record** — Polar, Paddle or Lemon Squeezy —
sells both the licence and the donations. They are the legal seller and remit
VAT and sales tax everywhere, which raw Stripe or PayPal would leave with the
maintainer from the very first EU sale. Checkout is **hosted, reached by plain
links**: no payment script on the site, no embedded frame, nothing tracking a
visitor who has not chosen to pay.

The page is built: `/support/`, driven entirely by `docs/_data/support.yml`.

Still open:

- **The URLs are blank.** An account has to exist before anything can be sold.
  Blank entries render nothing, so the page is honest in the meantime and
  points at the contact address instead.
- **Contributor Licence Agreement.** Required before any outside contribution
  can be merged, because contributed code must be includable in commercially
  licensed releases. Blocking for accepting pull requests.
- **Volume pricing.** $39 per seat at 10+, enterprise on request. Configured at
  the provider, not in this repository. Anchor at $49 and discount if needed —
  raising prices later punishes early buyers.
- **Licence key or activation.** Probably unnecessary and contrary to the
  product's spirit — commercial licensing can be honour-based, as Obsidian's is.
  Decide deliberately rather than by default. Any phone-home mechanism would
  contradict the privacy model **and break the promise in LICENSING.md**.
- **What the buyer actually receives.** With a merchant of record this is a file
  attached to the receipt. It does not exist yet.
- **A real test purchase**, on both paths, before announcing either anywhere.
  Nothing about payment can be verified from this repository.
- **Crypto** is donations only, as a published address — never for licences,
  which need a buyer you can identify and a receipt you can produce.

## Faster and easier import

Done in Milestone 3.5: watched inbox folder, re-import reporting, correct
guidance, and an optional browser script. See decisions D-023 and D-024, and
[RESEARCH.md](https://github.com/RootedGlobal/mindarchive/blob/main/project-memory/RESEARCH.md) R-004 for the export's real timings.

Still open:

- **Progress reporting during a long import.** A large archive on a slow
  filesystem takes minutes (R-005). The import runs on a background thread so
  nothing blocks, but the interface says nothing while it works.
- **A filesystem watcher.** Scanning on startup, on demand and on window focus
  covers every case so far. `watchdog` only if that stops being true.
- **Verify the browser script's output shape** against a real official export.
  Believed identical; unconfirmed.
- **Import several exports at once, in the background.** Choose multiple `.zip`
  or `.json` files and start them all with one action. The work must survive the
  import dialog being closed — closing the dialog cancels nothing. While it
  runs, the interface reports progress outside the dialog ("2 files waiting",
  "importing 3 of 5", "syncing"), as a notice that dismisses itself after a few
  seconds, with the option to dismiss it sooner or cancel the run outright.
  Needs: a job with an id and a status the frontend can poll, per-file results
  rather than one combined summary, and a decision on what "cancel" means for a
  file already half-written. The backend already imports on a background thread,
  so the groundwork is there; what is missing is a way to ask how it is going.
  Related: **Progress reporting during a long import**, above — the same
  mechanism serves both.

## Importing from more providers

**Already supported:** ChatGPT and Claude, both as `.zip` and as raw `.json`.
Detection is by the *shape* of the file, not its name (D-027), which is what
makes a bare `conversations.json` from either service work — they share that
filename. `apps/api/src/mind_archive/importers/` holds one adapter per provider
and the core imports none of them.

Still open:

- **Gemini, Cursor, Copilot, Perplexity, local runners, and whatever comes
  next.** Each is one adapter plus one test. The constraint is not the code, it
  is getting a real export of each format to write the adapter against.
- **A fixture per provider.** ChatGPT and Claude are covered by
  `test_chatgpt_importer.py` and `test_claude_importer.py`. New providers need
  the same. **Fixtures must be hand-written or heavily redacted, never a real
  personal export** — test files are committed, and a real export is a copy of
  someone's private conversations. Keep working copies of real exports in
  `tmp/` (git-ignored) while writing an adapter, and commit only a small
  synthetic sample that exercises the shape.
- **Say plainly which providers are supported**, in the import dialog and on the
  public page, so nobody exports from a service that will not import.

## Storage

- **`StorageProvider` interface.** Deferred from Milestone 5 to Milestone 6
  (D-028), where a real cloud adapter can shape it. An interface with one
  implementation is a guess about the second.

## Organisation

- **Projects.** Deferred in Milestone 4 (D-026). If still wanted after living
  with tags, most likely a reserved tag namespace (`project/bread`) rather than
  a parallel hierarchy — a second way to organise the same things needs a real
  reason to exist.
- **Renaming a tag everywhere**, and merging two tags.
- **Bulk tagging** from the list rather than one conversation at a time.
- **Suggested tags** from what is already in use, once there are enough to make
  typing them again tedious.

## Product ideas

- Import from Gemini, Google AI Studio, Copilot and local tools
- Attachments and images inside imported conversations
- Saved searches
- Timeline view of an archive
- Statistics that are genuinely useful rather than decorative
- Whole-archive export as a single portable bundle
- A command-line interface for import, search and export
- Optional local embedding-based semantic search, with no external service

## Technical ideas

- Rebuild the SQLite index from the filesystem as an explicit, tested command
- Structured logging with an explicit guarantee that content is never logged
- A schema version and migration path for the metadata database
- Import performance work — a large ChatGPT export is a real test case
- Accessibility audit with a screen reader
- Keyboard-first navigation
- Print stylesheet for reading and exporting conversations

## Explicitly rejected

Kept here so they are not re-proposed without new information.

- **Elasticsearch or OpenSearch.** SQLite FTS is sufficient for a personal
  archive. Revisit only with evidence of a real limit.
- **Redis, Kafka, Celery, RabbitMQ.** No requirement. The in-process event bus
  covers V1. See decision D-009.
- **Kubernetes or microservices.** A single-user local application.
- **A UI component framework.** See decision D-008.
- **Authentication and multi-user support.** Not before Milestone 7, and only
  if there is a genuine reason.
- **Telemetry of any kind.** Contradicts the product.
- **Mind Archive calling ChatGPT's undocumented API itself.** It would need a
  session token, which grants full account access — reading everything and
  sending messages as the user. Asking for that credential would contradict the
  entire product. The supported fast path is a script the user runs in their own
  browser, where the token never leaves the tab. See decision D-024.
- **Asking anyone to paste a session token into Mind Archive.** Not opt-in, not
  behind a warning, not at all.
