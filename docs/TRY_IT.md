---
title: Try it yourself
permalink: /try-it/
---

# Try it yourself

A clean run from nothing, and how to check each part works. Fifteen minutes.

You need **Docker Desktop running**. Nothing else.

> **`python` or `python3`?** On Linux, WSL and macOS it is `python3` — Ubuntu
> ships no bare `python`. On Windows PowerShell it is `python`. Every command
> below works either way; use whichever your shell has.

### On Windows: WSL2 works, with two things to set up first

WSL2 is a fully supported path, and the better one if you already live in a
Linux shell. Docker Desktop needs two adjustments that it does not make for you,
and both fail with errors that do not explain themselves:

**1. Turn on WSL integration for your distribution.**
Docker Desktop → Settings → Resources → WSL integration → enable your distro →
Apply & restart. Without it there is no `/var/run/docker.sock` and every command
fails with *"failed to connect to the docker API"*.

**2. Remove the Windows credential helper from WSL.**

```bash
cp ~/.docker/config.json ~/.docker/config.json.bak
printf '{}
' > ~/.docker/config.json
```

Docker Desktop writes `{"credsStore": "desktop.exe"}` into WSL's config, and the
Linux CLI cannot execute a Windows `.exe`. Builds fail on the very first image
pull with *"docker-credential-desktop.exe: exec format error"*. The setting only
affects signing in to private registries; Mind Archive pulls public images only.

**A note on speed.** A checkout under `/mnt/c` is on the Windows filesystem, and
file I/O across that boundary is roughly **27× slower** than native — measured,
see project-memory RESEARCH R-005. Everything works; imports just take minutes
instead of seconds. Cloning into your WSL home (`~/`) instead makes it
near-instant.

---

## 1. Start it

```bash
cd mindarchive
cp .env.example .env
python scripts/dev.py up --build
```

First build takes a few minutes. After that it is seconds.

Open **http://localhost:5173**. You should see the workspace, in light mode,
saying your archive is empty.

Also worth a look: **http://localhost:8000/docs** — the API, documented and
clickable.

```bash
python scripts/dev.py status      # what is running
python scripts/dev.py logs api -f # follow the backend (Ctrl+C to stop watching)
```

---

## 2. Get something to import

You have three options. **Option A needs nothing and works right now** — use it
to try everything, then come back to B or C for your real conversations.

### A. Make a synthetic export

```bash
python scripts/make_fixture_export.py data/inbox/test.zip --conversations 200
```

Deliberately messy: missing titles, missing dates, every content type, edited
branches, some deliberately broken. Good for seeing how it copes.

### B. Your real export — ChatGPT or Claude

| | Where | What to expect |
|---|---|---|
| **ChatGPT** | Settings → Data controls → Export data | Email says it "may take a few days" |
| **Claude** | Settings → Privacy → Export Data | Emailed link, also expires in 24 hours |

For both: **the download link expires 24 hours after the email arrives**, and
**asking again cancels your previous request**. Ask once, then wait.

When it arrives, save the `.zip` into `data/inbox/`. Mind Archive works out
which provider it came from by looking inside the file — both providers name
theirs `conversations.json`, so the filename proves nothing.

### C. Your real conversations, today

[docs/FASTER_IMPORT.md]({{ '/faster-import/' | relative_url }}) — a script you paste into your own
browser console. Takes minutes. Mind Archive never sees your session and never
contacts OpenAI; it only reads the file the script downloads.

---

## 3. Import it

**Just save the file into `data/inbox/`.** That is the whole thing.

In the interface, the Import panel shows the folder and how many files are
waiting. Click **Check that folder now**, or restart — it also scans on startup.

Or use the file picker in the Import panel if you prefer choosing a file.

**What you should see:** *"Read 1 file: 197 new."* — and the file has moved into
`data/inbox/imported/`. An empty inbox means everything is in.

---

## 4. Look at what it did

This is the part that matters most, so look at it directly:

```bash
ls data/archive/chatgpt/
cat "data/archive/chatgpt/<any folder>/conversation.md"
```

Ordinary Markdown with a YAML header, plus a `metadata.json` beside it. Readable
in any editor, on any machine, in ten years, whether or not Mind Archive still
exists. That is the whole point of the product.

---

## 5. Browse and search

Back in the interface:

- Conversations are listed newest first
- Type in the search box — results narrow as you type, with matches highlighted
- Click one to read it, `Esc` or **Back** to return
- Try nonsense: `C++`, `NEAR(`, a lone `"`. None of them should error

---

## 6. Tag something

Open any conversation. Under the title there is a tag box.

- Add a tag — it appears immediately
- Go **Back**: a filter bar has appeared above the list, with a count
- Click the tag to filter; click it again, or **All**, to clear it
- Search *and* filter at once — they combine, they do not replace each other

Then look at where it went:

```bash
cat "data/archive/chatgpt/<the folder>/metadata.json"
```

Your tag is in there, in the file, beside the conversation. **Not in the
database** — that is deliberate, and the next check shows why.

---

## 7. Take it all with you

Click **Export everything** at the top of the archive.

Unzip what you get and look inside. It is your archive folder — the same
Markdown, the same JSON, the same layout — plus a `README.txt` for whoever
opens it in five years without this application. No database, nothing that
needs Mind Archive to read it.

That is the whole promise of the product in one button, so it is worth actually
opening the zip rather than taking my word for it.

---

## 8. Worth trying, because these are the interesting cases

**Import the same file twice.** Save it into the inbox again.

> *"Nothing new — all 197 conversations were already in your archive."*

Nothing is rewritten. Check with `ls -l` — the timestamps do not move.

**Tag something, then re-import.** Your tags survive. Every export is a *full*
export, so importing next month's download rewrites all your metadata — and an
export contains no tags. Getting this wrong would erase months of your own
filing without anyone noticing.

**Delete the search index — after tagging something.**

```bash
rm data/mind_archive.db
python scripts/dev.py down && python scripts/dev.py up
```

Everything comes back, **including your tags**. The database is an index, never
your archive. Tags are the one thing here you made rather than imported, so if
they had lived only in SQLite, deleting a rebuildable cache would have destroyed
original work. If that ever stops being true, it is a bug.

**Edit a conversation by hand.** Open any `conversation.md`, change a word, save.
Refresh the interface — your edit is there. The files are the source of truth.

**Toggle dark mode**, top right. Reload; it remembers.

**Point the inbox at your own folder.** In `.env`:

```
MIND_ARCHIVE_INBOX_DIR=/path/to/where/you/keep/exports
```

Restart. Your files are read but **left exactly where they are**.

---

## 9. Check nothing leaks

```bash
python scripts/inspect_export.py data/inbox/imported/test.zip
```

Prints the *structure* of an export — counts, content types, branch depths — and
none of its content. Read the output: no titles, no messages, nothing private.
That is what makes it safe to paste into an issue when an importer misbehaves.

And confirm your data cannot be committed:

```bash
git status                              # data/ and .env should not appear
git check-ignore data .env local/*.zip  # all three should be listed
```

---

## 10. Run the tests

```bash
python scripts/dev.py verify
```

Everything: lint, types, both test suites, a production build, and a
project-memory check. Takes about a minute and tidies up after itself.

Nothing runs automatically while you work — you decide when to check.

---

## 11. Stop

```bash
python scripts/dev.py down     # stop; your archive stays in ./data
python scripts/dev.py clean    # also remove the built images
```

Your archive is a bind mount, not a Docker volume, so **no cleanup command can
delete it** — including `clean`.

---

## If something goes wrong

| Symptom | Likely cause |
|---|---|
| `Command 'python' not found` | You are on Linux, WSL or macOS. Use `python3` |
| `failed to connect to the docker API at unix:///var/run/docker.sock` | You are in WSL and Docker Desktop's WSL integration is off for that distribution. Either run from PowerShell instead, or turn it on: **Docker Desktop → Settings → Resources → WSL integration**, enable your distro, **Apply & restart** |
| `error getting credentials ... docker-credential-desktop.exe: exec format error` | Also WSL. Your `~/.docker/config.json` points at a Windows credential helper that Linux cannot run. Mind Archive only pulls public images, so the helper is not needed — remove it (see below) |
| Interface cannot reach the API | Backend still starting. `python scripts/dev.py logs api` |
| Port already in use | Change `MIND_ARCHIVE_API_PORT` or `WEB_PORT` in `.env` |
| Import is slow | Expected on Windows, and worst of all from WSL against `/mnt/c`. Docker's bind mount is ~27× slower than a native filesystem — see project-memory RESEARCH R-005. Clone into the WSL home directory (`~/`) rather than `/mnt/c` if you want speed |
| Nothing in the inbox is picked up | Only `.zip` and `.json` are read. Check the file is directly in the folder, not a subfolder |
| Changes are not showing | The frontend hot-reloads; the backend restarts on save. `python scripts/dev.py restart` if in doubt |

### Removing the Windows credential helper in WSL

```bash
cp ~/.docker/config.json ~/.docker/config.json.bak
python3 -c "import json,pathlib; p=pathlib.Path.home()/'.docker/config.json'; d=json.loads(p.read_text()); d.pop('credsStore',None); d.pop('credHelpers',None); p.write_text(json.dumps(d,indent=2))"
```

This only affects signing in to private registries. Mind Archive pulls
`python:3.12-slim` and `node:22-alpine`, both public, so nothing is lost. The
original is kept as `config.json.bak`.

---

## What exists so far

| | |
|---|---|
| **Milestone 1** | Runnable foundation — backend, frontend, Docker, CI |
| **Milestone 2** | ChatGPT importer |
| **Milestone 3** | Browse, read and search |
| **Milestone 3.5** | The inbox, honest re-import reporting, the faster route |
| **Milestone 4** | Tags |
| **Milestone 5** | Claude importer, whole-archive export |
| **Milestone 6** | Next: optional cloud, off by default |

**Not there yet:** projects, editing or deleting from the interface, attachments
(recorded as placeholders in the Markdown), providers beyond ChatGPT and Claude,
and anything cloud. See [ROADMAP.md]({{ '/roadmap/' | relative_url }}).

**Worth knowing before you judge it:** neither importer has ever seen a real
export. Both were written from documented formats and third-party parsers. If
something looks wrong with real data, that is the most useful bug you can find —
`python scripts/inspect_export.py <your-export.zip>` reports the structure
safely, without any conversation content.
