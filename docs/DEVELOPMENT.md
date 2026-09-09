# Development

How to set up, run and work on Mind Archive.

## Requirements

| | Docker path (recommended) | Native path |
|---|---|---|
| Docker Engine + Compose v2 | required | — |
| Python | — | **3.11 or newer** |
| Node.js | — | **20 or newer** |
| Git | required | required |

**Why Docker is recommended.** It gives every contributor an identical, current
runtime. The machine this project was started on had Python 3.7 on Windows and
3.8 in WSL2 — both end-of-life and neither suitable for the backend stack. That
is a common situation, and Docker removes it as a problem. See decision D-006.

## Running with Docker

> **`python` or `python3`?** On Windows it is `python`. On Linux, WSL and macOS
> it is usually `python3` — Ubuntu ships no bare `python`. Every `python ...`
> command below works either way; use whichever your shell has.

```bash
git clone https://github.com/YOUR-USERNAME/mind-archive.git
cd mind-archive
cp .env.example .env
python scripts/dev.py up --build
```

- Mind Archive — http://localhost:5173
- API — http://localhost:8000
- Interactive API docs — http://localhost:8000/docs

Both services hot-reload on file changes. Your archive is bind-mounted at
`./data`, which is git-ignored.

### Managing the stack

`scripts/dev.py` wraps Docker Compose so you do not have to remember the flags.

```bash
python scripts/dev.py status        # what is running
python scripts/dev.py logs api -f   # follow the backend log
python scripts/dev.py stop          # pause, keep containers
python scripts/dev.py down          # stop and remove containers
python scripts/dev.py down --volumes  # ... and delete Docker volumes
python scripts/dev.py clean         # also remove this project's images
python scripts/dev.py clean --all   # ... and prune dangling build cache
```

**Containers are disposable — do not leave them running.** Every check runs in
a throwaway container, and `verify` tears the stack down when it finishes. This
keeps Docker from quietly filling your disk (decision D-019).

Your archive lives in `./data`, a bind mount rather than a Docker volume. **No
cleanup command can delete it**, including `down --volumes` and `clean`. That
separation is deliberate.

The Compose project name is pinned to `mindarchive` in `docker-compose.yml`, so
it does not follow the name of the directory you cloned into. Without that pin,
renaming the folder makes Compose treat the already-running containers as
belonging to a different project, and `up` fails with a container name conflict
instead of reusing them. If you ever hit that error on an older checkout, remove
the stale container — `docker rm -f mind-archive-api` — and start again; your
archive is a bind mount and is not affected.

## Running natively

### Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn mind_archive.main:app --reload --port 8000
```

Checks:

```bash
pytest                # tests
ruff check .          # lint
ruff format --check . # formatting
mypy src              # types
```

### Frontend

```bash
cd apps/web
npm install
npm run dev           # http://localhost:5173
```

Checks:

```bash
npm test              # Vitest
npm run typecheck     # tsc --noEmit
npm run lint          # ESLint
npm run build         # production build
```

## Platform notes

### WSL2 (recommended on Windows)

Keep the repository **inside the Linux filesystem**, not on `/mnt/c`. Filesystem
performance across the Windows/Linux boundary is poor enough to make file
watching unreliable.

```bash
cd ~                                    # not /mnt/c
git clone https://github.com/YOUR-USERNAME/mind-archive.git
cd mind-archive
code .                                  # opens VS Code attached to WSL
```

Install the **WSL** extension for VS Code.

Docker Desktop needs two adjustments inside WSL, and neither is made for you:

**Enable WSL integration** for your distribution — Docker Desktop → Settings →
Resources → WSL integration → Apply & restart. Without it there is no
`/var/run/docker.sock` and every `docker` command fails.

**Remove the Windows credential helper**, which Docker Desktop writes into
WSL's config as `{"credsStore": "desktop.exe"}`. The Linux CLI cannot execute a
Windows `.exe`, so image pulls fail with `exec format error`:

```bash
cp ~/.docker/config.json ~/.docker/config.json.bak
printf '{}
' > ~/.docker/config.json
```

It only affects signing in to private registries. This project pulls public
images only.

If your distribution has an old Python, use the Docker path, or install a
current Python with `pyenv` or the deadsnakes PPA. Do not replace the system
Python.

### Windows (without WSL)

Docker Desktop works directly. For native development install Python 3.11+ from
python.org and Node 20+ from nodejs.org, then use PowerShell:

```powershell
cd apps\api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

If activation is blocked, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

Git may rewrite line endings. `.gitattributes` normalises this; if you see
whole-file diffs, check `git config core.autocrlf`.

### macOS

```bash
brew install python@3.12 node git
```

Then follow the native instructions. Docker Desktop also works unchanged.

## Configuration

Copy `.env.example` to `.env`. Every variable is documented in that file and
every one has a safe default. `.env` is git-ignored and must never be committed.

Settings are read once at startup into a typed `Settings` object in
`apps/api/src/mind_archive/config.py`. Add new settings there rather than
reading the environment directly.

## Project layout

```
mind-archive/
├── apps/
│   ├── api/           FastAPI backend
│   │   ├── src/mind_archive/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── web/           React frontend
│       ├── src/
│       └── package.json
├── docs/
│   ├── project-memory/   Decisions, state, milestones, sessions
│   └── archive/          Original planning notes
├── scripts/           Development helpers
├── data/              Your archive. Git-ignored.
└── docker-compose.yml
```

## Working on the project

Read [AGENTS.md](../AGENTS.md) before your first change. It applies to humans
and AI agents alike, and describes the read order, working method and the
definition of done.

The short version:

1. Understand before modifying. Read the relevant docs; find the affected files.
2. Make the smallest coherent change.
3. Iterate freely — run whichever checks are useful to you, when they are useful.
4. Review your diff.
5. Update the documentation your change affects.
6. Record any architectural decision in `docs/project-memory/DECISIONS.md`.
7. Log the session — see [Session memory](#session-memory) below.
8. At the milestone boundary, run `python scripts/dev.py verify` and fix what
   it finds.

Work on the current milestone only. Found something else worth doing? Put it in
[BACKLOG.md](BACKLOG.md).

## Session memory

Every working session is recorded in the repository, so that the project's
memory never depends on an AI chat history that will be lost.

```bash
python scripts/session.py start "short description of the work"
# ... do the work ...
python scripts/session.py end
python scripts/session.py check      # validates project memory
```

The mechanism is described in
[project-memory/SESSION_PROTOCOL.md](project-memory/SESSION_PROTOCOL.md).
`scripts/session.py check` also runs in CI.

## Tests and when to run them

**You decide when to verify. Nothing runs automatically** — there is no
pre-commit hook, no watcher, and no check wired into saving a file.

Checks are **required** at three points (decision D-018):

1. Before calling a milestone complete
2. Before opening a pull request
3. Before a release or deployment

```bash
python scripts/dev.py verify     # everything, then tidies up — the gate
```

In between, run whatever is relevant to what you touched, whenever you like:

```bash
python scripts/dev.py test              # both suites
python scripts/dev.py test backend      # or just one
python scripts/dev.py lint
python scripts/dev.py types
python scripts/dev.py format --fix      # rewrite files
python scripts/dev.py build             # production build
```

**Why it works this way.** Most development time goes on exploration — trying
an approach, throwing it away, trying another. The code is *expected* to be
broken during that, and running a full suite after every edit is slow enough
that people start skipping or working around it, which is worse than an honest
gate. Iterate freely; verify deliberately; let CI be the backstop.

**The one rule that does not bend:** never claim a check passed unless you ran
it. "I have not run the tests yet" is a perfectly good thing to say.

### Where tests live

Backend tests are in `apps/api/tests/` and use `pytest` with FastAPI's
`TestClient`. Frontend tests sit beside their components as `*.test.tsx` and
use Vitest with Testing Library.

Test the things that would actually hurt if they broke: API contracts,
importers against malformed and hostile input, path safety, and the user flows
that matter. Do not chase a coverage number.

### Running checks natively

If you are working outside Docker, the underlying commands are in the
[Running natively](#running-natively) section above. `scripts/dev.py` always
uses Docker.

## Git

```
feat:     a new capability
fix:      a bug fix
docs:     documentation only
refactor: no behaviour change
test:     tests only
chore:    tooling, config, housekeeping
```

Small, meaningful commits. The default branch is `main`.

Before committing, run `git status` and read `git diff --cached`. Confirm there
is no `.env`, no secret, no database file and no personal archive.

## Troubleshooting

**Port already in use.** Change `MIND_ARCHIVE_API_PORT` or `WEB_PORT` in `.env`.

**Frontend cannot reach the API.** Check `VITE_API_BASE_URL` in `.env` and that
your origin is in `MIND_ARCHIVE_CORS_ORIGINS`.

**File changes not detected in WSL.** The repository is probably on `/mnt/c`.
Move it into the Linux filesystem.

**`ModuleNotFoundError: mind_archive`.** The package was not installed in
editable mode. Run `pip install -e ".[dev]"` from `apps/api`.

**Docker build is slow the first time.** Expected. Later builds are cached.
