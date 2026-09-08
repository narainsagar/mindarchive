"""Safe filesystem path handling.

From Milestone 2 onward, Mind Archive reads archives exported by other
applications. Filenames inside those archives are written by someone else and
must be treated as hostile: a path like ``../../.ssh/authorized_keys`` inside a
zip is a well-known attack, and it is easy to fall for by accident.

Every path that comes from outside the application goes through this module.
Nothing else should join user-supplied path fragments by hand.

See docs/SECURITY.md.
"""

from __future__ import annotations

from pathlib import Path


class UnsafePathError(ValueError):
    """A path resolved outside the directory it was required to stay inside."""


def is_inside(child: Path, parent: Path) -> bool:
    """True if ``child`` is ``parent`` or lives somewhere beneath it.

    Both paths are fully resolved first, so symlinks and ``..`` segments cannot
    be used to escape.
    """
    try:
        resolved_child = child.resolve()
        resolved_parent = parent.resolve()
    except OSError:
        return False

    return (
        resolved_child == resolved_parent or resolved_parent in resolved_child.parents
    )


def safe_join(root: Path, *parts: str) -> Path:
    """Join untrusted ``parts`` onto ``root``, refusing to escape it.

    Raises ``UnsafePathError`` if the result would land outside ``root``, or if
    any part is an absolute path or a bare traversal segment.

        >>> safe_join(Path("/data"), "chats", "hello.md")
        PosixPath('/data/chats/hello.md')
        >>> safe_join(Path("/data"), "../etc/passwd")
        Traceback (most recent call last):
        UnsafePathError: ...
    """
    for part in parts:
        if not part or part in (".", ".."):
            raise UnsafePathError(f"Refusing to use path segment: {part!r}")
        if Path(part).is_absolute():
            raise UnsafePathError(f"Refusing to use absolute path segment: {part!r}")
        if "\x00" in part:
            raise UnsafePathError("Path segment contains a null byte")

    candidate = root.joinpath(*parts)

    if not is_inside(candidate, root):
        raise UnsafePathError(
            f"Refusing to write outside the archive: {'/'.join(parts)!r}"
        )

    return candidate


def safe_filename(name: str, fallback: str = "untitled") -> str:
    """Reduce an arbitrary string to something safe to use as a filename.

    Conversation titles come from provider exports and can contain path
    separators, control characters, or nothing at all.
    """
    cleaned = "".join(
        character if character.isalnum() or character in " -_." else "-"
        for character in name
    ).strip(" .-")

    # Collapse runs of dashes, which the substitution above tends to produce.
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")

    # Reserved on Windows, regardless of extension.
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
    if cleaned.upper() in reserved:
        cleaned = f"{cleaned}-file"

    return cleaned[:120] or fallback
