"""Searching and listing conversations.

Reads only from the index. Anything it returns exists on disk too.

## Why the query is rewritten

FTS5's `MATCH` takes a query *language*, not a string. Typing `AND`, a bare
`"`, or `NEAR(` into a search box would either raise a syntax error or quietly
mean something the person did not intend. `C++` is a syntax error. So the input
is broken into words and rebuilt as a safe quoted query, which is both harder to
break and closer to what someone typing into a search box expects.

This is a correctness measure, not a security one — the query is still passed
as a bound parameter, so it was never an injection risk.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from mind_archive.index.schema import connect

#: Anything that is not a letter, digit or underscore separates words. Keeps
#: FTS5 operators out by construction rather than by blocklist.
_WORD = re.compile(r"[^\w]+", re.UNICODE)

#: More terms than this and the person is pasting, not searching.
MAX_TERMS = 32

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


@dataclass
class SearchHit:
    """One conversation in a result list."""

    path: str
    title: str
    source: str
    created_at: str | None
    updated_at: str | None
    message_count: int

    #: A short piece of matching text with the match marked, when searching.
    snippet: str | None = None


def build_match_query(text: str) -> str | None:
    """Turn what someone typed into a safe FTS5 query.

    Every word is quoted, so operators and punctuation are treated as text.
    The final word gets a prefix wildcard, which is what makes a search feel
    responsive as you type: "sourd" finds "sourdough".

    Returns `None` when there is nothing searchable, which the caller treats
    as "no filter" rather than "no results".
    """
    words = [word for word in _WORD.split(text.strip()) if word][:MAX_TERMS]
    if not words:
        return None

    # Doubling a quote is how FTS5 escapes one inside a quoted string. Word
    # splitting has already removed them, but this stays correct if that
    # changes.
    quoted = [f'"{word.replace(chr(34), chr(34) * 2)}"' for word in words]
    quoted[-1] = quoted[-1] + " *"

    return " AND ".join(quoted)


class SearchIndex:
    """Queries against the conversation index."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def search(
        self,
        query: str = "",
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> tuple[list[SearchHit], int]:
        """Find conversations. Returns the page and the total match count.

        An empty query lists everything, newest first — which is what a person
        expects to see when they open the archive without searching.
        """
        limit = max(1, min(limit, MAX_LIMIT))
        offset = max(0, offset)

        match = build_match_query(query)
        connection = connect(self.database_path)
        try:
            if match is None:
                return self._list(connection, limit, offset)
            return self._search(connection, match, limit, offset)
        except sqlite3.OperationalError:
            # A query FTS5 still refuses. Better an empty result than a 500.
            return [], 0
        finally:
            connection.close()

    def _list(
        self, connection: sqlite3.Connection, limit: int, offset: int
    ) -> tuple[list[SearchHit], int]:
        total = int(
            connection.execute("SELECT COUNT(*) AS n FROM conversations").fetchone()[
                "n"
            ]
        )

        rows = connection.execute(
            """
            SELECT path, title, source, created_at, updated_at, message_count
            FROM conversations
            -- Undated conversations sort last rather than first: a missing
            -- date should not push a conversation to the top of the archive.
            ORDER BY created_at IS NULL, created_at DESC, title
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

        return [_hit(row) for row in rows], total

    def _search(
        self,
        connection: sqlite3.Connection,
        match: str,
        limit: int,
        offset: int,
    ) -> tuple[list[SearchHit], int]:
        total = int(
            connection.execute(
                "SELECT COUNT(*) AS n FROM search WHERE search MATCH ?", (match,)
            ).fetchone()["n"]
        )

        rows = connection.execute(
            """
            SELECT c.path, c.title, c.source, c.created_at, c.updated_at,
                   c.message_count,
                   snippet(search, 1, '<<', '>>', '…', 24) AS snippet
            FROM search
            JOIN conversations AS c ON c.id = search.rowid
            WHERE search MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
            """,
            (match, limit, offset),
        ).fetchall()

        return [_hit(row, snippet=row["snippet"]) for row in rows], total

    def get(self, path: str) -> SearchHit | None:
        """One conversation's indexed metadata, by its archive path."""
        connection = connect(self.database_path)
        try:
            row = connection.execute(
                """
                SELECT path, title, source, created_at, updated_at, message_count
                FROM conversations WHERE path = ?
                """,
                (path,),
            ).fetchone()
            return _hit(row) if row else None
        finally:
            connection.close()

    def sources(self) -> dict[str, int]:
        """How many conversations came from each provider."""
        connection = connect(self.database_path)
        try:
            return {
                row["source"]: int(row["n"])
                for row in connection.execute(
                    """
                    SELECT source, COUNT(*) AS n FROM conversations
                    GROUP BY source ORDER BY n DESC
                    """
                )
            }
        finally:
            connection.close()


def _hit(row: sqlite3.Row, snippet: str | None = None) -> SearchHit:
    return SearchHit(
        path=row["path"],
        title=row["title"],
        source=row["source"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        message_count=row["message_count"],
        snippet=snippet,
    )
