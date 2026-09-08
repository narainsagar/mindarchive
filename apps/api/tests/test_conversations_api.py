"""Tests for browsing and reading conversations."""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mind_archive.archive import ArchiveWriter
from mind_archive.config import Settings, get_settings
from mind_archive.events import EventBus
from mind_archive.index import Indexer
from mind_archive.main import app
from mind_archive.models import Conversation, Message


def conversation(
    *,
    title: str = "Making sourdough bread",
    source_id: str = "conversation-1",
    created: datetime | None = datetime(2024, 3, 14, 9, 30, tzinfo=UTC),
) -> Conversation:
    return Conversation(
        title=title,
        source="chatgpt",
        source_id=source_id,
        created_at=created,
        messages=[
            Message(role="user", text="How do I make a sourdough starter?"),
            Message(role="assistant", text="Mix flour and water, then wait."),
        ],
    )


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    settings = Settings(data_dir=tmp_path / "data")
    settings.ensure_directories()

    writer = ArchiveWriter(settings.archive_dir, bus=EventBus())
    writer.write(conversation(source_id="one"))
    writer.write(
        Conversation(
            title="Growing tomatoes",
            source="chatgpt",
            source_id="two",
            created_at=datetime(2024, 5, 2, tzinfo=UTC),
            messages=[
                Message(role="user", text="When do I plant seedlings?"),
                Message(role="assistant", text="After the last frost."),
            ],
        )
    )
    Indexer(settings.archive_dir, settings.database_path).rebuild()

    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        test_client.settings = settings  # type: ignore[attr-defined]
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Listing and searching
# ---------------------------------------------------------------------------


def test_lists_conversations(client: TestClient) -> None:
    body = client.get("/api/conversations").json()

    assert body["total"] == 2
    assert len(body["conversations"]) == 2


def test_a_listed_conversation_is_described(client: TestClient) -> None:
    first = client.get("/api/conversations").json()["conversations"][0]

    assert first["title"]
    assert first["source"] == "chatgpt"
    assert first["message_count"] == 2
    assert first["path"]


def test_searches_conversations(client: TestClient) -> None:
    body = client.get("/api/conversations", params={"q": "tomatoes"}).json()

    assert body["total"] == 1
    assert body["conversations"][0]["title"] == "Growing tomatoes"


def test_a_search_result_carries_a_snippet(client: TestClient) -> None:
    body = client.get("/api/conversations", params={"q": "starter"}).json()

    assert "<<" in body["conversations"][0]["snippet"]


def test_a_search_with_no_matches_is_not_an_error(client: TestClient) -> None:
    response = client.get("/api/conversations", params={"q": "kangaroo"})

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_awkward_search_input_is_not_an_error(client: TestClient) -> None:
    response = client.get("/api/conversations", params={"q": 'C++ NEAR( "'})

    assert response.status_code == 200


def test_results_can_be_paginated(client: TestClient) -> None:
    body = client.get("/api/conversations", params={"limit": 1, "offset": 1}).json()

    assert body["total"] == 2
    assert len(body["conversations"]) == 1
    assert body["offset"] == 1


def test_an_absurd_limit_is_rejected(client: TestClient) -> None:
    assert client.get("/api/conversations", params={"limit": 10_000}).status_code == 422


def test_the_list_reports_where_conversations_came_from(client: TestClient) -> None:
    assert client.get("/api/conversations").json()["sources"] == {"chatgpt": 2}


# ---------------------------------------------------------------------------
# Reading one
# ---------------------------------------------------------------------------


def test_reads_a_conversation(client: TestClient) -> None:
    path = client.get("/api/conversations").json()["conversations"][0]["path"]

    body = client.get(f"/api/conversations/{path}").json()

    assert body["title"]
    assert "sourdough" in body["body"].lower() or "tomato" in body["title"].lower()


def test_the_body_is_markdown_without_front_matter(client: TestClient) -> None:
    path = client.get("/api/conversations").json()["conversations"][0]["path"]

    body = client.get(f"/api/conversations/{path}").json()["body"]

    assert not body.startswith("---")
    assert "## You" in body


def test_the_api_never_returns_html(client: TestClient) -> None:
    """Rendering is the interface's job. The API returns Markdown."""
    path = client.get("/api/conversations").json()["conversations"][0]["path"]

    body = client.get(f"/api/conversations/{path}").json()["body"]

    assert "<p>" not in body
    assert "<h1>" not in body


def test_an_unknown_conversation_is_a_404(client: TestClient) -> None:
    assert client.get("/api/conversations/chatgpt/nope").status_code == 404


def test_a_hand_edited_conversation_is_read_from_disk(client: TestClient) -> None:
    """The files are the source of truth, so an edit shows without re-indexing."""
    path = client.get("/api/conversations").json()["conversations"][0]["path"]
    folder = client.settings.archive_dir / path  # type: ignore[attr-defined]
    folder.joinpath("conversation.md").write_text(
        "---\ntitle: x\n---\n\nEdited by hand.", encoding="utf-8"
    )

    body = client.get(f"/api/conversations/{path}").json()["body"]

    assert body == "Edited by hand."


# ---------------------------------------------------------------------------
# The path in the URL is untrusted
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hostile",
    [
        "../../../etc/passwd",
        "chatgpt/../../../etc/passwd",
        "....//....//etc/passwd",
        "chatgpt/../../.env",
    ],
)
def test_a_path_cannot_escape_the_archive(client: TestClient, hostile: str) -> None:
    response = client.get(f"/api/conversations/{hostile}")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_escaping_reveals_nothing_about_the_filesystem(client: TestClient) -> None:
    """A refusal must not describe the filesystem it refused to touch.

    Note that a client normalises `../` out of a URL before it is sent, so the
    handler often never sees the traversal at all — it 404s at the router. Both
    routes to a 404 are checked, and neither may leak a path.
    """
    for url in (
        "/api/conversations/../../../etc/passwd",
        "/api/conversations/chatgpt/../../../etc/passwd",
        "/api/conversations/chatgpt/not-here",
    ):
        response = client.get(url)

        assert response.status_code == 404
        body = response.text
        assert "/etc" not in body
        assert "archive" not in body.lower()
        assert "Traceback" not in body


# ---------------------------------------------------------------------------
# Rebuilding
# ---------------------------------------------------------------------------


def test_the_index_can_be_rebuilt(client: TestClient) -> None:
    body = client.post("/api/index/rebuild").json()

    assert body["ok"] is True
    assert body["indexed"] == 2
    assert "2 conversations" in body["message"]


def test_rebuilding_recovers_a_deleted_database(client: TestClient) -> None:
    client.settings.database_path.unlink()  # type: ignore[attr-defined]

    client.post("/api/index/rebuild")

    assert client.get("/api/conversations").json()["total"] == 2


# ---------------------------------------------------------------------------
# Importing and browsing together
# ---------------------------------------------------------------------------


def test_an_imported_conversation_becomes_searchable(tmp_path: Path) -> None:
    """The event bus keeps the index in step with imports (D-009)."""
    from conftest import make_conversation, write_export

    settings = Settings(data_dir=tmp_path / "data")
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(app) as test_client:
            export = write_export(tmp_path, [make_conversation()])
            with export.open("rb") as handle:
                test_client.post(
                    "/api/import",
                    files={"file": (export.name, handle, "application/zip")},
                )

            found = test_client.get(
                "/api/conversations", params={"q": "sourdough"}
            ).json()
    finally:
        app.dependency_overrides.clear()

    assert found["total"] == 1


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


def first_path(client: TestClient) -> str:
    return client.get("/api/conversations").json()["conversations"][0]["path"]


def test_tags_can_be_set(client: TestClient) -> None:
    path = first_path(client)

    body = client.put(
        f"/api/conversations/{path}/tags", json={"tags": ["recipes", "bread"]}
    ).json()

    assert body["tags"] == ["recipes", "bread"]


def test_tags_are_written_to_disk_not_just_the_index(client: TestClient) -> None:
    """D-025: tags are the one thing here a person made rather than imported."""
    path = first_path(client)
    client.put(f"/api/conversations/{path}/tags", json={"tags": ["recipes"]})

    folder = client.settings.archive_dir / path  # type: ignore[attr-defined]
    stored = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))

    assert stored["tags"] == ["recipes"]


def test_tags_appear_when_reading_a_conversation(client: TestClient) -> None:
    path = first_path(client)
    client.put(f"/api/conversations/{path}/tags", json={"tags": ["recipes"]})

    assert client.get(f"/api/conversations/{path}").json()["tags"] == ["recipes"]


def test_conversations_can_be_filtered_by_tag(client: TestClient) -> None:
    path = first_path(client)
    client.put(f"/api/conversations/{path}/tags", json={"tags": ["recipes"]})

    body = client.get("/api/conversations", params={"tag": "recipes"}).json()

    assert body["total"] == 1
    assert body["conversations"][0]["path"] == path


def test_the_listing_reports_every_tag_in_use(client: TestClient) -> None:
    path = first_path(client)
    client.put(f"/api/conversations/{path}/tags", json={"tags": ["recipes", "bread"]})

    assert client.get("/api/conversations").json()["tags"] == {
        "bread": 1,
        "recipes": 1,
    }


def test_tags_are_tidied_before_being_stored(client: TestClient) -> None:
    path = first_path(client)

    body = client.put(
        f"/api/conversations/{path}/tags",
        json={"tags": ["  Recipes  ", "recipes", "", "   "]},
    ).json()

    assert body["tags"] == ["Recipes"]


def test_tags_can_be_cleared(client: TestClient) -> None:
    path = first_path(client)
    client.put(f"/api/conversations/{path}/tags", json={"tags": ["recipes"]})

    assert (
        client.put(f"/api/conversations/{path}/tags", json={"tags": []}).json()["tags"]
        == []
    )


def test_tagging_an_unknown_conversation_is_a_404(client: TestClient) -> None:
    response = client.put(
        "/api/conversations/chatgpt/nope/tags", json={"tags": ["recipes"]}
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "hostile",
    ["../../../etc/passwd", "chatgpt/../../../etc/passwd"],
)
def test_tagging_cannot_escape_the_archive(client: TestClient, hostile: str) -> None:
    response = client.put(
        f"/api/conversations/{hostile}/tags", json={"tags": ["recipes"]}
    )

    assert response.status_code == 404
    assert "/etc" not in response.text
