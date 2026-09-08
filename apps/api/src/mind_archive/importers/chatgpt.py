"""Import a ChatGPT export.

Get one from ChatGPT: **Settings → Data controls → Export data**. The download
is a zip containing `conversations.json`, `chat.html`, `user.json` and any
images from your conversations. Only `conversations.json` is read.

## The shape of the file

`conversations.json` is a list of conversations. The awkward part is that
messages are **not** a list — they are a tree:

```
{
  "title": "Making bread",
  "create_time": 1699999999.123,
  "conversation_id": "abc-123",
  "current_node": "node-9",
  "mapping": {
    "node-1": {
      "message": null,             # the root carries no message
      "parent": null,
      "children": ["node-2"]
    },
    "node-2": {
      "message": {...},
      "parent": "node-1",
      "children": ["node-3", "node-7"]   # two children means a branch
    }
  }
}
```

The tree exists because editing a message or regenerating a reply creates a
branch rather than replacing anything. `current_node` points at the leaf of the
branch you would see if you opened the conversation in ChatGPT, so walking from
there up through `parent` and reversing gives the conversation as the person
last saw it.

Abandoned branches are deliberately not imported. They are drafts the person
moved on from, and including them would make the archive harder to read, not
more complete. This is worth revisiting if anyone actually wants them.

## Nothing here is trusted

Every field is checked before use. A real export has null titles, missing
timestamps, empty messages, tool output, images, and content types that did not
exist when this was written. It should import anyway, skipping what it cannot
read and saying so.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mind_archive.importers.base import ImportResult, ValidationResult
from mind_archive.importers.zip_safety import (
    UnsafeArchiveError,
    find_member,
    inspect,
    read_member,
)
from mind_archive.models import Conversation, Message

CONVERSATIONS_FILE = "conversations.json"

#: A single conversation with more nodes than this is not something we will
#: walk. Real conversations are in the hundreds; this is a guard against a
#: crafted file, not a real limit anyone will meet.
MAX_NODES_PER_CONVERSATION = 100_000

#: Roles we keep. Anything else is recorded in metadata and skipped.
KEPT_ROLES = {"user", "assistant", "tool"}


# ---------------------------------------------------------------------------
# Small helpers for reading untrusted JSON.
# Each returns a safe default rather than raising, so one odd field cannot
# take down an entire import.
# ---------------------------------------------------------------------------


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _as_time(value: Any) -> datetime | None:
    """Convert a ChatGPT epoch timestamp, or give up.

    A missing or nonsensical timestamp becomes `None`. An archive people will
    read in ten years is better with a gap than with a fabricated date.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=UTC)
    except (ValueError, OSError, OverflowError):
        return None


def _extract_text(content: dict[str, Any]) -> str:
    """Pull readable text out of a message's content block.

    ChatGPT uses several content types and adds more over time. Known ones are
    handled explicitly; anything unrecognised falls back to whatever looks like
    text, so a new content type degrades to "imported, possibly plainly" rather
    than "silently lost".
    """
    content_type = _as_text(content.get("content_type"))

    # Code, execution output and browsing results carry a "text" field.
    if content_type in {"code", "execution_output", "system_error"}:
        return _as_text(content.get("text"))

    if content_type == "tether_browsing_display":
        return _as_text(content.get("result")) or _as_text(content.get("text"))

    if content_type == "tether_quote":
        title = _as_text(content.get("title"))
        text = _as_text(content.get("text"))
        return f"> **{title}**\n>\n> {text}" if title and text else text

    # "text" and "multimodal_text" both use parts. Parts are usually strings,
    # but in multimodal messages they can be dicts describing an image.
    pieces: list[str] = []
    for part in _as_list(content.get("parts")):
        if isinstance(part, str):
            if part.strip():
                pieces.append(part.strip())
        elif isinstance(part, dict):
            placeholder = _describe_asset(part)
            if placeholder:
                pieces.append(placeholder)

    if pieces:
        return "\n\n".join(pieces)

    # Unknown content type with no parts: take a "text" field if there is one.
    return _as_text(content.get("text"))


def _describe_asset(part: dict[str, Any]) -> str:
    """Describe a non-text part in a way a person reading Markdown understands.

    Attachments themselves are not imported yet — that is a later milestone —
    so the archive records that something was there rather than pretending the
    message was empty.
    """
    pointer = _as_text(part.get("asset_pointer"))
    if not pointer:
        return ""

    kind = _as_text(part.get("content_type")) or "file"
    if "image" in kind or pointer.startswith(("file-service://", "sediment://")):
        return "_[image — not imported yet]_"
    return "_[attachment — not imported yet]_"


def _is_hidden(message: dict[str, Any], role: str) -> bool:
    """Should this message be left out of the readable conversation?

    ChatGPT hides its own system messages and some tool scaffolding. Importing
    them would make the archive noisier without making it more useful. A system
    message the *user* wrote — custom instructions — is kept.
    """
    metadata = _as_dict(message.get("metadata"))

    if metadata.get("is_visually_hidden_from_conversation") is True:
        return True

    if role == "system":
        return metadata.get("is_user_system_message") is not True

    return False


def _thread(mapping: dict[str, Any], current_node: str | None) -> list[dict[str, Any]]:
    """Walk from the current leaf back to the root, then reverse.

    Falls back to following first children from the root when `current_node` is
    missing or broken, and to every node in file order if the tree itself makes
    no sense. Something readable always comes out.
    """
    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()

    node_id = current_node if isinstance(current_node, str) else None

    while node_id and node_id in mapping and node_id not in seen:
        seen.add(node_id)
        node = _as_dict(mapping[node_id])
        nodes.append(node)

        parent = node.get("parent")
        node_id = parent if isinstance(parent, str) else None

        if len(nodes) > MAX_NODES_PER_CONVERSATION:
            break

    if nodes:
        nodes.reverse()
        return nodes

    # No usable current_node. Follow first children down from the root.
    roots = [
        node_key
        for node_key, node in mapping.items()
        if _as_dict(node).get("parent") is None
    ]
    if roots:
        node_id = roots[0]
        while node_id and node_id in mapping and node_id not in seen:
            seen.add(node_id)
            node = _as_dict(mapping[node_id])
            nodes.append(node)
            children = _as_list(node.get("children"))
            node_id = children[0] if children and isinstance(children[0], str) else None
            if len(nodes) > MAX_NODES_PER_CONVERSATION:
                break
        if nodes:
            return nodes

    # The tree is unusable. Take everything, in file order.
    return [
        _as_dict(node) for node in list(mapping.values())[:MAX_NODES_PER_CONVERSATION]
    ]


class ChatGPTImporter:
    """Adapter for ChatGPT and OpenAI exports."""

    name = "chatgpt"
    display_name = "ChatGPT"
    supported_formats = [".zip", ".json"]

    # -- Importer protocol --------------------------------------------------

    def detect(self, path: Path) -> bool:
        """Does this look like a ChatGPT export? Never raises."""
        try:
            if path.suffix.lower() == ".zip":
                with inspect(path) as archive:
                    return find_member(archive, CONVERSATIONS_FILE) is not None
            if path.suffix.lower() == ".json":
                return path.name.lower() == CONVERSATIONS_FILE
        except (UnsafeArchiveError, OSError):
            return False
        return False

    def validate(self, path: Path) -> ValidationResult:
        try:
            payload = self._load(path)
        except UnsafeArchiveError as error:
            return ValidationResult.invalid(str(error))
        except _ImportProblem as error:
            return ValidationResult.invalid(str(error))

        if not isinstance(payload, list):
            return ValidationResult.invalid(
                "That file does not look like a ChatGPT export — "
                "conversations.json should contain a list of conversations."
            )

        count = len(payload)
        if count == 0:
            return ValidationResult.valid("That export contains no conversations.", 0)

        return ValidationResult.valid(
            f"Found {count} {'conversation' if count == 1 else 'conversations'} "
            "ready to import.",
            count,
        )

    def parse(self, path: Path) -> ImportResult:
        result = ImportResult()

        try:
            payload = self._load(path)
        except (UnsafeArchiveError, _ImportProblem) as error:
            result.note_problem(str(error))
            return result

        if not isinstance(payload, list):
            result.note_problem(
                "conversations.json did not contain a list of conversations."
            )
            return result

        for index, raw in enumerate(payload):
            try:
                conversation = self._convert(_as_dict(raw))
            except Exception as error:  # noqa: BLE001 - one bad entry, not a failed import
                result.note_problem(
                    f"Conversation {index + 1} could not be read "
                    f"({type(error).__name__})."
                )
                continue

            if conversation is None:
                result.note_problem(
                    f"Conversation {index + 1} had no readable messages."
                )
                continue

            result.conversations.append(conversation)
            result.imported += 1

        return result

    # -- Internals ----------------------------------------------------------

    def _load(self, path: Path) -> Any:
        """Read and parse conversations.json from a zip or a bare JSON file."""
        if path.suffix.lower() == ".zip":
            with inspect(path) as archive:
                member = find_member(archive, CONVERSATIONS_FILE)
                if member is None:
                    raise _ImportProblem(
                        "That zip does not contain conversations.json, so it is "
                        "not a ChatGPT export."
                    )
                data = read_member(archive, member)
        else:
            try:
                data = path.read_bytes()
            except OSError as error:
                raise _ImportProblem("That file could not be read.") from error

        try:
            return json.loads(data.decode("utf-8"))
        except UnicodeDecodeError as error:
            raise _ImportProblem(
                "conversations.json is not valid UTF-8 text."
            ) from error
        except json.JSONDecodeError as error:
            raise _ImportProblem(
                f"conversations.json is not valid JSON (line {error.lineno})."
            ) from error

    def _convert(self, raw: dict[str, Any]) -> Conversation | None:
        """Turn one raw ChatGPT conversation into our own model."""
        mapping = _as_dict(raw.get("mapping"))
        current_node = raw.get("current_node")

        messages: list[Message] = []
        for node in _thread(
            mapping, current_node if isinstance(current_node, str) else None
        ):
            message = self._convert_message(_as_dict(node.get("message")))
            if message is not None:
                messages.append(message)

        if not messages:
            return None

        title = _as_text(raw.get("title")) or "Untitled conversation"

        source_id = _as_text(raw.get("conversation_id")) or _as_text(raw.get("id"))

        metadata: dict[str, str] = {}
        model = _as_text(raw.get("default_model_slug"))
        if model:
            metadata["model"] = model
        if raw.get("is_archived") is True:
            metadata["archived_in_chatgpt"] = "true"

        return Conversation(
            title=title,
            messages=messages,
            source=self.name,
            source_id=source_id or None,
            created_at=_as_time(raw.get("create_time")),
            updated_at=_as_time(raw.get("update_time")),
            metadata=metadata,
        )

    def _convert_message(self, raw: dict[str, Any]) -> Message | None:
        """Convert one message node, or return None to leave it out."""
        if not raw:
            return None

        role = _as_text(_as_dict(raw.get("author")).get("role"))
        if not role or _is_hidden(raw, role):
            return None

        if role == "system":
            # A user-written system message: custom instructions.
            role = "user"
        elif role not in KEPT_ROLES:
            return None

        text = _extract_text(_as_dict(raw.get("content")))
        if not text:
            return None

        metadata: dict[str, str] = {}
        model = _as_text(_as_dict(raw.get("metadata")).get("model_slug"))
        if model:
            metadata["model"] = model

        return Message(
            role=role,
            text=text,
            created_at=_as_time(raw.get("create_time")),
            metadata=metadata,
        )


class _ImportProblem(Exception):
    """Something in the file stopped the import, described for a person."""
