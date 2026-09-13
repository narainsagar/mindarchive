# Report — 2026-09-12-06

No separate report. The durable output is **D-048** in
`project-memory/DECISIONS.md`, and the tool's own docstring in
`scripts/publish_public.py`, which carries the allowlist model and the reasoning
where a reader will meet it.

The measured finding, recorded here so it is not lost if D-048 is skimmed: a
generated public tree currently contains a documentation site with **38 broken
links**, because the page generator and eight of the routes it produces are
private. The publisher is finished; the repository is not yet publishable.
