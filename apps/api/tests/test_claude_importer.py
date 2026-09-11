"""Tests for the Claude importer, and for telling the two providers apart.

The most valuable tests here are the detection ones. Both ChatGPT and Claude
ship a file called `conversations.json`, so before this importer existed the
ChatGPT one would confidently accept a Claude export and find nothing in it.
Filename-based detection was a latent bug that only a second provider could
expose.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import pytest

from conftest import make_conversation, write_download_manifest, write_export
from mind_archive.importers import find_importer
from mind_archive.importers.claude import ClaudeImporter


def claude_message(
    sender: str = "human",
    text: str = "How do I make a starter?",
    when: str | None = "2024-03-14T09:30:00.000000Z",
    content: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    message: dict[str, Any] = {
        "uuid": "message-1",
        "sender": sender,
        "text": text,
        "created_at": when,
        "updated_at": when,
        "attachments": [],
        "files": [],
    }
    message["content"] = (
        content if content is not None else [{"type": "text", "text": text}]
    )
    return message


def claude_conversation(
    *,
    name: str | None = "Making bread",
    uuid: str = "conversation-1",
    created: str | None = "2024-03-14T09:30:00.000000Z",
    messages: list[dict[str, Any]] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    conversation: dict[str, Any] = {
        "uuid": uuid,
        "name": name,
        "created_at": created,
        "updated_at": created,
        "account": {"uuid": "account-1"},
        "chat_messages": messages
        if messages is not None
        else [
            claude_message("human", "How do I make a starter?"),
            claude_message("assistant", "Mix flour and water, then wait."),
        ],
    }
    conversation.update(overrides)
    return conversation


def write_claude_export(
    directory: Path,
    conversations: list[dict[str, Any]],
    name: str = "claude-export.zip",
) -> Path:
    path = directory / name
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "conversations.json", json.dumps(conversations, ensure_ascii=False)
        )
        archive.writestr("users.json", json.dumps([{"uuid": "account-1"}]))
    return path


@pytest.fixture
def importer() -> ClaudeImporter:
    return ClaudeImporter()


@pytest.fixture
def export(tmp_path: Path):
    def build(conversations: list[dict[str, Any]] | None = None, **kwargs: Any) -> Path:
        if conversations is None:
            conversations = [claude_conversation()]
        return write_claude_export(tmp_path, conversations, **kwargs)

    return build


# ---------------------------------------------------------------------------
# Telling the two providers apart
# ---------------------------------------------------------------------------


def test_the_registry_picks_claude_for_a_claude_export(export) -> None:
    found = find_importer(export())

    assert found is not None
    assert found.name == "claude"


def test_the_registry_picks_chatgpt_for_a_chatgpt_export(tmp_path: Path) -> None:
    found = find_importer(write_export(tmp_path, [make_conversation()]))

    assert found is not None
    assert found.name == "chatgpt"


def test_chatgpt_does_not_claim_a_claude_export(export) -> None:
    """The bug a second provider exposed: both files are called
    conversations.json, so matching on the name claimed the wrong export."""
    from mind_archive.importers.chatgpt import ChatGPTImporter

    assert ChatGPTImporter().detect(export()) is False


def test_claude_does_not_claim_a_chatgpt_export(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    assert importer.detect(write_export(tmp_path, [make_conversation()])) is False


def test_claude_ignores_an_unrelated_zip(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    path = tmp_path / "holiday.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("beach.jpg", "not a photo")

    assert importer.detect(path) is False


def test_detection_never_raises_on_a_broken_file(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    path = tmp_path / "truncated.zip"
    path.write_bytes(b"PK\x03\x04 not really a zip")

    assert importer.detect(path) is False


# ---------------------------------------------------------------------------
# Reading a normal export
# ---------------------------------------------------------------------------


def test_validate_reports_how_many_conversations(
    importer: ClaudeImporter, export
) -> None:
    result = importer.validate(
        export([claude_conversation(uuid="one"), claude_conversation(uuid="two")])
    )

    assert result.ok is True
    assert result.conversation_count == 2


def test_parses_a_conversation(importer: ClaudeImporter, export) -> None:
    conversation = importer.parse(export()).conversations[0]

    assert conversation.title == "Making bread"
    assert conversation.source == "claude"
    assert conversation.source_id == "conversation-1"
    assert conversation.message_count == 2


def test_keeps_messages_in_order(importer: ClaudeImporter, export) -> None:
    """Claude's export is already a flat list in conversation order, which is
    a mercy after ChatGPT's tree."""
    conversation = claude_conversation(
        messages=[
            claude_message("human", "First"),
            claude_message("assistant", "Second"),
            claude_message("human", "Third"),
        ]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert [message.text for message in parsed.messages] == [
        "First",
        "Second",
        "Third",
    ]


def test_human_becomes_user(importer: ClaudeImporter, export) -> None:
    """Claude says "human"; the archive says "user" for every provider."""
    conversation = importer.parse(export()).conversations[0]

    assert [message.role for message in conversation.messages] == [
        "user",
        "assistant",
    ]


def test_iso_timestamps_are_understood(importer: ClaudeImporter, export) -> None:
    conversation = importer.parse(export()).conversations[0]

    assert conversation.created_at is not None
    assert conversation.created_at.year == 2024
    assert conversation.created_at.month == 3


def test_a_timestamp_without_a_zone_is_treated_as_utc(
    importer: ClaudeImporter, export
) -> None:
    conversation = claude_conversation(created="2024-03-14T09:30:00")

    parsed = importer.parse(export([conversation])).conversations[0]

    assert parsed.created_at is not None
    assert parsed.created_at.tzinfo is not None


def test_reads_a_bare_conversations_json(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    path = tmp_path / "conversations.json"
    path.write_text(json.dumps([claude_conversation()]), encoding="utf-8")

    assert importer.detect(path) is True
    assert importer.parse(path).imported == 1


# ---------------------------------------------------------------------------
# Content blocks
# ---------------------------------------------------------------------------


def test_content_blocks_are_preferred_over_text(
    importer: ClaudeImporter, export
) -> None:
    """`content[]` is the richer field, so it wins when both are present."""
    conversation = claude_conversation(
        messages=[
            claude_message(
                text="the plain fallback",
                content=[{"type": "text", "text": "the richer content"}],
            )
        ]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert parsed.messages[0].text == "the richer content"


def test_text_is_used_when_there_are_no_content_blocks(
    importer: ClaudeImporter, export
) -> None:
    conversation = claude_conversation(
        messages=[claude_message(text="only the plain field", content=[])]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert parsed.messages[0].text == "only the plain field"


def test_several_blocks_are_joined(importer: ClaudeImporter, export) -> None:
    conversation = claude_conversation(
        messages=[
            claude_message(
                content=[
                    {"type": "text", "text": "First part"},
                    {"type": "text", "text": "Second part"},
                ]
            )
        ]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert parsed.messages[0].text == "First part\n\nSecond part"


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("image", "image"),
        ("document", "document"),
        ("tool_use", "tool use"),
        ("tool_result", "tool result"),
    ],
)
def test_non_text_blocks_are_noted_rather_than_dropped(
    importer: ClaudeImporter, export, kind: str, expected: str
) -> None:
    conversation = claude_conversation(
        messages=[claude_message(text="", content=[{"type": kind}])]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert expected in parsed.messages[0].text
    assert "not imported yet" in parsed.messages[0].text


def test_thinking_blocks_are_kept_and_marked(importer: ClaudeImporter, export) -> None:
    conversation = claude_conversation(
        messages=[
            claude_message(
                sender="assistant",
                text="",
                content=[{"type": "thinking", "thinking": "Let me work through it."}],
            )
        ]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert "Thinking" in parsed.messages[0].text
    assert "work through it" in parsed.messages[0].text


def test_an_unknown_block_type_does_not_lose_the_message(
    importer: ClaudeImporter, export
) -> None:
    """A block type Anthropic adds later must degrade, not disappear."""
    conversation = claude_conversation(
        messages=[
            claude_message(
                text="",
                content=[{"type": "something_from_the_future", "text": "still here"}],
            )
        ]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert parsed.messages[0].text == "still here"


# ---------------------------------------------------------------------------
# Malformed input
# ---------------------------------------------------------------------------


def test_a_null_name_becomes_readable(importer: ClaudeImporter, export) -> None:
    parsed = importer.parse(export([claude_conversation(name=None)])).conversations[0]

    assert parsed.title == "Untitled conversation"


def test_a_missing_timestamp_is_left_missing(importer: ClaudeImporter, export) -> None:
    parsed = importer.parse(export([claude_conversation(created=None)])).conversations[
        0
    ]

    assert parsed.created_at is None


def test_an_unparseable_timestamp_is_left_missing(
    importer: ClaudeImporter, export
) -> None:
    parsed = importer.parse(
        export([claude_conversation(created="the fourteenth of March")])
    ).conversations[0]

    assert parsed.created_at is None


def test_an_unknown_sender_is_skipped(importer: ClaudeImporter, export) -> None:
    conversation = claude_conversation(
        messages=[
            claude_message("system", "scaffolding"),
            claude_message("human", "a real question"),
        ]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert parsed.message_count == 1
    assert parsed.messages[0].text == "a real question"


def test_empty_messages_are_dropped(importer: ClaudeImporter, export) -> None:
    conversation = claude_conversation(
        messages=[claude_message(text="   ", content=[]), claude_message(text="Real")]
    )

    parsed = importer.parse(export([conversation])).conversations[0]

    assert parsed.message_count == 1


def test_a_conversation_with_no_messages_is_skipped(
    importer: ClaudeImporter, export
) -> None:
    result = importer.parse(export([claude_conversation(messages=[])]))

    assert result.imported == 0
    assert result.skipped == 1


def test_one_broken_conversation_does_not_stop_the_others(
    importer: ClaudeImporter, export
) -> None:
    result = importer.parse(
        export(
            [
                claude_conversation(uuid="good-1"),
                {"name": "Broken", "chat_messages": "this should be a list"},
                claude_conversation(uuid="good-2"),
            ]
        )
    )

    assert result.imported == 2
    assert result.skipped == 1


@pytest.mark.parametrize(
    "junk",
    [
        {"chat_messages": [{"sender": None, "content": None}]},
        {"chat_messages": [{"sender": "human", "content": [None, 5]}]},
        {"chat_messages": [None]},
        {"name": 12345, "chat_messages": []},
        {"chat_messages": []},
    ],
)
def test_junk_conversations_never_crash_the_import(
    importer: ClaudeImporter, export, junk: dict
) -> None:
    result = importer.parse(export([junk, claude_conversation()]))

    assert result.imported == 1
    assert result.skipped == 1


def test_reports_invalid_json_plainly(importer: ClaudeImporter, tmp_path: Path) -> None:
    path = tmp_path / "broken.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("conversations.json", "{ not json at all")

    assert "not valid JSON" in importer.validate(path).message


def test_a_hostile_archive_is_refused(importer: ClaudeImporter, tmp_path: Path) -> None:
    path = tmp_path / "slip.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("conversations.json", json.dumps([claude_conversation()]))
        archive.writestr("../escaped.txt", "malicious")

    assert importer.detect(path) is False
    assert importer.validate(path).ok is False


# ---------------------------------------------------------------------------
# The download manifest
#
# Claude no longer hands you conversations directly. You get a small JSON of
# single-use links, and importing it can never work. It is recognised so the
# refusal can say what to download instead of "not recognised" (D-042).
# ---------------------------------------------------------------------------


def test_the_download_manifest_is_recognised(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    assert importer.detect(write_download_manifest(tmp_path)) is True


def test_the_manifest_is_refused_with_the_file_to_download(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    outcome = importer.validate(write_download_manifest(tmp_path))

    assert outcome.ok is False
    # The whole point: name the file, do not just say no.
    assert "conversations-000.zip" in outcome.message
    assert "only once" in outcome.message


def test_the_manifest_names_whatever_filename_it_actually_carries(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    """Read the filename from the manifest rather than assuming one."""
    path = write_download_manifest(
        tmp_path, conversations_filename="conversations-007.zip"
    )

    assert "conversations-007.zip" in importer.validate(path).message


def test_parsing_a_manifest_reports_the_same_advice(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    result = importer.parse(write_download_manifest(tmp_path))

    assert result.conversations == []
    assert any("conversations-000.zip" in problem for problem in result.problems)


def test_the_registry_sends_a_manifest_to_claude(tmp_path: Path) -> None:
    """ChatGPT is listed first and must not answer for this file."""
    found = find_importer(write_download_manifest(tmp_path))

    assert found is not None
    assert found.name == "claude"


def test_an_unrelated_json_object_is_not_a_manifest(
    importer: ClaudeImporter, tmp_path: Path
) -> None:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"data_files": ["not", "objects"]}), encoding="utf-8")

    assert importer.detect(path) is False
