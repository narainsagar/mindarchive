# AI Agent Protocol

How any AI coding agent — Claude, Gemini, Qwen, Cursor, Copilot, Aider,
OpenCode, or a local model — should work in this repository.

Humans are welcome to follow it too; it is just a sensible working method.

## The rule behind every other rule

**The repository is the permanent memory. Chat history is temporary.**

Never rely on a conversation as the only record of a decision. If something
matters, it is written down here before the session ends.

## Read order at the start of a session

Do not read the whole repository. Read these, in this order, and stop:

1. `AGENTS.md` — how to work here
2. `docs/project-memory/PROJECT_STATE.md` — what actually exists right now
3. `docs/project-memory/MILESTONES.md` — what is in scope
4. `docs/project-memory/DECISIONS.md` — what has already been decided
5. `git status` and recent `git log`

Then, and only then, locate the files your specific task touches.

Read `docs/ARCHITECTURE.md`, `docs/PRODUCT.md`, `docs/DEVELOPMENT.md` or
`docs/SECURITY.md` when your task touches those areas. Read `MASTER.md` only for
historical intent — `docs/` describes the product as it is now.

## Working method

**Before changing anything:**

1. Identify the relevant architecture and requirements.
2. Identify exactly which files are affected.
3. Identify whether a project decision changes. If it does, say so before you
   implement it.
4. Choose the smallest coherent change that fully solves the task.

**While changing things:**

- Do not blindly rewrite working code.
- Do not refactor code unrelated to the task.
- Do not silently change an architectural decision.
- Do not create a fake implementation to make a task look complete.
- Do not add a dependency without a reason you can state in one sentence.

**After changing things:**

1. Run the tests and checks. Actually run them.
2. Review the diff.
3. Update the documentation that the change affects.
4. Update project memory (see below).
5. Check for security and privacy consequences.
6. Report what changed and what remains.

## Never claim something works unless you ran it

This is not negotiable. Code inspection is not verification. If a check failed,
say it failed and show the output. If you skipped a step, say you skipped it.

## Updating project memory

At minimum, before ending a working session:

| If this happened | Update this |
|---|---|
| What exists in the repo changed | `PROJECT_STATE.md` |
| An architectural or product decision was made | `DECISIONS.md` |
| A researched assumption changed | `RESEARCH.md` |
| Milestone progress changed | `MILESTONES.md`, `docs/ROADMAP.md` |
| Any working session at all | `SESSION_LOG.md` |
| Behaviour changed | the relevant file in `docs/` |
| Development commands changed | `docs/DEVELOPMENT.md`, `README.md` |

Store durable knowledge. Do not paste conversations into the repository.

## Scope discipline

Work on the current milestone only. Do not start the next one because the
current one looks finished — say it looks finished and stop.

If you find a real problem outside your task, write it in `docs/BACKLOG.md`
rather than fixing it inline.

## Security obligations

- Never commit secrets, API keys, tokens, private keys, or personal archives.
- Treat every imported file as untrusted input.
- Never log private conversation content unnecessarily.
- Never enable cloud functionality by default.
- Check filesystem paths for traversal before using them.

## When you are uncertain

Choose the simplest maintainable approach and document the assumption. If
proceeding either way would waste real work, stop and ask.

If two project documents conflict, do not pick one silently. Name the conflict,
resolve it deliberately, and update both.
