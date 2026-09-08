# Session Protocol

How every working session on Mind Archive is recorded in the repository.

## Why this exists

AI chat history disappears. Sessions time out, quotas run out, context windows
fill up, tools get switched, machines get rebuilt. If the only record of what
happened lives in a conversation, the project loses its memory the moment that
conversation ends.

So the repository records it instead. Any agent — or any human — can open the
last session folder and know exactly what was done, what was asked, what was
decided, and what was left unfinished.

This is what makes "pick up where we left off" a real capability rather than a
hope.

## Where it lives

```
docs/project-memory/
├── SESSION_LOG.md              Short entry per session. The index.
├── SESSION_PROTOCOL.md         This file.
└── sessions/
    ├── TEMPLATE/               Copied when a session starts
    │   ├── SESSION.md
    │   ├── PROMPTS.md
    │   └── REPORT.md
    └── YYYY-MM-DD-NN-slug/     One folder per session
        ├── SESSION.md          What happened. The main record.
        ├── PROMPTS.md          The prompts given, verbatim.
        └── REPORT.md           Any report produced — audit, review, findings.
```

Folder names are `YYYY-MM-DD-NN-slug`: the date, a two-digit counter for
multiple sessions in one day, and a short kebab-case description. They sort
chronologically and read clearly in a directory listing.

## What goes in each file

**`SESSION.md`** — the record. Goal, what was actually done, decisions made,
files touched, checks run *and their real results*, what remains, and the exact
next step. This is the file someone reads to resume the work.

**`PROMPTS.md`** — the instructions given during the session, verbatim, in
order. Not the responses. This preserves intent, which summaries lose. If a
prompt contains a secret, redact it and say that you did.

**`REPORT.md`** — any substantial report the session produced: an audit, a
security review, a design analysis. Stored as it was written. If the session
produced no report, the file says so.

## At the start of a session

```bash
python scripts/session.py start "short description of the work"
```

This creates the folder and scaffolds the three files.

Then, before touching any code:

1. Read `AGENTS.md`.
2. Read `PROJECT_STATE.md` — what exists right now.
3. Read `MILESTONES.md` — what is in scope.
4. Read `DECISIONS.md` — what is already settled.
5. Read the previous session's `SESSION.md` — what was left unfinished.
6. Check `git status` and recent `git log`.

Record the session's goal in `SESSION.md` and paste the opening prompt into
`PROMPTS.md`.

## During the session

Append each new instruction to `PROMPTS.md` as it arrives — not at the end,
when the session may already have been cut short.

If a decision gets made, write it into `DECISIONS.md` *then*, not later.

## At the end of a session

```bash
python scripts/session.py end
```

Then complete the record:

1. Fill in `SESSION.md` — including checks that **failed**, honestly.
2. Confirm `PROMPTS.md` is complete.
3. Add `REPORT.md` if the session produced a report.
4. Update `PROJECT_STATE.md` if what exists changed.
5. Update `MILESTONES.md` and `docs/ROADMAP.md` if progress changed.
6. Add a short entry to `SESSION_LOG.md` linking the session folder.
7. Run `python scripts/session.py check`.
8. Review `git status` and commit.

## If a session ends unexpectedly

Quota exhausted, a crash, an interruption — the record must still be usable.

That is why `SESSION.md` and `PROMPTS.md` are written **as the session
progresses**, not composed at the end. A half-finished session record that
says "stopped mid-way through the frontend; backend tests passing; next step is
the theme toggle" is worth far more than a perfect record that was never
written.

If you find a session folder with no end time, that session was interrupted.
Read it, finish or correct whatever it left broken, and note in your own
session record that you did.

## Verifying the memory

```bash
python scripts/session.py check
```

It verifies that every required project-memory file exists, that every session
folder has its records, that every session is listed in `SESSION_LOG.md`, and
that nothing resembling a secret has been committed to project memory. It runs
in CI on every push.

## What not to record

- Whole conversations. Store the prompts and the durable conclusions.
- Secrets, API keys, tokens, credentials — redact and note the redaction.
- Personal archive content.
- Speculation. Record what happened, not what you assume happened.
