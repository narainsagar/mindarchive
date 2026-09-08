# Getting your conversations sooner

Requesting an export from ChatGPT is the right way to get your data, and it is
slow. OpenAI's own confirmation email says:

> We have started preparing your data export, this process may take a few days.
> We will email you when it is ready to download

This page covers what to expect, the trap that costs people their export, and an
optional faster route.

---

## First: request it now

The single most effective thing is to start the clock before you need to.
**Settings → Data controls → Export data**, at
[chatgpt.com/#settings/DataControls](https://chatgpt.com/#settings/DataControls).

Two things about that process are not obvious and both cost people their export:

**The download link expires 24 hours after the email arrives.** This is where
the widely repeated "24 hours" figure comes from. It is a deadline, not a wait.
Miss it and you start again.

**Only your most recent request is fulfilled.** Requesting a second time because
the first felt slow silently cancels the first. Ask once, then wait.

When it arrives, save the `.zip` into your inbox folder — `data/inbox/` by
default — and Mind Archive imports it on its own.

---

## The faster route

`scripts/browser/chatgpt-export.js` gets your conversations in minutes instead
of days.

It is a script **you** run, in **your** browser, on **your** account. It asks
ChatGPT's web app for your conversations the same way the page in front of you
already does, and saves them as a `conversations.json` file. You then put that
file in your inbox like any other export.

### Why this does not compromise Mind Archive

**Mind Archive never runs it, never sees your session, and never contacts
OpenAI.** It only ever reads a file you put in a folder. That separation is
deliberate, and it is the reason this is acceptable at all — see decision D-024.

Other tools ask you to paste your ChatGPT session token into their interface.
**Do not do that, with any tool, including one claiming to be ours.** That token
can read everything in your account and send messages as you. This script never
asks for it: the browser already holds the session, and the token never leaves
the tab.

### How to run it

1. Open [chatgpt.com](https://chatgpt.com) and make sure you are logged in.
2. Open the developer console — `F12`, or `Ctrl+Shift+J` (`Cmd+Option+J` on a
   Mac).
3. If the console asks you to type `allow pasting`, do that first. It is a
   safety feature, and it is right to make you think.
4. Open `scripts/browser/chatgpt-export.js`, **read it**, then paste the whole
   file and press Enter.
5. Wait. It prints progress and goes deliberately slowly.
6. `conversations.json` downloads when it finishes.
7. Move that file into `data/inbox/`.

### What you should know before using it

- **The endpoints are undocumented.** They are not part of OpenAI's public API
  and may change, break, or be blocked at any time. If the script stops working,
  that is why, and the official export is always there.
- **It may violate OpenAI's Terms of Use.** The counter-argument — that this is
  your own data, which GDPR Article 20 gives you a right to port — is a real one,
  but it is yours to weigh. We are not going to pretend the question does not
  exist.
- **It cannot fetch images or file attachments.** The official export can. If
  you want a complete archive, use the official export; if you want your
  conversations today, use this.
- **Going too fast can rate-limit your account.** The script pauses between
  requests for that reason. Do not remove the pauses.

### Use both

They are not alternatives. Run the script today so you can start using your
archive, and let the official export arrive in its own time. Re-importing costs
nothing: Mind Archive compares what is already in your archive and reports
"12 new, 8 updated, 392 already in your archive", writing only what actually
changed.

---

## Already have exports somewhere else?

Point the inbox at the folder you keep them in:

```bash
# in .env
MIND_ARCHIVE_INBOX_DIR=~/Documents/ai-exports
```

Mind Archive reads only `.zip` and `.json` files there, and **leaves your files
exactly where they are** — moving things out of a folder you use for other
purposes would be presumptuous. A small `.mind-archive-imported.json` ledger
records what has already been read so nothing is imported twice.

The default, `data/inbox/`, is a folder Mind Archive owns. There it does tidy
up: imported files move to `imported/`, unreadable ones to `failed/` with a note
saying why. An empty inbox means everything is in.

---

## Other providers

Only ChatGPT is supported today. Claude, Gemini and others are Milestone 5 —
see [ROADMAP.md](ROADMAP.md).
