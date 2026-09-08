#!/usr/bin/env python3
"""Generate a large, deliberately messy synthetic ChatGPT export.

    python scripts/make_fixture_export.py local/fixture.zip --conversations 2000

Hand-written fixtures test what their author thought of. This generates the
awkward cases at volume: every content type including invented ones, deep
branch trees, unicode and emoji, very long messages, nulls in every optional
field, titles that try to escape the filesystem.

It is not a substitute for a real export — it can only contain problems someone
already imagined. It is for finding crashes and measuring import speed without
waiting days for OpenAI.

**Entirely synthetic.** No real conversation content, here or in its output.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import zipfile
from pathlib import Path
from typing import Any

WORDS = (
    "sourdough tomato compiler kettle harbour lantern mixture pigeon "
    "quartz ribbon sandal thistle umbrella vinegar walnut xylophone "
    "yarrow zeppelin bracket cinnamon dovetail engine fathom granite"
).split()

# Titles that have historically broken something, plus ordinary ones.
AWKWARD_TITLES: list[Any] = [
    None,
    "",
    "   ",
    "../../escaped",
    "../../../etc/passwd",
    "CON",
    "NUL",
    "a" * 400,
    "Bread: a beginner's guide",
    'He said "hello" and left',
    "Ünïcödé and émojis 🥖🍅",
    "日本語のタイトル",
    "tabs\tand\nnewlines",
    "trailing dots...",
    "*asterisks* and _underscores_",
    12345,  # not a string at all
]

CONTENT_TYPES = [
    "text",
    "text",
    "text",
    "text",
    "multimodal_text",
    "code",
    "execution_output",
    "tether_browsing_display",
    "tether_quote",
    "system_error",
    # Something invented after the parser was written.
    "a_content_type_from_the_future",
]


def sentence(rng: random.Random, words: int = 12) -> str:
    return " ".join(rng.choice(WORDS) for _ in range(words)).capitalize() + "."


def content(rng: random.Random, kind: str) -> dict[str, Any]:
    if kind in {"code", "execution_output", "system_error"}:
        return {"content_type": kind, "text": sentence(rng)}

    if kind == "tether_browsing_display":
        return {"content_type": kind, "result": sentence(rng)}

    if kind == "tether_quote":
        return {"content_type": kind, "title": sentence(rng, 3), "text": sentence(rng)}

    if kind == "multimodal_text":
        return {
            "content_type": kind,
            "parts": [
                {
                    "content_type": "image_asset_pointer",
                    "asset_pointer": "file-service://file-abc123",
                },
                sentence(rng),
            ],
        }

    if kind == "a_content_type_from_the_future":
        # Parts, but shaped unfamiliarly. Should still import.
        return {"content_type": kind, "parts": [sentence(rng)], "extra": {"a": 1}}

    # Plain text, occasionally very long or oddly typed.
    roll = rng.random()
    if roll < 0.02:
        return {"content_type": "text", "parts": [sentence(rng, 4000)]}
    if roll < 0.04:
        return {"content_type": "text", "parts": [None, 42, sentence(rng)]}
    if roll < 0.06:
        return {"content_type": "text", "parts": []}
    return {"content_type": "text", "parts": [sentence(rng, rng.randint(4, 60))]}


def message(rng: random.Random, index: int, role: str, when: float | None) -> dict[str, Any]:
    return {
        "id": f"message-{index}",
        "author": {"role": role, "name": None, "metadata": {}},
        "create_time": when,
        "content": content(rng, rng.choice(CONTENT_TYPES)),
        "status": "finished_successfully",
        "metadata": {"model_slug": rng.choice(["gpt-4o", "gpt-4", "o1", "gpt-5"])},
        "recipient": "all",
    }


def conversation(rng: random.Random, number: int) -> dict[str, Any]:
    """One conversation, with a realistic branching mapping tree."""
    turns = rng.randint(1, 40)
    start: float | None = 1_600_000_000.0 + number * 3600

    mapping: dict[str, Any] = {
        "root": {"id": "root", "message": None, "parent": None, "children": []}
    }
    parent = "root"
    node_index = 0

    for turn in range(turns):
        role = "user" if turn % 2 == 0 else "assistant"
        node_id = f"node-{node_index}"
        node_index += 1

        when = None if rng.random() < 0.05 else (start + turn * 60 if start else None)

        mapping[parent]["children"].append(node_id)
        mapping[node_id] = {
            "id": node_id,
            "message": message(rng, node_index, role, when),
            "parent": parent,
            "children": [],
        }

        # Sometimes a message was edited or a reply regenerated: an abandoned
        # branch hangs off the same parent and must not be imported.
        if rng.random() < 0.15:
            dead_id = f"node-{node_index}-abandoned"
            node_index += 1
            mapping[parent]["children"].append(dead_id)
            mapping[dead_id] = {
                "id": dead_id,
                "message": message(rng, node_index, role, when),
                "parent": parent,
                "children": [],
            }

        parent = node_id

    # A few conversations are broken in ways real exports really are.
    roll = rng.random()
    current: Any = parent
    if roll < 0.02:
        current = "a-node-that-does-not-exist"
    elif roll < 0.03:
        current = None

    title = rng.choice(AWKWARD_TITLES) if rng.random() < 0.15 else sentence(rng, 4)

    result: dict[str, Any] = {
        "title": title,
        "create_time": None if rng.random() < 0.05 else start,
        "update_time": None if rng.random() < 0.1 else start,
        "mapping": mapping,
        "current_node": current,
        "conversation_id": f"conversation-{number}",
        "is_archived": rng.random() < 0.1,
        "default_model_slug": rng.choice(["gpt-4o", "gpt-4", "o1"]),
    }

    if rng.random() < 0.02:
        # Occasionally something entirely unparseable.
        result["mapping"] = "this should have been a dict"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a messy synthetic ChatGPT export for testing."
    )
    parser.add_argument("output", type=Path, help="where to write the .zip")
    parser.add_argument("--conversations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=1, help="for reproducibility")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    conversations = [conversation(rng, number) for number in range(args.conversations)]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "conversations.json", json.dumps(conversations, ensure_ascii=False)
        )
        archive.writestr("chat.html", "<html><body>synthetic</body></html>")
        archive.writestr("user.json", json.dumps({"id": "synthetic-user"}))

    size = args.output.stat().st_size
    print(
        f"Wrote {args.output} — {args.conversations} conversations, "
        f"{size / 1024 / 1024:.1f} MB"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
