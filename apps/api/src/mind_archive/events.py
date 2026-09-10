"""A small in-process event bus.

Mind Archive is event-driven by design, but a personal, single-user, local
application does not need a message broker. This is a synchronous
publish/subscribe helper — about fifty lines — that gives later milestones a
real extension point to build on.

If a genuine requirement ever appears for durability, ordering guarantees or
cross-process delivery, replace the transport behind this interface and record
the decision. Do not add infrastructure before the requirement.

See project-memory/DECISIONS.md D-009.

Event names are ``noun.verb``:

    archive.imported        conversation.created    conversation.updated
    document.created        document.indexed        search.indexed
    backup.requested        backup.completed
    sync.started            sync.completed          sync.failed

Usage::

    bus = EventBus()
    bus.subscribe("conversation.created", lambda event: print(event.name))
    bus.publish("conversation.created", {"id": "abc"})
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Event:
    """Something that happened.

    ``payload`` carries identifiers and counts — never conversation content.
    Events end up in logs, and logs must not contain the user's private
    material. See docs/SECURITY.md.
    """

    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


Handler = Callable[[Event], None]


class EventBus:
    """Synchronous in-process publish/subscribe."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Handler) -> None:
        """Call ``handler`` whenever ``event_name`` is published."""
        self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: Handler) -> None:
        """Stop calling ``handler``. Silently ignores an unknown handler."""
        if handler in self._handlers.get(event_name, []):
            self._handlers[event_name].remove(handler)

    def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> Event:
        """Publish an event and return it.

        A handler that raises is logged and skipped: one broken subscriber must
        not take down the operation that published the event, nor prevent the
        other subscribers from running.
        """
        event = Event(name=event_name, payload=payload or {})

        for handler in list(self._handlers.get(event_name, [])):
            try:
                handler(event)
            except Exception:
                logger.exception("Event handler failed for %s; continuing.", event_name)

        return event

    def handler_count(self, event_name: str) -> int:
        """How many handlers are subscribed. Useful in tests."""
        return len(self._handlers.get(event_name, []))


# The application-wide bus. Import this rather than constructing another one.
events = EventBus()
