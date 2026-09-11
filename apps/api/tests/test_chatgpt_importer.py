"""Tests for the ChatGPT importer.

Two halves: does it read a normal export correctly, and does it survive a
hostile or broken one. The second half matters more — a real export will
contain things this parser has never seen.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from conftest import (
    make_conversation,
    make_mapping,
    write_download_manifest,
    write_export,
    write_sharded_export,
)
from mind_archive.importers import find_importer
from mind_archive.importers.chatgpt import ChatGPTImporter


@pytest.fixture
def importer() -> ChatGPTImporter:
    return ChatGPTImporter()


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def test_detects_a_chatgpt_export(importer: ChatGPTImporter, export) -> None:
    assert importer.detect(export()) is True


def test_detects_an_export_wrapped_in_a_folder(
    importer: ChatGPTImporter, export
) -> None:
    """Exports are sometimes wrapped in a folder named after the export date."""
    assert importer.detect(export(inner_folder="chatgpt-export-2026-09-01")) is True


def test_does_not_detect_an_unrelated_zip(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    path = tmp_path / "holiday-photos.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("beach.jpg", "not really a photo")

    assert importer.detect(path) is False


def test_detection_never_raises_on_a_broken_file(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    path = tmp_path / "truncated.zip"
    path.write_bytes(b"PK\x03\x04 this is not a real zip")

    assert importer.detect(path) is False


def test_the_registry_finds_the_right_importer(export) -> None:
    found = find_importer(export())

    assert found is not None
    assert found.name == "chatgpt"


def test_the_registry_returns_nothing_for_an_unknown_file(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    assert find_importer(path) is None


# ---------------------------------------------------------------------------
# Reading a normal export
# ---------------------------------------------------------------------------


def test_validate_reports_how_many_conversations(
    importer: ChatGPTImporter, export
) -> None:
    result = importer.validate(export([make_conversation(), make_conversation()]))

    assert result.ok is True
    assert result.conversation_count == 2
    assert "2 conversations" in result.message


def test_parses_a_conversation(importer: ChatGPTImporter, export) -> None:
    result = importer.parse(export())

    assert result.imported == 1
    conversation = result.conversations[0]
    assert conversation.title == "Making bread"
    assert conversation.source == "chatgpt"
    assert conversation.source_id == "conversation-1"
    assert conversation.message_count == 2


def test_keeps_messages_in_order(importer: ChatGPTImporter, export) -> None:
    turns = [
        ("user", "First"),
        ("assistant", "Second"),
        ("user", "Third"),
        ("assistant", "Fourth"),
    ]
    result = importer.parse(export([make_conversation(turns=turns)]))

    texts = [message.text for message in result.conversations[0].messages]
    assert texts == ["First", "Second", "Third", "Fourth"]


def test_records_roles_and_timestamps(importer: ChatGPTImporter, export) -> None:
    conversation = importer.parse(export()).conversations[0]

    assert [message.role for message in conversation.messages] == [
        "user",
        "assistant",
    ]
    assert conversation.created_at is not None
    assert conversation.messages[0].created_at is not None


def test_keeps_the_model_in_metadata(importer: ChatGPTImporter, export) -> None:
    conversation = importer.parse(export()).conversations[0]

    assert conversation.metadata["model"] == "gpt-4o"


def test_reads_a_bare_conversations_json(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    """Some people unzip the export first."""
    path = tmp_path / "conversations.json"
    path.write_text(json.dumps([make_conversation()]), encoding="utf-8")

    assert importer.detect(path) is True
    assert importer.parse(path).imported == 1


# ---------------------------------------------------------------------------
# The message tree
# ---------------------------------------------------------------------------


def test_follows_the_branch_the_user_last_saw(
    importer: ChatGPTImporter, export
) -> None:
    """Editing a message creates a branch. Only the current one is imported."""
    mapping, _ = make_mapping([("user", "Original question")])

    # Two assistant replies branch from the same question: an original and a
    # regeneration. current_node points at the regeneration, which is what the
    # person would see if they opened the conversation.
    for node_id, text in (
        ("first-reply", "First answer"),
        ("second-reply", "Better answer"),
    ):
        mapping["node-0"]["children"].append(node_id)
        mapping[node_id] = {
            "id": node_id,
            "message": {
                "author": {"role": "assistant"},
                "content": {"content_type": "text", "parts": [text]},
                "create_time": 1_700_000_100.0,
                "metadata": {},
            },
            "parent": "node-0",
            "children": [],
        }

    conversation = make_conversation(turns=[])
    conversation["mapping"] = mapping
    conversation["current_node"] = "second-reply"

    parsed = importer.parse(export([conversation])).conversations[0]

    texts = [message.text for message in parsed.messages]
    assert texts == ["Original question", "Better answer"]
    assert "First answer" not in texts


def test_falls_back_when_current_node_is_missing(
    importer: ChatGPTImporter, export
) -> None:
    conversation = make_conversation(turns=[("user", "Hello"), ("assistant", "Hi")])
    conversation["current_node"] = "a-node-that-does-not-exist"

    result = importer.parse(export([conversation]))

    assert result.imported == 1
    assert result.conversations[0].message_count == 2


def test_survives_a_cycle_in_the_tree(importer: ChatGPTImporter, export) -> None:
    """A parent pointing back at its own descendant must not loop forever."""
    conversation = make_conversation(turns=[("user", "One"), ("assistant", "Two")])
    conversation["mapping"]["root"]["parent"] = "node-1"

    result = importer.parse(export([conversation]))

    assert result.imported == 1


# ---------------------------------------------------------------------------
# Content types
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ({"content_type": "text", "parts": ["Hello"]}, "Hello"),
        ({"content_type": "code", "text": "print(1)"}, "print(1)"),
        ({"content_type": "execution_output", "text": "1"}, "1"),
        ({"content_type": "text", "parts": ["A", "B"]}, "A\n\nB"),
        # A content type invented after this parser was written.
        (
            {"content_type": "something_new", "parts": ["Still readable"]},
            "Still readable",
        ),
        ({"content_type": "something_new", "text": "Fallback"}, "Fallback"),
    ],
)
def test_extracts_text_from_content_types(
    importer: ChatGPTImporter, export, content: dict, expected: str
) -> None:
    conversation = make_conversation(turns=[("user", "placeholder")])
    node = conversation["mapping"]["node-0"]["message"]
    node["content"] = content

    result = importer.parse(export([conversation]))

    assert result.conversations[0].messages[0].text == expected


def test_notes_images_rather_than_dropping_the_message(
    importer: ChatGPTImporter, export
) -> None:
    conversation = make_conversation(turns=[("user", "placeholder")])
    conversation["mapping"]["node-0"]["message"]["content"] = {
        "content_type": "multimodal_text",
        "parts": [
            {
                "content_type": "image_asset_pointer",
                "asset_pointer": "file-service://abc",
            },
            "What is in this picture?",
        ],
    }

    conversation_out = importer.parse(export([conversation])).conversations[0]

    text = conversation_out.messages[0].text
    assert "image" in text
    assert "What is in this picture?" in text


def test_skips_chatgpts_own_system_messages(importer: ChatGPTImporter, export) -> None:
    conversation = make_conversation(
        turns=[("system", "You are a helpful assistant."), ("user", "Hello")]
    )

    conversation_out = importer.parse(export([conversation])).conversations[0]

    assert conversation_out.message_count == 1
    assert conversation_out.messages[0].text == "Hello"


def test_keeps_a_user_written_system_message(importer: ChatGPTImporter, export) -> None:
    """Custom instructions are the user's own words and belong in the archive."""
    conversation = make_conversation(
        turns=[("system", "Always answer in British English."), ("user", "Hello")]
    )
    conversation["mapping"]["node-0"]["message"]["metadata"] = {
        "is_user_system_message": True
    }

    conversation_out = importer.parse(export([conversation])).conversations[0]

    assert conversation_out.message_count == 2


def test_skips_visually_hidden_messages(importer: ChatGPTImporter, export) -> None:
    conversation = make_conversation(
        turns=[("user", "Visible"), ("assistant", "Hidden")]
    )
    conversation["mapping"]["node-1"]["message"]["metadata"] = {
        "is_visually_hidden_from_conversation": True
    }

    conversation_out = importer.parse(export([conversation])).conversations[0]

    assert conversation_out.message_count == 1


# ---------------------------------------------------------------------------
# Malformed and hostile input
# ---------------------------------------------------------------------------


def test_a_null_title_becomes_readable(importer: ChatGPTImporter, export) -> None:
    result = importer.parse(export([make_conversation(title=None)]))

    assert result.conversations[0].title == "Untitled conversation"


def test_a_missing_timestamp_is_left_missing(importer: ChatGPTImporter, export) -> None:
    """Better a gap than an invented date."""
    result = importer.parse(export([make_conversation(create_time=None)]))

    assert result.conversations[0].created_at is None


def test_a_nonsense_timestamp_is_left_missing(
    importer: ChatGPTImporter, export
) -> None:
    result = importer.parse(export([make_conversation(create_time=99_999_999_999_999)]))

    assert result.conversations[0].created_at is None


def test_one_broken_conversation_does_not_stop_the_others(
    importer: ChatGPTImporter, export
) -> None:
    result = importer.parse(
        export(
            [
                make_conversation(conversation_id="good-1"),
                {"title": "Broken", "mapping": "this should be a dict"},
                make_conversation(conversation_id="good-2"),
            ]
        )
    )

    assert result.imported == 2
    assert result.skipped == 1
    assert result.problems


def test_a_conversation_with_no_messages_is_skipped(
    importer: ChatGPTImporter, export
) -> None:
    result = importer.parse(export([make_conversation(turns=[])]))

    assert result.imported == 0
    assert result.skipped == 1


def test_empty_messages_are_dropped(importer: ChatGPTImporter, export) -> None:
    conversation = make_conversation(turns=[("user", "Real"), ("assistant", "   ")])

    conversation_out = importer.parse(export([conversation])).conversations[0]

    assert conversation_out.message_count == 1


def test_reports_invalid_json_plainly(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    path = tmp_path / "broken.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("conversations.json", "{ not json at all")

    validation = importer.validate(path)

    assert validation.ok is False
    assert "not valid JSON" in validation.message


def test_reports_a_zip_without_conversations(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    path = tmp_path / "wrong.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("something-else.json", "[]")

    validation = importer.validate(path)

    assert validation.ok is False
    assert "conversations.json" in validation.message


def test_reports_json_that_is_not_a_list(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    path = tmp_path / "object.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("conversations.json", json.dumps({"conversations": []}))

    validation = importer.validate(path)

    assert validation.ok is False
    assert "list of conversations" in validation.message


def test_an_empty_export_is_valid_but_empty(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    path = write_export(tmp_path, [])

    validation = importer.validate(path)

    assert validation.ok is True
    assert validation.conversation_count == 0


@pytest.mark.parametrize(
    "junk",
    [
        {"mapping": {"a": {"message": {"author": None, "content": None}}}},
        {"mapping": {"a": {"message": {"author": {"role": 42}}}}},
        {"mapping": {"a": None}},
        {
            "mapping": {
                "a": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": [None, 5]},
                    }
                }
            }
        },
        {"title": 12345, "mapping": {}},
        {},
    ],
)
def test_junk_conversations_never_crash_the_import(
    importer: ChatGPTImporter, export, junk: dict
) -> None:
    """Whatever is in the file, the import finishes and reports honestly."""
    result = importer.parse(export([junk, make_conversation()]))

    assert result.imported == 1
    assert result.skipped == 1


# ---------------------------------------------------------------------------
# Sharded exports
#
# OpenAI no longer ships a single conversations.json. A real export contains
# conversations-000.json, -001, -002 and declares the mapping in
# export_manifest.json. Looking only for the plain name found nothing, so a
# 204-conversation export was reported as "not recognised" (D-042).
# ---------------------------------------------------------------------------


def _shards(tmp_path: Path, counts: list[int], **kwargs) -> Path:
    """A sharded export with `counts` conversations in each shard."""
    number = 0
    shards = []
    for count in counts:
        shard = []
        for _ in range(count):
            number += 1
            shard.append(make_conversation(conversation_id=f"conversation-{number}"))
        shards.append(shard)
    return write_sharded_export(tmp_path, shards, **kwargs)


def test_detects_a_sharded_export(importer: ChatGPTImporter, tmp_path: Path) -> None:
    assert importer.detect(_shards(tmp_path, [2, 2, 1])) is True


def test_reads_every_shard(importer: ChatGPTImporter, tmp_path: Path) -> None:
    """The count must be the sum, not the first shard."""
    result = importer.parse(_shards(tmp_path, [3, 3, 1]))

    assert result.imported == 7
    assert result.problems == []


def test_validate_counts_across_shards(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    outcome = importer.validate(_shards(tmp_path, [2, 2, 1]))

    assert outcome.ok is True
    assert "5 conversations" in outcome.message


def test_shards_are_read_in_manifest_order(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    first = [make_conversation(title="First", conversation_id="a")]
    second = [make_conversation(title="Second", conversation_id="b")]
    path = write_sharded_export(tmp_path, [first, second])

    result = importer.parse(path)

    assert [conversation.title for conversation in result.conversations] == [
        "First",
        "Second",
    ]


def test_shards_are_found_without_a_manifest(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    """Falling back to the filenames, for an export that declares nothing."""
    path = _shards(tmp_path, [2, 1], with_manifest=False)

    assert importer.detect(path) is True
    assert importer.parse(path).imported == 3


def test_sharded_export_inside_a_folder(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    path = _shards(tmp_path, [1, 1], inner_folder="chatgpt-export-2026-09-08")

    assert importer.detect(path) is True
    assert importer.parse(path).imported == 2


def test_the_plain_single_file_export_still_works(
    importer: ChatGPTImporter, export
) -> None:
    """Older exports have one conversations.json, and must keep working."""
    result = importer.parse(export([make_conversation(), make_conversation()]))

    assert result.imported == 2


def test_a_conversation_whose_nodes_have_no_children_key(
    importer: ChatGPTImporter, export
) -> None:
    """Current exports drop `children`; nodes are just id/message/parent.

    With `current_node` missing as well, the walk has to rebuild the tree from
    the parent links or the conversation comes out empty.
    """
    conversation = make_conversation(
        turns=[("user", "Only question"), ("assistant", "Only answer")]
    )
    for node in conversation["mapping"].values():
        node.pop("children", None)
    conversation["current_node"] = None

    result = importer.parse(export([conversation]))

    assert result.imported == 1
    assert len(result.conversations[0].messages) == 2


def test_a_claude_download_manifest_is_not_claimed(
    importer: ChatGPTImporter, tmp_path: Path
) -> None:
    """The registry lists this importer first, and it must not answer for a
    file Claude has a far better message for (D-042)."""
    assert importer.detect(write_download_manifest(tmp_path)) is False
