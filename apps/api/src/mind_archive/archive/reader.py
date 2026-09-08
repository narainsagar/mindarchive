"""Reading conversations back off disk.

The archive files are the source of truth, so this is what everything else
reads from — the index, the API, and any future export.

Two files per conversation:

- ``metadata.json`` — title, source, dates, message count
- ``conversation.md`` — the conversation itself, with YAML front matter

The Markdown is served as Markdown rather than parsed back into messages.
Round-tripping our own rendering would be fragile — a message containing the
text ``## You`` would break it — and pointless, since the file *is* the
readable artefact. The front matter is stripped because it duplicates the
metadata the API already returns.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mind_archive.archive.writer import CONVERSATION_FILE, METADATA_FILE
from mind_archive.models import clean_tags

#: Refuse to read a conversation file larger than this. Nothing we write comes
#: close; a file this big means something is wrong, and loading it would block
#: the server.
MAX_CONVERSATION_BYTES = 32 * 1024 * 1024


@dataclass
class StoredConversation:
    """A conversation as it exists on disk."""

    #: Folder path relative to the archive root. The conversation's identity.
    path: str
    title: str
    source: str
    source_id: str | None
    created_at: str | None
    updated_at: str | None
    message_count: int

    #: Labels the user applied. Stored on disk, never derived from an export.
    tags: list[str] = field(default_factory=list)

    #: The Markdown body, front matter removed. `None` when only metadata was
    #: asked for, which is the case when listing.
    body: str | None = None


def strip_front_matter(text: str) -> str:
    """Remove leading YAML front matter, if there is any.

    Only a block that starts on the very first line counts. A ``---`` further
    down is a horizontal rule in the middle of someone's conversation and must
    be left alone.
    """
    if not text.startswith("---"):
        return text

    lines = text.split("\n")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).lstrip("\n")

    # An opening marker with no closing one: not front matter, leave it.
    return text


def _as_str(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def read_conversation(
    archive_dir: Path, folder: Path, *, with_body: bool = False
) -> StoredConversation | None:
    """Read one conversation folder, or `None` if it is not one.

    Never raises for ordinary problems — a folder that is not a conversation,
    or whose metadata is unreadable, simply returns `None`. The archive is a
    folder on someone's computer, and people put things in folders.
    """
    metadata_path = folder / METADATA_FILE
    if not metadata_path.is_file():
        return None

    try:
        raw = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None

    if not isinstance(raw, dict):
        return None

    try:
        relative = folder.relative_to(archive_dir).as_posix()
    except ValueError:
        return None

    body: str | None = None
    if with_body:
        body = _read_body(folder / CONVERSATION_FILE)

    count = raw.get("message_count")

    return StoredConversation(
        path=relative,
        title=_as_str(raw.get("title")) or "Untitled conversation",
        source=_as_str(raw.get("source")) or "unknown",
        source_id=_as_str(raw.get("source_id")),
        created_at=_as_str(raw.get("created_at")),
        updated_at=_as_str(raw.get("updated_at")),
        message_count=count if isinstance(count, int) and count >= 0 else 0,
        tags=clean_tags(raw.get("tags") or []),
        body=body,
    )


def _read_body(path: Path) -> str | None:
    if not path.is_file():
        return None

    try:
        if path.stat().st_size > MAX_CONVERSATION_BYTES:
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    return strip_front_matter(text)


def iter_conversations(archive_dir: Path) -> Iterator[StoredConversation]:
    """Walk the archive, yielding every conversation found.

    Looks for `metadata.json` rather than assuming a folder depth, so the
    layout can change later without this needing to.
    """
    if not archive_dir.is_dir():
        return

    for metadata_path in sorted(archive_dir.rglob(METADATA_FILE)):
        conversation = read_conversation(archive_dir, metadata_path.parent)
        if conversation is not None:
            yield conversation
