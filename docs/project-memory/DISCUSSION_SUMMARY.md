# Discussion Summary

Durable conclusions from the planning conversations that preceded the first
line of code. This is a summary, not a transcript — the original conversations
are kept verbatim in [`docs/archive/`](../archive/) if the reasoning is ever
needed in full.

## What Mind Archive is

**Your Personal AI Mind Archive.** *Own your AI memory. Simple, private, and
yours.*

A local-first, source-available application for preserving, organising,
searching, importing and exporting a person's AI conversations, memories,
knowledge and files — and for keeping them useful after that person changes AI
provider.

## Conclusions reached during planning

**The product exists to prevent lock-in.** Every other requirement follows from
this. A personal archive that lives on a provider's server is not an archive.
ChatGPT is only the first importer target; no provider may become the
architectural centre.

**Simplicity is a product requirement, not a preference.** The interface should
feel like a calm, modern document archive: a single primary workspace, minimal
top navigation, no permanent sidebars, no dashboards, no unnecessary animation.
Light mode by default with a dark toggle.

**"Must not look AI-generated" is a real constraint.** It applies to UI labels,
error messages, settings, commands and documentation. Write "Import archive",
not "Initialize ingestion pipeline". Write "Your archive is stored locally",
not "Local persistence subsystem operational". This shaped the decision to use
plain CSS rather than a component library.

**Human readability beats visual novelty**, and data portability beats database
convenience. The user's content lives in Markdown, JSON and plain text on their
own filesystem. SQLite indexes it; SQLite does not own it.

**Build in milestones, and keep the repository runnable after each one.** The
first version should be simple enough for one developer to understand every
line, while leaving clean extension points for importers, storage and sync.

**Do not overengineer.** No microservices, Kubernetes, Redis, Kafka or
Elasticsearch without a documented reason grounded in an actual requirement.

**The repository must be agent-neutral.** The project should be handable to
Claude, Gemini, Qwen, Cursor, Copilot, Aider, OpenCode or a human, and each
should understand it from the repository alone. This produced `AGENTS.md` as the
canonical instruction file, with per-tool files kept thin.

**Local AI coding tools are a development choice, not a product dependency.**
A possible future workflow uses Qwen Code or OpenCode with Ollama and a local
model to keep development costs near zero. Mind Archive itself must never depend
on any of them. See [RESEARCH.md](RESEARCH.md) R-002.

## What the audit of 2026-09-08 found

The repository at that point contained a strong specification and no
implementation. Specifically:

- `MASTER.md` held a comprehensive, sound specification.
- All ten `docs/*.md` files, plus `AGENTS.md` and `README.md`, were 0 bytes.
- `docs/project-memory/` did not exist, despite being described as existing.
- Roughly half the repository by size was raw conversation transcript.
- There was no `.gitignore` — a live risk for a privacy-first project.
- Git had no commits and no configured identity.
- `CLAUDE.md` instructed agents to treat five empty files as the source of
  truth, and never mentioned `MASTER.md`, where the truth actually was.

Milestone 1 addressed all of the above. See [SESSION_LOG.md](SESSION_LOG.md).

## Agreed working workflow

1. Establish the repository foundation (Milestone 1).
2. Verify it runs: tests, Docker, Git.
3. Commit cleanly.
4. Only then measure the machine's hardware and consider a local model.
5. Use a local agent for routine development; use a stronger hosted model when
   the reasoning warrants it.

The repository foundation comes first, deliberately, so that no AI tooling
choice is ever load-bearing.
