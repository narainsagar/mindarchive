#!/usr/bin/env python3
"""Check that every internal link on the documentation site goes somewhere.

`GITHUB_PAGES.md` has said since D-036 that every internal link must be walked
and resolved — but no script did it. It was done by hand, once, after a global
`permalink:` key silently 404ed the entire navigation and the verification
written that day checked only the blog. D-036's own post-mortem is the argument
for this file: *"a check that only looks where you just worked cannot find what
you broke elsewhere."*

    python scripts/check_site_links.py

It reads the **source** rather than a built site, so it needs no Ruby, no Docker
and no Jekyll, and runs in well under a second inside `dev.py verify`.

**What it checks**

1. Every internal link resolves to a page that exists — Markdown links, Liquid
   `relative_url` links, and plain `href="/..."` in the layouts.
2. No link points at GitHub for a document that now has a page of its own. That
   is the exact regression this was written alongside (D-043): the site used to
   send a reader on `localhost:4000` to a repository that is not published yet.
3. No third-party script or frame, anywhere. A privacy-first product cannot
   load something that fingerprints every visitor, and the donate page is where
   that temptation lives (D-038).

**What it does not check.** Anchors within a page, external URLs (that needs the
network, and a link checker that fails when a stranger's server is down gets
switched off), and anything Jekyll does that the source does not show. Building
the site is still the final word; this catches the class of mistake that has
actually happened here.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

#: Directories Jekyll does not publish as pages.
SKIP = {"_site", ".jekyll-cache", "assets", "_drafts"}

#: Routes Jekyll creates that no front matter declares.
#:
#: Posts get `/blog/:title/` from `_config.yml`, and the feed comes from the
#: jekyll-feed plugin.
GENERATED = {"/blog/", "/feed.xml", "/404.html"}

_FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_PERMALINK = re.compile(r"^permalink:\s*(\S+)\s*$", re.MULTILINE)

#: `{{ '/support/' | relative_url }}` — the site's own link convention.
_LIQUID_LINK = re.compile(r"\{\{\s*'([^']+)'\s*\|\s*relative_url\s*\}\}")

#: A plain root-relative href in a layout or an HTML page.
_HREF = re.compile(r'href="(/[^"]*)"')

#: A Markdown link to something that is not a URL, an anchor or Liquid.
_MD_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#|\{\{)([^)\s]+)\)")

#: A GitHub link into the repository's own files.
_BLOB = re.compile(r"https://github\.com/[^/]+/[^/\s)]+/blob/[^/]+/([^)\s\"']+)")

#: Anything loaded from another company's server.
_THIRD_PARTY = re.compile(r'<(?:script|iframe)[^>]+src="https?://([^"/]+)', re.IGNORECASE)

#: Inside a fenced block or a code span, a link is an example being discussed,
#: not a link. The decision log explains the site's own convention by quoting
#: `[BACKLOG.md](BACKLOG.md)`, which is not a link to anywhere.
_FENCE = re.compile(r"```.*?```|`[^`\n]+`", re.DOTALL)

#: Content the site renders only where the private documents exist.
#:
#: The same `docs/` builds in two repositories. Pages generated from private
#: documents exist in one of them, so the links to them are wrapped in
#: `{% if site.data.private_pages %}`, and the data file is absent from a
#: published tree (D-048).
#:
#: This checker reads source rather than built output, so it has to honour the
#: same condition — otherwise it reports links that the build it is checking
#: would never render, which is a checker that cries wolf.
_PRIVATE_BLOCK = re.compile(
    r"\{%-?\s*if\s+site\.data\.private_pages\s*-?%\}(.*?)\{%-?\s*endif\s*-?%\}",
    re.DOTALL,
)
_PRIVATE_ELSE = re.compile(r"\{%-?\s*else\s*-?%\}", re.DOTALL)

#: Present only in the private repository. Its absence is the signal.
PRIVATE_PAGES_DATA = DOCS / "_data" / "private_pages.yml"


def strip_private_blocks(text: str) -> str:
    """Remove what this build will not render.

    In the private repository the blocks stay and their links are checked. In a
    published tree the data file is gone, so the block's body never renders and
    its links are not this site's problem — but an `{% else %}` branch is.
    """
    if PRIVATE_PAGES_DATA.exists():
        return text

    def keep_else(match: re.Match) -> str:
        parts = _PRIVATE_ELSE.split(match.group(1), maxsplit=1)
        return parts[1] if len(parts) == 2 else ""

    return _PRIVATE_BLOCK.sub(keep_else, text)


def site_files():
    """Every source file Jekyll will turn into a page or a layout."""
    for path in sorted(DOCS.rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".html", ".markdown"):
            continue
        if any(part in SKIP for part in path.relative_to(DOCS).parts):
            continue
        yield path


def known_routes():
    """Every URL the site will actually serve."""
    routes = set(GENERATED)

    for path in site_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        front = _FRONT.match(text)
        if not front:
            continue

        found = _PERMALINK.search(front.group(1))
        if found:
            routes.add(found.group(1).strip("'\""))
        elif path.parent == DOCS and path.name == "index.html":
            routes.add("/")

    # Posts, from their filenames: _config.yml gives them /blog/:title/.
    for post in (DOCS / "_posts").glob("*.m*"):
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post.stem)
        routes.add("/blog/%s/" % slug)

    return routes


def asset_exists(target: str) -> bool:
    """A link may point at a real file rather than a page — a stylesheet, say."""
    return (DOCS / target.lstrip("/")).exists()


def check() -> int:
    routes = known_routes()
    published = {}  # repo-relative source -> permalink, for the GitHub check

    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from sync_site_pages import LINKS  # noqa: PLC0415 - optional, by design

        published = dict(LINKS)
    except ImportError:
        pass

    problems = []

    for path in site_files():
        where = path.relative_to(ROOT).as_posix()
        text = strip_private_blocks(path.read_text(encoding="utf-8", errors="replace"))
        body = _FENCE.sub("", text)

        for target in _LIQUID_LINK.findall(body) + _HREF.findall(body):
            clean = target.split("#")[0].split("?")[0]
            if not clean or clean in routes or asset_exists(clean):
                continue
            problems.append("%s -> %s (no page serves this)" % (where, target))

        for target in _MD_LINK.findall(body):
            # A relative link between source files is not a site URL at all;
            # Kramdown leaves it alone and it 404s. D-036 banned these.
            if target.endswith(".md") or target.endswith(".markdown"):
                problems.append(
                    "%s -> %s (a .md link; use {{ '/permalink/' | relative_url }})"
                    % (where, target)
                )

        for target in _BLOB.findall(body):
            permalink = published.get(target.split("#")[0])
            if permalink:
                problems.append(
                    "%s -> github.com/.../%s, which is now published at %s"
                    % (where, target, permalink)
                )

        for host in _THIRD_PARTY.findall(text):
            problems.append("%s loads a third party: %s" % (where, host))

    if problems:
        print("Broken or discouraged links:\n")
        for problem in problems:
            print("  " + problem)
        print("\n%d problem(s). Every page on the site must resolve." % len(problems))
        return 1

    print("Every internal link resolves. %d routes." % len(routes))
    return 0


if __name__ == "__main__":
    raise SystemExit(check())
