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

from pathlib import Path
from typing import Any

from mind_archive.importers.base import ImportResult, ValidationResult
from mind_archive.importers.reading import (
    ImportProblem,
    as_dict,
    as_list,
    as_text,
    epoch_to_time,
    has_member,
    load_json_member,
    peek_conversations,
)
from mind_archive.importers.zip_safety import UnsafeArchiveError
from mind_archive.models import Conversation, Message

CONVERSATIONS_FILE = "conversations.json"

#: A single conversation with more nodes than this is not something we will
#: walk. Real conversations are in the hundreds; this is a guard against a
#: crafted file, not a real limit anyone will meet.
MAX_NODES_PER_CONVERSATION = 100_000

#: Roles we keep. Anything else is recorded in metadata and skipped.
KEPT_ROLES = {"user", "assistant", "tool"}


def looks_like_chatgpt(conversations: list[Any]) -> bool:
    """Does this list of conversations come from ChatGPT rather than Claude?

    Both providers ship a file called `conversations.json`, so matching on the
    filename alone claims the other provider's export. Before this existed, the
    ChatGPT importer would confidently accept a Claude export and then find
    nothing in it. `mapping` is ChatGPT's shape; `chat_messages` is Claude's.

    **ChatGPT is the fallback when the shape says nothing** — an empty export,
    or one whose conversations carry neither key. It is the primary target, and
    more importantly its validation messages are specific ("that export contains
    no conversations", "not valid JSON on line 4"). Refusing to claim an
    ambiguous file would replace all of those with "not recognised", which tells
    the user nothing about a file that is very nearly right.
    """
    for raw in conversations[:20]:
        conversation = as_dict(raw)
        if not conversation:
            continue
        if "chat_messages" in conversation:
            return False
        if "mapping" in conversation:
            return True

    return True


def _extract_text(content: dict[str, Any]) -> str:
    """Pull readable text out of a message's content block.

    ChatGPT uses several content types and adds more over time. Known ones are
    handled explicitly; anything unrecognised falls back to whatever looks like
    text, so a new content type degrades to "imported, possibly plainly" rather
    than "silently lost".
    """
    content_type = as_text(content.get("content_type"))

    # Code, execution output and browsing results carry a "text" field.
    if content_type in {"code", "execution_output", "system_error"}:
        return as_text(content.get("text"))

    if content_type == "tether_browsing_display":
        return as_text(content.get("result")) or as_text(content.get("text"))

    if content_type == "tether_quote":
        title = as_text(content.get("title"))
        text = as_text(content.get("text"))
        return f"> **{title}**\n>\n> {text}" if title and text else text

    # "text" and "multimodal_text" both use parts. Parts are usually strings,
    # but in multimodal messages they can be dicts describing an image.
    pieces: list[str] = []
    for part in as_list(content.get("parts")):
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
    return as_text(content.get("text"))


def _describe_asset(part: dict[str, Any]) -> str:
    """Describe a non-text part in a way a person reading Markdown understands.

    Attachments themselves are not imported yet — that is a later milestone —
    so the archive records that something was there rather than pretending the
    message was empty.
    """
    pointer = as_text(part.get("asset_pointer"))
    if not pointer:
        return ""

    kind = as_text(part.get("content_type")) or "file"
    if "image" in kind or pointer.startswith(("file-service://", "sediment://")):
        return "_[image — not imported yet]_"
    return "_[attachment — not imported yet]_"


def _is_hidden(message: dict[str, Any], role: str) -> bool:
    """Should this message be left out of the readable conversation?

    ChatGPT hides its own system messages and some tool scaffolding. Importing
    them would make the archive noisier without making it more useful. A system
    message the *user* wrote — custom instructions — is kept.
    """
    metadata = as_dict(message.get("metadata"))

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
        node = as_dict(mapping[node_id])
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
        if as_dict(node).get("parent") is None
    ]
    if roots:
        node_id = roots[0]
        while node_id and node_id in mapping and node_id not in seen:
            seen.add(node_id)
            node = as_dict(mapping[node_id])
            nodes.append(node)
            children = as_list(node.get("children"))
            node_id = children[0] if children and isinstance(children[0], str) else None
            if len(nodes) > MAX_NODES_PER_CONVERSATION:
                break
        if nodes:
            return nodes

    # The tree is unusable. Take everything, in file order.
    return [
        as_dict(node) for node in list(mapping.values())[:MAX_NODES_PER_CONVERSATION]
    ]


class ChatGPTImporter:
    """Adapter for ChatGPT and OpenAI exports."""

    name = "chatgpt"
    display_name = "ChatGPT"
    supported_formats = [".zip", ".json"]

    # -- Importer protocol --------------------------------------------------

    def detect(self, path: Path) -> bool:
        """Does this look like a ChatGPT export? Never raises."""
        conversations = peek_conversations(path, CONVERSATIONS_FILE)
        if conversations is None:
            # Either not our kind of file, or ours and unreadable. Claim the
            # second so `validate` can say what is actually wrong with it.
            return has_member(path, CONVERSATIONS_FILE)
        return looks_like_chatgpt(conversations)

    def validate(self, path: Path) -> ValidationResult:
        try:
            payload = self._load(path)
        except (UnsafeArchiveError, ImportProblem) as error:
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
        except (UnsafeArchiveError, ImportProblem) as error:
            result.note_problem(str(error))
            return result

        if not isinstance(payload, list):
            result.note_problem(
                "conversations.json did not contain a list of conversations."
            )
            return result

        for index, raw in enumerate(payload):
            try:
                conversation = self._convert(as_dict(raw))
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
        return load_json_member(path, CONVERSATIONS_FILE, "a ChatGPT")

    def _convert(self, raw: dict[str, Any]) -> Conversation | None:
        """Turn one raw ChatGPT conversation into our own model."""
        mapping = as_dict(raw.get("mapping"))
        current_node = raw.get("current_node")

        messages: list[Message] = []
        for node in _thread(
            mapping, current_node if isinstance(current_node, str) else None
        ):
            message = self._convert_message(as_dict(node.get("message")))
            if message is not None:
                messages.append(message)

        if not messages:
            return None

        title = as_text(raw.get("title")) or "Untitled conversation"

        source_id = as_text(raw.get("conversation_id")) or as_text(raw.get("id"))

        metadata: dict[str, str] = {}
        model = as_text(raw.get("default_model_slug"))
        if model:
            metadata["model"] = model
        if raw.get("is_archived") is True:
            metadata["archived_in_chatgpt"] = "true"

        return Conversation(
            title=title,
            messages=messages,
            source=self.name,
            source_id=source_id or None,
            created_at=epoch_to_time(raw.get("create_time")),
            updated_at=epoch_to_time(raw.get("update_time")),
            metadata=metadata,
        )

    def _convert_message(self, raw: dict[str, Any]) -> Message | None:
        """Convert one message node, or return None to leave it out."""
        if not raw:
            return None

        role = as_text(as_dict(raw.get("author")).get("role"))
        if not role or _is_hidden(raw, role):
            return None

        if role == "system":
            # A user-written system message: custom instructions.
            role = "user"
        elif role not in KEPT_ROLES:
            return None

        text = _extract_text(as_dict(raw.get("content")))
        if not text:
            return None

        metadata: dict[str, str] = {}
        model = as_text(as_dict(raw.get("metadata")).get("model_slug"))
        if model:
            metadata["model"] = model

        return Message(
            role=role,
            text=text,
            created_at=epoch_to_time(raw.get("create_time")),
            metadata=metadata,
        )
