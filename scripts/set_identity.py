#!/usr/bin/env python3
"""Apply the project identity from project.json across the repository.

Edit project.json, then run:

    python scripts/set_identity.py            # apply
    python scripts/set_identity.py --check    # report without changing anything
    python scripts/set_identity.py --git      # also set the local git identity

This replaces the YOUR-USERNAME placeholders in LICENSE, README.md,
CHANGELOG.md, the docs, the GitHub workflows and apps/web/package.json, so the
values live in exactly one place rather than being copied by hand.

Standard library only, so it runs anywhere without installing anything.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "project.json"

# Files that may contain identity placeholders. Missing files are skipped, so
# this list can name files that do not exist yet.
TARGETS = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "AGENTS.md",
    "docs/DEVELOPMENT.md",
    "docs/GITHUB_PAGES.md",
    "docs/BACKLOG.md",
    "docs/index.html",
    "docs/_config.yml",
    "apps/web/package.json",
    "apps/api/pyproject.toml",
    ".github/workflows/ci.yml",
    ".github/workflows/docs-pages.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    "project-memory/PROJECT_STATE.md",
]

PLACEHOLDER_USERNAME = "YOUR-USERNAME"


def load_config():
    if not CONFIG_PATH.exists():
        print("error: project.json not found at {}".format(CONFIG_PATH), file=sys.stderr)
        sys.exit(1)
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_replacements(config):
    github = config.get("github", {})
    copyright_ = config.get("copyright", {})

    username = github.get("username", PLACEHOLDER_USERNAME)
    repository = github.get("repository", "mindarchive")
    year = str(copyright_.get("year", "2026"))
    holder = copyright_.get("holder", "Mind Archive contributors")

    replacements = [
        # Full repository URLs first, so the shorter username rule cannot
        # partially rewrite them.
        (
            r"github\.com/" + re.escape(PLACEHOLDER_USERNAME) + r"/mindarchive",
            "github.com/{}/{}".format(username, repository),
        ),
        (
            re.escape(PLACEHOLDER_USERNAME) + r"\.github\.io/mindarchive",
            "{}.github.io/{}".format(username, repository),
        ),
        (re.escape(PLACEHOLDER_USERNAME), username),
        (
            r"Copyright \(c\) \d{4} .+",
            "Copyright (c) {} {}".format(year, holder),
        ),
    ]
    return replacements, username, holder


def apply_to_file(path, replacements, check_only):
    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0

    updated = original
    for pattern, value in replacements:
        updated = re.sub(pattern, value, updated)

    if updated == original:
        return 0

    changes = sum(
        1 for a, b in zip(original.splitlines(), updated.splitlines()) if a != b
    )
    if not check_only:
        path.write_text(updated, encoding="utf-8")
    return max(changes, 1)


def set_git_identity(config):
    author = config.get("author", {})
    name = author.get("name", "").strip()
    email = author.get("email", "").strip()

    if not name or not email:
        print(
            "skipped git identity: set author.name and author.email in project.json"
        )
        return

    for key, value in (("user.name", name), ("user.email", email)):
        subprocess.run(
            ["git", "config", "--local", key, value], cwd=str(REPO_ROOT), check=True
        )
    print("git identity set locally: {} <{}>".format(name, email))


def main():
    parser = argparse.ArgumentParser(
        description="Apply project.json identity across the repository."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report what would change without writing anything",
    )
    parser.add_argument(
        "--git",
        action="store_true",
        help="also set the local git user.name and user.email",
    )
    args = parser.parse_args()

    config = load_config()
    replacements, username, holder = build_replacements(config)

    if username == PLACEHOLDER_USERNAME:
        print("warning: github.username in project.json is still a placeholder.")
        print("         Edit project.json, then run this again.")
        print("")

    total_files = 0
    total_lines = 0
    for relative in TARGETS:
        path = REPO_ROOT / relative
        if not path.exists():
            continue
        changed = apply_to_file(path, replacements, args.check)
        if changed:
            total_files += 1
            total_lines += changed
            verb = "would update" if args.check else "updated"
            print("{} {} ({} line(s))".format(verb, relative, changed))

    if total_files == 0:
        print("Nothing to change. Identity is already applied.")
    else:
        verb = "would change" if args.check else "changed"
        print("")
        print("{} {} line(s) across {} file(s).".format(verb, total_lines, total_files))
        print("Copyright holder: {}".format(holder))
        print("GitHub: {}/{}".format(username, config["github"]["repository"]))

    if args.git and not args.check:
        set_git_identity(config)

    return 0


if __name__ == "__main__":
    sys.exit(main())
