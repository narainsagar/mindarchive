#!/usr/bin/env python3
"""Generate a public-safe tree from this private repository.

This repository is private and is the source of truth. A separate public
repository will eventually exist, with its own clean history (D-046). This
script produces the tree that goes into it.

    python3 scripts/publish_public.py --list             what would be published
    python3 scripts/publish_public.py --check            screen it, and say what is wrong
    python3 scripts/publish_public.py --build DIR        write the tree to DIR

**It copies an allowlist. It never copies everything and then deletes.** The
difference decides whether the mechanism fails open or closed: a denylist
publishes every file nobody has thought about yet, and the file nobody has
thought about is exactly the one that leaks. Two thirds of this repository is
private, so the default has to be "not published".

## What this script will not do

It does not run `git` at all — no `init`, no `commit`, no `remote`, no `push` —
and it does not create, rename or configure any GitHub repository. It writes
files to a directory you name and stops. Publishing is a deliberate human act
(D-046), and a tool that could perform it by accident is the wrong tool.

It never writes inside this repository, and never modifies the working tree.

## The allowlist model

**Files** are listed individually. **Directories** in `PUBLIC_TREES` are
published recursively, and a new file inside one is published automatically.

That is deliberate, and it is the practical half of the trade-off: `apps/api/src`
gains files constantly, and an allowlist that named every module would be out of
date within a day — a stale allowlist that everyone has learned to bypass is
worse than a recursive one. The safety does not come from enumerating files; it
comes from every file, new or old, having to pass `screen()` before it is copied,
and from `--check` printing the complete resolved list so that additions are
visible to a reviewer.

Anything not under an allowlisted path is never read, never screened and never
copied. It cannot leak by being forgotten, only by being added here on purpose.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# The allowlist
# ---------------------------------------------------------------------------

#: Individual files that may be published.
#:
#: Each one was read before being listed here. Anything carrying internal
#: process, commercial strategy or a pointer to private material is in
#: `WITHHELD` below, with the reason.
PUBLIC_FILES = (
    # The product's own front matter.
    "README.md",
    "LICENSE",
    "LICENSING.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    "project.json",
    # Running it.
    "docker-compose.yml",
    ".env.example",
    ".gitignore",
    ".gitattributes",
    # Documentation that describes the product rather than how it is made.
    "docs/PRODUCT.md",
    "docs/ARCHITECTURE.md",
    "docs/DEVELOPMENT.md",
    "docs/DEPLOYMENT.md",
    "docs/SECURITY.md",
    "docs/ROADMAP.md",
    "docs/TRY_IT.md",
    "docs/FASTER_IMPORT.md",
    "docs/GITHUB_PAGES.md",
    "docs/development/GIT_SSH_SETUP.md",
    # The site itself.
    "docs/_config.yml",
    # Named individually rather than publishing `docs/_data/` whole:
    # `private_pages.yml` lives beside it and must never be copied — its
    # absence is what removes the private links from the public site.
    "docs/_data/support.yml",
    "docs/index.html",
    "docs/documentation.html",
    "docs/blog.html",
    "docs/feed.xml",
    "docs/404.html",
    "docs/support.md",
    "docs/contribute.md",
    "docs/coming-next.md",
    "docs/_drafts/TEMPLATE.md",
    # Development tooling that is safe to hand to anyone.
    "scripts/dev.py",
    "scripts/check_site_links.py",
    "scripts/check_css_bands.py",
    "scripts/inspect_export.py",
    "scripts/make_fixture_export.py",
    "scripts/set_identity.py",
    "scripts/browser/chatgpt-export.js",
    # Publishable since the page list was split: the public half lives in the
    # script, the private half in project-memory/site_pages.json, which is not
    # copied. The published script therefore names no private document and
    # generates exactly the five pages whose sources are published (D-048).
    "scripts/sync_site_pages.py",
    # Explains why a real export must never be committed. Worth publishing.
    "local/README.md",
    # Repository furniture.
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
    ".github/workflows/docs-pages.yml",
)

#: Directories published in full, recursively. See "The allowlist model" above.
PUBLIC_TREES = (
    "apps/api/src",
    "apps/api/tests",
    "apps/web/src",
    "docs/_layouts",
    "docs/_posts",
    "docs/assets",
    ".github/ISSUE_TEMPLATE",
)

#: Files inside an allowlisted directory that are still not published.
#:
#: Kept short on purpose. A growing list here is a sign the directory should not
#: have been allowlisted whole.
TREE_EXCEPTIONS = (
    # Build output, never source.
    "apps/web/src/vite-env.d.ts.bak",
)

#: Loose files at the top of `apps/api` and `apps/web` that the trees miss.
PUBLIC_FILES += (
    "apps/api/pyproject.toml",
    "apps/api/Dockerfile",
    "apps/api/README.md",
    "apps/web/package.json",
    "apps/web/Dockerfile",
    "apps/web/index.html",
    "apps/web/vite.config.ts",
    "apps/web/tsconfig.json",
    "apps/web/eslint.config.js",
)

#: Deliberately withheld, with the reason. Nothing here is published, and the
#: list is documentation rather than logic — the allowlist above is what the
#: script acts on. Recording *why* stops each of these being re-argued.
WITHHELD = {
    "project-memory/": "The internal record: decisions, state, research, 26 session folders, verbatim prompts.",
    "prompts/": "The founding specification and agent prompts — the private development process itself.",
    ".claude/": "Internal agent rules.",
    "CLAUDE.md": "Agent entry point; imports AGENTS.md and points at project memory.",
    "GEMINI.md": "As above.",
    "QWEN.md": "As above.",
    "AGENTS.md": "Instructions for working inside the private repository: read order, session protocol, the public/private boundary itself. Reveals the development process rather than the product.",
    "AUDIT-REPORT.md": "An internal punch list naming every current weakness. Published, it is a to-do list for someone else.",
    "docs/DECISIONS.md": "A pointer to the private decision log; it would dangle.",
    "docs/BACKLOG.md": "Withdrawn commercial pricing, merchant-of-record research, and an 'explicitly rejected' section of internal reasoning.",
    "scripts/session.py": "The private session-memory tool. Useless without project-memory/, and it documents the protocol.",
    "project-memory/site_pages.json": "The private half of the site's page list. Its absence is what stops the public build generating pages for documents it does not have.",
    "docs/_data/private_pages.yml": "Its absence is what removes links to private-only routes from the public site.",
    "data/": "The user's archive. Real conversations.",
    "tmp/": "Scratch, including real provider exports.",
    "local/": "Scratch for real exports. Only its README is published.",
}

# ---------------------------------------------------------------------------
# The gates every candidate file passes
# ---------------------------------------------------------------------------

#: Path segments that must never appear in a published path, whatever the
#: allowlist says. The second lock on the same door.
DENY_SEGMENTS = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        ".jekyll-cache",
        "_site",
        "reference",  # docs/reference/ is generated from canonical files
        "project-memory",
        "sessions",
        "prompts",
        ".claude",
        "data",
        "tmp",
    }
)

#: File names and suffixes that are never published, whatever else is true.
DENY_NAMES = frozenset({".env", "CLAUDE.md", "GEMINI.md", "QWEN.md", "AUDIT-REPORT.md"})
DENY_SUFFIXES = (
    ".env",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".zip",
    ".log",
)
#: `.env.example` is the one intended exception to the `.env` rule.
DENY_EXCEPTIONS = frozenset({".env.example"})

#: Content that stops a publish. Deliberately few and specific: a scanner that
#: cries wolf is a scanner people learn to pass with `--force`.
SECRET_PATTERNS = (
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "a private key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}"), "a GitHub token"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}"), "an API key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key id"),
    (re.compile(r"\bssh-(rsa|ed25519) AAAA[0-9A-Za-z+/]{20,}"), "an SSH public key"),
    (
        re.compile(r"\b(?:192\.168|10\.(?:\d{1,3})|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"),
        "a private IP address",
    ),
    (re.compile(r"/home/(?!%s)[a-z][a-z0-9_-]*/" % "|".join(
        # Placeholder users, which are the point of an example path. A real
        # account name is what this rule is looking for.
        ("someone/", "you/", "user/", "username/", "example/", "me/", "dev/")
    )), "an absolute home path"),
    (re.compile(r"[A-Za-z]:\\Users\\(?!You\\|User\\|Example\\)[^\\\s]+"), "an absolute Windows user path"),
)

#: Mentions of material that is not published. Not secrets — a comment citing
#: `project-memory/DECISIONS.md D-009` leaks nothing. But for a reader of the
#: public repository it points at something they cannot open, so `--check`
#: reports them and a human decides. They do not stop a build.
REFERENCE_PATTERNS = (
    re.compile(r"project-memory/"),
    re.compile(r"(?<![\w/])prompts/(?:MASTER|AI-CODING)"),
    re.compile(r"(?<![\w/])\.claude/"),
    re.compile(r"AUDIT-REPORT\.md"),
    re.compile(r"(?<![\w/])CLAUDE\.md"),
    re.compile(r"session\.py"),
)

#: Suffixes worth reading. Everything else is copied unread — images, fonts and
#: the like — which is why binary formats are not in the allowlist by accident.
TEXT_SUFFIXES = frozenset(
    {
        ".py", ".js", ".ts", ".tsx", ".json", ".md", ".html", ".css", ".yml",
        ".yaml", ".toml", ".txt", ".xml", ".sh", ".example", ".gitignore",
        ".gitattributes",
    }
)


class Refused(Exception):
    """A file cannot be published, and the run stops."""


def is_text(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in {
        ".gitignore",
        ".gitattributes",
        ".env.example",
    }


def deny_reason(relative: str, path: Path) -> str | None:
    """Why this path may never be published, or None."""
    parts = Path(relative).parts

    for segment in parts[:-1]:
        if segment in DENY_SEGMENTS:
            return "it is under %s/, which is never published" % segment

    name = path.name
    if name in DENY_EXCEPTIONS:
        return None
    if name in DENY_NAMES:
        return "%s is withheld deliberately" % name
    if name.startswith(".env"):
        return "it is a .env file"
    if any(name.endswith(suffix) for suffix in DENY_SUFFIXES):
        return "its type is never published (%s)" % path.suffix
    if path.is_symlink():
        return "it is a symlink, and a symlink can point anywhere"
    return None


def scan(relative: str, path: Path):
    """Read a text file and return (secret findings, reference findings)."""
    if not is_text(path):
        return [], []

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # Unreadable as text. Copied unread, like any binary asset.
        return [], []

    secrets, references = [], []
    for number, line in enumerate(text.splitlines(), start=1):
        for pattern, what in SECRET_PATTERNS:
            if pattern.search(line):
                secrets.append("%s:%d looks like %s" % (relative, number, what))
        for pattern in REFERENCE_PATTERNS:
            if pattern.search(line):
                references.append("%s:%d mentions %s" % (relative, number, pattern.pattern))
                break

    return secrets, references


def resolve():
    """Every file the allowlist selects, as (relative path, absolute path).

    Missing entries are an error rather than a shrug: an allowlist that quietly
    skips a file it names is an allowlist nobody can trust to be complete.
    """
    found, missing = {}, []

    for relative in PUBLIC_FILES:
        path = ROOT / relative
        if path.is_file():
            found[relative] = path
        else:
            missing.append(relative)

    for tree in PUBLIC_TREES:
        base = ROOT / tree
        if not base.is_dir():
            missing.append(tree + "/")
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative in TREE_EXCEPTIONS:
                continue
            if any(segment in DENY_SEGMENTS for segment in path.relative_to(ROOT).parts[:-1]):
                continue  # __pycache__ and friends, silently
            found[relative] = path

    return dict(sorted(found.items())), missing


def screen(selected):
    """Check every selected file. Returns (failures, references)."""
    failures, references = [], []

    for relative, path in selected.items():
        reason = deny_reason(relative, path)
        if reason:
            failures.append("%s: %s" % (relative, reason))
            continue

        secrets, mentions = scan(relative, path)
        failures.extend(secrets)
        references.extend(mentions)

    return failures, references


def report(selected, missing, failures, references, verbose: bool) -> int:
    print("Allowlist selects %d files." % len(selected))

    if verbose:
        for relative in selected:
            print("    %s" % relative)

    if missing:
        print("\nAllowlisted but not found (%d):" % len(missing))
        for relative in missing:
            print("    %s" % relative)

    if references:
        # Summarised unless asked for in full. Forty lines of "mentions
        # project-memory/" on every run teaches people to skip the output, and
        # the run where it matters is the one they skip.
        print(
            "\n%d references to material that is not published."
            % len(references)
        )
        print("Not secrets — but a public reader cannot follow them.")
        if verbose:
            for line in references:
                print("    %s" % line)
        else:
            print("Run with --verbose to list them.")

    if failures:
        print("\nREFUSED (%d):" % len(failures))
        for line in failures:
            print("    %s" % line)
        print("\nNothing was written. Fix these, or correct the allowlist.")
        return 1

    print("\nNo secret or denied path found in the selected files.")
    if missing:
        print("Resolve the missing entries before publishing.")
        return 1
    return 0


def build(selected, destination: Path, force: bool) -> int:
    """Write the public tree. Never touches this repository."""
    destination = destination.resolve()

    # Refusals print to stdout as well as stderr. A refusal that scrolls past
    # in a stream nobody is watching is a refusal nobody acts on.
    def refuse(message: str) -> int:
        print("\nREFUSED: %s" % message)
        print("REFUSED: %s" % message, file=sys.stderr)
        return 1

    if destination == ROOT or ROOT in destination.parents:
        return refuse(
            "that path is inside the private repository (%s).\n"
            "         Choose a destination outside it." % ROOT
        )

    if destination.exists():
        if (destination / ".git").exists():
            # A public repository's history is not this script's to destroy,
            # with or without --force.
            return refuse(
                "%s contains a .git directory.\n"
                "         Refusing to touch a repository." % destination
            )
        if not force:
            return refuse(
                "%s already exists.\n"
                "         Pass --force to replace its contents." % destination
            )
        shutil.rmtree(destination)

    for relative, source in selected.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    print("Wrote %d files to %s" % (len(selected), destination))
    print("\nNo git repository was created and nothing was pushed — that is")
    print("deliberate, and it is yours to do (D-046).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a public-safe tree from this private repository.",
        epilog=(
            "The allowlist is in this file. Read it before changing it, and\n"
            "read the file you are adding before adding it."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="screen the allowlist and report")
    mode.add_argument("--list", action="store_true", help="print what would be published")
    mode.add_argument("--build", metavar="DIR", help="write the public tree to DIR")
    parser.add_argument("--force", action="store_true", help="replace an existing destination")
    parser.add_argument("--verbose", action="store_true", help="list every selected file")
    args = parser.parse_args()

    selected, missing = resolve()
    failures, references = screen(selected)

    if args.list:
        for relative in selected:
            print(relative)
        return 0

    status = report(selected, missing, failures, references, args.verbose or False)

    if args.check:
        return status

    if status != 0:
        print("\nNot building while --check fails.", file=sys.stderr)
        return status

    return build(selected, Path(args.build), args.force)


if __name__ == "__main__":
    raise SystemExit(main())
