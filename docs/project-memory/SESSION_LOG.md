# Session Log

One concise entry per working session. Newest first. Durable facts only — what
changed and why, not conversation.

---

## 2026-09-08 — Milestone 4: tags

**Session:** [2026-09-08-06-milestone-4-tags-and-organisation](sessions/2026-09-08-06-milestone-4-tags-and-organisation/SESSION.md)
· [prompts](sessions/2026-09-08-06-milestone-4-tags-and-organisation/PROMPTS.md)
· [report](sessions/2026-09-08-06-milestone-4-tags-and-organisation/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

**One question shaped the whole milestone.** Everything in the archive so far is
*derived* — conversations from an export, Markdown from those, the index from
the Markdown. Tags are the first thing a person **makes**. Putting them in
SQLite would have made a rebuildable cache load-bearing and broken D-004 exactly
where it would destroy original work. They live in `metadata.json`; SQLite
indexes them and holds nothing else (**D-025**).

**And the bug that would have followed.** Every ChatGPT export is a full export,
so re-importing rewrites every `metadata.json` — and an export has no tags. Done
naively, next month's import would have erased months of someone's filing,
silently, with nobody noticing until far too late. The writer merges tags
forward, and the test is named after that failure.

**Scope.** Only tags, not the full "Project, Memory, Document..." list
originally specified (**D-026**). Tags plus search already answer *"where is
that conversation about X?"*; building a second hierarchical scheme at the same
time means guessing how they interact before anyone has used either.

**Found by the tooling.** `Object.entries(undefined)` blanked the entire archive
panel when a response lacked `tags` — a fair stand-in for a cached frontend
meeting a newer backend. mypy caught a signature that lied: `clean_tags` claimed
`list[str]` while genuinely reading untrusted JSON. Six SQL-injection warnings
were checked rather than suppressed — the tag is a bound parameter and only our
own literals are interpolated — and each suppression carries its reasoning.

**Verified** with `dev.py verify`: 254 backend tests (was 217), 64 frontend (was
54), full gate green. **Not yet clicked through in a browser** — the user's WSL
environment is still the blocker, not the code.

**Outstanding, still:** no real ChatGPT export has been imported. Four
milestones now.

---

## 2026-09-08 — Import ergonomics: the inbox and honest re-import reporting

**Session:** [2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting](sessions/2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting/SESSION.md)
· [prompts](sessions/2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting/PROMPTS.md)
· [report](sessions/2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

Milestone 3.5, prompted by the importer having gone three milestones without
seeing a real export. The obstacle was the product, not the code.

**Research corrected the premise** (R-004). OpenAI's own email says an export
"may take a few days". The famous "24 hours" is how long the **download link**
lasts — a deadline, not a wait — and only the most recent request is fulfilled,
so asking twice cancels your own job. Our import panel had that number exactly
backwards. There is no official API for ChatGPT history, so the wait cannot be
automated.

**The inbox** (D-023): drop an export into a folder and it imports itself. No
filesystem watcher — three scan triggers cover it. Configurable to a folder you
already keep exports in, and **that folder is read, never rearranged**; a ledger
remembers instead.

**Honest re-import reporting.** Every export is a full export, so re-importing
now says "12 new, 8 updated, 392 already in your archive", and unchanged
conversations are not rewritten at all.

**The fast path** (D-024): a script the user runs in their own logged-in tab.
No token is pasted anywhere, and Mind Archive never contacts OpenAI. Tools that
ask you to paste a session token are a different and much worse proposition —
that token can send messages as you. Mind Archive calling those endpoints itself
is rejected outright.

**Measuring beat guessing.** A 2,000-conversation import took 194s and looked
like a code problem. It takes 4.7s on the container filesystem and 127s on the
Windows bind mount — **27× slower, same code** (R-005). No optimisation needed;
recorded so nobody optimises the wrong thing later. It did justify moving the
startup scan to a background thread, after an inline version left the server
refusing connections for minutes.

**`inspect_export.py` leaked content in its first draft** by listing archive
filenames — ChatGPT names attachments after what they are. A tool built to avoid
leaking leaked, on draft one.

**Verified**: 217 backend tests (was 197), 54 frontend (was 45), full gate
green, plus 2,000 conversations imported end to end with the API responsive
throughout.

**Outstanding, still:** no real ChatGPT export has been imported. This makes it
cheap rather than replacing it.

---

## 2026-09-08 — Milestone 3: archive browser and search

**Session:** [2026-09-08-04-milestone-3-archive-browser-and-search](sessions/2026-09-08-04-milestone-3-archive-browser-and-search/SESSION.md)
· [prompts](sessions/2026-09-08-04-milestone-3-archive-browser-and-search/PROMPTS.md)
· [index and search notes](sessions/2026-09-08-04-milestone-3-archive-browser-and-search/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

You can now read and search what you imported, rather than opening the files
yourself.

**The index stays honest.** SQLite with FTS5, built three ways from one code
path: at startup when the archive has content but the index does not, on import
through the `conversation.created` event, and on demand. The D-004 rule — the
database is derived, never original — is enforced by
`test_deleting_the_database_loses_nothing`, which deletes it, rebuilds, and
requires identical results.

**Search takes what people type.** `MATCH` is a query language; a search box is
not. `C++`, `NEAR(` and a lone `"` are all FTS5 syntax errors, so input is split
into quoted words joined with `AND`, last word prefixed. All words must match,
the last matches as a prefix, and nothing searchable means no filter rather than
no results (D-022).

**Conversations are rendered as whole Markdown files** (D-020) rather than
parsed back into messages — round-tripping our own rendering would break on a
message containing `## You`, and the file is the readable artefact anyway. Read
from disk, not the index, so a hand-edited file shows immediately.

**Untrusted content cannot become markup.** `react-markdown` with raw HTML off
for bodies (D-021), and `<<`/`>>` delimiters rather than HTML for search
snippets. Both tested with an `<img onerror=...>`.

**A real design flaw, found by a failing test.** The index event handler called
the cached `get_settings()`, so it ignored dependency overrides and indexed the
real archive while the route wrote to a temporary one. Settings are now bound
when the handler is built; `lifespan` had the same problem. Separately, an
unusable archive folder used to crash startup and now logs and continues.

**Verified** with `dev.py verify`: 197 backend tests (was 137), 45 frontend
(was 29), ruff, mypy strict, eslint, tsc, production build — all passed. Also
end-to-end against the running stack: import, list, search, prefix search, read,
rebuild, hostile paths, and the web interface serving.

**Outstanding, unchanged:** no real ChatGPT export has been imported yet.

---

## 2026-09-08 — Milestone 2: the ChatGPT importer

**Session:** [2026-09-08-03-milestone-2-chatgpt-importer](sessions/2026-09-08-03-milestone-2-chatgpt-importer/SESSION.md)
· [prompts](sessions/2026-09-08-03-milestone-2-chatgpt-importer/PROMPTS.md)
· [format and security notes](sessions/2026-09-08-03-milestone-2-chatgpt-importer/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

Mind Archive can now archive something.

**The importer interface.** `detect()`, `validate()`, `parse()` and a registry,
so core code never imports a provider module. `parse()` writes nothing — it
returns `Conversation` objects and storing them is the archive's job, which kept
every parser test filesystem-free.

**The ChatGPT parser.** The format's real difficulty is that `mapping` is a
tree, not a list: editing or regenerating a message forks the conversation
rather than replacing anything. Walking up from `current_node` gives what the
person last saw. Abandoned branches are deliberately not imported. Full notes in
the session report.

**Hostile input** is the theme of this milestone. Zip slip, zip bombs, size
caps, and conversation titles that try to escape the archive when they become
folder names. `local/` was created and git-ignored *before* any importer code,
so a real export can never be committed by accident.

**Three real problems found and fixed.** A hostile archive was being reported as
merely "not recognised", which was untrue. The interface showed
`/data/archive` — the path inside the container, which does not exist on the
user's machine; `MIND_ARCHIVE_DISPLAY_DATA_DIR` fixes that. An unwritable
archive folder produced a raw 500 instead of an explanation.

**Verified** with `dev.py verify`: 137 backend tests (was 33), 29 frontend
tests, ruff, mypy strict, eslint, tsc, production build — all passed. Also
tested end-to-end against the running stack with a synthetic export containing a
normal, an awkward and a broken conversation.

**Outstanding:** only synthetic exports have been tested. The user is placing a
real ChatGPT export in `local/`; verifying against it is the next step, before
Milestone 3.

---

## 2026-09-08 — Archive cleanup and developer-controlled workflow

**Session:** [2026-09-08-02-archive-cleanup-and-dev-workflow](sessions/2026-09-08-02-archive-cleanup-and-dev-workflow/SESSION.md)
· [prompts](sessions/2026-09-08-02-archive-cleanup-and-dev-workflow/PROMPTS.md)
· [archive audit](sessions/2026-09-08-02-archive-cleanup-and-dev-workflow/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

Groundwork before Milestone 2, all from explicit direction.

**`docs/archive/` removed.** Audited all nine files: only `SETUP.md` held
durable content not already in project memory, and it was merged into
`RESEARCH.md` R-002 with the `pc_specs` probe commands. The rest were duplicates
of session 01's verbatim prompts or superseded by the real repository layout.
Deleted rather than kept, because all nine are committed in `fcf1f5c` and so
remain recoverable. Eight files with dangling links now point at that commit.
Also caught a Milestone 1 mistake: `agent-tooling-research.md` was misnamed —
it was a prompt, not research.

**D-018 — verification is developer-controlled.** Tests no longer run on every
change. Required before a milestone completes, before a pull request, and before
a release. Exploratory work is expected to leave the code broken; a slow gate
after every edit gets skipped, which is worse than an explicit one.

**D-019 — Docker containers are disposable.** Checks run in throwaway
containers, `verify` tears the stack down, `clean` removes this project's
images. `./data` is a bind mount, so no cleanup command can touch the archive.

**`scripts/dev.py`** added as the single entry point for both the stack and the
checks. Two small bugs fixed along the way: `slugify` truncated session folder
names mid-word, and `dev.py` emitted ANSI escapes into consoles that cannot
render them.

**Verified** with `dev.py verify`: 33 backend tests, 19 frontend tests, ruff,
mypy strict, eslint, tsc, production build — all passed. The memory check
correctly failed until this session's record was written.

**Next:** Milestone 2, the ChatGPT importer.

---

## 2026-09-08 — Audit and Milestone 1

**Session:** [2026-09-08-01-audit-and-milestone-1](sessions/2026-09-08-01-audit-and-milestone-1/SESSION.md)
· [prompts](sessions/2026-09-08-01-audit-and-milestone-1/PROMPTS.md)
· [audit report](sessions/2026-09-08-01-audit-and-milestone-1/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

**Audit findings.** The repository held a strong specification (`MASTER.md`) and
no implementation. All ten `docs/*.md` files, `AGENTS.md` and `README.md` were
0 bytes. `docs/project-memory/` did not exist despite being described as
existing. There was no `.gitignore`, no `.env.example`, and no `LICENSE`. Git
had no commits and no configured `user.name` or `user.email`, so committing was
impossible. About half the repository by size was raw conversation transcript.
`CLAUDE.md` directed agents to read five empty files as the source of truth and
never mentioned `MASTER.md`.

**Measured environment.** Windows 11; Node.js absent on the Windows host and
v24.18.0 in WSL2 (Ubuntu 22.04.2); Python 3.7.9 on Windows and 3.8.10 in WSL2,
both end-of-life; Docker 29.7.2 with Compose v5.4.0, daemon running. Recorded in
[RESEARCH.md](RESEARCH.md) R-001.

**Implemented.** Milestone 1 in full: `.gitignore` first as the priority safety
item; the eight project-memory files; `AGENTS.md` as canonical cross-agent
instructions with `CLAUDE.md`, `GEMINI.md` and `QWEN.md` as pointers; all
product documentation; MIT `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
`CHANGELOG.md`, `.env.example`; a FastAPI backend with health and config
endpoints, typed settings and a small in-process event bus; a React +
TypeScript + Vite single-page workspace with light default and dark toggle;
tests on both sides; Docker and Compose; GitHub Actions CI; a GitHub Pages
documentation foundation.

**Verified by running, not reading.** 33 backend tests, 19 frontend tests, ruff,
mypy strict, eslint, tsc, a production build, both Docker images, the full stack
up with both endpoints answering correctly. Three real bugs surfaced this way
and were fixed — see the session record.

**Decisions recorded.** D-006 Docker as the primary backend path (forced by the
end-of-life local Pythons), D-007 Python 3.11 floor, D-008 plain CSS over a UI
framework, D-009 in-process event bus for V1, D-010 `docs/project-memory/` as
the single memory system, D-015 `main` branch with per-repository git identity,
**D-016 PolyForm Noncommercial 1.0.0 replacing MIT** — decided mid-session,
before anything was published, because licence changes only travel one way —
and D-017 no git remote for now.

**Added on request.** Session memory (`SESSION_PROTOCOL.md`, `sessions/`,
`scripts/session.py`) so no future session depends on a chat history, and
project identity configuration (`project.json`, `scripts/set_identity.py`).

**Repository cleanup.** Durable knowledge was extracted from the planning
transcripts into project memory. The substantive transcripts moved verbatim to
`docs/archive/`; scratch fragments carrying nothing durable were removed.
`MASTER.md` was kept at the root as the founding specification.

**Not done, deliberately.** No importer, archive browser, search, cloud or sync
code — all belong to later milestones.

**Next:** Milestone 2, the ChatGPT importer.
