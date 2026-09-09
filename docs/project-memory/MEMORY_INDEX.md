# Memory Index

This folder is Mind Archive's **permanent project memory**.

The repository — not any AI chat history — is the source of truth. If a decision
matters, it belongs in a file here or in `docs/`. If it only exists in a
conversation with Claude, Gemini, Qwen, Cursor or ChatGPT, it does not exist.

## Where to find what

| File | What it holds | Read it when |
|---|---|---|
| [PROJECT_STATE.md](PROJECT_STATE.md) | What is actually built right now | Starting any session |
| [MILESTONES.md](MILESTONES.md) | The milestone plan and what is done | Planning work |
| [DECISIONS.md](DECISIONS.md) | Numbered, dated architectural decisions | Before changing architecture |
| [RESEARCH.md](RESEARCH.md) | Researched technical findings and assumptions | Before re-researching something |
| [AI_AGENT_PROTOCOL.md](AI_AGENT_PROTOCOL.md) | How any AI agent should work in this repo | Starting any session |
| [DISCUSSION_SUMMARY.md](DISCUSSION_SUMMARY.md) | Durable conclusions from planning conversations | Wondering *why* the project is shaped this way |
| [SESSION_LOG.md](SESSION_LOG.md) | One short entry per working session | Picking up where someone left off |
| [SESSION_PROTOCOL.md](SESSION_PROTOCOL.md) | How sessions are recorded, start and end | Beginning or ending a session |
| [sessions/](sessions/) | Full record of each session: what happened, the prompts, any report | Resuming work, or asking what was actually asked for |
| git history `fcf1f5c` | The original planning transcripts, before they were merged into the files above | Almost never |

## Session memory

Every working session leaves a folder under [`sessions/`](sessions/) holding
what was done (`SESSION.md`), the instructions given verbatim (`PROMPTS.md`),
and any report produced (`REPORT.md`).

This exists so the project survives losing a chat history — which happens
constantly: sessions time out, quotas run out, tools get switched. If work stops
unexpectedly, the last session folder says exactly where things stood and what
was left broken.

```bash
python scripts/session.py start "what you are about to do"
python scripts/session.py end
python scripts/session.py check      # also runs in CI
```

See [SESSION_PROTOCOL.md](SESSION_PROTOCOL.md).

## How this relates to the rest of the repository

```
prompts/MASTER.md          Founding specification. Historical intent.
    |
    v
docs/                      Living documentation. Current truth about the product.
    |
    v
docs/project-memory/       Why we got here, what state we are in, what is next.
    |
    v
AGENTS.md                  How to work here (all AI agents and humans).
```

If any two of these conflict, `docs/` and `docs/project-memory/` win over
`prompts/MASTER.md`, and the conflict must be resolved rather than left in
place.

## Rules for writing to project memory

1. Store **durable knowledge, not chat noise**.
2. Convert relative dates ("last week") to absolute dates.
3. Never paste an entire conversation into a memory file.
4. Update `PROJECT_STATE.md` whenever reality changes.
5. Add to `DECISIONS.md` whenever an architectural or product decision is made.
6. Append one concise entry to `SESSION_LOG.md` per working session.
7. Never record secrets, API keys, or personal archive contents.
