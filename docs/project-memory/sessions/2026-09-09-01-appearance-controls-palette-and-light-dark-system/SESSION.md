# Session: appearance controls: palette and light/dark/system

**ID:** 2026-09-09-01-appearance-controls-palette-and-light-dark-system
**Started:** 2026-09-09 07:20
**Ended:** 2026-09-09 07:23
**Agent / developer:** Claude Opus 5 (Claude Code)

---

## Goal

Three unrelated things, in the order they came up: repair a file move that had
broken agent instructions, unblock `docker compose up`, and then design and
implement user-facing appearance controls — a palette choice and a three-way
light / dark / system theme choice.

## Starting state

Branch `main`, clean at `310cbb2`, working tree then dirtied by an
uncommitted file move. `CLAUDE.md`, `GEMINI.md`, `QWEN.md` and `MASTER.md` had
been moved into `prompts/` to shorten the repository root. `docker compose up`
was failing outright.

## What was done

**1. The `prompts/` move was partly wrong, and had to be undone.**

`CLAUDE.md`, `GEMINI.md` and `QWEN.md` only function at the repository root —
Claude Code, Gemini CLI and Qwen Code each auto-load their file from there and
report nothing when it is absent. Left in `prompts/`, every future agent session
would have silently run with no project instructions. The three were restored to
the root; `MASTER.md` has no such constraint and stayed at `prompts/MASTER.md`,
recorded by git as a rename.

References to `MASTER.md` were updated in the five live documents only —
`README.md`, `AGENTS.md`, `CLAUDE.md`, `MEMORY_INDEX.md`,
`AI_AGENT_PROTOCOL.md`. `CHANGELOG.md`, `SESSION_LOG.md`, `DISCUSSION_SUMMARY.md`
and the previous session records were deliberately left alone: they describe
what was true when written, and rewriting them would falsify the record.

**2. The docker failure was a stale container, not a naming problem.**

`docker compose up --build` failed with a container-name conflict on
`mind-archive-api`. The container was still running — it had not been deleted —
and its labels said `com.docker.compose.project=mindarchiveapp`, from before the
directory was renamed to `mindarchive-v1`. Compose derives the project name from
the directory, so it saw a foreign project and refused to reuse a container whose
name `docker-compose.yml` pins.

Removed the orphan, then pinned `name: mindarchive` in `docker-compose.yml` so a
future directory rename cannot repeat this. `scripts/dev.py` calls plain
`docker compose` with no `-p`, so it needed no change. Documented in
`docs/DEVELOPMENT.md`, including the recovery command for older checkouts.

**3. Design previews, then the appearance controls.**

Three palettes were drawn from the references the user supplied
(`lu-labs.ai`, `freellmapi.co`) and published as a preview artifact — one full
landing page and one full workspace, with a live palette and theme switcher, so
the choice could be made against real layout rather than swatches. The user then
asked for that switcher itself to ship.

Implemented as two independent, remembered choices:

```
mind-archive-palette   minimal | warm | violet     default: minimal
mind-archive-theme     light   | dark | system     default: system
```

The old toggle had a real defect worth recording: `getInitialTheme` resolved the
system preference into a concrete `light`/`dark` and `applyTheme` wrote it to
storage immediately, so a first visit permanently pinned the reader to whatever
their computer said at that moment. There was no way to say "follow the system".
`system` is now a stored choice of its own, and `watchSystemTheme` keeps
following it while it is selected.

Because `resolveTheme` stamps an already-resolved `light`/`dark` on `<html>`,
the stylesheet selects on `[data-palette][data-theme]` alone. That removed the
pre-existing duplication where the dark token values appeared verbatim in both
`@media (prefers-color-scheme: dark)` and `:root[data-theme="dark"]`.

Controls are real radio inputs inside a `fieldset` (`SegmentedControl`), so
keyboard and screen-reader behaviour is the browser's. `ThemeToggle.tsx` was
fully absorbed and removed.

**A numbering collision was caught before it landed.** The new decision was first
written as D-020, which is already "A conversation is served and rendered as one
Markdown file". Renumbered to D-029 throughout, and added to the `docs/DECISIONS.md`
index — the step a previous milestone missed for D-025 and D-026.

## Decisions made

**D-029 — Appearance is two choices: a palette, and light / dark / system.**
Supersedes the control shape in D-014, keeps its principle: light is still what
a reader gets when nothing else is known. D-014 marked superseded in both
`DECISIONS.md` and the `docs/DECISIONS.md` index.

Pinning the Compose project name was a build-configuration fix, not an
architectural decision, so it is documented rather than numbered.

## Files changed

```
Added:
  apps/web/src/components/SegmentedControl.tsx
  apps/web/src/components/AppearanceControls.tsx
  docs/project-memory/sessions/2026-09-09-01-appearance-controls-palette-and-light-dark-system/

Modified:
  apps/web/src/theme.ts                     rewritten: palette + 3-way theme
  apps/web/src/styles.css                   6 palette/theme token blocks; segmented control
  apps/web/src/App.tsx                      palette state, system watcher
  apps/web/src/components/Header.tsx        hosts AppearanceControls
  apps/web/index.html                       pre-paint script stamps both attributes
  apps/web/src/theme.test.ts                rewritten for the new API
  apps/web/src/App.test.tsx                 "the theme" -> "appearance"
  docker-compose.yml                        name: mindarchive
  docs/DEVELOPMENT.md                       pinned project name + recovery
  docs/PRODUCT.md                           appearance section
  docs/DECISIONS.md                         D-029 added; D-014 struck
  docs/project-memory/DECISIONS.md          D-029; D-014 superseded
  README.md, AGENTS.md, CLAUDE.md           prompts/MASTER.md
  docs/project-memory/MEMORY_INDEX.md       prompts/MASTER.md
  docs/project-memory/AI_AGENT_PROTOCOL.md  prompts/MASTER.md

Removed:
  apps/web/src/components/ThemeToggle.tsx   absorbed by AppearanceControls

Renamed:
  MASTER.md -> prompts/MASTER.md
```

## Checks run

| Check | Command | Result |
|---|---|---|
| Compose config | `docker compose config --quiet` | Passed — `name: mindarchive` |
| Stack up | `dev.py up --build` | Passed — both containers created |
| Stack status | `dev.py status` | api `Up (healthy)`, web up |
| Frontend tests | `dev.py test frontend` | Passed — 82 tests, 5 files |
| Lint | `dev.py lint` | Passed — ruff + eslint |
| Types | `dev.py types` | Passed — mypy 26 files, tsc |
| Build | `dev.py build` | Passed — vite, 199 modules |
| Full gate | `dev.py verify` | **Passed — all checks passed** |
| Project memory | `session.py check` | Passed — consistent |

The full gate was run before the D-020 → D-029 renumbering and the session
record; those are documentation-only edits, and `session.py check` was run again
afterwards.

## What remains

- **Nothing is committed.** Every change above is in the working tree.
- **The layout restyle was not done.** The published preview also showed a new
  spacing rhythm, type scale and a rebuilt landing page. Only the colour system
  and the controls shipped; `docs/index.html` is untouched and still carries its
  own duplicated token subset, so the public page and the app can now drift.
- **The preview's typography did not ship.** It used Newsreader and IBM Plex from
  Google Fonts, which a privacy-first app must not fetch at runtime. The app
  still uses the system stack. Self-hosting the fonts is the open question.
- Three near-duplicate chip styles (`.tagbar__tag`, `.archive__tag`,
  `.tags__tag`) are still unmerged.

## Exact next step

Decide whether to self-host Newsreader/IBM Plex or keep the system font stack,
then rebuild `docs/index.html` on the same token names as `styles.css` so the
public page and the workspace cannot drift.
