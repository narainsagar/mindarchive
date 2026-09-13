# Prompts

The instruction given during this session. Abridged — it was a structured brief.

---

**1.** *("Build the private-to-public repository publication mechanism".)*

Design and implement a safe publication tool, preferably
`scripts/publish_public.py`, standard library only, supporting at minimum
`--check` and a generation mode such as `--build <destination>`.

Core requirements, verbatim where they decide the design:

> **1. Explicit allowlist.** The public output must be based on an explicit
> allowlist of files/directories that are permitted to be published. Do NOT
> implement "copy everything, then delete private files". That is specifically
> prohibited because it is too easy for a newly added private file to leak.
>
> **2. Fail closed.** The publisher should fail rather than silently publish an
> unexpected path. If an allowed directory contains a new file, decide and
> document whether it is automatically included because the directory itself is
> explicitly public, OR it must be individually allowlisted. Use the safest
> practical model.
>
> **3. Private exclusions** — `project-memory/`, `sessions/`, `prompts/`,
> `.claude/`, `CLAUDE.md`, `GEMINI.md`, `QWEN.md`, private agent rules, private
> research, development transcripts, machine/network-specific information,
> infrastructure details, personal archives, credentials, `.env`, databases and
> runtime data. **Inspect the repository rather than relying only on this list.**
>
> **6. Secrets and privacy checks** — detect obvious secret and private patterns
> and fail safely. "Do not build a brittle scanner that produces huge false
> positives. Use sensible checks and document limitations."
>
> **7.** The tree must preserve relative paths, contain no Git metadata, be
> reproducible, be safe to delete and regenerate, and **never modify the private
> working tree.** Prefer generating outside the repository.
>
> **8.** The tool must NOT initialize or manipulate the final public *[the brief
> ends mid-sentence here]*.

`AGENTS.md` to be published "only if it is confirmed safe for public release;
otherwise exclude it", and the supplied candidate list treated as "a starting
point, NOT as permission to blindly include everything".

Boundaries: proceed autonomously with local non-destructive work; stop only for
git push, GitHub repositories or settings, deployment, DNS/TLS, credentials, paid
services, destructive operations, or history rewriting. **Do not commit until
explicitly approved. Do not push.**
