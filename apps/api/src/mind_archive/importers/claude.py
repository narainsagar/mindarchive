"""Import a Claude export.

Get one from Claude: **Settings → Privacy → Export Data**. Anthropic emails a
link to a zip containing `conversations.json`. As with ChatGPT, **the download
link expires after 24 hours**.

## How it differs from ChatGPT

This is the importer that justified the adapter interface, because almost
nothing about the two formats is the same:

| | ChatGPT | Claude |
|---|---|---|
| Messages | a `mapping` tree plus `current_node` | a flat `chat_messages` list |
| Title | `title` | `name` |
| Identifier | `conversation_id` | `uuid` |
| Timestamps | Unix epoch floats | ISO 8601 strings |
| Speaker | `author.role`, `"user"` | `sender`, `"human"` |
| Text | `content.parts[]` | `text`, plus `content[]` blocks |

The flat list is a mercy after ChatGPT's branching tree: Claude's export is
already in the order the conversation happened.

```json
[
  {
    "uuid": "abc-123",
    "name": "Making bread",
    "created_at": "2024-03-14T09:30:00.000000Z",
    "chat_messages": [
      {
        "uuid": "msg-1",
        "sender": "human",
        "text": "How do I make a starter?",
        "created_at": "2024-03-14T09:30:00.000000Z",
        "content": [{"type": "text", "text": "How do I make a starter?"}]
      }
    ]
  }
]
```

Both `text` and `content[]` carry the message. `content[]` is the richer of the
two — it is where images, documents and thinking blocks appear — so it is
preferred, with `text` as the fallback.

**Nothing here is trusted.** Same as every importer: every field is checked
before use, and one unreadable conversation is skipped and reported rather than
failing the import.

**Written from Anthropic's documented export and third-party parsers, not from
a real export.** The same caveat as the ChatGPT importer had at this stage:
`scripts/inspect_export.py` reports the structure of a real one safely, and this
should be checked against that when one is available.
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
    iso_to_time,
    load_json_member,
    peek_conversations,
)
from mind_archive.importers.zip_safety import UnsafeArchiveError
from mind_archive.models import Conversation, Message

CONVERSATIONS_FILE = "conversations.json"

#: A conversation with more messages than this is not something we will walk.
MAX_MESSAGES = 100_000

#: Claude's word for the person, mapped to ours.
ROLES = {"human": "user", "assistant": "assistant"}


def looks_like_claude(conversations: list[Any]) -> bool:
    """Does this list of conversations come from Claude rather than ChatGPT?

    Both providers ship a file called `conversations.json`, so the filename
    proves nothing. `chat_messages` is Claude's and `mapping` is ChatGPT's, and
    checking for both — rather than just one — means a format that grows a
    `chat_messages` key later cannot quietly be claimed by the wrong importer.
    """
    for raw in conversations[:20]:
        conversation = as_dict(raw)
        if not conversation:
            continue
        if "mapping" in conversation:
            return False
        if "chat_messages" in conversation:
            return True

    return False


def _extract_text(message: dict[str, Any]) -> str:
    """Pull readable text out of a message.

    `content[]` is preferred over `text`: it is the richer field, and it is
    where anything that is not plain prose shows up. Unknown block types are
    noted rather than dropped, so a format Anthropic adds later degrades to
    "imported, with a placeholder" instead of "silently lost".
    """
    pieces: list[str] = []

    for block in as_list(message.get("content")):
        item = as_dict(block)
        if not item:
            continue

        kind = as_text(item.get("type"))

        if kind == "text":
            text = as_text(item.get("text"))
            if text:
                pieces.append(text)
        elif kind == "thinking":
            thinking = as_text(item.get("thinking")) or as_text(item.get("text"))
            if thinking:
                pieces.append(f"> _Thinking:_ {thinking}")
        elif kind in {"image", "document"}:
            pieces.append(f"_[{kind} — not imported yet]_")
        elif kind in {"tool_use", "tool_result"}:
            pieces.append(f"_[{kind.replace('_', ' ')} — not imported yet]_")
        else:
            # A block type invented after this was written. Take any text it
            # has rather than losing the message.
            text = as_text(item.get("text"))
            pieces.append(text if text else f"_[{kind or 'unknown'}]_")

    if pieces:
        return "\n\n".join(pieces)

    return as_text(message.get("text"))


class ClaudeImporter:
    """Adapter for Claude exports."""

    name = "claude"
    display_name = "Claude"
    supported_formats = [".zip", ".json"]

    # -- Importer protocol --------------------------------------------------

    def detect(self, path: Path) -> bool:
        """Does this look like a Claude export? Never raises."""
        conversations = peek_conversations(path, CONVERSATIONS_FILE)
        if conversations is None:
            return False
        return looks_like_claude(conversations)

    def validate(self, path: Path) -> ValidationResult:
        try:
            payload = self._load(path)
        except (UnsafeArchiveError, ImportProblem) as error:
            return ValidationResult.invalid(str(error))

        if not isinstance(payload, list):
            return ValidationResult.invalid(
                "That file does not look like a Claude export — "
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
            except Exception as error:  # noqa: BLE001 - one entry, not the import
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
        return load_json_member(path, CONVERSATIONS_FILE, "a Claude")

    def _convert(self, raw: dict[str, Any]) -> Conversation | None:
        messages: list[Message] = []

        for entry in as_list(raw.get("chat_messages"))[:MAX_MESSAGES]:
            message = self._convert_message(as_dict(entry))
            if message is not None:
                messages.append(message)

        if not messages:
            return None

        metadata: dict[str, str] = {}
        model = as_text(raw.get("model"))
        if model:
            metadata["model"] = model

        return Conversation(
            title=as_text(raw.get("name")) or "Untitled conversation",
            messages=messages,
            source=self.name,
            source_id=as_text(raw.get("uuid")) or None,
            created_at=iso_to_time(raw.get("created_at")),
            updated_at=iso_to_time(raw.get("updated_at")),
            metadata=metadata,
        )

    def _convert_message(self, raw: dict[str, Any]) -> Message | None:
        if not raw:
            return None

        sender = as_text(raw.get("sender")).lower()
        role = ROLES.get(sender)
        if role is None:
            return None

        text = _extract_text(raw)
        if not text:
            return None

        return Message(
            role=role, text=text, created_at=iso_to_time(raw.get("created_at"))
        )
