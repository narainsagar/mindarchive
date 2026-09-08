#!/usr/bin/env python3
"""Session memory for Mind Archive.

Every working session is recorded in the repository so the project's memory
never depends on an AI chat history that will be lost.

    python scripts/session.py start "add the chatgpt importer"
    python scripts/session.py end
    python scripts/session.py check
    python scripts/session.py list

See docs/project-memory/SESSION_PROTOCOL.md.

Standard library only, so it runs anywhere without installing anything.
"""

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = REPO_ROOT / "docs" / "project-memory"
SESSIONS_DIR = MEMORY_DIR / "sessions"
TEMPLATE_DIR = SESSIONS_DIR / "TEMPLATE"
SESSION_LOG = MEMORY_DIR / "SESSION_LOG.md"
CURRENT_MARKER = SESSIONS_DIR / ".current"

REQUIRED_MEMORY_FILES = [
    "MEMORY_INDEX.md",
    "PROJECT_STATE.md",
    "MILESTONES.md",
    "DECISIONS.md",
    "RESEARCH.md",
    "DISCUSSION_SUMMARY.md",
    "AI_AGENT_PROTOCOL.md",
    "SESSION_PROTOCOL.md",
    "SESSION_LOG.md",
]

REQUIRED_SESSION_FILES = ["SESSION.md", "PROMPTS.md"]

# Patterns that should never appear in project memory. Kept deliberately
# narrow: a noisy check is a check people learn to ignore.
SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style API key"),
    (r"sk-ant-[A-Za-z0-9\-_]{20,}", "Anthropic API key"),
    (r"ghp_[A-Za-z0-9]{30,}", "GitHub personal access token"),
    (r"AIza[A-Za-z0-9\-_]{30,}", "Google API key"),
    (r"AKIA[A-Z0-9]{16}", "AWS access key id"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
]


def slugify(text, limit=50):
    """Make a short, readable folder name.

    Truncates at a word boundary — a name cut mid-word reads as a typo in a
    directory listing.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(slug) <= limit:
        return slug or "session"
    trimmed = slug[:limit].rsplit("-", 1)[0]
    return trimmed or slug[:limit]


def today():
    return dt.date.today().isoformat()


def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def next_session_dir(description):
    """Pick the next YYYY-MM-DD-NN-slug folder name for today."""
    date = today()
    existing = sorted(p.name for p in SESSIONS_DIR.glob(date + "-*") if p.is_dir())
    counter = 1
    for name in existing:
        match = re.match(re.escape(date) + r"-(\d{2})-", name)
        if match:
            counter = max(counter, int(match.group(1)) + 1)
    return SESSIONS_DIR / "{}-{:02d}-{}".format(date, counter, slugify(description))


def cmd_start(args):
    description = " ".join(args.description).strip()
    if not description:
        print("error: give a short description of the work", file=sys.stderr)
        return 1

    if CURRENT_MARKER.exists():
        open_session = CURRENT_MARKER.read_text(encoding="utf-8").strip()
        print("A session is already open: {}".format(open_session))
        print("Close it with 'python scripts/session.py end' first.")
        return 1

    session_dir = next_session_dir(description)
    session_dir.mkdir(parents=True, exist_ok=True)

    for name in ["SESSION.md", "PROMPTS.md", "REPORT.md"]:
        template = TEMPLATE_DIR / name
        content = template.read_text(encoding="utf-8") if template.exists() else ""
        content = (
            content.replace("{{DESCRIPTION}}", description)
            .replace("{{DATE}}", today())
            .replace("{{STARTED}}", now())
            .replace("{{SESSION_ID}}", session_dir.name)
        )
        (session_dir / name).write_text(content, encoding="utf-8")

    CURRENT_MARKER.write_text(session_dir.name + "\n", encoding="utf-8")

    rel = session_dir.relative_to(REPO_ROOT).as_posix()
    print("Session started: {}".format(session_dir.name))
    print("  {}/SESSION.md   what happens, and what remains".format(rel))
    print("  {}/PROMPTS.md   paste each instruction as it arrives".format(rel))
    print("  {}/REPORT.md    any report this session produces".format(rel))
    print("")
    print("Before changing anything, read:")
    print("  AGENTS.md, PROJECT_STATE.md, MILESTONES.md, DECISIONS.md")
    print("  and the previous session's SESSION.md")
    return 0


def cmd_end(args):
    if not CURRENT_MARKER.exists():
        print("No session is currently open.", file=sys.stderr)
        print("Start one with: python scripts/session.py start \"...\"", file=sys.stderr)
        return 1

    session_name = CURRENT_MARKER.read_text(encoding="utf-8").strip()
    session_dir = SESSIONS_DIR / session_name
    session_file = session_dir / "SESSION.md"

    if session_file.exists():
        text = session_file.read_text(encoding="utf-8")
        if "{{ENDED}}" in text:
            text = text.replace("{{ENDED}}", now())
        elif "**Ended:**" not in text:
            text += "\n**Ended:** {}\n".format(now())
        session_file.write_text(text, encoding="utf-8")

    CURRENT_MARKER.unlink()

    print("Session closed: {}".format(session_name))
    print("")
    print("Before you commit, confirm:")
    print("  [ ] SESSION.md records what was done, including checks that failed")
    print("  [ ] PROMPTS.md is complete")
    print("  [ ] REPORT.md holds any report produced")
    print("  [ ] PROJECT_STATE.md reflects what now exists")
    print("  [ ] MILESTONES.md and docs/ROADMAP.md updated if progress changed")
    print("  [ ] SESSION_LOG.md has an entry linking this session")
    print("  [ ] python scripts/session.py check passes")
    return 0


def cmd_list(args):
    sessions = sorted(
        p for p in SESSIONS_DIR.glob("*") if p.is_dir() and p.name != "TEMPLATE"
    )
    if not sessions:
        print("No sessions recorded yet.")
        return 0
    current = (
        CURRENT_MARKER.read_text(encoding="utf-8").strip()
        if CURRENT_MARKER.exists()
        else None
    )
    for session in sessions:
        marker = "  <- open" if session.name == current else ""
        print("{}{}".format(session.name, marker))
    return 0


def cmd_check(args):
    problems = []
    warnings = []

    # 1. The required memory files must exist and not be empty.
    for name in REQUIRED_MEMORY_FILES:
        path = MEMORY_DIR / name
        if not path.exists():
            problems.append("missing: docs/project-memory/{}".format(name))
        elif path.stat().st_size == 0:
            problems.append("empty: docs/project-memory/{}".format(name))

    # 2. Every session folder must carry its records.
    sessions = sorted(
        p for p in SESSIONS_DIR.glob("*") if p.is_dir() and p.name != "TEMPLATE"
    )
    for session in sessions:
        for name in REQUIRED_SESSION_FILES:
            path = session / name
            if not path.exists():
                problems.append("missing: {}/{}".format(session.name, name))
            elif path.stat().st_size == 0:
                problems.append("empty: {}/{}".format(session.name, name))

    # 3. Every session must be referenced from the log.
    if SESSION_LOG.exists():
        log_text = SESSION_LOG.read_text(encoding="utf-8")
        for session in sessions:
            if session.name not in log_text:
                problems.append(
                    "{} is not referenced in SESSION_LOG.md".format(session.name)
                )

    # 4. Nothing resembling a secret may live in project memory.
    for path in MEMORY_DIR.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, text):
                problems.append(
                    "possible {} in {}".format(
                        label, path.relative_to(REPO_ROOT).as_posix()
                    )
                )

    # 5. An unclosed session is worth flagging, but is not a failure.
    if CURRENT_MARKER.exists():
        warnings.append(
            "session {} is still open".format(
                CURRENT_MARKER.read_text(encoding="utf-8").strip()
            )
        )
    for session in sessions:
        session_file = session / "SESSION.md"
        if session_file.exists():
            text = session_file.read_text(encoding="utf-8")
            if "{{" in text:
                warnings.append(
                    "{}/SESSION.md still has unfilled placeholders".format(session.name)
                )

    for warning in warnings:
        print("warning: {}".format(warning))

    if problems:
        print("")
        for problem in problems:
            print("FAIL: {}".format(problem))
        print("")
        print("{} problem(s) found in project memory.".format(len(problems)))
        return 1

    print(
        "Project memory is consistent. {} session(s) recorded.".format(len(sessions))
    )
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Record Mind Archive working sessions in the repository."
    )
    sub = parser.add_subparsers(dest="command")

    start = sub.add_parser("start", help="begin a session")
    start.add_argument("description", nargs="+", help="short description of the work")
    start.set_defaults(func=cmd_start)

    end = sub.add_parser("end", help="close the open session")
    end.set_defaults(func=cmd_end)

    check = sub.add_parser("check", help="validate project memory")
    check.set_defaults(func=cmd_check)

    listing = sub.add_parser("list", help="list recorded sessions")
    listing.set_defaults(func=cmd_list)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
