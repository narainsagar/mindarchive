# Mind Archive

**Your Personal AI Mind Archive.**

*Own your AI memory. Simple, private, and yours.*

Mind Archive is a local-first, source-available application for preserving,
organising, searching and exporting your AI conversations, memories, knowledge
and files — so that they stay yours, and stay useful even when you change AI
provider.

Your archive lives on your own computer. There is no account, no server, and
nothing is uploaded anywhere unless you explicitly configure it.

> **Status: early development.** Milestone 1 is complete — this is a runnable,
> documented foundation with a working frontend, backend, Docker setup and CI.
> It does not import or browse conversations yet. That is Milestone 2.

---

## Quick start

The supported way to run Mind Archive is Docker.

```bash
git clone https://github.com/YOUR-USERNAME/mind-archive.git
cd mind-archive
cp .env.example .env
python scripts/dev.py up --build
```

Then open:

- **Mind Archive** — http://localhost:5173
- **API** — http://localhost:8000
- **API documentation** — http://localhost:8000/docs

To stop: `python scripts/dev.py down`. Your archive stays in `./data`.

Plain `docker compose up --build` works too — `scripts/dev.py` is a convenience
wrapper, not a requirement.

## Running without Docker

You need **Python 3.11 or newer** and **Node.js 20 or newer**.

**Backend:**

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn mind_archive.main:app --reload --port 8000
```

**Frontend, in a second terminal:**

```bash
cd apps/web
npm install
npm run dev
```

Full instructions, including WSL2 and Windows specifics, are in
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## What makes Mind Archive different

**Local first.** Everything works with no network connection and no account.

**Privacy first.** Nothing leaves your machine. Cloud features are opt-in,
off by default, and can never be enabled silently.

**You own your data.** Conversations are stored as ordinary Markdown and JSON
files you can read, search, back up and move with any tool you like. SQLite is
used only for indexing — delete it and your archive is still intact.

**No provider lock-in.** ChatGPT is simply the first import format. Claude,
Gemini, Google AI Studio, local models and future providers all plug in through
the same adapter interface. None of them sits at the centre.

**Human readable.** The interface, the documentation and the stored data are all
written to be read by a person.

## Project layout

```
mind-archive/
├── apps/
│   ├── api/          Python + FastAPI backend
│   └── web/          React + TypeScript + Vite frontend
├── docs/             Documentation
│   ├── project-memory/   Decisions, state, milestones
│   └── archive/          Original planning notes (history)
├── data/             Your archive. Never committed.
├── AGENTS.md         Instructions for AI agents and contributors
├── MASTER.md         The founding specification
└── docker-compose.yml
```

## Configuration

Copy `.env.example` to `.env` and edit it. Every setting has a safe default;
the file documents what each one does. `.env` is git-ignored and must never be
committed.

## Documentation

| Document | What it covers |
|---|---|
| [PRODUCT.md](docs/PRODUCT.md) | What Mind Archive is and who it is for |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the system is put together |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Setting up and working on the project |
| [SECURITY.md](docs/SECURITY.md) | Privacy model and reporting a vulnerability |
| [ROADMAP.md](docs/ROADMAP.md) | Where the project is going |
| [BACKLOG.md](docs/BACKLOG.md) | Ideas and known gaps |
| [DECISIONS.md](docs/DECISIONS.md) | Why the project is built this way |
| [GITHUB_PAGES.md](docs/GITHUB_PAGES.md) | Publishing the documentation site |

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) — the
second one applies whether you are a human or an AI coding agent.

Outside contributions are not being accepted yet: a Contributor Licence
Agreement has to exist first, because commercial licences are sold. Issues and
ideas are welcome in the meantime.

You should be able to clone, install, run, understand, modify and test the
project without any private credentials.

## License

Mind Archive is **source-available**, not open source.

- **Free** for any noncommercial use, under
  [PolyForm Noncommercial 1.0.0](LICENSE) — personal use, study, research,
  hobby projects, and use by charities, schools, public research bodies and
  government institutions.
- **Commercial use requires a licence.** See [LICENSING.md](LICENSING.md).

Your archive is yours under every tier. Licensing governs the software, never
your data.
