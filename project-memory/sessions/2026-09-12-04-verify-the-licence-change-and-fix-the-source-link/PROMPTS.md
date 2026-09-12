# Prompts

The instruction given during this session. Abridged — it was a structured brief;
the substance is below.

---

**1.** *("Complete the License/Private-Repository Policy Step".)* Continue
autonomously from the working tree, within the same boundaries:

> 1. Run: `python scripts/dev.py test frontend`
> 2. If the frontend tests fail because of the licence/policy changes: diagnose,
>    fix the underlying issue, rerun until they pass.
> 3. Inspect `ContributePanel` and resolve the remaining issue identified in the
>    handoff: *"Read the source" must not misleadingly point users toward a
>    private repository while the product is explicitly proprietary and not
>    source-available.* Choose the smallest coherent product/UI wording or
>    behavior change. Preserve the intended contribution/contact experience.
> 4. Review whether `CHANGELOG.md` should now receive a concise entry for the
>    licence/repository-policy change. This is now in scope. Do not rewrite
>    historical entries.
> 5. Run the relevant verification after all changes.
> 6. Review the resulting diff for accidental unrelated changes.

Hard boundaries restated: no commit, no push, no GitHub settings, no public
repository, no visibility change, no rename, no history rewriting, no deploy, no
DNS, no Pages, no building the public-release mechanism yet, no copying
`project-memory/`, no removing historical or session records that mention
PolyForm, and no new commercial or payment system.
