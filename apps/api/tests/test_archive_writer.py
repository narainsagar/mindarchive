"""Tests for writing conversations to disk.

Two things are being protected here: that the files stay readable by a person,
and that a hostile conversation title cannot write outside the archive.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from mind_archive.archive import ArchiveWriter
from mind_archive.archive.writer import render_markdown
from mind_archive.events import EventBus
from mind_archive.models import Conversation, Message


def conversation(
    *,
    title: str = "Making bread",
    source_id: str | None = "conversation-1",
    created: datetime | None = datetime(2024, 3, 14, 9, 30, tzinfo=UTC),
    messages: list[Message] | None = None,
) -> Conversation:
    return Conversation(
        title=title,
        source="chatgpt",
        source_id=source_id,
        created_at=created,
        messages=messages
        or [
            Message(role="user", text="How do I make sourdough?"),
            Message(role="assistant", text="Start with a starter."),
        ],
    )


# ---------------------------------------------------------------------------
# What gets written
# ---------------------------------------------------------------------------


def test_writes_a_folder_per_conversation(archive_dir: Path) -> None:
    folder = ArchiveWriter(archive_dir).write(conversation())

    assert (folder / "conversation.md").is_file()
    assert (folder / "metadata.json").is_file()


def test_the_folder_name_is_readable(archive_dir: Path) -> None:
    folder = ArchiveWriter(archive_dir).write(conversation())

    assert folder.name == "2024-03-14-Making bread"
    assert folder.parent.name == "chatgpt"


def test_an_undated_conversation_is_still_filed(archive_dir: Path) -> None:
    folder = ArchiveWriter(archive_dir).write(conversation(created=None))

    assert folder.name.startswith("undated-")


def test_the_markdown_is_readable(archive_dir: Path) -> None:
    folder = ArchiveWriter(archive_dir).write(conversation())
    text = (folder / "conversation.md").read_text(encoding="utf-8")

    assert "# Making bread" in text
    assert "## You" in text
    assert "## Assistant" in text
    assert "How do I make sourdough?" in text


def test_the_markdown_has_front_matter(archive_dir: Path) -> None:
    folder = ArchiveWriter(archive_dir).write(conversation())
    text = (folder / "conversation.md").read_text(encoding="utf-8")

    assert text.startswith("---\n")
    assert "source: chatgpt" in text
    assert "messages: 2" in text


def test_the_metadata_is_valid_json(archive_dir: Path) -> None:
    folder = ArchiveWriter(archive_dir).write(conversation())
    metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))

    assert metadata["title"] == "Making bread"
    assert metadata["source"] == "chatgpt"
    assert metadata["source_id"] == "conversation-1"
    assert metadata["message_count"] == 2


def test_roles_are_written_in_human_words() -> None:
    text = render_markdown(conversation())

    assert "## You" in text
    assert "user" not in text.split("---")[2]  # not in the body


def test_a_title_with_a_colon_does_not_break_the_front_matter(
    archive_dir: Path,
) -> None:
    folder = ArchiveWriter(archive_dir).write(
        conversation(title="Bread: a beginner's guide")
    )
    text = (folder / "conversation.md").read_text(encoding="utf-8")

    assert 'title: "Bread: a beginner\'s guide"' in text


# ---------------------------------------------------------------------------
# Hostile titles
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hostile_title",
    [
        "../../escaped",
        "../../../etc/passwd",
        "folder/nested",
        "..",
        "CON",
        "",
        "   ",
    ],
)
def test_a_hostile_title_cannot_escape_the_archive(
    archive_dir: Path, hostile_title: str
) -> None:
    folder = ArchiveWriter(archive_dir).write(conversation(title=hostile_title))

    assert archive_dir.resolve() in folder.resolve().parents
    assert folder.is_dir()


def test_nothing_is_written_above_the_archive(archive_dir: Path) -> None:
    ArchiveWriter(archive_dir).write(conversation(title="../../escaped"))

    assert not (archive_dir.parent / "escaped").exists()
    assert not (archive_dir.parent.parent / "escaped").exists()


def test_a_very_long_title_is_truncated(archive_dir: Path) -> None:
    folder = ArchiveWriter(archive_dir).write(conversation(title="a" * 500))

    assert len(folder.name) < 200


# ---------------------------------------------------------------------------
# Collisions and re-imports
# ---------------------------------------------------------------------------


def test_re_importing_the_same_conversation_updates_it(archive_dir: Path) -> None:
    writer = ArchiveWriter(archive_dir)

    first = writer.write(conversation())
    second = writer.write(conversation())

    assert first == second
    assert len(list((archive_dir / "chatgpt").iterdir())) == 1


def test_two_different_conversations_with_the_same_name_both_survive(
    archive_dir: Path,
) -> None:
    """Losing someone's conversation to a name collision is unforgivable."""
    writer = ArchiveWriter(archive_dir)

    first = writer.write(conversation(source_id="one"))
    second = writer.write(conversation(source_id="two"))

    assert first != second
    assert first.is_dir() and second.is_dir()
    assert len(list((archive_dir / "chatgpt").iterdir())) == 2


def test_write_all_reports_what_it_wrote(archive_dir: Path) -> None:
    result = ArchiveWriter(archive_dir).write_all(
        [conversation(source_id="one"), conversation(source_id="two")]
    )

    assert result.written == 2
    assert result.skipped == 0
    assert len(result.folders) == 2


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


def test_writing_publishes_an_event(archive_dir: Path) -> None:
    bus = EventBus()
    seen = []
    bus.subscribe("conversation.created", seen.append)

    ArchiveWriter(archive_dir, bus=bus).write(conversation())

    assert len(seen) == 1
    assert seen[0].payload["source"] == "chatgpt"


def test_events_do_not_carry_conversation_content(archive_dir: Path) -> None:
    """Events reach logs. Logs must never contain what was said."""
    bus = EventBus()
    seen = []
    bus.subscribe("conversation.created", seen.append)

    ArchiveWriter(archive_dir, bus=bus).write(
        conversation(
            messages=[Message(role="user", text="my bank password is hunter2")]
        )
    )

    assert "hunter2" not in str(seen[0].payload)
