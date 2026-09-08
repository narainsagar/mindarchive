"""Browsing and searching the archive.

- ``GET  /api/conversations``            list or search
- ``GET  /api/conversations/{path}``     read one
- ``POST /api/index/rebuild``            rebuild the index from disk

**The path in the URL is untrusted.** `/api/conversations/../../etc/passwd` is
a request anyone can make, so every path goes through `safe_join` before it
touches the filesystem. See `docs/SECURITY.md`.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from mind_archive.archive.reader import read_conversation
from mind_archive.config import Settings, get_settings
from mind_archive.index import Indexer, SearchIndex
from mind_archive.index.search import DEFAULT_LIMIT, MAX_LIMIT
from mind_archive.paths import UnsafePathError, safe_join

logger = logging.getLogger(__name__)

router = APIRouter(tags=["conversations"])


class ConversationSummary(BaseModel):
    """One conversation in a list."""

    path: str
    title: str
    source: str
    created_at: str | None = None
    updated_at: str | None = None
    message_count: int = 0

    #: Matching text with the match wrapped in `<<` and `>>`, when searching.
    #: Delimited rather than pre-rendered as HTML so the interface decides how
    #: to display it, and no markup crosses the wire.
    snippet: str | None = None


class ConversationList(BaseModel):
    conversations: list[ConversationSummary]
    total: int
    limit: int
    offset: int

    #: How many conversations came from each provider.
    sources: dict[str, int] = Field(default_factory=dict)


class ConversationDetail(ConversationSummary):
    """A conversation with its text.

    `body` is Markdown, exactly as written to disk minus the front matter. The
    interface renders it; the API does not produce HTML.
    """

    body: str
    source_id: str | None = None


class RebuildResult(BaseModel):
    ok: bool
    message: str
    indexed: int


@router.get(
    "/api/conversations",
    response_model=ConversationList,
    summary="List or search conversations",
)
def list_conversations(
    settings: Annotated[Settings, Depends(get_settings)],
    q: Annotated[str, Query(description="Search text. Empty lists everything.")] = "",
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ConversationList:
    index = SearchIndex(settings.database_path)
    hits, total = index.search(q, limit=limit, offset=offset)

    return ConversationList(
        conversations=[ConversationSummary(**vars(hit)) for hit in hits],
        total=total,
        limit=limit,
        offset=offset,
        sources=index.sources(),
    )


@router.get(
    "/api/conversations/{path:path}",
    response_model=ConversationDetail,
    summary="Read one conversation",
)
def get_conversation(
    settings: Annotated[Settings, Depends(get_settings)],
    path: str,
) -> ConversationDetail:
    # The archive on disk is the source of truth, so the conversation is read
    # from the files rather than the index. A conversation edited by hand shows
    # its edits without waiting for a re-index.
    try:
        folder = safe_join(settings.archive_dir, *path.split("/"))
    except UnsafePathError:
        logger.warning("Refused a conversation path that escaped the archive")
        raise HTTPException(status_code=404, detail="No such conversation.") from None

    stored = read_conversation(settings.archive_dir, folder, with_body=True)
    if stored is None:
        raise HTTPException(status_code=404, detail="No such conversation.")

    return ConversationDetail(
        path=stored.path,
        title=stored.title,
        source=stored.source,
        source_id=stored.source_id,
        created_at=stored.created_at,
        updated_at=stored.updated_at,
        message_count=stored.message_count,
        body=stored.body or "",
    )


@router.post(
    "/api/index/rebuild",
    response_model=RebuildResult,
    summary="Rebuild the search index from the files on disk",
)
def rebuild_index(
    settings: Annotated[Settings, Depends(get_settings)],
) -> RebuildResult:
    """Rebuild the index by re-reading the archive.

    Safe at any time, and safe to lose: the index holds nothing that is not
    already in the files. Useful after editing conversations by hand or
    copying an archive from another machine.
    """
    settings.ensure_directories()
    indexer = Indexer(settings.archive_dir, settings.database_path)
    count = indexer.rebuild()

    return RebuildResult(
        ok=True,
        message=(
            f"Indexed {count} {'conversation' if count == 1 else 'conversations'} "
            "from your archive."
        ),
        indexed=count,
    )
