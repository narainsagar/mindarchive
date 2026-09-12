---
title: Git and SSH setup
permalink: /git-ssh/
description: Clone, pull and push Mind Archive over SSH from WSL2 — including the network where port 22 does not work.
---

# Git and SSH setup

Getting Git talking to GitHub over SSH from inside WSL2, once, so that day-to-day
work needs no thought.

**Read [Development]({{ '/development/' | relative_url }}) first** for installing
and running the project. This page is only about authentication and the remote.

---

## The shape of it

```text
Windows
 └── VS Code  ──(WSL extension)──┐
                                 │
WSL2 (Ubuntu)  ←─────────────────┘
 ├── the repository, on the Linux filesystem
 ├── git
 └── ssh  ──►  ssh-agent  ──►  GitHub
```

Everything Git-related happens **inside WSL**. VS Code runs on Windows and
attaches to WSL, so the terminal you type into is a Linux shell and uses WSL's
Git, WSL's SSH keys and WSL's agent. Windows has its own Git and its own keys;
mixing the two is the cause of most "it works in one terminal but not the other"
confusion.

Keep the repository **inside the Linux filesystem** (`~/projects/...`), never on
`/mnt/c` — see the WSL2 notes in
[Development]({{ '/development/' | relative_url }}#wsl2-recommended-on-windows).

## Why SSH rather than HTTPS

The repository is **private** (D-046), so every clone, fetch and push is
authenticated. GitHub removed password authentication for Git in 2021, which
leaves two options: a personal access token over HTTPS, or an SSH key.

A key is the better default. It does not normally expire on its own — unlike a
token with a lifetime — and it can be revoked at any moment by deleting it from
**GitHub → Settings → SSH and GPG keys**, which cuts off that machine and nothing
else. It is also not a secret you paste into a prompt, and once the agent holds
it you stop thinking about it.

## 1. Create a key

Inside WSL:

```bash
ssh-keygen -t ed25519 -C "your-github-email@example.com"
```

Accept the default location (`~/.ssh/id_ed25519`) and **set a passphrase**. You
will not be typing it all day: once the key is loaded into the agent, the
passphrase is entered once and every Git operation in that session uses the key
without asking again.

Ed25519 rather than RSA: shorter, faster, and the current default recommendation.
An existing key is fine; you do not need a new one per project.

While you are there, make sure the directory itself is private — SSH refuses to
use keys that other accounts on the machine can read:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
```

## 2. Start the agent, and keep it started

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

That lasts until the shell closes. To have it on every shell, add this to
`~/.bashrc` (or `~/.zshrc`):

```bash
# Reuse one agent across shells rather than starting a new one each time.
if [ -z "$SSH_AUTH_SOCK" ] || ! ssh-add -l >/dev/null 2>&1; then
  eval "$(ssh-agent -s)" >/dev/null
  ssh-add -q ~/.ssh/id_ed25519 2>/dev/null
fi
```

WSL does not run a login session manager the way a desktop Linux does, so
nothing starts the agent for you.

## 3. Give GitHub the public key

Print it — **the one ending `.pub`**, which is the half that is safe to share:

```bash
cat ~/.ssh/id_ed25519.pub
```

Paste it into **GitHub → Settings → SSH and GPG keys → New SSH key**. Name it
after the machine, so it is obvious which one to revoke later.

**Never share, commit or paste `~/.ssh/id_ed25519`** — the file without `.pub`
is the private key. `.gitignore` refuses `*.pem` and `*.key`, and CI fails if
either is ever tracked, but the surest protection is that keys live in `~/.ssh`
and never inside the repository.

## 4. Test it

```bash
ssh -T git@github.com
```

Expected:

```
Hi <your-username>! You've successfully authenticated, but GitHub does not
provide shell access.
```

That message *is* success — GitHub offers no shell, so it says so.

## 5. If that hangs: SSH over port 443

Some networks block or drop outbound **port 22**, which is what SSH normally
uses. Corporate networks, guest and hotel Wi-Fi, some mobile tethering and some
ISPs all do it. The symptom is unmistakable:

```
ssh: connect to host github.com port 22: Connection timed out
```

It hangs rather than refusing, because the packets go nowhere.

**GitHub runs the same SSH service on port 443**, the HTTPS port, which is open
essentially everywhere. Point SSH at it in `~/.ssh/config`:

```ssh-config
Host github.com
    HostName ssh.github.com
    User git
    Port 443
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

`IdentitiesOnly yes` makes SSH offer **only** the key named above. Without it the
agent offers every key it holds, in whatever order, and GitHub can reject the
connection after too many wrong ones — which looks like a permissions problem
rather than what it is.

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
ssh -T git@github.com
```

The same success message should appear, usually immediately.

**This is a documented GitHub feature, not a workaround to be ashamed of.**
Nothing else changes: remote URLs stay `git@github.com:...`, because the `Host`
alias rewrites the hostname and port underneath.

To test the route before committing to the config:

```bash
ssh -T -p 443 git@ssh.github.com
```

## 6. Point the remote at SSH

```bash
git remote -v                                    # what it uses today
git remote set-url origin git@github.com:narainsagar/mindarchive.git
git remote -v                                    # confirm
```

A fresh clone:

```bash
cd ~                                             # not /mnt/c
git clone git@github.com:narainsagar/mindarchive.git
cd mindarchive
```

**Check the remote against `project.json`** before pushing for the first time.
Its `github` block holds the owner and the repository name —
`{"username": "…", "repository": "…"}` — and a mismatch means the clone commands
throughout the documentation point somewhere that does not exist. That has
happened here once already.

## 7. Set your identity for this repository only

```bash
git config user.name  "Your Name"
git config user.email "you@example.com"
```

**Per repository, not `--global`** (D-015), so an identity chosen for one project
does not follow you into every other one. `scripts/set_identity.py --git` sets
these from the `author` block in `project.json`.

Confirm before your first commit:

```bash
git config user.name && git config user.email
```

Commit authorship is permanent and public in any repository that ever becomes
public. Decide it deliberately rather than discovering it later.

## Everyday use

```bash
git status                    # start here, always
git diff                      # what changed
git add -u                    # stage tracked changes only
git diff --cached             # read what you are about to commit
git commit
git pull --rebase             # a linear history beats a merge bubble
git push
```

**`git add -u` rather than `git add -A`.** The second sweeps up untracked files,
including whatever you happen to be drafting; it has twice pulled unrelated work
into a commit in this repository. Stage by path when you mean specific files.

Before committing, confirm there is no `.env`, no secret, no database file and no
personal archive in the diff. Commit message conventions are in
[Development]({{ '/development/' | relative_url }}#git).

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `connect to host github.com port 22: Connection timed out` | Port 22 blocked. Use the 443 config above. |
| `git@github.com: Permission denied (publickey)` | The agent has no key. `ssh-add -l` to list; `ssh-add ~/.ssh/id_ed25519` to load. |
| Passphrase asked for on every command | No agent, or a new agent per shell. Add the `~/.bashrc` block above. |
| Works in one terminal, fails in another | Two environments. Windows Git and WSL Git have separate keys — do Git work inside WSL. |
| `Host key verification failed` | First connection, or GitHub rotated a host key. Check the published fingerprints, then retry. |
| `Bad owner or permissions on ~/.ssh/config` | `chmod 600 ~/.ssh/config`. SSH refuses configs others can read. |
| Push rejected, `non-fast-forward` | Someone pushed first. `git pull --rebase`, resolve, push again. |
| VS Code cannot see your key | Confirm the window is attached to WSL, bottom-left. A Windows window uses Windows SSH. |

## What this page deliberately does not contain

No hostnames, addresses, network names or key material — nothing specific to one
machine or one network. The port-443 route is described because it is a general
solution to a common condition, not because of anything particular to this
project's developers.

The private material in this repository — project memory, session records,
prompts, agent rules — is listed in D-046 and never reaches a published page.
