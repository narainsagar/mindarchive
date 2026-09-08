# Report — 2026-09-08-01-audit-and-milestone-1

The repository audit produced at the start of this session, stored as it was
written, before any file was modified.

It describes the repository **as it was on 2026-09-08 before Milestone 1**.
Everything it lists as missing was subsequently built. It is kept because the
reasoning behind Milestone 1 only makes sense against this starting point.

---

# MIND ARCHIVE — REPOSITORY AUDIT

## 1. CURRENT REPOSITORY

26 files, ~93 KB, **zero source code**. Git initialised (`master`), **no commits**, no remote.

```
mindarchive.app/
├── AGENTS.md                    0 bytes  ← EMPTY
├── README.md                    0 bytes  ← EMPTY
├── CLAUDE.md                5,276 bytes  ← real content
├── GEMINI.md                1,117 bytes  ← real content
├── MASTER.md               18,679 bytes  ← the real spec
├── SETUP.md                16,422 bytes  ← chat transcript
├── start.txt               16,931 bytes  ← chat transcript
├── sreps.md                   606 bytes  ← scratch notes
├── NEXT_TBR.txt             1,113 bytes  ← scratch notes
├── structure.md             2,555 bytes  ← proposed tree + chat
├── pc_specs.md / pc_specs.sh           ← hardware probe notes
├── docs/
│   ├── ARCHITECTURE.md      0 bytes  ← EMPTY
│   ├── BACKLOG.md           0 bytes  ← EMPTY
│   ├── DECISIONS.md         0 bytes  ← EMPTY
│   ├── DEVELOPMENT.md       0 bytes  ← EMPTY
│   ├── GITHUB_PAGES.md      0 bytes  ← EMPTY
│   ├── PRODUCT.md           0 bytes  ← EMPTY
│   ├── ROADMAP.md           0 bytes  ← EMPTY
│   └── SECURITY.md          0 bytes  ← EMPTY
├── prompts/
│   ├── AI-CODING.md         1,318 bytes  ← real content
│   ├── first_time.md       12,476 bytes  ← prompt dump
│   └── local_claude.md     12,829 bytes  ← prompt dump
├── .claude/
│   ├── code.md              1,453 bytes  ← chat transcript (misplaced)
│   └── rules/{backend,frontend,security}.md  ← real content
└── .qwen/                   ← exists, completely empty
```

**Absent entirely:** `apps/`, `scripts/`, `.github/`, `.gitignore`, `.env.example`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`, `docker-compose.yml`, `Dockerfile`, `QWEN.md`.

## 2. PROJECT MEMORY STATUS

**⚠️ The audit prompt's central premise is incorrect.**

The prompt states: *"The project-memory system already exists under `docs/project-memory/`. Read and understand it."*

**`docs/project-memory/` does not exist.** None of the eight files listed exist — no `MEMORY_INDEX.md`, `PROJECT_STATE.md`, `DISCUSSION_SUMMARY.md`, `DECISIONS.md`, `RESEARCH.md`, `AI_AGENT_PROTOCOL.md`, `MILESTONES.md`, or `SESSION_LOG.md`.

What exists instead is an *ad-hoc* memory layer: durable knowledge is real, but it lives in `MASTER.md` (excellent, comprehensive) plus raw chat transcripts at the repo root. Project memory is **not** connected to a development workflow, because there is no development workflow yet.

The prompt also says *"Do NOT assume that empty files are missing requirements."* The exception has to be flagged: the ten 0-byte files are placeholders, not deliberate choices. Their intended content is fully specified in `MASTER.md` §22.

## 3. CURRENT IMPLEMENTATION

Nothing. No React, no Vite, no FastAPI, no Python package, no `package.json`, no `pyproject.toml`, no tests, no Docker, no CI. The project is 100% specification, 0% implementation.

## 4. MILESTONE 1 STATUS

| Item | Status |
|---|---|
| Repository | 🟡 folder exists, Git init'd, **no commits, no identity, no remote** |
| React + TypeScript + Vite | 🔴 missing |
| FastAPI backend | 🔴 missing |
| SQLite foundation | 🔴 missing |
| Docker / Compose | 🔴 missing |
| `.env.example` | 🔴 missing |
| `.gitignore` | 🔴 **missing — actively risky** |
| Light/dark UI | 🔴 missing |
| GitHub Actions CI | 🔴 missing |
| GitHub Pages foundation | 🔴 missing (`docs/GITHUB_PAGES.md` empty) |
| LICENSE / CONTRIBUTING / COC / CHANGELOG | 🔴 missing |
| Tests | 🔴 missing |
| Documentation | 🟡 specified in `MASTER.md`, all target files empty |
| AI instructions | 🟡 `CLAUDE.md` good; `AGENTS.md` empty; `QWEN.md` absent |
| Project memory | 🔴 directory absent |

**Effectively complete: ~5%.** Only the specification and the Claude rule files.

## 5. ARCHITECTURE REVIEW

The *documented* architecture (`MASTER.md`) is sound and internally consistent — local-first, privacy-first, provider-agnostic, human-readable storage, optional cloud, event-driven, simple V1. No objection to any of it; recommend implementing it as written.

There is no *implemented* architecture to review. Frontend/backend separation cannot be assessed — the `apps/web` + `apps/api` split from `structure.md` is a good, simple choice and should be adopted unchanged.

One genuine gap in the spec: `MASTER.md` describes event names (`archive.imported`, `sync.completed`, …) but no minimal event interface. Milestone 1 should ship a tiny in-process event bus (~40 lines) so the extension point is real rather than aspirational.

## 6. SECURITY / PRIVACY REVIEW

**No secrets found.** Every file was searched — no API keys, tokens, passwords, or personal archives. `.env` does not exist. Nothing has ever been committed. Clean.

Real issues:

1. **No `.gitignore` — highest-priority risk.** With none present, a first `git add -A` would commit `node_modules/`, `.venv/`, `__pycache__/`, `*.db`, and — critically — any `.env` or imported personal archive the moment one appears. This is the single most important gap for a privacy-first project.
2. **No `.env.example`**, so there is no documented safe configuration surface.
3. `pc_specs.md` / `pc_specs.sh` contain hardware-probe commands. Harmless now, but if real output is ever pasted in, it becomes machine fingerprinting in a public repo.
4. Cloud is correctly absent — nothing can silently upload, because nothing exists.

## 7. DEVELOPMENT ENVIRONMENT REVIEW

Verified on this machine (read-only):

| | Windows | WSL2 (Ubuntu 22.04.2) |
|---|---|---|
| Node | **not installed** | v24.18.0 ✅ |
| npm | not installed | 11.16.0 ✅ |
| Python | **3.7.9 — EOL** ⚠️ | **3.8.10 — EOL** ⚠️ |
| Git | 2.50.1 ✅ | 2.34.1 ✅ |
| Docker | 29.7.2, daemon running, Linux containers ✅ | via Docker Desktop ✅ |
| Compose | v5.4.0 ✅ | ✅ |

**Consequence:** neither host has a Python new enough to run a modern FastAPI/Pydantic v2 stack well (3.8 reached end-of-life in October 2024). **Docker must be the primary supported path for the backend**, with native development documented as requiring Python 3.11+ installed separately. This is a real finding that should be recorded as a decision — it is not in `MASTER.md`.

Frontend native development works fine today in WSL (Node 24 satisfies Vite 7).

**Git is unusable for committing right now:** `user.name` and `user.email` are unset both locally and globally. Any commit attempt will fail.

Branch is `master`; GitHub's default is `main` — worth aligning before the first push.

## 8. DOCUMENTATION REVIEW

`MASTER.md` is genuinely good — clear, opinionated, human-readable, and the correct source of truth. `CLAUDE.md`, `GEMINI.md`, `prompts/AI-CODING.md` and the three `.claude/rules/` files are concise and useful.

The problem is **`CLAUDE.md` instructs agents to read `README.md`, `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md` as "the project's source of truth" — and all five are empty.** Every agent that follows the project's own rules currently reads nothing and learns nothing. `CLAUDE.md` never mentions `MASTER.md`, where the actual truth lives. This is the most damaging documentation defect in the repo.

## 9. DUPLICATES / CONFLICTS

1. **Two competing memory layouts.** `structure.md` proposes a flat `docs/`; `start.txt` proposes `docs/project-memory/` with eight files. Neither is built. **Must be resolved before writing anything.**
2. **`CLAUDE.md` points at empty files** and omits `MASTER.md` (§8 above).
3. **`AGENTS.md` is empty** but is designated the canonical cross-agent file by `start.txt` §6 and `structure.md`. Currently it is the *least* useful file in the repo.
4. **Spec duplication ×4.** `MASTER.md`, `start.txt`, `prompts/first_time.md`, `prompts/local_claude.md` restate the same project definition with drift between them. Four sources of truth means zero.
5. **`structure.md` promises files that don't exist:** `QWEN.md`, `prompts/CHATGPT.md`, `prompts/CLAUDE.md`, `prompts/GEMINI.md`, `.claude/rules/documentation.md`, `.claude/rules/git.md`, `.claude/skills/`, `.github/`, `scripts/`.
6. **`.claude/code.md` is a chat transcript** about choosing coding agents, sitting in a directory reserved for agent rules. Wrong place, wrong kind of content.

## 10. UNNECESSARY COMPLEXITY

The *plan* is admirably lean — no Kubernetes, Redis, Kafka, or Elasticsearch anywhere. Good.

The *repository* is the opposite: **~48 KB (over half of all content) is raw conversation transcript** — `start.txt`, `SETUP.md`, `.claude/code.md`, `sreps.md`, `NEXT_TBR.txt`, and large parts of `prompts/first_time.md` / `local_claude.md`. This directly violates the project's own rule: *"Store durable knowledge, not chat noise."* It also costs every future AI agent tokens to wade through, defeating the token-efficiency goal in `SETUP.md`.

The durable knowledge inside them is worth perhaps 3–4 KB (the Qwen/Ollama hardware research, the agent-independence rationale, the workflow steps). The rest is noise.

## 11. MISSING ITEMS

**Critical:** `.gitignore`, `.env.example`, git identity, `docs/project-memory/`, all ten empty docs, `apps/web/`, `apps/api/`.

**Required for Milestone 1:** Docker + Compose, `.github/workflows/ci.yml`, GitHub Pages foundation, `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`, tests both sides, `QWEN.md`, populated `AGENTS.md`.

## 12. THINGS WE SHOULD NOT BUILD YET

ChatGPT importer (M2) · archive browser, Markdown rendering, full-text search (M3) · projects/tags/metadata (M4) · plugin system (M5) · **any cloud or sync adapter** (M6) · auth, multi-user, production hardening (M7) · Elasticsearch, Redis, Celery, message brokers · mobile UI · Ollama/local-model integration *inside the app* (dev-tooling only) · real settings beyond theme + read-only config display.

## 13. EXACT IMPLEMENTATION PLAN

Seven sequential milestones, repo runnable after each.

**M1.0 — Safety & memory foundation.** `.gitignore` (Node, Python, SQLite, `.env`, archives) first, before anything else. Create `docs/project-memory/` with the eight files, seeded from `MASTER.md`. Populate `AGENTS.md` as the canonical cross-agent file; add `QWEN.md`; correct `CLAUDE.md`/`GEMINI.md` to point at real files.

**M1.1 — Documentation.** Fill all ten empty docs from `MASTER.md`. Write `README.md`, `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`, `.env.example`.

**M1.2 — Backend.** `apps/api/` — FastAPI, `pyproject.toml`, Python 3.11+ target. `GET /api/health`, `GET /api/config` (returns non-secret config: storage mode, archive path, cloud=disabled). Config via pydantic-settings. Minimal in-process event bus. SQLite path prepared, no schema yet. `pytest` tests.

**M1.3 — Frontend.** `apps/web/` — React + TS + Vite. Single-page workspace, minimal top bar, light mode default, dark toggle persisted to `localStorage`, honours `prefers-color-scheme`. Shows backend health + storage location. Plain CSS with variables — no UI framework. Vitest tests.

**M1.4 — Docker.** `apps/api/Dockerfile` (python:3.12-slim), `apps/web/Dockerfile` (node:24-alpine), `docker-compose.yml` wiring 5173 → 8000 with a named volume for local data.

**M1.5 — CI & Pages.** `.github/workflows/ci.yml` (backend lint/type/test + frontend lint/build/test), `docs-pages.yml`, issue/PR templates, `docs/GITHUB_PAGES.md` + minimal Pages source.

**M1.6 — Cleanup & memory update.** Move durable knowledge out of the transcripts into project memory; archive the transcripts. Update `PROJECT_STATE.md`, `DECISIONS.md`, `MILESTONES.md`, `SESSION_LOG.md`. Set git identity, rename `master` → `main`, review diff, single clean commit.

**Dependencies kept minimal:** backend — `fastapi`, `uvicorn`, `pydantic-settings`, `pytest`, `httpx`, `ruff`, `mypy`. Frontend — `react`, `react-dom`, `vite`, `typescript`, `vitest`, `eslint`. Nothing else.

**New decisions to record:** Docker as the primary backend path (local Python is EOL); Python 3.11+ floor; plain CSS over a UI framework; `docs/project-memory/` as the single memory layout; in-process event bus for V1.

## 14. VERIFICATION PLAN

Backend: `ruff check`, `mypy`, `pytest` (health + config endpoints). Frontend: `tsc --noEmit`, `eslint`, `vitest`, `vite build`. Docker: `docker compose build` then `up -d`, curl both ports, `down`. Config: confirm `.env.example` has placeholders only and `.env` is ignored. Memory: confirm no doc claims something the code doesn't do. Git: `git status` + full `git diff --cached` reviewed for secrets before committing.

These will be run and reported with actual output, including failures.

## 15. RECOMMENDED NEXT COMMAND

Answer the four clarifying questions, then proceed through M1.0 → M1.6 and stop.

---

## Questions asked at the end of the audit, and the answers given

1. **Which memory layout?** → Build `docs/project-memory/` with the eight files.
2. **What to do with the chat transcripts?** → Extract durable knowledge, archive
   the substantive transcripts, delete the pure noise.
3. **GitHub identity?** → "I'll provide it now" — not yet supplied at the time of
   writing; `YOUR-USERNAME` placeholders used.
4. **Git identity and branch?** → Set local identity, rename `master` → `main`,
   one clean foundation commit.
