"""Tests for the watched inbox folder.

Two shapes to cover: a folder Mind Archive owns and tidies, and a folder the
user chose, where files must be left exactly where they are.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from conftest import make_conversation, write_export
from mind_archive.config import Settings
from mind_archive.inbox import FAILED_DIR, IMPORTED_DIR, LEDGER_FILE, Inbox


@pytest.fixture
def managed(tmp_path: Path) -> Settings:
    """The default: an inbox Mind Archive owns and tidies up."""
    settings = Settings(data_dir=tmp_path / "data", inbox_dir_setting="")
    settings.ensure_directories()
    return settings


@pytest.fixture
def borrowed(tmp_path: Path) -> Settings:
    """An inbox the user pointed at a folder of their own."""
    folder = tmp_path / "Downloads"
    folder.mkdir()
    settings = Settings(data_dir=tmp_path / "data", inbox_dir_setting=str(folder))
    settings.ensure_directories()
    return settings


def inbox(settings: Settings) -> Inbox:
    # No settle wait: nothing here is being written to while we look at it.
    return Inbox(settings, settle_seconds=0)


# ---------------------------------------------------------------------------
# The managed inbox
# ---------------------------------------------------------------------------


def test_imports_an_export_left_in_the_folder(managed: Settings) -> None:
    write_export(managed.inbox_dir, [make_conversation()])

    result = inbox(managed).scan()

    assert result.imported_files == 1
    assert result.new == 1
    assert list(managed.archive_dir.rglob("conversation.md"))


def test_an_imported_file_is_tidied_away(managed: Settings) -> None:
    export = write_export(managed.inbox_dir, [make_conversation()])

    inbox(managed).scan()

    assert not export.exists()
    assert (managed.inbox_dir / IMPORTED_DIR / export.name).is_file()


def test_a_tidied_file_is_not_imported_again(managed: Settings) -> None:
    write_export(managed.inbox_dir, [make_conversation()])
    inbox(managed).scan()

    second = inbox(managed).scan()

    assert second.scanned == 0
    assert second.summary() == "Nothing new in your inbox."


def test_an_unreadable_file_is_moved_aside_with_a_reason(
    managed: Settings,
) -> None:
    broken = managed.inbox_dir / "broken.zip"
    with zipfile.ZipFile(broken, "w") as archive:
        archive.writestr("conversations.json", "{ not json at all")

    result = inbox(managed).scan()

    assert result.failed_files == 1
    moved = managed.inbox_dir / FAILED_DIR / "broken.zip"
    assert moved.is_file()
    reason = moved.with_suffix(".zip.txt")
    assert reason.is_file()
    assert "JSON" in reason.read_text(encoding="utf-8")


def test_a_hostile_archive_is_refused_and_explained(managed: Settings) -> None:
    hostile = managed.inbox_dir / "slip.zip"
    with zipfile.ZipFile(hostile, "w") as archive:
        archive.writestr("conversations.json", "[]")
        archive.writestr("../escaped.txt", "malicious")

    result = inbox(managed).scan()

    assert result.failed_files == 1
    assert any("outside" in problem for problem in result.problems)
    assert not (managed.inbox_dir.parent / "escaped.txt").exists()


def test_files_that_are_not_exports_are_left_alone(managed: Settings) -> None:
    note = managed.inbox_dir / "shopping-list.txt"
    note.write_text("milk", encoding="utf-8")

    result = inbox(managed).scan()

    assert result.scanned == 0
    assert note.is_file()


def test_hidden_files_are_ignored(managed: Settings) -> None:
    (managed.inbox_dir / ".DS_Store.json").write_text("{}", encoding="utf-8")

    assert inbox(managed).waiting() == []


def test_already_tidied_files_are_not_rescanned(managed: Settings) -> None:
    """The imported/ folder is inside the inbox and must not be re-read."""
    write_export(managed.inbox_dir, [make_conversation()])
    inbox(managed).scan()

    assert inbox(managed).waiting() == []


def test_several_exports_are_all_imported(managed: Settings) -> None:
    write_export(
        managed.inbox_dir, [make_conversation(conversation_id="one")], name="a.zip"
    )
    write_export(
        managed.inbox_dir, [make_conversation(conversation_id="two")], name="b.zip"
    )

    result = inbox(managed).scan()

    assert result.imported_files == 2
    assert result.new == 2


def test_a_bare_conversations_json_is_imported(managed: Settings) -> None:
    """Which is what the browser script produces."""
    import json

    (managed.inbox_dir / "conversations.json").write_text(
        json.dumps([make_conversation()]), encoding="utf-8"
    )

    assert inbox(managed).scan().new == 1


# ---------------------------------------------------------------------------
# A folder the user chose
# ---------------------------------------------------------------------------


def test_a_borrowed_folder_keeps_its_files(borrowed: Settings) -> None:
    """Moving files out of somebody's own folder would be rude."""
    export = write_export(borrowed.inbox_dir, [make_conversation()])

    result = inbox(borrowed).scan()

    assert result.new == 1
    assert export.is_file()
    assert not (borrowed.inbox_dir / IMPORTED_DIR).exists()


def test_a_borrowed_folder_remembers_what_it_imported(borrowed: Settings) -> None:
    write_export(borrowed.inbox_dir, [make_conversation()])
    inbox(borrowed).scan()

    assert (borrowed.inbox_dir / LEDGER_FILE).is_file()
    assert inbox(borrowed).scan().scanned == 0


def test_a_borrowed_folder_is_not_created_for_the_user(tmp_path: Path) -> None:
    """Silently making folders somewhere a person chose is not our business."""
    settings = Settings(
        data_dir=tmp_path / "data",
        inbox_dir_setting=str(tmp_path / "does-not-exist"),
    )
    settings.ensure_directories()

    assert not settings.inbox_dir.exists()
    assert inbox(settings).waiting() == []


def test_a_changed_file_is_imported_again(borrowed: Settings) -> None:
    """The ledger keys on size and modification time, so an updated export
    with the same name is picked up."""
    write_export(borrowed.inbox_dir, [make_conversation()], name="export.zip")
    inbox(borrowed).scan()

    write_export(
        borrowed.inbox_dir,
        [make_conversation(), make_conversation(conversation_id="two")],
        name="export.zip",
    )

    assert inbox(borrowed).scan().scanned == 1


# ---------------------------------------------------------------------------
# Re-importing
# ---------------------------------------------------------------------------


def test_the_same_export_twice_reports_nothing_new(managed: Settings) -> None:
    """The normal case: every provider export is a full export."""
    write_export(managed.inbox_dir, [make_conversation()], name="first.zip")
    inbox(managed).scan()

    write_export(managed.inbox_dir, [make_conversation()], name="second.zip")
    result = inbox(managed).scan()

    assert result.new == 0
    assert result.unchanged == 1
    assert "already in your archive" in result.summary()


def test_nothing_is_rewritten_when_nothing_changed(managed: Settings) -> None:
    """A file's timestamp should mean "this changed"."""
    write_export(managed.inbox_dir, [make_conversation()], name="first.zip")
    inbox(managed).scan()

    written = next(managed.archive_dir.rglob("conversation.md"))
    before = written.stat().st_mtime_ns

    write_export(managed.inbox_dir, [make_conversation()], name="second.zip")
    inbox(managed).scan()

    assert written.stat().st_mtime_ns == before


def test_a_grown_conversation_is_reported_as_updated(managed: Settings) -> None:
    write_export(
        managed.inbox_dir,
        [make_conversation(turns=[("user", "Hello")])],
        name="first.zip",
    )
    inbox(managed).scan()

    write_export(
        managed.inbox_dir,
        [make_conversation(turns=[("user", "Hello"), ("assistant", "Hi there")])],
        name="second.zip",
    )
    result = inbox(managed).scan()

    assert result.updated == 1
    assert result.new == 0


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def test_an_empty_inbox_says_so(managed: Settings) -> None:
    assert inbox(managed).scan().summary() == "Nothing new in your inbox."


def test_a_missing_inbox_folder_is_not_an_error(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path / "nowhere", inbox_dir_setting="")

    assert inbox(settings).waiting() == []
    assert inbox(settings).scan().scanned == 0


def test_the_summary_counts_files_and_conversations(managed: Settings) -> None:
    write_export(
        managed.inbox_dir,
        [
            make_conversation(conversation_id="one"),
            make_conversation(conversation_id="two"),
        ],
    )

    summary = inbox(managed).scan().summary()

    assert "1 file" in summary
    assert "2 new" in summary
