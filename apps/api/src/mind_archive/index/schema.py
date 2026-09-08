"""The SQLite index.

**This database is an index, never the archive.** Everything in it is derived
from the Markdown and JSON files on disk, and it can be deleted and rebuilt at
any time without losing a single word the user wrote. That rule is what keeps
Mind Archive from becoming another silo — see decision D-004.

If you are ever tempted to store something here that is not on disk, do not.
Put it in the archive files and index it from there.

Plain `sqlite3` from the standard library. No ORM: there are two tables, the
queries are short, and an ORM would add a dependency to hide SQL that is
already easier to read than the code hiding it would be.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

#: Bumped when the schema changes. A mismatch rebuilds from disk rather than
#: migrating — which is free, because nothing here is original.
SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE conversations (
    id            INTEGER PRIMARY KEY,
    -- Folder path relative to the archive root, e.g.
    -- "chatgpt/2024-03-14-Making bread". This is the stable identity of a
    -- conversation and the key the API uses.
    path          TEXT    NOT NULL UNIQUE,
    title         TEXT    NOT NULL,
    source        TEXT    NOT NULL,
    source_id     TEXT,
    created_at    TEXT,
    updated_at    TEXT,
    message_count INTEGER NOT NULL DEFAULT 0,
    indexed_at    TEXT    NOT NULL
);

CREATE INDEX conversations_source  ON conversations (source);
CREATE INDEX conversations_created ON conversations (created_at DESC);

-- Full-text search. Contentless would save space, but keeping the text here
-- lets SQLite produce snippets without re-reading files from disk.
CREATE VIRTUAL TABLE search USING fts5(
    title,
    body,
    tokenize = 'porter unicode61'
);
"""


def connect(database_path: Path) -> sqlite3.Connection:
    """Open the index, creating or rebuilding the schema when needed.

    Returns a connection with rows accessible by column name.
    """
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    # Reads and writes can overlap: an import can index while someone searches.
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA foreign_keys = ON")

    if _needs_rebuild(connection):
        _create(connection)

    return connection


def _needs_rebuild(connection: sqlite3.Connection) -> bool:
    """Is the schema missing or from an older version?"""
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version != SCHEMA_VERSION:
        return True

    tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table')"
        )
    }
    return not {"conversations", "search"}.issubset(tables)


def _create(connection: sqlite3.Connection) -> None:
    """Drop anything there and build the schema fresh.

    Dropping is safe precisely because this database holds nothing original.
    The caller is expected to re-index from disk afterwards.
    """
    with connection:
        connection.execute("DROP TABLE IF EXISTS search")
        connection.execute("DROP TABLE IF EXISTS conversations")
        connection.executescript(SCHEMA)
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def supports_fts5() -> bool:
    """Is this SQLite build compiled with FTS5?

    Standard CPython builds are. A stripped system SQLite might not be, and
    finding that out at startup with a clear message beats an obscure error
    the first time someone searches.
    """
    probe = sqlite3.connect(":memory:")
    try:
        probe.execute("CREATE VIRTUAL TABLE probe USING fts5(x)")
        return True
    except sqlite3.OperationalError:
        return False
    finally:
        probe.close()
