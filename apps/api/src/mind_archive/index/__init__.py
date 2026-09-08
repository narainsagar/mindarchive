"""The SQLite index over the archive.

Everything here is derived from the files on disk and can be rebuilt from them.
The archive is the truth; this is a convenience that makes it searchable.
"""

from mind_archive.index.indexer import Indexer
from mind_archive.index.schema import SCHEMA_VERSION, connect, supports_fts5
from mind_archive.index.search import SearchHit, SearchIndex, build_match_query

__all__ = [
    "SCHEMA_VERSION",
    "Indexer",
    "SearchHit",
    "SearchIndex",
    "build_match_query",
    "connect",
    "supports_fts5",
]
