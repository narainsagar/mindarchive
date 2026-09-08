#!/usr/bin/env python3
"""Development commands for Mind Archive.

One entry point for running the stack and running checks.

**Nothing here runs automatically.** There is no pre-commit hook, no watcher,
and no check wired into saving a file. You decide when to verify, which is the
point — see docs/project-memory/DECISIONS.md D-018.

Running the stack::

    python scripts/dev.py up               # start it
    python scripts/dev.py up --build       # rebuild images first
    python scripts/dev.py status           # what is running
    python scripts/dev.py logs api -f      # follow the backend log
    python scripts/dev.py stop             # pause, keep containers
    python scripts/dev.py down             # stop and remove containers
    python scripts/dev.py down --volumes   # ... and delete Docker volumes
    python scripts/dev.py clean            # remove this project's images too
    python scripts/dev.py clean --all      # ... and prune dangling build cache

Checking your work, when you want to::

    python scripts/dev.py test             # both test suites
    python scripts/dev.py test backend     # just one
    python scripts/dev.py lint
    python scripts/dev.py types
    python scripts/dev.py format --fix
    python scripts/dev.py build            # checks the build compiles;
                                           # does NOT start anything
    python scripts/dev.py verify           # everything, then tidy up

`verify` is the milestone gate: run it before finishing a milestone, before
opening a pull request, and before releasing. CI runs the same checks.

Every check runs in a throwaway container (`--rm`), so nothing is left behind.

Standard library only.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Checks run in one-shot containers. --no-deps so checking the frontend does
# not drag the backend up with it.
RUN = ["docker", "compose", "run", "--rm", "--no-deps"]

def _supports_colour() -> bool:
    """Only colour real terminals.

    Piping into a file, or an older Windows console, otherwise fills the output
    with escape sequences that make it harder to read, not easier.
    """
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        # Windows Terminal and VS Code set this; the legacy console does not.
        return bool(os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM"))
    return True


if _supports_colour():
    GREEN, RED, YELLOW, DIM, RESET = (
        "\033[32m",
        "\033[31m",
        "\033[33m",
        "\033[2m",
        "\033[0m",
    )
else:
    GREEN = RED = YELLOW = DIM = RESET = ""


def say(message: str, colour: str = "") -> None:
    print(f"{colour}{message}{RESET}" if colour else message)


def run(command: list, capture: bool = False) -> int:
    """Run a command in the repository root and return its exit code."""
    say(f"$ {' '.join(command)}", DIM)
    try:
        result = subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            stdout=subprocess.DEVNULL if capture else None,
            stderr=subprocess.DEVNULL if capture else None,
        )
    except FileNotFoundError:
        say(f"Could not find '{command[0]}'. Is it installed and on your PATH?", RED)
        return 127
    return result.returncode


def require_docker() -> None:
    if shutil.which("docker") is None:
        say("Docker is not installed, or not on your PATH.", RED)
        say("Mind Archive's supported development path needs Docker.", DIM)
        say("See docs/DEVELOPMENT.md for the native alternative.", DIM)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Running the stack
# ---------------------------------------------------------------------------


def cmd_up(args) -> int:
    require_docker()
    command = ["docker", "compose", "up", "-d"]
    if args.build:
        command.append("--build")
    code = run(command)
    if code == 0:
        say("\nMind Archive is running.", GREEN)
        say("  Interface  http://localhost:5173")
        say("  API        http://localhost:8000")
        say("  API docs   http://localhost:8000/docs")
        say("\nStop it with: python scripts/dev.py down", DIM)
    return code


def cmd_down(args) -> int:
    require_docker()
    command = ["docker", "compose", "down"]
    if args.volumes:
        command.append("--volumes")
        say("Removing Docker volumes. Your ./data folder is a bind mount and", YELLOW)
        say("is NOT affected — your archive is safe.", YELLOW)
    code = run(command)
    if code == 0:
        say("Stopped.", GREEN)
    return code


def cmd_stop(args) -> int:
    require_docker()
    code = run(["docker", "compose", "stop"])
    if code == 0:
        say("Paused. Start again with: python scripts/dev.py up", GREEN)
    return code


def cmd_restart(args) -> int:
    require_docker()
    return run(["docker", "compose", "restart"])


def cmd_status(args) -> int:
    require_docker()
    return run(
        [
            "docker",
            "compose",
            "ps",
            "--format",
            "table {{.Service}}\t{{.State}}\t{{.Status}}",
        ]
    )


def cmd_logs(args) -> int:
    require_docker()
    command = ["docker", "compose", "logs"]
    if args.follow:
        command.append("-f")
    if args.service:
        command.append(args.service)
    return run(command)


def cmd_clean(args) -> int:
    """Remove this project's containers, networks and images."""
    require_docker()

    say("Removing Mind Archive containers, networks and images.", YELLOW)
    say("Your archive in ./data is a bind mount and is not touched.", DIM)

    # --rmi local removes the images this project built, not pulled base images.
    code = run(["docker", "compose", "down", "--volumes", "--rmi", "local"])

    if args.all:
        say("\nPruning dangling images and build cache.", YELLOW)
        run(["docker", "image", "prune", "-f"])
        run(["docker", "builder", "prune", "-f"])

    if code == 0:
        say("\nCleaned. Next 'up --build' will rebuild from scratch.", GREEN)
    return code


# ---------------------------------------------------------------------------
# Checks — run them when you decide to
# ---------------------------------------------------------------------------


def backend(*command: str) -> list:
    return RUN + ["api"] + list(command)


def frontend(*command: str) -> list:
    return RUN + ["web"] + list(command)


def cmd_test(args) -> int:
    require_docker()
    target = args.target or "all"
    failures = []

    if target in ("backend", "all"):
        say("\n── Backend tests ──", DIM)
        if run(backend("pytest")) != 0:
            failures.append("backend tests")

    if target in ("frontend", "all"):
        say("\n── Frontend tests ──", DIM)
        if run(frontend("npm", "test")) != 0:
            failures.append("frontend tests")

    return report(failures)


def cmd_lint(args) -> int:
    require_docker()
    failures = []

    say("\n── Backend lint ──", DIM)
    if run(backend("ruff", "check", ".")) != 0:
        failures.append("backend lint")

    say("\n── Frontend lint ──", DIM)
    if run(frontend("npm", "run", "lint")) != 0:
        failures.append("frontend lint")

    return report(failures)


def cmd_types(args) -> int:
    require_docker()
    failures = []

    say("\n── Backend types ──", DIM)
    if run(backend("mypy", "src")) != 0:
        failures.append("backend types")

    say("\n── Frontend types ──", DIM)
    if run(frontend("npm", "run", "typecheck")) != 0:
        failures.append("frontend types")

    return report(failures)


def cmd_format(args) -> int:
    require_docker()

    if args.fix:
        say("\n── Formatting backend ──", DIM)
        run(backend("ruff", "check", "--fix", "."))
        return run(backend("ruff", "format", "."))

    say("\n── Backend formatting ──", DIM)
    return report([] if run(backend("ruff", "format", "--check", ".")) == 0 else ["formatting"])


def cmd_build(args) -> int:
    require_docker()
    say("\n── Frontend production build ──", DIM)
    return report([] if run(frontend("npm", "run", "build")) == 0 else ["frontend build"])


def cmd_verify(args) -> int:
    """Everything. The milestone gate.

    Run this before finishing a milestone, opening a pull request, or
    releasing — not after every edit.
    """
    require_docker()
    failures = []

    steps = [
        ("Backend lint", backend("ruff", "check", ".")),
        ("Backend formatting", backend("ruff", "format", "--check", ".")),
        ("Backend types", backend("mypy", "src")),
        ("Backend tests", backend("pytest")),
        ("Frontend lint", frontend("npm", "run", "lint")),
        ("Frontend types", frontend("npm", "run", "typecheck")),
        ("Frontend tests", frontend("npm", "test")),
        ("Frontend build", frontend("npm", "run", "build")),
        ("Project memory", [sys.executable, "scripts/session.py", "check"]),
    ]

    for name, command in steps:
        say(f"\n── {name} ──", DIM)
        if run(command) != 0:
            failures.append(name)

    if not args.keep_up:
        say("\n── Tidying up ──", DIM)
        run(["docker", "compose", "down"], capture=True)

    return report(failures, gate=True)


def report(failures: list, gate: bool = False) -> int:
    print()
    if failures:
        say(f"FAILED: {', '.join(failures)}", RED)
        if gate:
            say("Fix these before finishing the milestone.", DIM)
        return 1

    say("All checks passed." if gate else "Passed.", GREEN)
    return 0


# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Development commands for Mind Archive.",
        epilog=(
            "To start Mind Archive:  dev.py up --build\n"
            "'build' on its own is a check, not a way to start anything.\n\n"
            "Nothing runs automatically. You decide when to check your work."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    up = sub.add_parser("up", help="START Mind Archive")
    up.add_argument(
        "--build", action="store_true", help="rebuild the Docker images first"
    )
    up.set_defaults(func=cmd_up)

    down = sub.add_parser("down", help="stop and remove containers")
    down.add_argument(
        "--volumes", action="store_true", help="also delete Docker volumes"
    )
    down.set_defaults(func=cmd_down)

    sub.add_parser("stop", help="pause without removing").set_defaults(func=cmd_stop)
    sub.add_parser("restart", help="restart the stack").set_defaults(func=cmd_restart)
    sub.add_parser("status", help="what is running").set_defaults(func=cmd_status)

    logs = sub.add_parser("logs", help="show logs")
    logs.add_argument("service", nargs="?", help="api or web; both if omitted")
    logs.add_argument("-f", "--follow", action="store_true")
    logs.set_defaults(func=cmd_logs)

    clean = sub.add_parser("clean", help="remove containers, volumes and images")
    clean.add_argument(
        "--all", action="store_true", help="also prune dangling images and build cache"
    )
    clean.set_defaults(func=cmd_clean)

    test = sub.add_parser("test", help="run tests")
    test.add_argument("target", nargs="?", choices=["backend", "frontend", "all"])
    test.set_defaults(func=cmd_test)

    sub.add_parser("lint", help="run linters").set_defaults(func=cmd_lint)
    sub.add_parser("types", help="run type checkers").set_defaults(func=cmd_types)

    fmt = sub.add_parser("format", help="check formatting")
    fmt.add_argument("--fix", action="store_true", help="rewrite files in place")
    fmt.set_defaults(func=cmd_format)

    # Named for what it checks, not what it starts. "up --build" is the one
    # that starts Mind Archive; this only asks whether the frontend still
    # compiles for production.
    sub.add_parser(
        "build", help="CHECK the frontend production build compiles"
    ).set_defaults(func=cmd_build)

    verify = sub.add_parser("verify", help="every check — the milestone gate")
    verify.add_argument(
        "--keep-up", action="store_true", help="leave the stack running afterwards"
    )
    verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
