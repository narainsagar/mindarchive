#!/usr/bin/env python3
"""Describe the *shape* of a provider export, without revealing its contents.

    python scripts/inspect_export.py local/chatgpt-export.zip

Mind Archive's importer has to survive real exports, which are far messier than
anything anyone writes by hand. But a real export is somebody's private
conversations, so it cannot be shared to find out how it is shaped.

This script closes that gap. It reports **structure only** — how many
conversations, which content types appear, how deep the branch trees go, which
fields are null, which keys exist that we do not handle. It never prints a
title, a message, a snippet, or any value that came from a conversation.

**The output is safe to paste into a chat or an issue.** That is the entire
point: it lets the parser be hardened against real data without anyone reading
your conversations.

If you would rather check that for yourself before sharing anything — and you
should — read this file. It is short, and the rule is simple: only counts,
lengths, booleans, and key names appear anywhere in the output.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

# Keys we know about. Anything else is reported by name so a format change is
# noticed rather than silently ignored. Key names are structure, not content.
KNOWN_CONVERSATION_KEYS = {
    "title", "create_time", "update_time", "mapping", "current_node",
    "conversation_id", "id", "is_archived", "default_model_slug",
    "moderation_results", "plugin_ids", "conversation_template_id", "gizmo_id",
    "safe_urls", "async_status", "is_starred", "memory_scope",
    "blocked_urls", "conversation_origin", "voice", "sugar_item_id",
}

KNOWN_MESSAGE_KEYS = {
    "id", "author", "create_time", "update_time", "content", "status",
    "end_turn", "weight", "metadata", "recipient", "channel",
}


def load(path: Path) -> Any:
    """Read conversations.json out of a zip, or straight off disk."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            members = archive.namelist()
            names = [
                name for name in members if Path(name).name == "conversations.json"
            ]
            if not names:
                raise SystemExit("No conversations.json inside that zip.")

            # Extensions and counts, never filenames. A ChatGPT export names
            # attachments after what they are — "file-abc-passport-scan.png" —
            # so listing filenames would leak exactly what this script exists
            # to protect.
            kinds: Counter[str] = Counter(
                Path(name).suffix.lower() or "<no extension>"
                for name in members
                if not name.endswith("/")
            )
            print(f"Archive contains {len(members)} entries:")
            for suffix, count in kinds.most_common():
                print(f"  {count:>8}  {suffix}")

            member = min(names, key=lambda name: name.count("/"))
            with archive.open(member) as handle:
                return json.load(handle)

    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def thread_depth(mapping: dict[str, Any], current: Any) -> int:
    """How many nodes from the current leaf back to the root."""
    depth = 0
    seen: set[str] = set()
    node_id = current if isinstance(current, str) else None

    while node_id and node_id in mapping and node_id not in seen:
        seen.add(node_id)
        depth += 1
        parent = mapping[node_id].get("parent") if isinstance(mapping[node_id], dict) else None
        node_id = parent if isinstance(parent, str) else None

    return depth


def inspect(conversations: list[Any]) -> None:
    content_types: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    recipients: Counter[str] = Counter()
    models: Counter[str] = Counter()
    part_types: Counter[str] = Counter()
    unknown_conversation_keys: Counter[str] = Counter()
    unknown_message_keys: Counter[str] = Counter()
    metadata_keys: Counter[str] = Counter()

    null_titles = empty_titles = 0
    null_create = null_update = 0
    missing_mapping = missing_current = broken_current = 0
    not_a_dict = 0
    archived = 0

    node_counts: list[int] = []
    thread_lengths: list[int] = []
    branching = 0
    total_branch_points = 0
    message_lengths: list[int] = []
    title_lengths: list[int] = []

    for raw in conversations:
        if not isinstance(raw, dict):
            not_a_dict += 1
            continue

        for key in raw:
            if key not in KNOWN_CONVERSATION_KEYS:
                unknown_conversation_keys[key] += 1

        title = raw.get("title")
        if title is None:
            null_titles += 1
        elif isinstance(title, str):
            if not title.strip():
                empty_titles += 1
            title_lengths.append(len(title))

        if raw.get("create_time") is None:
            null_create += 1
        if raw.get("update_time") is None:
            null_update += 1
        if raw.get("is_archived") is True:
            archived += 1

        model = raw.get("default_model_slug")
        if isinstance(model, str):
            models[model] += 1

        mapping = raw.get("mapping")
        if not isinstance(mapping, dict):
            missing_mapping += 1
            continue

        node_counts.append(len(mapping))

        current = raw.get("current_node")
        if not isinstance(current, str):
            missing_current += 1
        elif current not in mapping:
            broken_current += 1

        depth = thread_depth(mapping, current)
        if depth:
            thread_lengths.append(depth)

        has_branch = False
        for node in mapping.values():
            if not isinstance(node, dict):
                continue

            children = node.get("children")
            if isinstance(children, list) and len(children) > 1:
                has_branch = True
                total_branch_points += 1

            message = node.get("message")
            if not isinstance(message, dict):
                continue

            for key in message:
                if key not in KNOWN_MESSAGE_KEYS:
                    unknown_message_keys[key] += 1

            author = message.get("author")
            role = author.get("role") if isinstance(author, dict) else None
            roles[str(role)] += 1

            recipient = message.get("recipient")
            if isinstance(recipient, str):
                recipients[recipient] += 1

            metadata = message.get("metadata")
            if isinstance(metadata, dict):
                for key in metadata:
                    metadata_keys[key] += 1

            content = message.get("content")
            if not isinstance(content, dict):
                content_types["<not a dict>"] += 1
                continue

            content_types[str(content.get("content_type"))] += 1

            parts = content.get("parts")
            if isinstance(parts, list):
                for part in parts:
                    if isinstance(part, str):
                        part_types["str"] += 1
                        message_lengths.append(len(part))
                    elif isinstance(part, dict):
                        kind = part.get("content_type")
                        part_types[f"dict:{kind}"] += 1
                    else:
                        part_types[type(part).__name__] += 1

        if has_branch:
            branching += 1

    report(
        total=len(conversations),
        not_a_dict=not_a_dict,
        null_titles=null_titles,
        empty_titles=empty_titles,
        null_create=null_create,
        null_update=null_update,
        archived=archived,
        missing_mapping=missing_mapping,
        missing_current=missing_current,
        broken_current=broken_current,
        branching=branching,
        total_branch_points=total_branch_points,
        node_counts=node_counts,
        thread_lengths=thread_lengths,
        message_lengths=message_lengths,
        title_lengths=title_lengths,
        content_types=content_types,
        roles=roles,
        recipients=recipients,
        models=models,
        part_types=part_types,
        unknown_conversation_keys=unknown_conversation_keys,
        unknown_message_keys=unknown_message_keys,
        metadata_keys=metadata_keys,
    )


def stats(values: list[int]) -> str:
    if not values:
        return "none"
    ordered = sorted(values)
    return (
        f"min {ordered[0]}, median {ordered[len(ordered) // 2]}, "
        f"max {ordered[-1]}, total {sum(ordered)}"
    )


def show(title: str, counter: Counter[str], limit: int = 25) -> None:
    print(f"\n{title}")
    if not counter:
        print("  none")
        return
    for name, count in counter.most_common(limit):
        print(f"  {count:>8}  {name}")
    if len(counter) > limit:
        print(f"  ... and {len(counter) - limit} more")


def report(**data: Any) -> None:
    print("\n" + "=" * 66)
    print("STRUCTURE ONLY — no conversation content appears below")
    print("=" * 66)

    print(f"\nConversations: {data['total']}")
    print(f"  not an object:            {data['not_a_dict']}")
    print(f"  null title:               {data['null_titles']}")
    print(f"  empty title:              {data['empty_titles']}")
    print(f"  no create_time:           {data['null_create']}")
    print(f"  no update_time:           {data['null_update']}")
    print(f"  archived in ChatGPT:      {data['archived']}")
    print(f"  mapping missing/not dict: {data['missing_mapping']}")
    print(f"  current_node missing:     {data['missing_current']}")
    print(f"  current_node not in map:  {data['broken_current']}")
    print(f"  contain a branch:         {data['branching']}")
    print(f"  branch points in total:   {data['total_branch_points']}")

    print(f"\nNodes per conversation:    {stats(data['node_counts'])}")
    print(f"Thread length (current):   {stats(data['thread_lengths'])}")
    print(f"Message length in chars:   {stats(data['message_lengths'])}")
    print(f"Title length in chars:     {stats(data['title_lengths'])}")

    show("Content types", data["content_types"])
    show("Author roles", data["roles"])
    show("Recipients", data["recipients"])
    show("Part types", data["part_types"])
    show("Models", data["models"])
    show("Message metadata keys", data["metadata_keys"], limit=40)
    show("UNKNOWN conversation keys", data["unknown_conversation_keys"])
    show("UNKNOWN message keys", data["unknown_message_keys"])

    print("\n" + "=" * 66)
    print("Safe to share: counts, lengths and key names only.")
    print("=" * 66 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report the structure of a provider export, never its content.",
    )
    parser.add_argument("export", type=Path, help="an export .zip or conversations.json")
    args = parser.parse_args()

    if not args.export.exists():
        print(f"No such file: {args.export}", file=sys.stderr)
        return 1

    data = load(args.export)
    if not isinstance(data, list):
        print(
            f"Expected a list of conversations, found {type(data).__name__}.",
            file=sys.stderr,
        )
        return 1

    inspect(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
