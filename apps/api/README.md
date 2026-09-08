# Mind Archive — backend

The Python + FastAPI backend for Mind Archive.

Most people should run the whole stack with Docker from the repository root:

```bash
docker compose up --build
```

## Running just the backend

Requires **Python 3.11 or newer**.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn mind_archive.main:app --reload --port 8000
```

- API — http://localhost:8000
- Interactive documentation — http://localhost:8000/docs

## Checks

```bash
pytest                  # tests
ruff check .            # lint
ruff format --check .   # formatting
mypy src                # types
```

## Layout

```
src/mind_archive/
├── main.py       FastAPI application, CORS, router wiring
├── config.py     Typed settings from the environment
├── events.py     In-process event bus
├── paths.py      Traversal-safe filesystem paths
└── routes/
    ├── health.py     GET /api/health
    └── config.py     GET /api/config
```

## Things to know before changing this

**Settings are typed and centralised.** Add new options to `config.py` rather
than reading `os.environ` directly.

**`/api/config` goes straight to the browser.** Never add a secret to
`PublicConfig`. There is a test that will fail if you do.

**Untrusted paths go through `paths.py`.** From Milestone 2 the application
writes files using names taken from other people's archive exports. Never join
those onto a directory by hand.

**Events carry identifiers, not content.** Events end up in logs, and logs must
never contain the user's conversations.

See [`../../AGENTS.md`](../../AGENTS.md) and
[`../../docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md).
