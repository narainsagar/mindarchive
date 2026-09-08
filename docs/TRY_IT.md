# Try it yourself

A clean run from nothing, and how to check each part works. Fifteen minutes.

You need **Docker Desktop running**. Nothing else.

---

## 1. Start it

```bash
cd mind-archive
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

### B. Your real ChatGPT export — the official way

In ChatGPT: **Settings → Data controls → Export data**.

- ChatGPT's email says preparing it **may take a few days**
- **The download link expires 24 hours after that email arrives**
- **Asking again cancels your previous request** — ask once, then wait

When it arrives, save the `.zip` into `data/inbox/`.

### C. Your real conversations, today

[docs/FASTER_IMPORT.md](FASTER_IMPORT.md) — a script you paste into your own
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

## 6. Worth trying, because these are the interesting cases

**Import the same file twice.** Save it into the inbox again.

> *"Nothing new — all 197 conversations were already in your archive."*

Nothing is rewritten. Check with `ls -l` — the timestamps do not move.

**Delete the search index.**

```bash
rm data/mind_archive.db
python scripts/dev.py down && python scripts/dev.py up
```

Everything comes back. The database is an index, never your archive — if that
ever stops being true, it is a bug.

**Edit a conversation by hand.** Open any `conversation.md`, change a word, save.
Refresh the interface — your edit is there. The files are the source of truth.

**Toggle dark mode**, top right. Reload; it remembers.

**Point the inbox at your own folder.** In `.env`:

```
MIND_ARCHIVE_INBOX_DIR=/path/to/where/you/keep/exports
```

Restart. Your files are read but **left exactly where they are**.

---

## 7. Check nothing leaks

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

## 8. Run the tests

```bash
python scripts/dev.py verify
```

Everything: lint, types, both test suites, a production build, and a
project-memory check. Takes about a minute and tidies up after itself.

Nothing runs automatically while you work — you decide when to check.

---

## 9. Stop

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
| Interface cannot reach the API | Backend still starting. `python scripts/dev.py logs api` |
| Port already in use | Change `MIND_ARCHIVE_API_PORT` or `WEB_PORT` in `.env` |
| Import is slow | Expected on Windows. Docker's bind mount is ~27× slower than a native filesystem — see project-memory RESEARCH R-005. On Linux or inside WSL2 it is near-instant |
| Nothing in the inbox is picked up | Only `.zip` and `.json` are read. Check the file is directly in the folder, not a subfolder |
| Changes are not showing | The frontend hot-reloads; the backend restarts on save. `python scripts/dev.py restart` if in doubt |

---

## What exists so far

| | |
|---|---|
| **Milestone 1** | Runnable foundation — backend, frontend, Docker, CI |
| **Milestone 2** | ChatGPT importer |
| **Milestone 3** | Browse, read and search |
| **Milestone 3.5** | The inbox, honest re-import reporting, the faster route |
| **Milestone 4** | Next: tags, projects, organisation |

**Not there yet:** tags and projects, editing or deleting from the interface,
attachments (recorded as placeholders), any provider but ChatGPT, and anything
cloud. See [ROADMAP.md](ROADMAP.md).
