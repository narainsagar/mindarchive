#!/usr/bin/env python3
"""Publish the repository's canonical documents as pages on the Jekyll site.

Jekyll is rooted at `docs/` and cannot read above it. That is why `LICENSING.md`,
`CONTRIBUTING.md`, `AGENTS.md` and everything under `project-memory/` were linked
as `github.com/.../blob/main/...` URLs: there was no local page to point at. On
`localhost:4000` those links go nowhere useful, and until the repository is
public they go nowhere at all (D-043).

Symlinks are not an option — the Pages build runs Jekyll in safe mode and will
not follow one out of the source folder.

So the pages are generated. **The output is git-ignored**, written to
`docs/reference/`, and regenerated before every build. Nothing is duplicated in
the repository, so the copy cannot drift from the canonical file — which is
better than committing copies and adding a check that notices when they differ.

Run it:

    python scripts/sync_site_pages.py            # write the pages
    python scripts/sync_site_pages.py --list     # say what would be written

`dev.py verify` runs it, and so does the Pages workflow before Jekyll builds.

## Links inside the content

Kramdown does not rewrite `.md` links, so `[RESEARCH.md](RESEARCH.md)` inside a
published page points at a file that is not in the output. Every internal link
is rewritten to the site convention D-036 set:

    [RESEARCH.md](RESEARCH.md)  ->  [RESEARCH.md]({{ '/research/' | relative_url }})

`relative_url` is required rather than a bare `/research/` because this is a
project site served from `/mindarchive/`.

**A link to a document that is not published is an error, not a silent 404.**
Publishing a page whose own links dead-end just moves the problem one click
deeper, which is the thing this script exists to stop.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

#: Where generated pages land. Git-ignored; see `.gitignore`.
#:
#: Deliberately not `_generated` — Jekyll skips directories whose name starts
#: with an underscore, and the pages would never be published.
OUT = DOCS / "reference"

#: Pages generated from a canonical file: source, output name, title, permalink.
#:
#: `LICENSE`, `CODE_OF_CONDUCT.md` and `AI_AGENT_PROTOCOL.md` are here because
#: the documents above them link to those 22 times between them, not because
#: anybody asked for them directly.
PAGES = (
    ("LICENSING.md", "licensing.md", "Licensing", "/licensing/"),
    ("LICENSE", "license.md", "Licence", "/license/"),
    ("CONTRIBUTING.md", "contributing.md", "Contributing", "/contributing/"),
    ("CODE_OF_CONDUCT.md", "code-of-conduct.md", "Code of Conduct", "/code-of-conduct/"),
    ("AGENTS.md", "agents.md", "AGENTS.md", "/agents/"),
    (".env.example", "env-example.md", "Configuration reference", "/env-example/"),
    (
        "project-memory/DECISIONS.md",
        "decision-log.md",
        "Decision log",
        "/decisions/log/",
    ),
    ("project-memory/MILESTONES.md", "milestones.md", "Milestones", "/milestones/"),
    ("project-memory/RESEARCH.md", "research.md", "Research", "/research/"),
    (
        "project-memory/SESSION_PROTOCOL.md",
        "session-protocol.md",
        "Session protocol",
        "/session-protocol/",
    ),
    (
        "project-memory/AI_AGENT_PROTOCOL.md",
        "agent-protocol.md",
        "AI agent protocol",
        "/agent-protocol/",
    ),
)

#: Every document that has a page, by its path from the repository root.
#:
#: Both halves matter: the generated pages above, and the hand-written pages
#: already in `docs/`. A link from a generated page to `docs/SECURITY.md` has to
#: become `/security/` just as surely as one to `RESEARCH.md` becomes
#: `/research/`.
LINKS = {
    "docs/ARCHITECTURE.md": "/architecture/",
    "docs/BACKLOG.md": "/backlog/",
    "docs/DECISIONS.md": "/decisions/",
    "docs/DEPLOYMENT.md": "/deployment/",
    "docs/DEVELOPMENT.md": "/development/",
    "docs/FASTER_IMPORT.md": "/faster-import/",
    "docs/GITHUB_PAGES.md": "/github-pages/",
    "docs/PRODUCT.md": "/product/",
    "docs/ROADMAP.md": "/roadmap/",
    "docs/SECURITY.md": "/security/",
    "docs/TRY_IT.md": "/try-it/",
    "docs/coming-next.md": "/coming-next/",
    "docs/contribute.md": "/contribute/",
    "docs/support.md": "/support/",
}
for _source, _name, _title, _permalink in PAGES:
    LINKS[_source] = _permalink

#: `.env.example` is not Markdown. It is shown as one code block.
CODE_BLOCKS = {".env.example": "bash"}

#: A Markdown link whose target is not a URL and not a bare anchor.
_LINK = re.compile(r"\[([^\]]*)\]\((?!https?://|mailto:|#)([^)\s]+)\)")

#: Liquid that was already in the source document, as text about Liquid.
#:
#: Backticks do not protect it: Liquid runs over the whole file before Kramdown
#: sees any Markdown, so `` `{{ '/backlog/' | relative_url }}` `` in a document
#: *explaining the convention* renders as the evaluated URL instead of the
#: syntax it is trying to show. D-036's own entry does exactly this.
_LIQUID = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.DOTALL)

#: A `raw` block the author wrote themselves. Already protected; leave it be.
_RAW_BLOCK = re.compile(r"\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}", re.DOTALL)

#: A lone `raw` or `endraw` tag, written as prose *about* the tag.
#:
#: These cannot be escaped the usual way: `{% endraw %}` inside a raw block is
#: what ends the block. Only the opening brace has to be hidden, so Liquid
#: prints that one character and the rest is ordinary text.
_RAW_TAG = re.compile(r"\{%-?\s*(raw|endraw)\s*-?%\}")

#: How Liquid itself finds tags and outputs, and the reason case 3 is awkward.
#:
#: An output ends at the *first* `}`, not at the first `}}` — Liquid's
#: `VariableIncompleteEnd` is `}}?`. So `{{ '{% raw %}' }}`, the obvious way to
#: print a tag from a string literal, ends at the `}` of `%}` inside the quotes
#: and Liquid reports an unterminated variable. This is the regex `check_liquid`
#: reads the page with, so the check sees what the renderer will see.
_TOKEN = re.compile(r"\{%.*?%\}|\{\{.*?\}\}?", re.DOTALL)

#: Either of the above, or any other Liquid — matched in this order so that a
#: complete raw block wins over the tags inside it.
_ESCAPABLE = re.compile(
    "%s|%s|%s" % (_RAW_BLOCK.pattern, _RAW_TAG.pattern, _LIQUID.pattern),
    re.DOTALL,
)

#: A fenced block. Everything inside one is an example, never a link.
_FENCE = re.compile(r"```.*?```", re.DOTALL)

BANNER = (
    "<!-- Generated from {source} by scripts/sync_site_pages.py.\n"
    "     Edit that file, not this one. This copy is git-ignored. -->"
)


class UnknownTarget(Exception):
    """A published page links to a document that is not published."""


class BrokenLiquid(Exception):
    """The generated page would not parse as Liquid."""


def escape_liquid(text: str) -> str:
    """Stop Liquid already in the document from being executed as Liquid.

    Must run **before** the links are rewritten — what this protects is the
    author's text, not the tags this script goes on to insert.

    Three cases, and getting the third wrong took the whole site down:

    1. An ordinary tag or output — wrap it in `raw` so it is shown, not run.
    2. A `raw` block the author already wrote — leave it completely alone.
       Wrapping it produced `{% raw %}{% raw %}...{% endraw %}{% endraw %}`,
       and Jekyll refused to build: *Unknown tag 'endraw'*.
    3. A lone `raw` or `endraw` tag, in prose *about* escaping. It cannot go
       inside a raw block — `endraw` is precisely what closes one — so Liquid
       prints the opening brace and the rest stays as text:
       `{% raw %}` is written `{{ '{' }}% raw %}`. Printing the whole tag from
       one string literal looks tidier and does not work; see `_TOKEN`.
    """

    def replace(match):
        found = match.group(0)
        if _RAW_BLOCK.fullmatch(found):
            return found
        if _RAW_TAG.fullmatch(found):
            return "{{ '{' }}" + found[1:]
        return "{% raw %}" + found + "{% endraw %}"

    return _ESCAPABLE.sub(replace, text)


def check_liquid(text: str, name: str) -> None:
    """Refuse to write a page that Liquid will not parse.

    The bugs this exists for reached a running Jekyll before anyone saw them:
    the generator was happy, the link checker reads source rather than Liquid,
    and `dev.py verify` does not build the site. Catching them here means the
    generator cannot emit a page that will not parse.

    It reads the page the way Liquid tokenises it (`_TOKEN`), so both failures
    that have actually happened are caught: an `endraw` with nothing open, and
    an output ended early by a `%}` inside it.

    A raw block is open or it is not — Liquid does not nest them. Inside one,
    everything up to the next `endraw` is literal text, including another `raw`
    and including an output that never closes. That is why raw blocks wrapped
    around raw blocks failed on the *trailing* `endraw` rather than the inner
    tag: the first `endraw` had already closed the block, leaving the last one
    with nothing to close. Jekyll called it *Unknown tag 'endraw'*.
    """
    open_at = None
    for token in _TOKEN.finditer(text):
        found = token.group(0)
        tag = _RAW_TAG.fullmatch(found)

        if open_at is not None:
            if tag is not None and tag.group(1) == "endraw":
                open_at = None
            continue

        if found.startswith("{{"):
            if not found.endswith("}}"):
                raise BrokenLiquid(
                    "%s: an output is never closed, at character %d: %r\n"
                    "    Liquid ends one at the first `}`, so a `%%}` inside it "
                    "closes it early." % (name, token.start(), found)
                )
            continue

        if tag is None:
            continue

        if tag.group(1) == "raw":
            open_at = token.start()
        else:
            raise BrokenLiquid(
                "%s: endraw with nothing open, at character %d. Jekyll reports "
                "this as Unknown tag 'endraw'." % (name, token.start())
            )

    if open_at is not None:
        raise BrokenLiquid(
            "%s: a raw block opened at character %d is never closed."
            % (name, open_at)
        )


def rewrite_links(text: str, source: str):
    """Point every internal link at its page. Returns the text and any misses.

    Targets resolve relative to the source document, the way they do when you
    read the file in place: `RESEARCH.md` inside `project-memory/DECISIONS.md`
    means `project-memory/RESEARCH.md`.
    """
    base = Path(source).parent
    misses = []

    def resolve(target: str) -> str:
        # Split the anchor off before resolving, and put it back afterwards.
        path, _, anchor = target.partition("#")
        if not path:
            return target

        resolved = str((base / path).as_posix())
        # `../docs/DEPLOYMENT.md` from project-memory/ needs normalising.
        parts = []
        for part in resolved.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part not in ("", "."):
                parts.append(part)
        return "/".join(parts) + (("#" + anchor) if anchor else "")

    def replace(match):
        # A whole link wrapped in backticks is a link being *discussed*, not
        # followed — `project-memory/DECISIONS.md` explains the convention using
        # `[BACKLOG.md](BACKLOG.md)` as its example. Backticks *inside* the
        # label are ordinary code formatting and must not stop the rewrite;
        # missing that distinction left three real links unconverted.
        whole = match.string
        before = whole[match.start() - 1 : match.start()]
        after = whole[match.end() : match.end() + 1]
        if before == "`" and after == "`":
            return match.group(0)

        label, target = match.group(1), match.group(2)
        resolved = resolve(target)
        path, _, anchor = resolved.partition("#")

        permalink = LINKS.get(path)
        if permalink is None:
            misses.append(target)
            return match.group(0)

        suffix = ("#" + anchor) if anchor else ""
        return "[%s]({{ '%s' | relative_url }}%s)" % (label, permalink, suffix)

    # Rebuild around the fenced blocks rather than replacing inside them.
    out = []
    last = 0
    for fence in _FENCE.finditer(text):
        out.append(_LINK.sub(replace, text[last : fence.start()]))
        out.append(fence.group(0))
        last = fence.end()
    out.append(_LINK.sub(replace, text[last:]))

    return "".join(out), misses


def build_page(source: str, title: str, permalink: str) -> str:
    body = escape_liquid((ROOT / source).read_text(encoding="utf-8"))

    language = CODE_BLOCKS.get(source)
    if language:
        # Not Markdown. Show it as what it is, with a heading so the page is
        # not a wall of code with no explanation of what it is for.
        body = (
            "# %s\n\nThe annotated `%s` from the repository, in full. Copy it to "
            "`.env` and edit what you need — every value has a working default.\n"
            "\n```%s\n%s\n```\n" % (title, source, language, body.rstrip())
        )
        misses = []
    else:
        body, misses = rewrite_links(body, source)

    if misses:
        raise UnknownTarget(
            "%s links to %s, which has no page on the site.\n"
            "    Either add it to PAGES in scripts/sync_site_pages.py, or "
            "change the link in the source document." % (source, ", ".join(sorted(set(misses))))
        )

    front = "---\ntitle: %s\npermalink: %s\n---\n\n%s\n\n" % (
        title,
        permalink,
        BANNER.format(source=source),
    )
    page = front + body
    check_liquid(page, source)
    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--list", action="store_true", help="say what would be written, and stop"
    )
    args = parser.parse_args()

    if args.list:
        for source, name, title, permalink in PAGES:
            print("%-38s -> %-22s %s" % (source, permalink, "docs/reference/" + name))
        return 0

    missing = [source for source, _, _, _ in PAGES if not (ROOT / source).exists()]
    if missing:
        print("Cannot generate: missing " + ", ".join(missing), file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)

    # Anything left from a previous run whose page has since been removed would
    # otherwise stay published for ever.
    wanted = {name for _, name, _, _ in PAGES}
    for stale in OUT.glob("*.md"):
        if stale.name not in wanted:
            stale.unlink()

    try:
        for source, name, title, permalink in PAGES:
            (OUT / name).write_text(build_page(source, title, permalink), encoding="utf-8")
    except UnknownTarget as error:
        print("Broken link in a generated page:\n    %s" % error, file=sys.stderr)
        return 1
    except BrokenLiquid as error:
        print("Generated page would not build:\n    %s" % error, file=sys.stderr)
        return 1

    print("Generated %d pages in docs/reference/" % len(PAGES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
