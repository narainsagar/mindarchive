# local/

Scratch space for **your own** data while developing. Everything in this folder
is git-ignored except this README.

Put a real provider export here when you want to test an importer against
genuine data:

```
local/
├── README.md                    <- the only file that is committed
└── chatgpt-export.zip           <- ignored
```

## Why this folder exists

Importers have to survive real exports, which are far messier than anything
anyone writes by hand: unusual titles, deleted branches, missing timestamps,
multimodal messages, tool output.

But a real export contains your private conversations, so it must never enter
version control. Keeping it in one clearly-ignored folder makes that hard to get
wrong.

## Rules

- **Never commit anything from this folder.** `.gitignore` covers it, and CI
  fails the build if an export, database or `.env` is ever tracked.
- **Never paste conversation content into an issue, pull request or commit
  message.** Describe the shape of the problem instead: "a conversation with a
  null title and 400 messages", not the messages themselves.
- Test fixtures that *are* committed live in `apps/api/tests/fixtures/` and are
  entirely synthetic — written by hand to exercise specific cases, containing no
  real conversation.

## Getting a ChatGPT export

In ChatGPT: **Settings → Data controls → Export data**. ChatGPT emails you when
it is ready — its own message says this "may take a few days".

**The download link expires 24 hours after that email arrives**, and requesting
again cancels your previous request. Ask once, then wait.

The archive contains `conversations.json`, `chat.html`, `user.json` and any
images or files from your conversations.

`conversations.json` is the only file Mind Archive currently reads.
