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

    metadata: dict[str, str] = Field(default_factory=dict)

    @property
    def message_count(self) -> int:
        return len(self.messages)
