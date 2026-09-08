"""Tests for path safety.

These matter more than they look. From Milestone 2 the application writes files
using names taken from archives exported by other software, and those names are
attacker-controlled.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mind_archive.paths import UnsafePathError, is_inside, safe_filename, safe_join


def test_a_normal_join_works(tmp_path: Path) -> None:
    result = safe_join(tmp_path, "chatgpt", "conversation.md")

    assert result == tmp_path / "chatgpt" / "conversation.md"


def test_parent_traversal_is_refused(tmp_path: Path) -> None:
    with pytest.raises(UnsafePathError):
        safe_join(tmp_path, "..", "escaped.md")


def test_traversal_hidden_inside_a_segment_is_refused(tmp_path: Path) -> None:
    with pytest.raises(UnsafePathError):
        safe_join(tmp_path, "chats/../../escaped.md")


def test_an_absolute_segment_is_refused(tmp_path: Path) -> None:
    with pytest.raises(UnsafePathError):
        safe_join(tmp_path, "/etc/passwd")


def test_an_empty_segment_is_refused(tmp_path: Path) -> None:
    with pytest.raises(UnsafePathError):
        safe_join(tmp_path, "")


def test_a_null_byte_is_refused(tmp_path: Path) -> None:
    with pytest.raises(UnsafePathError):
        safe_join(tmp_path, "evil\x00.md")


def test_is_inside_recognises_a_child(tmp_path: Path) -> None:
    child = tmp_path / "archive" / "note.md"
    child.parent.mkdir(parents=True)
    child.write_text("hello", encoding="utf-8")

    assert is_inside(child, tmp_path) is True


def test_is_inside_rejects_a_sibling(tmp_path: Path) -> None:
    inside = tmp_path / "archive"
    outside = tmp_path / "elsewhere"
    inside.mkdir()
    outside.mkdir()

    assert is_inside(outside, inside) is False


def test_a_directory_is_inside_itself(tmp_path: Path) -> None:
    assert is_inside(tmp_path, tmp_path) is True


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("Hello world", "Hello world"),
        ("../../etc/passwd", "etc-passwd"),
        ("what:is/this?", "what-is-this"),
        ("  spaced  ", "spaced"),
        ("...", "untitled"),
        ("", "untitled"),
    ],
)
def test_filenames_are_cleaned(given: str, expected: str) -> None:
    assert safe_filename(given) == expected


def test_reserved_windows_names_are_avoided() -> None:
    assert safe_filename("CON") == "CON-file"
    assert safe_filename("com1") == "com1-file"


def test_long_filenames_are_truncated() -> None:
    assert len(safe_filename("a" * 500)) == 120
