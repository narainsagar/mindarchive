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


def write_sharded_export(
    directory: Path,
    shards: list[list[dict[str, Any]]],
    *,
    name: str = "chatgpt-export.zip",
    with_manifest: bool = True,
    inner_folder: str = "",
) -> Path:
    """Write a zip shaped like a *current* ChatGPT export.

    Real exports no longer contain `conversations.json`. They contain
    `conversations-000.json`, `-001`, `-002` and declare the mapping in
    `export_manifest.json`. Everything here is synthetic — a real export is a
    copy of somebody's private conversations and must never be committed
    (D-042).
    """
    path = directory / name
    prefix = f"{inner_folder}/" if inner_folder else ""
    names = [f"conversations-{index:03d}.json" for index in range(len(shards))]

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, conversations in zip(names, shards, strict=True):
            archive.writestr(
                f"{prefix}{filename}",
                json.dumps(conversations, ensure_ascii=False),
            )

        if with_manifest:
            archive.writestr(
                f"{prefix}export_manifest.json",
                json.dumps(
                    {
                        "export_files": [{"path": n} for n in names],
                        "logical_files": {
                            "conversations.json": {
                                "files": names,
                                "shard_count": len(names),
                                "sharded": True,
                            },
                            "chat.html": {"files": ["chat.html"], "sharded": False},
                        },
                    }
                ),
            )

        archive.writestr(f"{prefix}chat.html", "<html><body>ignored</body></html>")
        archive.writestr(f"{prefix}user.json", json.dumps({"id": "user-1"}))

    return path


def write_download_manifest(
    directory: Path,
    *,
    name: str = "manifest-abc123.json",
    conversations_filename: str = "conversations-000.zip",
) -> Path:
    """A Claude download manifest: links, not conversations.

    Modelled on the real shape. The URL is deliberately a placeholder — a real
    manifest carries single-use signed links.
    """
    path = directory / name
    path.write_text(
        json.dumps(
            {
                "instructions": (
                    "Download each file using the export_url. Note: Each "
                    "export URL can only be used once."
                ),
                "created_at": "2026-09-08T21:20:02.000000+00:00",
                "total_files": 3,
                "version": "1.0",
                "data_files": [
                    {
                        "batch_index": 0,
                        "part": 0,
                        "category": "light_metadata",
                        "filename": "light_metadata-000.zip",
                        "export_url": "https://claude.ai/placeholder/one",
                    },
                    {
                        "batch_index": 1,
                        "part": 0,
                        "category": "projects",
                        "filename": "projects-000.zip",
                        "export_url": "https://claude.ai/placeholder/two",
                    },
                    {
                        "batch_index": 2,
                        "part": 0,
                        "category": "conversations",
                        "filename": conversations_filename,
                        "export_url": "https://claude.ai/placeholder/three",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
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
