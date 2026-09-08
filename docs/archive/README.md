# Archive

Original planning material from before Mind Archive had any code, kept verbatim.

**This is history, not documentation.** Nothing here is authoritative. Some of
it is already contradicted by decisions taken since. For what is actually true
now, read [`../../docs/`](../) and
[`../project-memory/`](../project-memory/).

You almost never need to open these files. The durable knowledge in them has
been extracted into project memory:

| Where the knowledge went | What it covers |
|---|---|
| [`project-memory/DISCUSSION_SUMMARY.md`](../project-memory/DISCUSSION_SUMMARY.md) | The conclusions these conversations reached |
| [`project-memory/RESEARCH.md`](../project-memory/RESEARCH.md) | Local AI tooling and hardware findings |
| [`project-memory/DECISIONS.md`](../project-memory/DECISIONS.md) | Decisions, numbered and dated |
| [`project-memory/AI_AGENT_PROTOCOL.md`](../project-memory/AI_AGENT_PROTOCOL.md) | The agreed working method |

## What is here

| File | What it is |
|---|---|
| `start.txt` | The planning conversation that produced the audit and Milestone 1 prompts, plus the recommended workflow |
| `SETUP.md` | Research comparing local AI coding agents — Qwen Code, OpenCode, Cline, Aider — and the hardware needed to run local models |
| `agent-tooling-research.md` | Shorter notes on the same topic. Was `.claude/code.md`, which put a transcript in a directory meant for agent rules |
| `structure.md` | An early proposed repository tree. Superseded by the actual layout |
| `pc_specs.md`, `pc_specs.sh` | Commands for measuring the development machine before choosing a local model |
| `first_time.md`, `local_claude.md` | Early prompt drafts. Were in `prompts/` |

## Why they were moved

On 2026-09-08 these files sat in the repository root and in `prompts/`, and
made up roughly half the repository by size. That contradicted the project's own
rule — *store durable knowledge, not chat noise* — and cost every AI agent
reading the repository a significant amount of context before it reached the
actual specification.

They were moved rather than deleted because the reasoning in them is
occasionally worth re-reading, and nothing had been committed yet, so deletion
would have been unrecoverable.

`MASTER.md` stayed at the repository root. It is the founding specification, not
a transcript, and it remains genuinely useful.

This folder is excluded from the published documentation site — see
[`../_config.yml`](../_config.yml).
