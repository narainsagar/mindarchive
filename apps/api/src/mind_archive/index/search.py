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

## About the `# noqa: S608` comments

Several queries are assembled with f-strings, which a security linter rightly
flags. The safety property, in every case:

- **The tag itself is never interpolated.** It is a bound `?` parameter, exactly
  like the search text.
- The only interpolated values are `_tag_filter`'s fixed clause, the literals
  `"conversations.id"` / `"c.id"` / `"WHERE"` / `"AND"` written at the call
  sites, and a run of `?` characters.

Nothing derived from a request reaches the SQL text. The suppressions are
deliberate and each one is worth re-checking if these queries change.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
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
    tags: list[str] = field(default_factory=list)

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
        tag: str = "",
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> tuple[list[SearchHit], int]:
        """Find conversations. Returns the page and the total match count.

        An empty query lists everything, newest first — which is what a person
        expects to see when they open the archive without searching. A `tag`
        narrows either case, and combines with a search rather than replacing
        it: "what I tagged `recipes` that also mentions sourdough".
        """
        limit = max(1, min(limit, MAX_LIMIT))
        offset = max(0, offset)

        match = build_match_query(query)
        connection = connect(self.database_path)
        try:
            if match is None:
                return self._list(connection, tag, limit, offset)
            return self._search(connection, match, tag, limit, offset)
        except sqlite3.OperationalError:
            # A query FTS5 still refuses. Better an empty result than a 500.
            return [], 0
        finally:
            connection.close()

    def _list(
        self, connection: sqlite3.Connection, tag: str, limit: int, offset: int
    ) -> tuple[list[SearchHit], int]:
        where, params = _tag_filter(tag, "conversations.id")

        total = int(
            connection.execute(
                f"SELECT COUNT(*) AS n FROM conversations {where}",  # noqa: S608
                params,
            ).fetchone()["n"]
        )

        rows = connection.execute(
            f"""
            SELECT id, path, title, source, created_at, updated_at, message_count
            FROM conversations
            {where}
            -- Undated conversations sort last rather than first: a missing
            -- date should not push a conversation to the top of the archive.
            ORDER BY created_at IS NULL, created_at DESC, title
            LIMIT ? OFFSET ?
            """,  # noqa: S608 - only our own literals are interpolated
            (*params, limit, offset),
        ).fetchall()

        return self._with_tags(connection, rows, snippets=False), total

    def _search(
        self,
        connection: sqlite3.Connection,
        match: str,
        tag: str,
        limit: int,
        offset: int,
    ) -> tuple[list[SearchHit], int]:
        where, params = _tag_filter(tag, "c.id", prefix="AND")

        total = int(
            connection.execute(
                f"""
                SELECT COUNT(*) AS n
                FROM search
                JOIN conversations AS c ON c.id = search.rowid
                WHERE search MATCH ? {where}
                """,  # noqa: S608 - only our own literals are interpolated
                (match, *params),
            ).fetchone()["n"]
        )

        rows = connection.execute(
            f"""
            SELECT c.id, c.path, c.title, c.source, c.created_at, c.updated_at,
                   c.message_count,
                   snippet(search, 1, '<<', '>>', '…', 24) AS snippet
            FROM search
            JOIN conversations AS c ON c.id = search.rowid
            WHERE search MATCH ? {where}
            ORDER BY rank
            LIMIT ? OFFSET ?
            """,  # noqa: S608 - only our own literals are interpolated
            (match, *params, limit, offset),
        ).fetchall()

        return self._with_tags(connection, rows, snippets=True), total

    def _with_tags(
        self,
        connection: sqlite3.Connection,
        rows: list[sqlite3.Row],
        *,
        snippets: bool,
    ) -> list[SearchHit]:
        """Attach each conversation's tags in one query rather than one each."""
        if not rows:
            return []

        ids = [row["id"] for row in rows]
        placeholders = ",".join("?" * len(ids))

        by_id: dict[int, list[str]] = {}
        for tag_row in connection.execute(
            # placeholders is a run of "?" characters and nothing else.
            f"SELECT conversation_id, tag FROM tags "  # noqa: S608
            f"WHERE conversation_id IN ({placeholders}) ORDER BY tag",
            ids,
        ):
            by_id.setdefault(tag_row["conversation_id"], []).append(tag_row["tag"])

        return [
            _hit(
                row,
                snippet=row["snippet"] if snippets else None,
                tags=by_id.get(row["id"], []),
            )
            for row in rows
        ]

    def get(self, path: str) -> SearchHit | None:
        """One conversation's indexed metadata, by its archive path."""
        connection = connect(self.database_path)
        try:
            row = connection.execute(
                """
                SELECT id, path, title, source, created_at, updated_at,
                       message_count
                FROM conversations WHERE path = ?
                """,
                (path,),
            ).fetchone()
            if row is None:
                return None
            return self._with_tags(connection, [row], snippets=False)[0]
        finally:
            connection.close()

    def tags(self) -> dict[str, int]:
        """Every tag in use, and how many conversations carry it."""
        connection = connect(self.database_path)
        try:
            return {
                row["tag"]: int(row["n"])
                for row in connection.execute(
                    """
                    SELECT tag, COUNT(*) AS n FROM tags
                    GROUP BY tag ORDER BY n DESC, tag
                    """
                )
            }
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


def _tag_filter(
    tag: str, id_column: str, prefix: str = "WHERE"
) -> tuple[str, tuple[str, ...]]:
    """SQL narrowing results to one tag, or nothing at all if none was given.

    Matched case-insensitively: someone filtering for "recipes" means the same
    thing as the "Recipes" they typed when tagging.
    """
    label = " ".join(tag.split())
    if not label:
        return "", ()

    # The tag is a bound parameter. `prefix` and `id_column` are literals
    # written at the call sites, never anything from a request.
    return (
        f"{prefix} EXISTS (SELECT 1 FROM tags WHERE tags.conversation_id = "  # noqa: S608
        f"{id_column} AND tags.tag = ? COLLATE NOCASE)",
        (label,),
    )


def _hit(
    row: sqlite3.Row, snippet: str | None = None, tags: list[str] | None = None
) -> SearchHit:
    return SearchHit(
        path=row["path"],
        title=row["title"],
        source=row["source"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        message_count=row["message_count"],
        tags=tags or [],
        snippet=snippet,
    )
