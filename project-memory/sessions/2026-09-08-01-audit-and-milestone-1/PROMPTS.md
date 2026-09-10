# Prompts — 2026-09-08-01-audit-and-milestone-1

The instructions given during this session, verbatim and in order.

No secrets appeared in any prompt, so nothing has been redacted.

Prompt 1 was pasted by the user from `prompts/local_claude.md` (now in
`docs/archive/`, later merged into project memory and removed — see commit
`fcf1f5c`) and combines three prompts that were designed to be sent
separately: the audit prompt, the Milestone 1 implementation prompt, and the
template for future sessions.

---

## Prompt 1 — 2026-09-08, session start

```
You are now the primary senior software engineer and project maintainer for the open-source project "Mind Archive".

IMPORTANT: DO NOT MODIFY ANY FILES YET.

The repository already exists locally. I have already created/copied the project structure, Markdown files, project-memory files, prompts, and initial instructions discussed previously.

Your first job is ONLY to understand and audit the existing repository.

==================================================
PROJECT IDENTITY
==================================================

Project:
Mind Archive

Tagline:
Your Personal AI Mind Archive.

Slogan:
Own your AI memory. Simple, private, and yours.

Mind Archive is an open-source, local-first, privacy-first personal AI archive.

The long-term purpose is to allow users to own, preserve, organize, search, import, export, and eventually synchronize their AI conversations, memories, knowledge, files, and related personal information.

The project must remain:

- local-first
- privacy-first
- user-owned
- provider agnostic
- human-readable
- portable
- open source
- contributor friendly
- simple
- extensible without premature complexity

ChatGPT/OpenAI is only an initial importer target.

Claude, Gemini, Qwen, OpenAI, local models, Cursor, OpenCode, and other AI systems must NOT become the architectural center of the product.

==================================================
MOST IMPORTANT RULE — PROJECT MEMORY
==================================================

The repository is the permanent source of truth.

AI chat history is temporary.

Never depend on this conversation, Claude's memory, Gemini's memory, Cursor's memory, or any other AI's memory as the project's only memory.

Important project knowledge MUST be represented inside the repository.

Whenever an important:

- product decision
- architecture decision
- feature decision
- UX decision
- technical decision
- configuration decision
- workflow decision
- deployment decision
- security/privacy decision
- research finding
- roadmap decision
- requirement

is created or changed, update the appropriate Markdown/source-of-truth file.

The project-memory system already exists under:

project-memory/

Read and understand it.

Do not create duplicate project-memory systems.

If documents conflict, identify the conflict before making changes.

==================================================
FIRST TASK — AUDIT ONLY
==================================================

Read the repository before doing anything.

At minimum inspect:

AGENTS.md
CLAUDE.md
QWEN.md
GEMINI.md

project-memory/MEMORY_INDEX.md
project-memory/PROJECT_STATE.md
project-memory/DISCUSSION_SUMMARY.md
project-memory/DECISIONS.md
project-memory/RESEARCH.md
project-memory/AI_AGENT_PROTOCOL.md
project-memory/MILESTONES.md
project-memory/SESSION_LOG.md

Also inspect, if present:

README.md
docs/PRODUCT.md
docs/ARCHITECTURE.md
docs/DEVELOPMENT.md
docs/SECURITY.md
docs/ROADMAP.md
docs/BACKLOG.md
CHANGELOG.md
docker-compose.yml
.env.example

Then inspect the actual source tree, package files, configuration, tests, scripts, Git state, and existing implementation.

Do NOT assume that empty files are missing requirements.
Do NOT recreate working files.
Do NOT replace existing architecture merely because you prefer another approach.

==================================================
AUDIT QUESTIONS
==================================================

Determine:

1. What already exists?

2. What is actually implemented?

3. What is merely documented?

4. Which files are empty?

5. Which files contain useful existing information?

6. Are there duplicate or conflicting instructions?

7. Is AGENTS.md suitable as the canonical cross-agent instruction file?

8. Is project memory sufficiently connected to the actual development workflow?

9. What is already complete from Milestone 1?

10. What remains for Milestone 1?

11. Is the current architecture consistent with:
    - local-first
    - privacy-first
    - provider agnostic
    - human-readable storage
    - optional cloud
    - event-driven principles
    - simple V1

12. Are there unnecessary dependencies or infrastructure?

13. Are there security/privacy problems?

14. Are there secrets or unsafe environment files?

15. Are Docker, WSL/Linux, Windows, and local development considerations correct?

16. Is the frontend/backend separation clean?

17. Are tests/checks present?

18. Is Git configured correctly?

19. Is GitHub Actions/CI present or missing?

20. Is GitHub Pages documentation foundation present or missing?

21. What should NOT be implemented yet because it belongs to a later milestone?

==================================================
TOKEN / CONTEXT EFFICIENCY
==================================================

Do not repeatedly read the entire repository.

Use this strategy:

1. Read project instructions.
2. Read project memory.
3. Identify relevant files.
4. Inspect only relevant source/configuration.
5. Build a concise understanding.
6. Do not dump the entire repository into the conversation.

The repository should remain the source of truth rather than creating enormous prompts.

==================================================
IMPORTANT HARDWARE / LOCAL AI NOTE
==================================================

The development environment may eventually use:

Qwen Code
+
Ollama
+
local coding model

or:

OpenCode
+
Ollama
+
local coding model

This is a development option only.

Mind Archive itself must NOT depend on Ollama, Qwen, Claude, Gemini, Cursor, or any other AI coding tool.

Do not implement AI-agent-specific application architecture.

==================================================
DO NOT MODIFY
==================================================

During this first task:

- do not edit files
- do not create files
- do not delete files
- do not install packages
- do not change dependencies
- do not initialize/rewrite Git history
- do not run destructive commands

Inspection and read-only commands are allowed.

==================================================
AUDIT OUTPUT
==================================================

After inspection, give me a concise but complete report with exactly these sections:

1. CURRENT REPOSITORY
2. PROJECT MEMORY STATUS
3. CURRENT IMPLEMENTATION
4. MILESTONE 1 STATUS
5. ARCHITECTURE REVIEW
6. SECURITY/PRIVACY REVIEW
7. DEVELOPMENT ENVIRONMENT REVIEW
8. DOCUMENTATION REVIEW
9. DUPLICATES/CONFLICTS
10. UNNECESSARY COMPLEXITY
11. MISSING ITEMS
12. THINGS WE SHOULD NOT BUILD YET
13. EXACT IMPLEMENTATION PLAN
14. VERIFICATION PLAN
15. RECOMMENDED NEXT COMMAND

Do not implement anything yet.

Wait or Ask for my approval after the audit.


The audit is approved.

Now implement Milestone 1 only.

Before changing anything, use the audit and the existing repository as the source of truth.

IMPORTANT:

Do NOT rebuild the project from scratch.

Do NOT replace working components.

Do NOT introduce unrelated refactoring.

Do NOT start Milestone 2.

Preserve all existing valid project documentation and decisions.

==================================================
MILESTONE 1
==================================================

Establish a clean, runnable, documented foundation for Mind Archive.

The target foundation is:

Frontend:
- React
- TypeScript
- Vite

Backend:
- Python
- FastAPI

Local data:
- SQLite where useful
- human-readable Markdown/JSON/plain-text archive data

Development:
- Windows
- WSL2/Linux
- macOS-compatible where reasonably practical
- Docker/Docker Compose

Project:
- Git
- GitHub-ready repository
- GitHub Actions CI
- GitHub Pages documentation foundation

UX:
- simple
- professional
- human-readable
- light mode by default
- dark mode available
- desktop/laptop first
- avoid unnecessary dashboard/sidebar complexity

Architecture:
- local-first
- privacy-first
- provider agnostic
- event-driven where appropriate
- optional cloud
- no silent data upload

==================================================
PROJECT MEMORY
==================================================

Project memory is part of the implementation.

Whenever implementation reveals or changes an important decision:

1. update the appropriate project-memory Markdown file;
2. keep code and documentation consistent;
3. update PROJECT_STATE.md when project reality changes;
4. update DECISIONS.md when an architectural/product decision is made;
5. update RESEARCH.md when a researched technical assumption changes;
6. update MILESTONES.md/ROADMAP/BACKLOG when appropriate;
7. add a concise SESSION_LOG entry for this implementation session.

Do not copy the whole conversation into the repository.

Store durable knowledge, not chat noise.

==================================================
QUALITY
==================================================

Use clean interfaces.

Keep provider-specific code behind adapters/interfaces.

Keep cloud functionality separate from the local core.

Do not add unnecessary dependencies.

Do not introduce microservices unless clearly necessary.

Do not introduce Redis, Kafka, Kubernetes, distributed queues, or other infrastructure merely for future scalability.

V1 should be simple enough for one developer while maintaining clean extension points.

==================================================
SECURITY
==================================================

Never commit:

- API keys
- passwords
- tokens
- private keys
- personal archives
- credentials

Maintain .env.example with safe placeholders.

Review .gitignore.

Cloud operations must never be silently enabled.

==================================================
VERIFICATION
==================================================

After implementation:

1. Run frontend checks/build.
2. Run backend tests/checks.
3. Run relevant lint/type checks.
4. Verify Docker.
5. Verify environment configuration.
6. Verify project-memory check.
7. Review Git diff.
8. Review Git status.
9. Fix errors found.
10. Update documentation to reflect reality.

Do not claim success based only on code inspection.

==================================================
GIT
==================================================

Do not destroy existing Git history.

If this repository has no meaningful commits yet, prepare a clean initial foundation commit.

Before committing:

- inspect git diff
- inspect git status
- ensure no secrets
- ensure generated files are excluded appropriately

Use an appropriate commit message, for example:

chore: establish Mind Archive project foundation

==================================================
FINAL OUTPUT
==================================================

At completion report:

1. Files created
2. Files modified
3. Architecture implemented
4. Tests/checks executed
5. Build results
6. Docker result
7. Project-memory updates
8. Security review
9. Git status
10. Commit hash if committed
11. Known limitations
12. Exact next step

Stop after Milestone 1.

Do not start Milestone 2.



Read AGENTS.md and the relevant project-memory files.

We are continuing Mind Archive.

First inspect the current PROJECT_STATE.md, MILESTONES.md,
DECISIONS.md and Git status.

Work only on:

[YOUR TASK]

Before implementation:
- identify the relevant architecture and requirements;
- identify affected files;
- identify whether a project decision changes.

Implement the smallest coherent solution.

After implementation:
- test it;
- review the diff;
- update project memory and documentation;
- update roadmap/backlog/project state where applicable;
- check security/privacy;
- report what changed and what remains.

Do not start unrelated work or the next milestone. Ask before starting or incase of failure or quota limit expire please have everything stored in local project memory so we can continue for where left off and fix broken changes or things before hand starting any new work. Please start now

ABive have first promot and second and active all togehter. Start now
```

---

## Prompt 2 — answers to the four clarifying questions asked after the audit

The audit ended with four questions. The answers given:

| Question | Answer |
|---|---|
| Which memory layout? | **Build `project-memory/`** — the eight files, seeded from `MASTER.md` |
| What to do with the chat transcripts? | *"Do first two options and clean the all uncessary files behore hand"* — extract durable knowledge, archive the substantive transcripts, delete the noise |
| GitHub identity? | *"I'll provide it now"* — but the username and copyright name were not supplied; placeholders used |
| Git identity and branch? | **Set local identity, rename `master` → `main`**, then one clean foundation commit |

---

## Prompt 3 — mid-session

```
Please also save the audit complete report after final completion and also write mechanism to do it every next prompts including current session history prompts and your audit completion final report as it is including the current ones too from start till end the session, on every session start and end , make smarter and intelligent memory locally within the project.

Choose the folder structure and everything accordingly as you are senior lead developer.
```

This produced `SESSION_PROTOCOL.md`, `sessions/`, `scripts/session.py`, and this
file.

---

## Prompt 4 — mid-session

```
Please ask calrifying questions before hand, if or whenever needed. :)
```

Standing instruction: ask when a choice would genuinely change the work, rather
than assuming.
