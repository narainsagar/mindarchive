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

## Commercial and licensing

None of this is application work — it belongs on the project website, not in
this repository. Recorded here so the plan is not lost. See
[LICENSING.md](../LICENSING.md) and decision D-016.

- **Contributor Licence Agreement.** Required before any outside contribution
  can be merged, because contributed code must be includable in commercially
  licensed releases. Blocking for accepting pull requests.
- **Merchant of record, not raw Stripe.** Selling internationally means EU VAT,
  UK VAT and US sales tax liability. Lemon Squeezy, Paddle and Polar act as
  merchant of record and handle all of it for a few percent. Raw Stripe or
  PayPal leaves the tax compliance burden on the seller. Evaluate before taking
  the first payment.
- **Commercial licence pricing.** $49 per seat perpetual with one year of
  updates; $39 per seat at 10+; enterprise on request. Anchor here and discount
  if needed — raising prices later punishes early buyers.
- **Donations.** Coffee $5, beer $10, lunch $20, or a custom amount. Optional,
  unlocks nothing, funds ongoing importer maintenance as provider export formats
  change.
- **Licence key or activation.** Probably unnecessary and contrary to the
  product's spirit — commercial licensing can be honour-based, as Obsidian's is.
  Decide deliberately rather than by default. Any phone-home mechanism would
  contradict the privacy model.
- **Website.** Downloads, pricing, donations and documentation. The application
  must never contain payment code or contact a server.

## Product ideas

- Import from Claude, Gemini, Google AI Studio, Copilot and local tools
- Attachments and images inside imported conversations
- Deduplication when the same export is imported twice
- Incremental import — only what is new since last time
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
