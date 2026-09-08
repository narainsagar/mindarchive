"""Building the index from the files on disk.

The index is derived, always. Delete `mind_archive.db` and everything here
rebuilds it by reading the archive — that is the guarantee that makes the
archive portable rather than trapped (decision D-004).

There is a test that deletes the database and checks the rebuild produces the
same results. If that test ever fails, something has started living only in
SQLite, and that is a bug.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from mind_archive.archive.reader import StoredConversation, read_conversation
from mind_archive.archive.writer import METADATA_FILE
from mind_archive.index.schema import connect

logger = logging.getLogger(__name__)


class Indexer:
    """Keeps the SQLite index in step with the archive folder."""

    def __init__(self, archive_dir: Path, database_path: Path) -> None:
        self.archive_dir = archive_dir
        self.database_path = database_path

    # -- Building -----------------------------------------------------------

    def rebuild(self) -> int:
        """Rebuild the whole index from disk. Returns how many were indexed.

        Cheap enough to run whenever there is doubt: a personal archive is
        thousands of conversations, not millions.
        """
        connection = connect(self.database_path)
        try:
            with connection:
                connection.execute("DELETE FROM search")
                connection.execute("DELETE FROM conversations")

            count = 0
            for metadata_path in sorted(self.archive_dir.rglob(METADATA_FILE)):
                if self._index_folder(connection, metadata_path.parent):
                    count += 1

            logger.info("Indexed %s conversations", count)
            return count
        finally:
            connection.close()

    def index_one(self, folder: Path) -> bool:
        """Index or re-index a single conversation folder."""
        connection = connect(self.database_path)
        try:
            return self._index_folder(connection, folder)
        finally:
            connection.close()

    def _index_folder(self, connection: sqlite3.Connection, folder: Path) -> bool:
        conversation = read_conversation(self.archive_dir, folder, with_body=True)
        if conversation is None:
            return False

        self._store(connection, conversation)
        return True

    def _store(
        self, connection: sqlite3.Connection, conversation: StoredConversation
    ) -> None:
        """Insert or replace one conversation and its searchable text."""
        with connection:
            existing = connection.execute(
                "SELECT id FROM conversations WHERE path = ?", (conversation.path,)
            ).fetchone()

            if existing is not None:
                connection.execute(
                    "DELETE FROM search WHERE rowid = ?", (existing["id"],)
                )
                connection.execute(
                    "DELETE FROM conversations WHERE id = ?", (existing["id"],)
                )

            cursor = connection.execute(
                """
                INSERT INTO conversations
                    (path, title, source, source_id, created_at, updated_at,
                     message_count, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation.path,
                    conversation.title,
                    conversation.source,
                    conversation.source_id,
                    conversation.created_at,
                    conversation.updated_at,
                    conversation.message_count,
                    datetime.now(UTC).isoformat(),
                ),
            )

            connection.execute(
                "INSERT INTO search (rowid, title, body) VALUES (?, ?, ?)",
                (cursor.lastrowid, conversation.title, conversation.body or ""),
            )

    # -- Housekeeping -------------------------------------------------------

    def count(self) -> int:
        connection = connect(self.database_path)
        try:
            row = connection.execute(
                "SELECT COUNT(*) AS n FROM conversations"
            ).fetchone()
            return int(row["n"])
        finally:
            connection.close()

    def is_empty(self) -> bool:
        return self.count() == 0

    def has_archive(self) -> bool:
        """Are there conversations on disk, indexed or not?"""
        if not self.archive_dir.is_dir():
            return False
        return next(self.archive_dir.rglob(METADATA_FILE), None) is not None

    def ensure_built(self) -> int:
        """Index on startup if the archive has content but the index does not.

        Covers the case that matters: someone deletes `mind_archive.db`, or
        copies their archive folder to a new machine, and expects it to work.
        """
        if self.is_empty() and self.has_archive():
            logger.info("Index is empty but the archive is not; rebuilding")
            return self.rebuild()
        return 0
