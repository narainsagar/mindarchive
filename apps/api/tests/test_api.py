"""Tests for the HTTP API.

These check the contract the frontend depends on, and the privacy promises the
product makes.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mind_archive import __version__
from mind_archive.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_root_describes_the_application(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "Mind Archive"


def test_health_reports_ok(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__


def test_health_message_is_written_for_humans(client: TestClient) -> None:
    """The product rule: no jargon in anything a person reads."""
    message = client.get("/api/health").json()["message"]

    assert message == "Mind Archive is running."


def test_config_reports_where_the_archive_lives(client: TestClient) -> None:
    response = client.get("/api/config")

    assert response.status_code == 200
    body = response.json()
    assert body["archive_location"]
    assert body["database_location"]


def test_cloud_is_disabled_by_default(client: TestClient) -> None:
    """Decision D-011. If this test ever fails, something is badly wrong."""
    body = client.get("/api/config").json()

    assert body["cloud_enabled"] is False
    assert body["storage_mode"] == "local"


def test_config_tells_the_user_nothing_is_uploaded(client: TestClient) -> None:
    body = client.get("/api/config").json()

    assert "only on this computer" in body["privacy_note"]


def test_config_exposes_no_secrets(client: TestClient) -> None:
    """The config response goes straight to the browser.

    This guards against someone adding a sensitive field later without
    thinking about where the response ends up.
    """
    body = client.get("/api/config").json()

    allowed = {
        "version",
        "storage_mode",
        "cloud_enabled",
        "archive_location",
        "database_location",
        "privacy_note",
    }
    assert set(body) == allowed

    serialised = str(body).lower()
    for forbidden in ("password", "secret", "token", "api_key", "apikey"):
        assert forbidden not in serialised


def test_unknown_route_is_a_clean_404(client: TestClient) -> None:
    assert client.get("/api/does-not-exist").status_code == 404
