"""The archive's own model of a conversation.

Deliberately small, and deliberately not shaped like any provider's export.
Every importer normalises into these types, so the rest of the application never
learns what ChatGPT's JSON looks like.

Fields that a provider might not supply are optional. An importer that cannot
find a timestamp records ``None`` rather than inventing one — a wrong date is
worse than a missing one in an archive people will still be reading in ten
years.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    """One turn in a conversation."""

    role: str = Field(description="user, assistant, system or tool")
    text: str = Field(description="The message, as plain text or Markdown")
    created_at: datetime | None = None

    #: Where this came from, for anything the archive does not model directly:
    #: the model that produced it, a content type we passed through verbatim,
    #: an attachment reference. Kept as strings so it stays readable in JSON.
    metadata: dict[str, str] = Field(default_factory=dict)


#: A tag is a label, not a document.
MAX_TAG_LENGTH = 50

#: More than this on one conversation is a filing system, not a set of labels.
MAX_TAGS = 50


def clean_tags(tags: Sequence[object]) -> list[str]:
    """Tidy a list of tags into the form the archive stores.

    Takes `object`, not `str`, on purpose: tags arrive from `metadata.json` and
    from request bodies, and a file on someone's disk can contain anything at
    all. The type says what is actually accepted rather than what we hope for.

    Trimmed, internal whitespace collapsed, empties dropped, length and count
    capped, and duplicates removed **case-insensitively** — "Bread" and "bread"
    are the same label, and keeping both would split a person's own filing
    without them noticing. The first spelling wins, because that is the one
    they chose.
    """
    cleaned: list[str] = []
    seen: set[str] = set()

    for tag in tags:
        if not isinstance(tag, str):
            continue

        label = " ".join(tag.split())[:MAX_TAG_LENGTH].strip()
        if not label:
            continue

        key = label.casefold()
        if key in seen:
            continue

        seen.add(key)
        cleaned.append(label)

        if len(cleaned) >= MAX_TAGS:
            break

    return cleaned


class Conversation(BaseModel):
    """A single conversation, normalised."""

    title: str
    messages: list[Message]

    #: The provider this came from: "chatgpt", "claude", "gemini", ...
    source: str

    #: The provider's own identifier, kept so a re-import can recognise a
    #: conversation it has already seen.
    source_id: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    #: Labels the *user* applied. Never set by an importer — an export contains
    #: no tags, and an import must never remove one. See DECISIONS.md D-025.
    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, str] = Field(default_factory=dict)

    @property
    def message_count(self) -> int:
        return len(self.messages)
