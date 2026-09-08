"""Tests for the index and search.

The most important test in this file is
`test_deleting_the_database_loses_nothing`. If it ever fails, something has
started living only in SQLite, and the archive has stopped being portable.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from mind_archive.archive import ArchiveWriter
from mind_archive.archive.reader import read_conversation, strip_front_matter
from mind_archive.events import EventBus
from mind_archive.index import Indexer, SearchIndex, build_match_query
from mind_archive.models import Conversation, Message


def conversation(
    *,
    title: str = "Making sourdough bread",
    source_id: str = "conversation-1",
    created: datetime | None = datetime(2024, 3, 14, 9, 30, tzinfo=UTC),
    messages: list[Message] | None = None,
) -> Conversation:
    return Conversation(
        title=title,
        source="chatgpt",
        source_id=source_id,
        created_at=created,
        messages=messages
        or [
            Message(role="user", text="How do I make a sourdough starter?"),
            Message(role="assistant", text="Mix flour and water, then wait."),
        ],
    )


def tomatoes() -> Conversation:
    """A second conversation with nothing in common with the first.

    Sharing message text between fixtures makes "this search matched one
    conversation" assertions meaningless.
    """
    return Conversation(
        title="Growing tomatoes",
        source="chatgpt",
        source_id="two",
        created_at=datetime(2024, 5, 2, tzinfo=UTC),
        messages=[
            Message(role="user", text="When should I plant seedlings outside?"),
            Message(role="assistant", text="After the last frost."),
        ],
    )


@pytest.fixture
def archive(tmp_path: Path) -> Path:
    directory = tmp_path / "archive"
    directory.mkdir()
    return directory


@pytest.fixture
def database(tmp_path: Path) -> Path:
    return tmp_path / "mind_archive.db"


def populate(archive: Path, *conversations: Conversation) -> None:
    # A quiet bus: these tests are about indexing, not about events.
    writer = ArchiveWriter(archive, bus=EventBus())
    for item in conversations:
        writer.write(item)


# ---------------------------------------------------------------------------
# The rule that matters
# ---------------------------------------------------------------------------


def test_deleting_the_database_loses_nothing(archive: Path, database: Path) -> None:
    """The index holds nothing original. Delete it, rebuild, get it back.

    This is decision D-004 expressed as a test. If it fails, the archive has
    stopped being portable and something needs moving back onto disk.
    """
    populate(
        archive,
        conversation(source_id="one"),
        tomatoes(),
    )
    indexer = Indexer(archive, database)
    indexer.rebuild()

    before, before_total = SearchIndex(database).search("sourdough")

    database.unlink()

    rebuilt = Indexer(archive, database).rebuild()
    after, after_total = SearchIndex(database).search("sourdough")

    assert rebuilt == 2
    assert before_total == after_total == 1
    assert [hit.path for hit in before] == [hit.path for hit in after]


def test_an_archive_copied_from_another_machine_indexes_itself(
    archive: Path, database: Path
) -> None:
    """Copying the archive folder to a new computer must be enough."""
    populate(archive, conversation())

    indexed = Indexer(archive, database).ensure_built()

    assert indexed == 1
    assert SearchIndex(database).search("")[1] == 1


def test_nothing_is_rebuilt_when_the_index_is_already_current(
    archive: Path, database: Path
) -> None:
    populate(archive, conversation())
    indexer = Indexer(archive, database)
    indexer.rebuild()

    assert indexer.ensure_built() == 0


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------


def test_indexes_what_is_on_disk(archive: Path, database: Path) -> None:
    populate(archive, conversation(source_id="one"), conversation(source_id="two"))

    assert Indexer(archive, database).rebuild() == 2


def test_an_empty_archive_indexes_nothing(archive: Path, database: Path) -> None:
    assert Indexer(archive, database).rebuild() == 0


def test_re_indexing_does_not_duplicate(archive: Path, database: Path) -> None:
    populate(archive, conversation())
    indexer = Indexer(archive, database)

    indexer.rebuild()
    indexer.rebuild()

    assert indexer.count() == 1


def test_folders_that_are_not_conversations_are_ignored(
    archive: Path, database: Path
) -> None:
    """People put things in folders. That must not break the index."""
    populate(archive, conversation())
    (archive / "notes").mkdir()
    (archive / "notes" / "shopping.txt").write_text("milk", encoding="utf-8")
    (archive / "chatgpt" / "broken").mkdir()
    (archive / "chatgpt" / "broken" / "metadata.json").write_text(
        "{ not json", encoding="utf-8"
    )

    assert Indexer(archive, database).rebuild() == 1


def test_a_conversation_edited_by_hand_is_re_indexed(
    archive: Path, database: Path
) -> None:
    populate(archive, conversation())
    indexer = Indexer(archive, database)
    indexer.rebuild()

    folder = next(archive.rglob("conversation.md")).parent
    folder.joinpath("conversation.md").write_text(
        "---\ntitle: Making sourdough bread\n---\n\nPineapple upside down cake.",
        encoding="utf-8",
    )
    indexer.rebuild()

    hits, total = SearchIndex(database).search("pineapple")
    assert total == 1
    assert hits[0].title == "Making sourdough bread"


# ---------------------------------------------------------------------------
# Searching
# ---------------------------------------------------------------------------


def test_finds_a_conversation_by_its_text(archive: Path, database: Path) -> None:
    populate(archive, conversation())
    Indexer(archive, database).rebuild()

    hits, total = SearchIndex(database).search("starter")

    assert total == 1
    assert hits[0].title == "Making sourdough bread"


def test_finds_a_conversation_by_its_title(archive: Path, database: Path) -> None:
    populate(archive, conversation())
    Indexer(archive, database).rebuild()

    assert SearchIndex(database).search("sourdough")[1] == 1


def test_search_is_case_insensitive(archive: Path, database: Path) -> None:
    populate(archive, conversation())
    Indexer(archive, database).rebuild()

    assert SearchIndex(database).search("SOURDOUGH")[1] == 1


def test_search_matches_word_stems(archive: Path, database: Path) -> None:
    """The porter tokenizer means "bake" finds "baking"."""
    populate(
        archive,
        conversation(messages=[Message(role="user", text="I enjoy baking on Sundays")]),
    )
    Indexer(archive, database).rebuild()

    assert SearchIndex(database).search("bake")[1] == 1


def test_the_last_word_matches_as_a_prefix(archive: Path, database: Path) -> None:
    """Searching feels responsive if "sourd" already finds "sourdough"."""
    populate(archive, conversation())
    Indexer(archive, database).rebuild()

    assert SearchIndex(database).search("sourd")[1] == 1


def test_all_words_must_match(archive: Path, database: Path) -> None:
    populate(
        archive,
        conversation(source_id="one"),
        tomatoes(),
    )
    Indexer(archive, database).rebuild()

    assert SearchIndex(database).search("sourdough tomatoes")[1] == 0


def test_a_result_carries_a_snippet(archive: Path, database: Path) -> None:
    populate(archive, conversation())
    Indexer(archive, database).rebuild()

    hits, _ = SearchIndex(database).search("starter")

    assert hits[0].snippet is not None
    assert "<<" in hits[0].snippet


def test_an_empty_search_lists_everything(archive: Path, database: Path) -> None:
    populate(archive, conversation(source_id="one"), conversation(source_id="two"))
    Indexer(archive, database).rebuild()

    hits, total = SearchIndex(database).search("")

    assert total == 2
    assert len(hits) == 2


def test_listing_puts_the_newest_first(archive: Path, database: Path) -> None:
    populate(
        archive,
        conversation(
            title="Older", source_id="one", created=datetime(2023, 1, 1, tzinfo=UTC)
        ),
        conversation(
            title="Newer", source_id="two", created=datetime(2025, 1, 1, tzinfo=UTC)
        ),
    )
    Indexer(archive, database).rebuild()

    hits, _ = SearchIndex(database).search("")

    assert [hit.title for hit in hits] == ["Newer", "Older"]


def test_undated_conversations_sort_last(archive: Path, database: Path) -> None:
    """A missing date must not push a conversation to the top of the archive."""
    populate(
        archive,
        conversation(title="Undated", source_id="one", created=None),
        conversation(
            title="Dated", source_id="two", created=datetime(2020, 1, 1, tzinfo=UTC)
        ),
    )
    Indexer(archive, database).rebuild()

    hits, _ = SearchIndex(database).search("")

    assert [hit.title for hit in hits] == ["Dated", "Undated"]


def test_results_are_paginated(archive: Path, database: Path) -> None:
    populate(archive, *[conversation(source_id=f"c-{n}") for n in range(5)])
    Indexer(archive, database).rebuild()

    hits, total = SearchIndex(database).search("", limit=2, offset=2)

    assert total == 5
    assert len(hits) == 2


def test_counts_conversations_by_source(archive: Path, database: Path) -> None:
    populate(archive, conversation(source_id="one"), conversation(source_id="two"))
    Indexer(archive, database).rebuild()

    assert SearchIndex(database).sources() == {"chatgpt": 2}


# ---------------------------------------------------------------------------
# Queries people actually type
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query",
    [
        'unbalanced " quote',
        "C++",
        "NEAR(",
        "a AND OR b",
        "*",
        "^",
        "()",
        "-",
        '"""',
        "term:",
        "\\",
    ],
)
def test_awkward_queries_never_raise(archive: Path, database: Path, query: str) -> None:
    """FTS5 MATCH takes a query language. Search boxes take whatever people
    type. Nothing typed into one should ever produce an error."""
    populate(archive, conversation())
    Indexer(archive, database).rebuild()

    hits, total = SearchIndex(database).search(query)

    assert isinstance(hits, list)
    assert total >= 0


def test_operators_are_treated_as_text_not_syntax() -> None:
    assert build_match_query("a AND b") == '"a" AND "AND" AND "b" *'


def test_a_query_of_only_punctuation_finds_everything() -> None:
    """Nothing searchable means no filter, not no results."""
    assert build_match_query("!!! ???") is None


def test_too_many_terms_are_capped() -> None:
    query = build_match_query(" ".join(f"word{n}" for n in range(100)))

    assert query is not None
    assert query.count(" AND ") < 40


# ---------------------------------------------------------------------------
# Reading back off disk
# ---------------------------------------------------------------------------


def test_front_matter_is_stripped() -> None:
    text = "---\ntitle: A\n---\n\n# A\n\nHello."

    assert strip_front_matter(text) == "# A\n\nHello."


def test_a_horizontal_rule_mid_document_is_left_alone() -> None:
    """A `---` further down is someone's content, not front matter."""
    text = "# A\n\nFirst\n\n---\n\nSecond"

    assert strip_front_matter(text) == text


def test_unclosed_front_matter_is_left_alone() -> None:
    text = "---\ntitle: A\n\nno closing marker"

    assert strip_front_matter(text) == text


def test_reading_a_folder_that_is_not_a_conversation(archive: Path) -> None:
    (archive / "random").mkdir()

    assert read_conversation(archive, archive / "random") is None
