"""Test fixtures.

Everything here is **synthetic** — hand-written to exercise specific cases.
No real conversation content is committed to this repository, ever. A real
export for manual testing goes in `local/`, which is git-ignored.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import pytest


def make_mapping(
    turns: list[tuple[str, str]],
    *,
    start_time: float = 1_700_000_000.0,
) -> tuple[dict[str, Any], str]:
    """Build a ChatGPT `mapping` tree from a linear list of turns.

    Returns the mapping and the id of the last node, which is what a real
    export puts in `current_node`.

    Real exports always have a root node carrying no message, so this does too.
    """
    mapping: dict[str, Any] = {
        "root": {"id": "root", "message": None, "parent": None, "children": []}
    }
    parent = "root"

    for index, (role, text) in enumerate(turns):
        node_id = f"node-{index}"
        mapping[parent]["children"].append(node_id)
        mapping[node_id] = {
            "id": node_id,
            "message": {
                "id": f"message-{index}",
                "author": {"role": role, "name": None, "metadata": {}},
                "create_time": start_time + index * 60,
                "content": {"content_type": "text", "parts": [text]},
                "status": "finished_successfully",
                "metadata": {},
                "recipient": "all",
            },
            "parent": parent,
            "children": [],
        }
        parent = node_id

    return mapping, parent


def make_conversation(
    *,
    title: str | None = "Making bread",
    turns: list[tuple[str, str]] | None = None,
    conversation_id: str = "conversation-1",
    create_time: float | None = 1_700_000_000.0,
    **overrides: Any,
) -> dict[str, Any]:
    """One conversation, shaped the way a ChatGPT export shapes them."""
    if turns is None:
        turns = [
            ("user", "How do I make sourdough?"),
            ("assistant", "Start with a starter."),
        ]

    mapping, current = make_mapping(turns)

    conversation: dict[str, Any] = {
        "title": title,
        "create_time": create_time,
        "update_time": create_time,
        "mapping": mapping,
        "current_node": current,
        "conversation_id": conversation_id,
        "is_archived": False,
        "default_model_slug": "gpt-4o",
    }
    conversation.update(overrides)
    return conversation


def write_export(
    directory: Path,
    conversations: list[dict[str, Any]],
    *,
    name: str = "chatgpt-export.zip",
    inner_folder: str = "",
    extra_files: dict[str, str] | None = None,
) -> Path:
    """Write a zip that looks like a ChatGPT export."""
    path = directory / name
    prefix = f"{inner_folder}/" if inner_folder else ""

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            f"{prefix}conversations.json",
            json.dumps(conversations, ensure_ascii=False),
        )
        archive.writestr(f"{prefix}chat.html", "<html><body>ignored</body></html>")
        archive.writestr(f"{prefix}user.json", json.dumps({"id": "user-1"}))
        for filename, content in (extra_files or {}).items():
            archive.writestr(f"{prefix}{filename}", content)

    return path


@pytest.fixture
def export(tmp_path: Path):
    """A factory for synthetic ChatGPT exports."""

    def build(conversations: list[dict[str, Any]] | None = None, **kwargs: Any) -> Path:
        if conversations is None:
            conversations = [make_conversation()]
        return write_export(tmp_path, conversations, **kwargs)

    return build


@pytest.fixture
def archive_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "archive"
    directory.mkdir()
    return directory
