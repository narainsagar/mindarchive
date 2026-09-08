"""Tests for tags.

Tags are the only thing in the archive a person *made* rather than imported, so
they get more protection than anything else. Two tests here matter more than the
rest:

- `test_importing_again_does_not_erase_tags` — the data loss nobody would notice
  until months later.
- `test_deleting_the_database_does_not_lose_tags` — D-004, applied to the one
  case where breaking it would destroy original work.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from mind_archive.archive import ArchiveWriter
from mind_archive.archive.writer import METADATA_FILE, read_tags, write_tags
from mind_archive.events import EventBus
from mind_archive.index import Indexer, SearchIndex
from mind_archive.models import (
    MAX_TAG_LENGTH,
    MAX_TAGS,
    Conversation,
    Message,
    clean_tags,
)


def conversation(
    *,
    title: str = "Making sourdough",
    source_id: str = "conversation-1",
    tags: list[str] | None = None,
    text: str = "How do I make a starter?",
) -> Conversation:
    return Conversation(
        title=title,
        source="chatgpt",
        source_id=source_id,
        created_at=datetime(2024, 3, 14, tzinfo=UTC),
        tags=tags or [],
        messages=[Message(role="user", text=text)],
    )


@pytest.fixture
def archive(tmp_path: Path) -> Path:
    directory = tmp_path / "archive"
    directory.mkdir()
    return directory


@pytest.fixture
def database(tmp_path: Path) -> Path:
    return tmp_path / "mind_archive.db"


def writer(archive: Path) -> ArchiveWriter:
    return ArchiveWriter(archive, bus=EventBus())


# ---------------------------------------------------------------------------
# The two that matter
# ---------------------------------------------------------------------------


def test_importing_again_does_not_erase_tags(archive: Path) -> None:
    """An export has no tags. Re-importing must not take that as "remove them".

    Every ChatGPT export is a full export, so this happens every single time
    somebody imports their monthly download. Getting it wrong would silently
    destroy months of a person's own filing.
    """
    folder = writer(archive).write(conversation()).folder
    write_tags(folder / METADATA_FILE, ["recipes", "bread"])

    # The same conversation arrives again from a fresh export, carrying no tags.
    writer(archive).write(conversation())

    assert read_tags(folder / METADATA_FILE) == ["recipes", "bread"]


def test_deleting_the_database_does_not_lose_tags(
    archive: Path, database: Path
) -> None:
    """Tags live on disk, so the index can be thrown away like any other cache."""
    folder = writer(archive).write(conversation()).folder
    write_tags(folder / METADATA_FILE, ["recipes"])
    Indexer(archive, database).rebuild()

    database.unlink()
    Indexer(archive, database).rebuild()

    hits, total = SearchIndex(database).search("", tag="recipes")
    assert total == 1
    assert hits[0].tags == ["recipes"]


# ---------------------------------------------------------------------------
# Storing them
# ---------------------------------------------------------------------------


def test_tags_are_written_to_the_metadata_file(archive: Path) -> None:
    folder = writer(archive).write(conversation()).folder

    write_tags(folder / METADATA_FILE, ["recipes"])

    stored = json.loads((folder / METADATA_FILE).read_text(encoding="utf-8"))
    assert stored["tags"] == ["recipes"]


def test_tagging_leaves_the_rest_of_the_metadata_alone(archive: Path) -> None:
    """Relabelling must not disturb anything derived from the export."""
    folder = writer(archive).write(conversation()).folder
    before = json.loads((folder / METADATA_FILE).read_text(encoding="utf-8"))

    write_tags(folder / METADATA_FILE, ["recipes"])
    after = json.loads((folder / METADATA_FILE).read_text(encoding="utf-8"))

    del before["tags"], after["tags"]
    assert before == after


def test_tags_survive_an_update_to_the_conversation(archive: Path) -> None:
    """A conversation that has grown keeps the tags it already had."""
    folder = writer(archive).write(conversation()).folder
    write_tags(folder / METADATA_FILE, ["recipes"])

    writer(archive).write(conversation(text="A longer question entirely."))

    assert read_tags(folder / METADATA_FILE) == ["recipes"]


def test_replacing_tags_replaces_them(archive: Path) -> None:
    folder = writer(archive).write(conversation()).folder
    write_tags(folder / METADATA_FILE, ["recipes", "bread"])

    write_tags(folder / METADATA_FILE, ["baking"])

    assert read_tags(folder / METADATA_FILE) == ["baking"]


def test_tags_can_be_removed_entirely(archive: Path) -> None:
    folder = writer(archive).write(conversation()).folder
    write_tags(folder / METADATA_FILE, ["recipes"])

    write_tags(folder / METADATA_FILE, [])

    assert read_tags(folder / METADATA_FILE) == []


def test_a_conversation_with_no_tags_reads_as_empty(archive: Path) -> None:
    folder = writer(archive).write(conversation()).folder

    assert read_tags(folder / METADATA_FILE) == []


def test_unreadable_metadata_does_not_crash_a_read(tmp_path: Path) -> None:
    broken = tmp_path / "metadata.json"
    broken.write_text("{ not json", encoding="utf-8")

    assert read_tags(broken) == []


def test_writing_to_unreadable_metadata_is_an_error(tmp_path: Path) -> None:
    broken = tmp_path / "metadata.json"
    broken.write_text("{ not json", encoding="utf-8")

    with pytest.raises(ValueError):
        write_tags(broken, ["recipes"])


# ---------------------------------------------------------------------------
# Tidying what people type
# ---------------------------------------------------------------------------


def test_whitespace_is_trimmed_and_collapsed() -> None:
    assert clean_tags(["  bread   making  "]) == ["bread making"]


def test_empty_tags_are_dropped() -> None:
    assert clean_tags(["", "   ", "bread"]) == ["bread"]


def test_duplicates_are_removed_ignoring_case() -> None:
    """ "Bread" and "bread" are one label. Keeping both splits someone's own
    filing without them noticing."""
    assert clean_tags(["Bread", "bread", "BREAD"]) == ["Bread"]


def test_the_first_spelling_wins() -> None:
    assert clean_tags(["Recipes", "recipes"]) == ["Recipes"]


def test_a_very_long_tag_is_truncated() -> None:
    assert len(clean_tags(["x" * 500])[0]) <= MAX_TAG_LENGTH


def test_too_many_tags_are_capped() -> None:
    assert len(clean_tags([f"tag-{n}" for n in range(500)])) == MAX_TAGS


def test_things_that_are_not_strings_are_ignored() -> None:
    assert clean_tags([None, 42, {"a": 1}, "bread"]) == ["bread"]  # type: ignore[list-item]


def test_order_is_preserved() -> None:
    assert clean_tags(["one", "two", "three"]) == ["one", "two", "three"]


# ---------------------------------------------------------------------------
# Finding things by tag
# ---------------------------------------------------------------------------


def populate(archive: Path, database: Path) -> None:
    write = writer(archive)
    bread = write.write(conversation(source_id="one")).folder
    tomatoes = write.write(
        conversation(
            title="Growing tomatoes",
            source_id="two",
            text="When do I plant seedlings?",
        )
    ).folder

    write_tags(bread / METADATA_FILE, ["recipes", "bread"])
    write_tags(tomatoes / METADATA_FILE, ["garden"])
    Indexer(archive, database).rebuild()


def test_filters_by_tag(archive: Path, database: Path) -> None:
    populate(archive, database)

    hits, total = SearchIndex(database).search("", tag="recipes")

    assert total == 1
    assert hits[0].title == "Making sourdough"


def test_filtering_by_tag_ignores_case(archive: Path, database: Path) -> None:
    populate(archive, database)

    assert SearchIndex(database).search("", tag="RECIPES")[1] == 1


def test_an_unknown_tag_finds_nothing(archive: Path, database: Path) -> None:
    populate(archive, database)

    assert SearchIndex(database).search("", tag="nonexistent")[1] == 0


def test_a_tag_narrows_a_search_rather_than_replacing_it(
    archive: Path, database: Path
) -> None:
    populate(archive, database)

    assert SearchIndex(database).search("sourdough", tag="recipes")[1] == 1
    assert SearchIndex(database).search("sourdough", tag="garden")[1] == 0


def test_no_tag_means_no_filter(archive: Path, database: Path) -> None:
    populate(archive, database)

    assert SearchIndex(database).search("", tag="")[1] == 2
    assert SearchIndex(database).search("", tag="   ")[1] == 2


def test_results_carry_their_tags(archive: Path, database: Path) -> None:
    populate(archive, database)

    hits, _ = SearchIndex(database).search("sourdough")

    assert sorted(hits[0].tags) == ["bread", "recipes"]


def test_counts_every_tag_in_use(archive: Path, database: Path) -> None:
    populate(archive, database)

    assert SearchIndex(database).tags() == {"bread": 1, "garden": 1, "recipes": 1}


def test_re_indexing_does_not_duplicate_tags(archive: Path, database: Path) -> None:
    populate(archive, database)
    Indexer(archive, database).rebuild()

    assert SearchIndex(database).tags() == {"bread": 1, "garden": 1, "recipes": 1}


def test_removing_a_tag_removes_it_from_the_index(
    archive: Path, database: Path
) -> None:
    populate(archive, database)
    folder = next(archive.rglob("metadata.json")).parent

    write_tags(folder / METADATA_FILE, [])
    Indexer(archive, database).index_one(folder)

    assert "recipes" not in SearchIndex(database).tags()
