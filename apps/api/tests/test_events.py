"""Tests for the in-process event bus."""

from __future__ import annotations

from mind_archive.events import Event, EventBus


def test_a_subscriber_receives_the_event() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe("conversation.created", received.append)

    bus.publish("conversation.created", {"id": "abc"})

    assert len(received) == 1
    assert received[0].name == "conversation.created"
    assert received[0].payload == {"id": "abc"}


def test_every_subscriber_is_called() -> None:
    bus = EventBus()
    calls: list[str] = []
    bus.subscribe("archive.imported", lambda event: calls.append("first"))
    bus.subscribe("archive.imported", lambda event: calls.append("second"))

    bus.publish("archive.imported")

    assert calls == ["first", "second"]


def test_publishing_with_no_subscribers_is_fine() -> None:
    bus = EventBus()

    event = bus.publish("nobody.listening")

    assert event.name == "nobody.listening"


def test_only_matching_subscribers_are_called() -> None:
    bus = EventBus()
    calls: list[str] = []
    bus.subscribe("sync.started", lambda event: calls.append("sync"))

    bus.publish("archive.imported")

    assert calls == []


def test_a_broken_handler_does_not_stop_the_others() -> None:
    """One bad subscriber must not break the operation that published."""
    bus = EventBus()
    calls: list[str] = []

    def explode(event: Event) -> None:
        raise RuntimeError("this handler is broken")

    bus.subscribe("document.indexed", explode)
    bus.subscribe("document.indexed", lambda event: calls.append("still ran"))

    bus.publish("document.indexed")

    assert calls == ["still ran"]


def test_unsubscribe_stops_delivery() -> None:
    bus = EventBus()
    calls: list[str] = []

    def handler(event: Event) -> None:
        calls.append(event.name)

    bus.subscribe("backup.completed", handler)
    bus.unsubscribe("backup.completed", handler)
    bus.publish("backup.completed")

    assert calls == []
    assert bus.handler_count("backup.completed") == 0


def test_unsubscribing_something_unknown_is_harmless() -> None:
    bus = EventBus()

    bus.unsubscribe("never.subscribed", lambda event: None)


def test_events_are_timestamped() -> None:
    bus = EventBus()

    event = bus.publish("search.indexed")

    assert event.occurred_at.tzinfo is not None
