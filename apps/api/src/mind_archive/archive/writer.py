"""Writing conversations to disk as readable files.

Each conversation becomes a folder holding two files:

```
data/archive/chatgpt/2024-03-14-making-bread/
├── conversation.md     what you read
└── metadata.json       what the machine reads
```

Markdown because a person should be able to open the archive in any editor, on
any machine, in ten years, without Mind Archive existing. JSON alongside it so
the application can rebuild its index without re-parsing prose.

Deleting the database must never lose anything. Everything needed to rebuild it
is in these files — that is the rule that stops the archive becoming another
silo (decision D-004).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

from mind_archive.events import EventBus, events
from mind_archive.models import Conversation
from mind_archive.paths import safe_filename, safe_join

CONVERSATION_FILE = "conversation.md"
METADATA_FILE = "metadata.json"


#: What happened to one conversation when it was written.
Status = Literal["new", "updated", "unchanged"]


@dataclass
class Written:
    """Where a conversation went, and whether anything actually changed."""

    folder: Path
    status: Status


@dataclass
class WriteResult:
    """What was written, and what was not.

    The new/updated/unchanged split matters because every provider export is a
    *full* export. The second one contains everything the first did, so
    "imported 412 conversations" would be true and useless. What a person wants
    to know is what arrived that they did not already have.
    """

    new: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped: int = 0
    problems: list[str] = field(default_factory=list)
    folders: list[str] = field(default_factory=list)

    @property
    def written(self) -> int:
        """Conversations that reached the archive, changed or not."""
        return self.new + self.updated + self.unchanged

    def note(self, status: Status) -> None:
        if status == "new":
            self.new += 1
        elif status == "updated":
            self.updated += 1
        else:
            self.unchanged += 1

    def note_problem(self, problem: str) -> None:
        self.skipped += 1
        if len(self.problems) < 50:
            self.problems.append(problem)

    def summary(self) -> str:
        """What happened, in words a person would use.

        Says only what is true: an import with nothing new says so rather than
        claiming a number that means nothing.
        """
        if self.written == 0:
            return "Nothing was imported."

        # Nothing arrived that was not already here. Common, and worth saying
        # plainly rather than dressing up as a number.
        if not self.new and not self.updated:
            return (
                f"Nothing new — all {self.unchanged} "
                f"{'conversation was' if self.unchanged == 1 else 'conversations were'}"
                " already in your archive."
            )

        # A first import: everything is new, so the breakdown says nothing.
        if not self.updated and not self.unchanged:
            return (
                f"Imported {self.new} "
                f"{'conversation' if self.new == 1 else 'conversations'}."
            )

        parts: list[str] = []
        if self.new:
            parts.append(f"{self.new} new")
        if self.updated:
            parts.append(f"{self.updated} updated")
        if self.unchanged:
            parts.append(f"{self.unchanged} already in your archive")

        return "Imported " + ", ".join(parts) + "."


class ArchiveWriter:
    """Writes conversations into the archive folder."""

    def __init__(self, archive_dir: Path, bus: EventBus | None = None) -> None:
        self.archive_dir = archive_dir
        self.bus = bus if bus is not None else events

    def write_all(self, conversations: list[Conversation]) -> WriteResult:
        result = WriteResult()

        for index, conversation in enumerate(conversations):
            try:
                written = self.write(conversation)
            except Exception as error:  # noqa: BLE001 - one bad one, not a failed import
                # The conversation's title is not logged: it is user content.
                result.note_problem(
                    f"Conversation {index + 1} could not be saved "
                    f"({type(error).__name__})."
                )
                continue

            result.note(written.status)
            result.folders.append(str(written.folder))

        return result

    def write(self, conversation: Conversation) -> Written:
        """Write one conversation, unless it is already there unchanged.

        Re-importing the same export is the normal case, not the exception —
        every provider export is a full export. So an unchanged conversation is
        left completely alone: no write, no modified timestamp, no event. A
        file's timestamp should mean "this changed", and it stops meaning that
        if every import rewrites everything.
        """
        folder = self._folder_for(conversation)

        markdown = render_markdown(conversation)
        metadata = (
            json.dumps(_metadata(conversation), indent=2, ensure_ascii=False) + "\n"
        )

        markdown_path = folder / CONVERSATION_FILE
        metadata_path = folder / METADATA_FILE

        existed = markdown_path.is_file()
        if (
            existed
            and _unchanged(markdown_path, markdown)
            and _unchanged(metadata_path, metadata)
        ):
            return Written(folder=folder, status="unchanged")

        folder.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(markdown, encoding="utf-8")
        metadata_path.write_text(metadata, encoding="utf-8")

        self.bus.publish(
            "conversation.updated" if existed else "conversation.created",
            {
                "source": conversation.source,
                # The folder relative to the archive root — the conversation's
                # identity everywhere else. Published rather than left to be
                # reconstructed, so a subscriber cannot rebuild it wrongly.
                "path": folder.relative_to(self.archive_dir).as_posix(),
                "messages": str(conversation.message_count),
            },
        )

        return Written(folder=folder, status="updated" if existed else "new")

    def _folder_for(self, conversation: Conversation) -> Path:
        """Build a readable, unique, traversal-safe folder name.

        The title comes from a provider export, so it is untrusted: it may
        contain slashes, control characters, a Windows reserved name, or
        nothing at all. Every path segment goes through `safe_join`.
        """
        source = safe_filename(conversation.source, fallback="unknown-source")

        date = (
            conversation.created_at.strftime("%Y-%m-%d")
            if conversation.created_at
            else "undated"
        )
        title = safe_filename(conversation.title, fallback="untitled")
        base = f"{date}-{title}"

        folder = safe_join(self.archive_dir, source, base)

        # Two conversations can genuinely share a date and title. Suffix rather
        # than overwrite — losing someone's conversation to a name collision
        # would be unforgivable.
        if folder.exists() and not self._is_same_conversation(folder, conversation):
            for suffix in range(2, 1000):
                candidate = safe_join(self.archive_dir, source, f"{base}-{suffix}")
                if not candidate.exists() or self._is_same_conversation(
                    candidate, conversation
                ):
                    return candidate
            raise ValueError("Too many conversations with the same name.")

        return folder

    def _is_same_conversation(self, folder: Path, conversation: Conversation) -> bool:
        """Is this folder already holding this same conversation?

        Re-importing the same export should update it in place rather than
        creating a second copy. Matched on the provider's own identifier.
        """
        if not conversation.source_id:
            return False

        metadata_path = folder / METADATA_FILE
        if not metadata_path.is_file():
            return False

        try:
            existing = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False

        return (
            isinstance(existing, dict)
            and existing.get("source_id") == conversation.source_id
        )


def _unchanged(path: Path, content: str) -> bool:
    """Is the file already exactly this text?

    A plain comparison rather than a hash: these files are kilobytes, the
    comparison is exact, and there is no digest to get wrong.
    """
    try:
        return path.read_text(encoding="utf-8") == content
    except (OSError, UnicodeDecodeError):
        return False


def _metadata(conversation: Conversation) -> dict[str, object]:
    return {
        "title": conversation.title,
        "source": conversation.source,
        "source_id": conversation.source_id,
        "created_at": _iso(conversation.created_at),
        "updated_at": _iso(conversation.updated_at),
        "message_count": conversation.message_count,
        "metadata": conversation.metadata,
    }


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def render_markdown(conversation: Conversation) -> str:
    """Render a conversation as Markdown a person would want to read.

    YAML front matter at the top, because that is what note-taking tools expect
    and it costs nothing if you do not use one.
    """
    lines: list[str] = [
        "---",
        f"title: {_yaml_value(conversation.title)}",
        f"source: {conversation.source}",
    ]
    if conversation.created_at:
        lines.append(f"created: {conversation.created_at.isoformat()}")
    if conversation.updated_at:
        lines.append(f"updated: {conversation.updated_at.isoformat()}")
    lines.append(f"messages: {conversation.message_count}")
    for key, value in sorted(conversation.metadata.items()):
        lines.append(f"{key}: {_yaml_value(value)}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {conversation.title}")
    lines.append("")

    for message in conversation.messages:
        lines.append(f"## {_speaker(message.role)}")
        if message.created_at:
            lines.append("")
            lines.append(f"*{message.created_at.strftime('%d %B %Y, %H:%M')} UTC*")
        lines.append("")
        lines.append(message.text)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _speaker(role: str) -> str:
    """A human word for a role. "You", not "user"."""
    return {
        "user": "You",
        "assistant": "Assistant",
        "tool": "Tool",
        "system": "System",
    }.get(role, role.title())


def _yaml_value(value: str) -> str:
    """Quote a YAML scalar when it would otherwise break the front matter.

    Titles come from an export and can contain colons, quotes and newlines.
    """
    cleaned = value.replace("\n", " ").replace("\r", " ").strip()
    if not cleaned:
        return '""'
    if (
        any(character in cleaned for character in ":#\"'{}[]&*!|>%@`")
        or cleaned[0].isdigit()
    ):
        escaped = cleaned.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return cleaned
