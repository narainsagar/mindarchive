# Report — 2026-09-08-02-archive-cleanup-and-dev-workflow

Audit of `docs/archive/`, and the decision to remove it.

---

## What was in the archive

Nine files, 2,565 lines, moved there during Milestone 1 rather than deleted
because nothing had been committed yet.

| File | Lines | Verdict |
|---|---|---|
| `start.txt` | 676 | Prompts, now verbatim in session 01's `PROMPTS.md`. Workflow already in `DISCUSSION_SUMMARY.md`. **Redundant** |
| `SETUP.md` | 636 | The only file with unextracted durable content — hardware tiers, agent ranking, builder/reviewer pattern. **Merged into `RESEARCH.md` R-002** |
| `local_claude.md` | 516 | The pasted prompt, verbatim in session 01's `PROMPTS.md`. **Redundant** |
| `first_time.md` | 479 | **99.6% identical to `local_claude.md`** — only 2 unique lines, both already in session 01's `PROMPTS.md`. **Redundant** |
| `structure.md` | 102 | Proposed tree, superseded by the actual layout and D-013. **Redundant** |
| `agent-tooling-research.md` | 61 | **Misnamed during the Milestone 1 move — it is a prompt, not research.** Duplicates `prompts/AI-CODING.md`. **Redundant** |
| `pc_specs.md` | 35 | Hardware probe commands. **Merged into `RESEARCH.md` R-002** |
| `pc_specs.sh` | 13 | Same commands as a script. **Merged, then redundant** |
| `README.md` | 47 | Index of the above. Redundant once the folder goes |

## What was merged

Into `project-memory/RESEARCH.md`, R-002:

- Qwen Code's own hardware requirements, as distinct from the model's
- The three machine tiers (minimum practical / recommended / enthusiast)
- The agent ranking reached during planning
- The proposed builder/reviewer two-agent pattern, marked as never adopted
- The hardware probe commands from `pc_specs.md` and `pc_specs.sh`

Everything else was already represented in `RESEARCH.md`,
`DISCUSSION_SUMMARY.md`, `DECISIONS.md`, `AI_AGENT_PROTOCOL.md`, or session
01's verbatim `PROMPTS.md`.

## Decision: delete the folder

All nine files are committed in `fcf1f5c`, so **removal is fully recoverable
via git history** — which is what made deletion the right call rather than a
risk. Keeping a second, worse copy in the working tree earns nothing.

This also honours the project's own rule, *store durable knowledge, not chat
noise*, and removes 2,565 lines that every AI agent would otherwise read past.

Dangling references were fixed in `CLAUDE.md`, `GEMINI.md`, `QWEN.md`,
`MEMORY_INDEX.md`, `DISCUSSION_SUMMARY.md`, `RESEARCH.md`, `CHANGELOG.md`, and
session 01's `PROMPTS.md`, each now pointing at commit `fcf1f5c` instead.

## Correction to the Milestone 1 record

Session 01 renamed `.claude/code.md` to `docs/archive/agent-tooling-research.md`
on the assumption it held agent research. It did not — it was an early prompt.
The Milestone 1 session record describes the move accurately; only the chosen
name was wrong, and the file is now gone.

## Second half of this session: workflow changes

Two decisions recorded, both from explicit direction:

**D-018 — verification is developer-controlled.** Tests no longer run on every
change. Required at three points: before a milestone is complete, before a pull
request, before a release. `scripts/dev.py verify` is the gate.

**D-019 — Docker containers are disposable.** Every check runs in a throwaway
container; `verify` tears the stack down; `dev.py clean` removes this project's
containers, volumes and images. `./data` is a bind mount, so no cleanup command
can reach the user's archive.

`scripts/dev.py` was written to serve both, giving one entry point for the
stack (`up`, `down`, `stop`, `logs`, `status`, `clean`) and for checks (`test`,
`lint`, `types`, `format`, `build`, `verify`).
