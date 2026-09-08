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
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from mind_archive.archive.reader import read_conversation
from mind_archive.archive.writer import METADATA_FILE, write_tags
from mind_archive.config import Settings, get_settings
from mind_archive.events import events
from mind_archive.index import Indexer, SearchIndex
from mind_archive.index.search import DEFAULT_LIMIT, MAX_LIMIT
from mind_archive.paths import UnsafePathError, safe_join

logger = logging.getLogger(__name__)

router = APIRouter(tags=["conversations"])


def _folder_for(settings: Settings, path: str) -> Path:
    """Resolve a conversation path from a URL, refusing to leave the archive.

    `/api/conversations/../../etc/passwd` is a request anyone can make. A
    refusal is reported as a plain 404 so it is indistinguishable from a
    conversation that simply is not there.
    """
    try:
        return safe_join(settings.archive_dir, *path.split("/"))
    except UnsafePathError:
        logger.warning("Refused a conversation path that escaped the archive")
        raise HTTPException(status_code=404, detail="No such conversation.") from None


class ConversationSummary(BaseModel):
    """One conversation in a list."""

    path: str
    title: str
    source: str
    created_at: str | None = None
    updated_at: str | None = None
    message_count: int = 0

    #: Labels the user applied. Stored on disk, never derived from an export.
    tags: list[str] = Field(default_factory=list)

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

    #: Every tag in use, and how many conversations carry it.
    tags: dict[str, int] = Field(default_factory=dict)


class ConversationDetail(ConversationSummary):
    """A conversation with its text.

    `body` is Markdown, exactly as written to disk minus the front matter. The
    interface renders it; the API does not produce HTML.
    """

    body: str
    source_id: str | None = None


class TagUpdate(BaseModel):
    """The complete new set of tags for a conversation."""

    tags: list[str] = Field(
        default_factory=list,
        description="Replaces the existing tags entirely.",
    )


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
    tag: Annotated[str, Query(description="Show only this tag.")] = "",
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ConversationList:
    index = SearchIndex(settings.database_path)
    hits, total = index.search(q, tag=tag, limit=limit, offset=offset)

    return ConversationList(
        conversations=[ConversationSummary(**vars(hit)) for hit in hits],
        total=total,
        limit=limit,
        offset=offset,
        sources=index.sources(),
        tags=index.tags(),
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
    folder = _folder_for(settings, path)

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
        tags=stored.tags,
        body=stored.body or "",
    )


@router.put(
    "/api/conversations/{path:path}/tags",
    response_model=ConversationSummary,
    summary="Replace a conversation's tags",
)
def set_tags(
    settings: Annotated[Settings, Depends(get_settings)],
    path: str,
    update: TagUpdate,
) -> ConversationSummary:
    """Set the tags on one conversation.

    Written to that conversation's `metadata.json`, not to the database. Tags
    are the one thing here a person made rather than imported, so they belong
    on disk with everything else they own (D-025). The index is updated after,
    and could be rebuilt from the files if it were lost.
    """
    folder = _folder_for(settings, path)

    stored = read_conversation(settings.archive_dir, folder)
    if stored is None:
        raise HTTPException(status_code=404, detail="No such conversation.")

    try:
        applied = write_tags(folder / METADATA_FILE, update.tags)
    except (ValueError, OSError) as error:
        logger.error("Could not write tags: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Those tags could not be saved to your archive folder.",
        ) from error

    Indexer(settings.archive_dir, settings.database_path).index_one(folder)
    events.publish(
        "conversation.tagged", {"path": stored.path, "tags": str(len(applied))}
    )

    return ConversationSummary(
        path=stored.path,
        title=stored.title,
        source=stored.source,
        created_at=stored.created_at,
        updated_at=stored.updated_at,
        message_count=stored.message_count,
        tags=applied,
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
