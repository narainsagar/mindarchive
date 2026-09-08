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

**Assumption this supports:** The repository must be understandable by any agent
or by a human, from the repository alone (D-013). Mind Archive itself must never
depend on Ollama, Qwen, Claude, Gemini, Cursor or any coding tool.

**Explicitly out of scope:** Local-model integration *inside the product*. This
research concerns the development environment only.

**Revisit when:** Choosing a local model to install, which requires measuring
the machine's actual CPU, RAM, GPU and VRAM first. Not yet done.

---

## R-003 — Repository structure reduces agent token usage

Coding agents can spend a substantial share of their interaction budget simply
searching a repository for context. A clear, indexed source of truth lets an
agent read a small number of known files instead of exploring.

**Assumption this supports:** The read order defined in
[AI_AGENT_PROTOCOL.md](AI_AGENT_PROTOCOL.md), and the decision to keep planning
transcripts out of the working tree root (they were moved to `docs/archive/` on
2026-09-08).

**Observed on 2026-09-08:** Before cleanup, roughly half the repository's
content by size was raw conversation transcript, which every agent had to read
past to find the actual specification.
