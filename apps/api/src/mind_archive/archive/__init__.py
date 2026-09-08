"""Storing conversations on disk, as files a person can read.

The archive is the point of the product. SQLite will index it later; it never
owns it. See docs/project-memory/DECISIONS.md D-004.
"""

from mind_archive.archive.writer import ArchiveWriter, WriteResult

__all__ = ["ArchiveWriter", "WriteResult"]
