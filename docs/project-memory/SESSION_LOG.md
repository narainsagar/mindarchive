# Session Log

One concise entry per working session. Newest first. Durable facts only — what
changed and why, not conversation.

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
