# Research

Technical findings and the assumptions they support. Update an entry when the
underlying assumption changes — do not delete it, so the reasoning stays
traceable.

---

## R-001 — Development machine capability (measured 2026-09-08)

Measured on the primary development machine, Windows 11 Home 10.0.26200:

| Tool | Windows host | WSL2 (Ubuntu 22.04.2 LTS) |
|---|---|---|
| Node.js | not installed | v24.18.0 |
| npm | not installed | 11.16.0 |
| Python | 3.7.9 (end-of-life) | 3.8.10 (end-of-life) |
| Git | 2.50.1 | 2.34.1 |
| Docker Engine | 29.7.2, daemon running, Linux containers | via Docker Desktop |
| Docker Compose | v5.4.0 | v5.4.0 |

**Findings:**

1. Neither host has a Python new enough for a comfortable modern FastAPI +
   Pydantic v2 stack. Python 3.8 reached end-of-life in October 2024.
2. WSL2 has a current Node.js, so frontend development runs natively there today.
3. Docker and Compose are current and working, so containers are the reliable
   path for the backend.

**The development environment is WSL2**, deliberately and permanently. The
developer keeps the Windows host free of developer tooling and works in bash;
git, python3 and Node are already installed in the distribution. Documentation
should therefore lead with bash and `python3`, and a WSL problem should be
fixed rather than routed around with "use PowerShell instead".

Two Docker Desktop defaults break WSL and neither explains itself, so both are
documented in `docs/DEVELOPMENT.md` and `docs/TRY_IT.md`:

1. WSL integration is off per-distribution by default — no
   `/var/run/docker.sock`.
2. `~/.docker/config.json` is written as `{"credsStore": "desktop.exe"}`, and
   the Linux CLI cannot execute a Windows `.exe`, so the first image pull fails
   with `exec format error`. Fixed by emptying the file; it only affects
   private-registry logins.

**Assumption this supports:** Docker is the primary supported backend path
(see [DECISIONS.md](DECISIONS.md) D-006) and Python 3.11+ is the floor (D-007).

**Revisit when:** A current Python is installed on the host, or the WSL distro
is upgraded. The decision to keep Docker primary should survive that anyway,
because it also serves contributors.

---

## R-002 — Local AI coding agents are a development tool, never a product dependency

Planning research compared terminal and IDE coding agents for developing Mind
Archive at low cost: Qwen Code, OpenCode, Cline, Aider, Goose, OpenHands, and
Code Buddy.

**Key distinction established:** the *agent* (software that reads files, edits,
runs tests, uses Git) is separate from the *model* (the AI generating the code).
Free agent software does not mean free inference. Genuinely unlimited,
zero-cost usage means running a model locally, typically through Ollama, vLLM
or LM Studio behind an OpenAI-compatible API.

**Findings:**

- Qwen Code requires Node.js 22+ for npm/manual installation and supports local
  inference servers through an OpenAI-compatible API.
- Qwen Code's earlier Qwen OAuth free tier was discontinued on 2026-04-15.
  Planning must not assume a hosted free tier will remain available.
- Practical local-model sizing, approximate and quantisation-dependent:

  | Hardware | Workable model size | Experience |
  |---|---|---|
  | 8 GB RAM, no GPU | 3B–4B | very limited |
  | 16 GB RAM, no GPU | 7B–8B | usable |
  | 32 GB RAM, no GPU | 14B | good |
  | 32 GB RAM + 8 GB VRAM | 7B–14B | very good |
  | 64 GB RAM + 12–16 GB VRAM | 14B–32B | excellent |

- VRAM matters far more than system RAM for inference speed. A model that does
  not fit in VRAM can spill to system RAM, with a significant performance cost.
- Qwen Code itself is lightweight — any modern 4-core CPU, 8 GB RAM minimum
  (16 GB recommended), ~2–5 GB of storage. The hardware demand comes almost
  entirely from running a model locally, not from the agent.

**Machine tiers for running this project plus a local model:**

| Tier | CPU | RAM | GPU | Disk |
|---|---|---|---|---|
| Minimum practical | 4+ cores | 16 GB | none | 100 GB free |
| Recommended | 6–12 cores | 32 GB | 8–12 GB VRAM | 200 GB free |
| Enthusiast | 12+ cores | 64 GB+ | 16–24 GB+ VRAM | 500 GB free |

Mind Archive itself is undemanding — React, FastAPI, SQLite and a filesystem
run comfortably on an ordinary laptop. Only the optional local model is heavy.

**Agent ranking reached during planning**, best first for this project: Qwen
Code with a local Qwen model; OpenCode with a local model; Cline (if you prefer
working inside VS Code); Aider (strongest for Git-centric edits); Goose;
OpenHands (heavier than V1 needs).

**A two-agent pattern was proposed:** one agent as the builder for routine
development, a second as an occasional reviewer for architecture, security and
alternative implementations, with a stronger hosted model consulted for
difficult problems. Never adopted formally, and not a project requirement.

**Assumption this supports:** The repository must be understandable by any agent
or by a human, from the repository alone (D-013). Mind Archive itself must never
depend on Ollama, Qwen, Claude, Gemini, Cursor or any coding tool.

**Explicitly out of scope:** Local-model integration *inside the product*. This
research concerns the development environment only.

**Revisit when:** Choosing a local model to install. That requires measuring the
machine first — not yet done. On Linux or WSL2:

```bash
lscpu | grep -E 'Model name|CPU\(s\)'   # CPU
free -h                                  # RAM
nvidia-smi 2>/dev/null || echo "no NVIDIA GPU"   # GPU and VRAM
df -h /                                  # disk
```

Measure before installing a model, rather than downloading something the
machine cannot comfortably run.

---

## R-004 — Getting a ChatGPT export: timings, traps, and whether it can be automated

Researched 2026-09-08, because the importer had been built and tested for two
milestones without ever seeing a real export, and the reason turned out to be
that getting one is slow and its rules are not obvious.

### The official export

| | |
|---|---|
| How long it takes | **OpenAI's own confirmation email says "this process may take a few days".** Help-centre documentation allows up to 7 days. In practice reports range from an hour to two days. |
| **Link expiry** | **The download link expires 24 hours after the email arrives.** |
| **Repeat requests** | **Only the most recent request is fulfilled.** Requesting again silently cancels the previous job. |
| Route | Settings → Data controls → Export data, at `https://chatgpt.com/#settings/DataControls` |
| Contents | `conversations.json`, `chat.html`, `user.json`, `message_feedback.json`, plus images and files |

**Primary source, observed 2026-09-08.** The confirmation email received after
requesting an export reads, verbatim:

> You recently requested a copy of your ChatGPT data.
>
> We have started preparing your data export, this process may take a few days.
> We will email you when it is ready to download

This is worth recording because it contradicts what people expect. The figure
"24 hours" is widely believed — it appears in ChatGPT's own interface — but it
refers to the **download link's expiry**, not the wait. The email itself
promises nothing faster than "a few days".

**So there are two separate clocks, and confusing them is what costs people
their export:**

1. **Preparing it:** a few days, per OpenAI's email. Nothing can speed this up.
2. **Downloading it:** 24 hours from when the email arrives, then the link is
   dead and you start over.

Someone who requests an export, misses the email for a day, and finds a dead
link has to begin again — and if impatience leads them to request twice, they
cancel their own job. Both facts belong in the interface; neither was there
before this was researched.

An earlier version of the import panel told users the export takes "up to 24
hours". That was wrong in the most misleading possible way: it set an
expectation of one day for something that takes several, using a number that
actually describes a deadline.

### There is no official API for ChatGPT history

The OpenAI Platform API (`api.openai.com`) does not expose ChatGPT consumer
conversation history. Its `conversation` objects hold conversations *created
through the API*; they are a different product and a different data store.
There is no endpoint for "my ChatGPT chats", and this has been a standing
feature request for years.

**So the acquisition delay cannot be legitimately automated.** The export job
runs on OpenAI's infrastructure and the queue is theirs. Anything Mind Archive
does to make importing faster has to be on the ingestion side.

### The unofficial route

ChatGPT's web app uses undocumented `/backend-api/` endpoints —
`/backend-api/conversations` to list and `/backend-api/conversation/{id}` for
detail — authenticated by the session JWT from `chatgpt.com/api/auth/session`.
Several third-party tools use these.

Findings, all consistent across sources:

- **Undocumented and unstable.** They may change, break or be blocked at any
  time without notice. Excessive use can trigger rate limits.
- **May violate OpenAI's Terms of Use.** Tool authors disclaim rather than
  assert compliance.
- **The session token grants full account access** — reading all history and
  sending new messages as the user. This is the decisive point.
- The counter-argument is real: it is the user's own data, and GDPR Article 20
  gives a right to data portability.

**Two shapes of the same idea, with very different risk:**

1. A tool that asks you to **paste your session token into its UI**. The
   credential leaves the browser and enters an application. For a product whose
   pitch is privacy, asking for this is self-defeating.
2. A script you paste into the **console of your own logged-in tab**. It reuses
   the session the browser already has, no token is pasted anywhere, and the
   result is a JSON file downloaded locally.

The second keeps the credential inside the browser entirely. It is the basis of
D-024: Mind Archive never contacts OpenAI and never handles a token; the fast
path is a user-run browser script whose output is dropped into the inbox like
any other file.

**Unverified:** whether the unofficial endpoints return the same structure as
`conversations.json`. The detail endpoint is believed to return the same
`mapping` tree, since the export is generated from the same data, but this needs
checking against both. `scripts/inspect_export.py` runs on either and reports
structure, which is how to compare them.

**Revisit when:** a real export has been imported, or when the endpoints change.

**Sources:** OpenAI Help Center on exporting history and data; OpenAI developer
community threads on retrieving ChatGPT conversations via the API; the README
disclaimers of `ezwep/chatgpt-exporter` and similar tools.

---

## R-005 — Import speed is bounded by the filesystem, not by our code

Measured 2026-09-08 against a synthetic export of 2,000 conversations
(`scripts/make_fixture_export.py`), inside the API container.

| Where the archive is written | Write | Index | Total |
|---|---|---|---|
| Container filesystem (`/tmp`) | 1.9s | 2.8s | **4.7s** |
| Windows bind mount (`./data` via Docker Desktop) | 48.2s | 79.2s | **127.4s** |

Parsing the export itself takes 1.3s in both cases — it never touches the disk.

**The bind mount is 27× slower.** The same code, the same data, the same
container; only the filesystem differs. Import speed is dominated by
per-file I/O across the Windows/Linux boundary, and each conversation is two
small file writes plus a read-back when indexing.

**What this means:**

- **Do not optimise the importer against this number.** Batching writes or
  pooling SQLite connections would win almost nothing; the cost is in the
  filesystem crossing, not in our code. 4.7s for 2,000 conversations is the
  honest measure of the code's speed.
- It is the same root cause as the existing advice in `docs/DEVELOPMENT.md` to
  keep the repository inside the WSL2 filesystem rather than `/mnt/c`.
- On Linux, macOS, or with the archive inside the WSL2 filesystem, imports are
  effectively instant.
- It justifies scanning the inbox on a background thread: on a slow filesystem
  a large import takes minutes, and doing it inline would leave the server
  refusing connections throughout.

**Revisit when:** someone reports a slow import on a native Linux filesystem.
That would mean the bottleneck has genuinely moved into our code, and the
measurement should be repeated before anything is changed.

---

## R-003 — Repository structure reduces agent token usage

Coding agents can spend a substantial share of their interaction budget simply
searching a repository for context. A clear, indexed source of truth lets an
agent read a small number of known files instead of exploring.

**Assumption this supports:** The read order defined in
[AI_AGENT_PROTOCOL.md](AI_AGENT_PROTOCOL.md), and the decision to keep planning
transcripts out of the working tree entirely (merged into project memory and
removed on 2026-09-08; they remain in git history at commit `fcf1f5c`).

**Observed on 2026-09-08:** Before cleanup, roughly half the repository's
content by size was raw conversation transcript, which every agent had to read
past to find the actual specification.
