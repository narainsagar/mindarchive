"""Tests for hostile zip handling.

These are the tests that matter most in this milestone. A provider export
arrives from outside the application, and a malicious one must be refused
rather than trusted.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from mind_archive.importers.chatgpt import ChatGPTImporter
from mind_archive.importers.zip_safety import (
    MAX_ENTRIES,
    UnsafeArchiveError,
    find_member,
    inspect,
    read_member,
)


def build(path: Path, entries: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return path


# ---------------------------------------------------------------------------
# Zip slip
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hostile_name",
    [
        "../escaped.json",
        "../../../../etc/passwd",
        "folder/../../escaped.json",
        "/absolute/path.json",
    ],
)
def test_refuses_entries_that_escape_the_archive(
    tmp_path: Path, hostile_name: str
) -> None:
    path = build(tmp_path / "slip.zip", {hostile_name: "malicious"})

    with pytest.raises(UnsafeArchiveError, match="outside"):
        inspect(path)


def test_a_traversal_entry_makes_the_whole_export_unreadable(
    tmp_path: Path,
) -> None:
    """One hostile entry poisons the archive: nothing is imported from it."""
    path = build(
        tmp_path / "mixed.zip",
        {"conversations.json": "[]", "../escaped.txt": "malicious"},
    )

    result = ChatGPTImporter().validate(path)

    assert result.ok is False
    assert "outside" in result.message


def test_nothing_is_written_outside_the_target(tmp_path: Path) -> None:
    """The real guarantee: a traversal entry never lands on disk."""
    path = build(tmp_path / "slip.zip", {"../escaped.json": "malicious"})

    with pytest.raises(UnsafeArchiveError):
        inspect(path)

    assert not (tmp_path.parent / "escaped.json").exists()


# ---------------------------------------------------------------------------
# Size and bombs
# ---------------------------------------------------------------------------


def test_refuses_an_archive_with_too_many_entries(tmp_path: Path) -> None:
    path = tmp_path / "many.zip"
    with zipfile.ZipFile(path, "w") as archive:
        for index in range(MAX_ENTRIES + 1):
            archive.writestr(f"file-{index}.txt", "x")

    with pytest.raises(UnsafeArchiveError, match="more than"):
        inspect(path)


def test_refuses_a_highly_compressed_member(tmp_path: Path) -> None:
    """A classic zip bomb: a tiny file that expands enormously."""
    path = tmp_path / "bomb.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        # 50 MB of zeros compresses to almost nothing.
        archive.writestr("conversations.json", "\0" * (50 * 1024 * 1024))

    with pytest.raises(UnsafeArchiveError, match="expands far more"):
        inspect(path)


def test_a_bomb_is_reported_rather_than_read(tmp_path: Path) -> None:
    path = tmp_path / "bomb.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("conversations.json", "\0" * (50 * 1024 * 1024))

    result = ChatGPTImporter().validate(path)

    assert result.ok is False
    assert "expands far more" in result.message


def test_ordinary_compression_is_fine(tmp_path: Path) -> None:
    """Real JSON compresses well. That must not be mistaken for an attack."""
    path = tmp_path / "normal.zip"
    content = '[{"title": "A perfectly normal conversation"}]' * 5_000
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("conversations.json", content)

    with inspect(path) as archive:
        assert find_member(archive, "conversations.json") is not None


# ---------------------------------------------------------------------------
# Malformed archives
# ---------------------------------------------------------------------------


def test_rejects_a_file_that_is_not_a_zip(tmp_path: Path) -> None:
    path = tmp_path / "not-a-zip.zip"
    path.write_bytes(b"just some bytes")

    with pytest.raises(UnsafeArchiveError, match="not a valid zip"):
        inspect(path)


def test_rejects_a_truncated_zip(tmp_path: Path) -> None:
    path = build(tmp_path / "whole.zip", {"conversations.json": "[]"})
    data = path.read_bytes()
    path.write_bytes(data[: len(data) // 2])

    with pytest.raises(UnsafeArchiveError):
        inspect(path)


def test_rejects_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(UnsafeArchiveError):
        inspect(tmp_path / "does-not-exist.zip")


# ---------------------------------------------------------------------------
# Finding and reading members
# ---------------------------------------------------------------------------


def test_finds_a_member_at_the_root(tmp_path: Path) -> None:
    path = build(tmp_path / "flat.zip", {"conversations.json": "[]"})

    with inspect(path) as archive:
        assert find_member(archive, "conversations.json") == "conversations.json"


def test_finds_a_member_inside_a_folder(tmp_path: Path) -> None:
    path = build(tmp_path / "nested.zip", {"export-2026/conversations.json": "[]"})

    with inspect(path) as archive:
        assert find_member(archive, "conversations.json") == (
            "export-2026/conversations.json"
        )


def test_prefers_the_shallowest_match(tmp_path: Path) -> None:
    path = build(
        tmp_path / "both.zip",
        {"conversations.json": "[]", "backup/old/conversations.json": "[]"},
    )

    with inspect(path) as archive:
        assert find_member(archive, "conversations.json") == "conversations.json"


def test_returns_nothing_when_the_member_is_absent(tmp_path: Path) -> None:
    path = build(tmp_path / "empty.zip", {"readme.txt": "hello"})

    with inspect(path) as archive:
        assert find_member(archive, "conversations.json") is None


def test_reads_a_member(tmp_path: Path) -> None:
    path = build(tmp_path / "read.zip", {"conversations.json": "[1, 2, 3]"})

    with inspect(path) as archive:
        assert read_member(archive, "conversations.json") == b"[1, 2, 3]"


def test_reading_an_unknown_member_is_an_error(tmp_path: Path) -> None:
    path = build(tmp_path / "read.zip", {"conversations.json": "[]"})

    with inspect(path) as archive, pytest.raises(UnsafeArchiveError, match="not in"):
        read_member(archive, "nothing.json")
