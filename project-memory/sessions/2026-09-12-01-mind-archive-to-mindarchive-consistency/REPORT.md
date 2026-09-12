# Report — repository audit, 2026-09-11

**The audit now lives at [`AUDIT-REPORT.md`](../../../AUDIT-REPORT.md) in the
repository root**, where the maintainer moved it, and it is kept current there:
each finding is marked Resolved, Partly done or Open as the work lands.

The full text was copied into this file when it was written, because the original
had been left in a scratch directory outside the repository. Keeping a second full
copy here would guarantee the two disagree — the reason D-010 refuses a second
decision log — so this file is a pointer instead.

**What the audit found**, in one line each, so this session's record stands alone:
the first push would have published twenty dead links because the git remote and
every documented URL disagreed about the repository name; the frontend CI job
fails on its first run for want of a `package-lock.json`; nine statements in the
repository were no longer true; six claims are believed rather than verified; and
three duplicated values have nothing checking that they still agree.

This session resolved the repository name and two of the nine false statements.
