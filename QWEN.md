# Qwen Code — Mind Archive

Read [`AGENTS.md`](AGENTS.md) first. It is the canonical instruction file for
every agent working on this project, and it is not repeated here.

Then read, in order:

1. `docs/project-memory/PROJECT_STATE.md`
2. `docs/project-memory/MILESTONES.md`
3. `docs/project-memory/DECISIONS.md`

## Notes specific to this tool

Qwen Code may be run against a local model through Ollama, vLLM or LM Studio,
or against a hosted provider. That choice is a **development preference only**.

Mind Archive itself must never depend on Qwen, Ollama, or any AI coding tool.
Do not add product code that assumes a particular agent or model is present.

## Token efficiency

This repository is organised so you do not have to explore it. Read the four
files above, then open only the files your task touches. Avoid repeatedly
re-reading the tree.

Planning transcripts live in `docs/archive/`. They are history. You almost
never need them.
