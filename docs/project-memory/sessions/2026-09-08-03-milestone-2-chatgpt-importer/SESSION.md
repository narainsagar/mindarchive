# Session: Milestone 2 — the ChatGPT importer

**ID:** 2026-09-08-03-milestone-2-chatgpt-importer
**Started:** 2026-09-08
**Ended:** 2026-09-08
**Agent:** Claude Opus 5 (Claude Code, VS Code extension)

---

## Goal

Milestone 2: import a ChatGPT export and store it as human-readable files. The
point at which Mind Archive becomes useful rather than merely runnable.

## Starting state

`main` at `14159dc`, working tree clean. Milestone 1 complete, verified, and
the developer-controlled verification workflow (D-018) in place.

## What was done

**Privacy protection first.** Before anything else, `local/` was created and
git-ignored, with a committed README explaining that a real export goes there
and never into version control. `.gitignore` also gained `chat.html`,
`user.json`, `message_feedback.json` and `model_comparisons.json`.

**The importer interface.** `Importer` protocol with `detect()`, `validate()`
and `parse()`, plus a registry in `importers/__init__.py`. Core code never
imports a provider module; adding a provider means writing an adapter and
adding it to one list.

**`parse()` writes nothing** — it returns `Conversation` objects, and storing
them is the archive's job. That split kept every parser test filesystem-free.

**The ChatGPT parser.** The hard part is that `mapping` is a tree, not a list:
editing a message or regenerating a reply creates a branch. Walking from
`current_node` up through `parent` and reversing gives the conversation as the
person last saw it. Abandoned branches are deliberately not imported —
documented, and revisitable if anyone wants them.

Handled: several content types with a fallback for ones invented after this was
written, multimodal parts recorded as placeholders, ChatGPT's own hidden system
messages skipped while user-written custom instructions are kept, null titles,
missing and nonsensical timestamps.

**Hostile input.** `zip_safety.py` refuses path traversal, zip bombs, oversized
members and excessive entry counts. Conversation titles reach the filesystem
only through `paths.py`. One unreadable conversation is skipped and reported,
never silently dropped.

**The archive writer.** One folder per conversation holding `conversation.md`
(YAML front matter, human speaker names) and `metadata.json`. Re-importing the
same export updates in place rather than duplicating, matched on the provider's
own identifier; genuinely different conversations that collide get suffixed
rather than overwritten.

**API and interface.** `GET /api/importers`, `POST /api/import` with a streamed,
size-capped upload written to a temporary folder that is always removed. An
import panel that explains where to get an export, reassures the user nothing is
being uploaded anywhere, and lists what could not be read.

## Problems found and fixed

**A hostile archive was reported as "not recognised".** Caught by a test.
`detect()` never raises, so an unsafe zip simply matched no importer and the
user was told something untrue. Added `safety_problem()`, so the refusal is
explained. Fixed the code, not the test.

**The interface showed a path that does not exist.** End-to-end testing showed
`archive_location: /data/archive` — the path *inside the container*. Added
`MIND_ARCHIVE_DISPLAY_DATA_DIR`, set by Compose to `./data`, so the user is told
where their conversations actually are. The writer still uses the real path.

**An unwritable archive folder produced a raw 500.** Found by accidentally
deleting `data/` under a running container. A user could hit this with an
unplugged drive or a permissions problem, so it now explains itself.

## Decisions made

None new. The milestone implemented D-002 (providers are adapters) and D-004
(human-readable storage) as designed. `MIND_ARCHIVE_DISPLAY_DATA_DIR` is a
configuration detail, recorded in `.env.example` and `ARCHITECTURE.md` rather
than as a decision.

## Files changed

```
Added:    apps/api/src/mind_archive/models.py
          apps/api/src/mind_archive/importers/{__init__,base,chatgpt,zip_safety}.py
          apps/api/src/mind_archive/archive/{__init__,writer}.py
          apps/api/src/mind_archive/routes/import_.py
          apps/api/tests/{conftest,test_chatgpt_importer,test_zip_safety,
                          test_archive_writer,test_import_api,test_config}.py
          apps/web/src/components/ImportPanel.tsx (+ .test.tsx)
          local/README.md

Modified: .gitignore .env.example docker-compose.yml CHANGELOG.md
          apps/api/pyproject.toml (python-multipart)
          apps/api/src/mind_archive/{main,config}.py
          apps/api/src/mind_archive/routes/config.py
          apps/web/src/{App.tsx,api.ts,styles.css}
          docs/{ARCHITECTURE,ROADMAP}.md
          docs/project-memory/{MILESTONES,PROJECT_STATE,SESSION_LOG}.md
```

## Checks run

`python scripts/dev.py verify`

| Check | Result |
|---|---|
| Backend lint (ruff) | **passed** |
| Backend formatting | **passed**, 26 files |
| Backend types (mypy strict) | **passed**, 16 files |
| Backend tests | **137 passed** (was 33) |
| Frontend lint | **passed** |
| Frontend types | **passed** |
| Frontend tests | **29 passed** (was 19) |
| Frontend build | **passed** |
| Project memory | **passed** |

**End-to-end, against the running stack**, not just unit tests: a synthetic
export containing a normal conversation, an awkward one (null title, no
timestamp, a colon in the text) and a deliberately broken one was uploaded
through `POST /api/import`. Result: 2 imported, 1 skipped and reported, correct
Markdown and metadata on disk, `archive_location` reported as `./data/archive`.

Three failures were found and fixed during the session, described above.

## What remains

- Attachments and images are recorded as placeholders, not imported.
- Abandoned conversation branches are not imported, by design.
- Only tested against synthetic exports so far. **The user is downloading a
  real ChatGPT export to `local/` for verification** — that is the first thing
  to do next session.
- Unchanged from Milestone 1: placeholder GitHub identity, no git remote, no
  committed `package-lock.json`, frontend image runs the dev server.

## Exact next step

Import the user's real ChatGPT export from `local/`, confirm the parser handles
genuine data, and fix whatever it finds. Only then start Milestone 3.
