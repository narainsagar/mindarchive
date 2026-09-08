"""Tests for the import endpoints."""

from __future__ import annotations

import zipfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from conftest import make_conversation, write_export
from mind_archive.config import Settings, get_settings
from mind_archive.main import app


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    """A client whose archive is a throwaway folder, not the real one."""
    settings = Settings(data_dir=tmp_path / "data")
    app.dependency_overrides[get_settings] = lambda: settings

    with TestClient(app) as test_client:
        test_client.archive_dir = settings.archive_dir  # type: ignore[attr-defined]
        yield test_client

    app.dependency_overrides.clear()


def upload(client: TestClient, path: Path):
    with path.open("rb") as handle:
        return client.post(
            "/api/import",
            files={"file": (path.name, handle, "application/zip")},
        )


# ---------------------------------------------------------------------------


def test_lists_the_supported_importers(client: TestClient) -> None:
    response = client.get("/api/importers")

    assert response.status_code == 200
    names = [importer["name"] for importer in response.json()]
    assert "chatgpt" in names


def test_importers_are_described_for_people(client: TestClient) -> None:
    body = client.get("/api/importers").json()

    assert body[0]["display_name"] == "ChatGPT"
    assert ".zip" in body[0]["supported_formats"]


def test_imports_an_export(client: TestClient, tmp_path: Path) -> None:
    export = write_export(
        tmp_path,
        [
            make_conversation(conversation_id="one"),
            make_conversation(conversation_id="two"),
        ],
    )

    response = upload(client, export)

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["imported"] == 2
    assert body["source"] == "chatgpt"


def test_the_conversations_land_on_disk(client: TestClient, tmp_path: Path) -> None:
    export = write_export(tmp_path, [make_conversation()])

    upload(client, export)

    written = list(client.archive_dir.rglob("conversation.md"))  # type: ignore[attr-defined]
    assert len(written) == 1
    assert "sourdough" in written[0].read_text(encoding="utf-8")


def test_the_message_is_written_for_a_person(
    client: TestClient, tmp_path: Path
) -> None:
    export = write_export(tmp_path, [make_conversation()])

    message = upload(client, export).json()["message"]

    assert message == "Imported 1 conversation."


def test_an_unrecognised_file_is_explained(client: TestClient, tmp_path: Path) -> None:
    path = tmp_path / "holiday.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("beach.jpg", "not a photo")

    body = upload(client, path).json()

    assert body["ok"] is False
    assert "ChatGPT" in body["message"]
    assert "Settings" in body["message"]


def test_an_empty_file_is_rejected(client: TestClient, tmp_path: Path) -> None:
    path = tmp_path / "empty.zip"
    path.write_bytes(b"")

    response = upload(client, path)

    assert response.status_code == 400


def test_a_hostile_archive_is_refused(client: TestClient, tmp_path: Path) -> None:
    path = tmp_path / "slip.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("conversations.json", "[]")
        archive.writestr("../escaped.txt", "malicious")

    body = upload(client, path).json()

    assert body["ok"] is False
    assert "outside" in body["message"]
    assert not (tmp_path.parent / "escaped.txt").exists()


def test_broken_conversations_are_reported_not_hidden(
    client: TestClient, tmp_path: Path
) -> None:
    export = write_export(
        tmp_path,
        [make_conversation(), {"title": "Broken", "mapping": "not a dict"}],
    )

    body = upload(client, export).json()

    assert body["ok"] is True
    assert body["imported"] == 1
    assert body["skipped"] == 1
    assert body["problems"]


def test_an_export_with_nothing_readable_says_so(
    client: TestClient, tmp_path: Path
) -> None:
    export = write_export(tmp_path, [])

    body = upload(client, export).json()

    assert body["ok"] is False
    assert "No conversations" in body["message"]


def test_importing_twice_does_not_duplicate(client: TestClient, tmp_path: Path) -> None:
    export = write_export(tmp_path, [make_conversation()])

    upload(client, export)
    upload(client, export)

    written = list(client.archive_dir.rglob("conversation.md"))  # type: ignore[attr-defined]
    assert len(written) == 1


def test_the_response_says_where_the_archive_is(
    client: TestClient, tmp_path: Path
) -> None:
    export = write_export(tmp_path, [make_conversation()])

    body = upload(client, export).json()

    assert body["archive_location"]


def test_the_uploaded_file_is_not_kept(client: TestClient, tmp_path: Path) -> None:
    """The archive holds readable conversations, never the provider's zip."""
    export = write_export(tmp_path, [make_conversation()])

    upload(client, export)

    assert list(client.archive_dir.rglob("*.zip")) == []  # type: ignore[attr-defined]


def test_an_unwritable_archive_folder_is_explained(tmp_path: Path) -> None:
    """An unplugged drive or a permissions problem must not produce a 500."""
    blocked = tmp_path / "blocked"
    # A file where the archive folder should be: writing there cannot work.
    blocked.write_text("not a folder", encoding="utf-8")

    settings = Settings(data_dir=blocked)
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(app) as client:
            export = write_export(tmp_path, [make_conversation()])
            response = upload(client, export)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert "could not write" in body["message"].lower()
    assert "permission" in body["message"].lower()
