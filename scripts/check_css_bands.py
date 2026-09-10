#!/usr/bin/env python3
"""No band element may use the `padding` shorthand.

A layout band gives a page its side gutter with:

    padding-inline: var(--gutter);

Any rule on the *same element* that uses the `padding` shorthand resets that to
zero, and the content goes flush against the window edge.

This is not hypothetical. `.doc { padding: 48px 0 72px }` did exactly that to
all twenty document pages, and it survived several rounds of verification
because no other check reads CSS — the link checker, the band checker and the
privacy checker all passed the whole time. See decision D-041.

    python scripts/check_css_bands.py
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Classes that land on an element carrying a layout band, plus the band
# classes themselves. A `padding` shorthand on any of these is the bug.
GUARDED = {
    "docs/assets/site.css": [
        "wrap",  # the band itself
        "doc",  # <main class="wrap doc">
        "home",  # <main class="wrap home">
        "site-header__in",
        "site-header__panel-in",
        "site-footer__in",
    ],
    "apps/web/src/styles.css": [
        "header__inner",
        "header__panel-inner",
        "workspace",
    ],
}

RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
# `padding:` but not `padding-block:` or `padding-inline:`.
SHORTHAND = re.compile(r"(?<![-\w])padding\s*:", re.I)


# No `list[str]` annotation: these scripts run on whatever Python the
# developer has, and this machine's is 3.8 — which is the whole reason Docker
# is the supported path for the application (D-006, D-007).
def targets_element(selector, names):
    """Does this selector target the guarded element itself, not a descendant?

    `.doc` and `.wrap.doc` yes; `.doc pre` no — a rule on a child cannot
    affect its parent's padding.
    """
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        last = part.split()[-1]
        for name in names:
            if re.fullmatch(rf"(\.[\w-]+)*\.{re.escape(name)}(\.[\w-]+)*", last):
                return True
    return False


def main() -> int:
    failures = []
    checked = 0

    for relative, names in GUARDED.items():
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"missing: {relative}")
            continue

        # Strip comments, so a commented-out example never trips this.
        css = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)

        for match in RULE.finditer(css):
            selector = " ".join(match.group(1).split())
            if not targets_element(selector, names):
                continue

            checked += 1
            if SHORTHAND.search(match.group(2)):
                line = css[: match.start()].count("\n") + 1
                failures.append(
                    "{}:~{}  {} uses the `padding` shorthand — "
                    "use `padding-block`".format(relative, line, selector)
                )

    print("band rules checked: {}".format(checked))

    if failures:
        print("\nFAIL ({}):".format(len(failures)))
        for failure in failures:
            print("  " + failure)
        return 1

    print("no band rule uses the padding shorthand")
    return 0


if __name__ == "__main__":
    sys.exit(main())
