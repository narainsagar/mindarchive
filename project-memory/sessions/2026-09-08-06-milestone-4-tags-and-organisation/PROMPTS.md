# Prompts — 2026-09-08-06-milestone-4-tags-and-organisation

The instructions given during this session, verbatim and in order.

No secrets appeared in any prompt, so nothing has been redacted.

---

## Prompt 1

```
I want to setup alias inside my windows powershell or project to use python3 as its been already there on python command just like we do on linux bash profile.
```

Windows has no `python3`; the name resolves to a Microsoft Store stub that opens
the Store. A `Set-Alias` in `$PROFILE.CurrentUserAllHosts` takes precedence over
anything on PATH, so `python3` now means the same interpreter as `python` in
PowerShell and VS Code's terminal. Outside the repository, so not committed.

## Prompt 2 — after a third WSL environment failure

```
Still errors so lets continue with next milestones until last one by one each,
```

The Docker credential-helper error had not been fixed, so the build still failed
in WSL. Rather than keep debugging the environment, moved on to Milestone 4 as
asked. The fix and the PowerShell alternative are both documented in
`docs/TRY_IT.md`.
