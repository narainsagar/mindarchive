"""Tests for settings.

Mostly about one thing: telling the user where their archive is in a way that
is true on *their* machine, not just inside a container.
"""

from __future__ import annotations

from pathlib import Path

from mind_archive.config import Settings


def test_the_real_path_is_shown_when_running_natively(tmp_path: Path) -> None:
    # Explicitly empty: this test runs inside the container during CI, where
    # MIND_ARCHIVE_DISPLAY_DATA_DIR is set, and we are testing the case where
    # it is not.
    settings = Settings(data_dir=tmp_path / "data", display_data_dir="")

    assert settings.archive_location == str(settings.archive_dir)


def test_the_host_path_is_shown_when_running_in_docker() -> None:
    """Inside a container the archive is at /data, but the user's folder is
    ./data. Sending someone to a path that does not exist on their own machine
    is worse than saying nothing.
    """
    settings = Settings(data_dir=Path("/data"), display_data_dir="./data")

    assert settings.archive_location == "./data/archive"


def test_the_writer_still_uses_the_real_path() -> None:
    """The display path is cosmetic. Files must go where they really belong."""
    settings = Settings(data_dir=Path("/data"), display_data_dir="./data")

    assert settings.archive_dir == Path("/data/archive")


def test_a_trailing_slash_does_not_double_up() -> None:
    settings = Settings(data_dir=Path("/data"), display_data_dir="./data/")

    assert settings.archive_location == "./data/archive"


def test_cloud_is_off_by_default() -> None:
    """D-011: cloud can never be enabled by accident."""
    settings = Settings()

    assert settings.cloud_enabled is False
    assert settings.storage_mode == "local"


def test_the_database_lives_beside_the_archive(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path / "data")

    assert settings.database_path.parent == settings.archive_dir.parent


def test_a_relative_data_dir_is_made_absolute() -> None:
    settings = Settings(data_dir=Path("some/where"))

    assert settings.data_dir.is_absolute()


def test_cors_origins_are_split_and_trimmed() -> None:
    settings = Settings(cors_origins="http://a.test , http://b.test ,")

    assert settings.cors_origin_list == ["http://a.test", "http://b.test"]
