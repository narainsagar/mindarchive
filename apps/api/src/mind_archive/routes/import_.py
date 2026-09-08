"""Importing a provider export.

- ``GET  /api/importers``   — which providers are supported
- ``POST /api/import``      — upload an export and archive it
- ``GET  /api/inbox``       — where the watched folder is, and what is in it
- ``POST /api/inbox/scan``  — import whatever is sitting in that folder

Two ways in, because getting an export out of ChatGPT takes days and the moment
it arrives should be as easy as possible: choose the file here, or just save it
into the inbox folder.

An uploaded file is written to a temporary location, read, and deleted. It is
never stored in the archive folder: the archive holds readable conversations,
not provider zips.

**Both routes are untrusted.** Uploads are size-capped on the way in, inbox
files are size-checked before opening, and the importer treats the contents of
either as hostile throughout. See `docs/SECURITY.md`.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from mind_archive.archive import ArchiveWriter
from mind_archive.config import Settings, get_settings
from mind_archive.events import events
from mind_archive.importers import available_importers, find_importer
from mind_archive.importers.zip_safety import safety_problem
from mind_archive.inbox import Inbox
from mind_archive.paths import safe_filename

logger = logging.getLogger(__name__)

router = APIRouter(tags=["import"])

#: Largest upload we accept. A very large ChatGPT export is a few hundred MB.
MAX_UPLOAD_BYTES = 1024 * 1024 * 1024  # 1 GB

#: How much we read at a time while saving the upload.
CHUNK_BYTES = 1024 * 1024


class ImporterInfo(BaseModel):
    name: str
    display_name: str
    supported_formats: list[str]


class ImportSummary(BaseModel):
    """What happened, in language the interface can show directly."""

    ok: bool
    message: str
    source: str | None = None

    #: Conversations that reached the archive, changed or not.
    imported: int = 0
    #: Of those: not already there, already there but grown, and identical.
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped: int = 0

    #: Descriptions of what could not be read. Never conversation content.
    problems: list[str] = []

    #: Where the conversations were written, so the user can go and look.
    archive_location: str | None = None


@router.get(
    "/api/importers",
    response_model=list[ImporterInfo],
    summary="Which providers can be imported",
)
def list_importers() -> list[ImporterInfo]:
    return [ImporterInfo(**info) for info in available_importers()]  # type: ignore[arg-type]


@router.post(
    "/api/import",
    response_model=ImportSummary,
    summary="Import an export file",
)
async def import_export(
    settings: Annotated[Settings, Depends(get_settings)],
    file: Annotated[UploadFile, File(description="A provider export")],
) -> ImportSummary:
    filename = safe_filename(file.filename or "upload", fallback="upload")

    # A temporary directory outside the archive. Removed however this ends.
    workspace = Path(tempfile.mkdtemp(prefix="mind-archive-import-"))
    upload_path = workspace / filename

    try:
        written = await _save_upload(file, upload_path)
        # Size, not name, and certainly not content.
        logger.info("Import received: %s bytes", written)

        importer = find_importer(upload_path)
        if importer is None:
            # No importer matched. That might mean the file is simply not an
            # export — or that it was refused for safety, which the user
            # deserves to be told about specifically.
            refusal = safety_problem(upload_path)
            if refusal:
                logger.warning("Refused an unsafe archive: %s", refusal)
                return ImportSummary(ok=False, message=refusal)

            return ImportSummary(
                ok=False,
                message=(
                    "That file was not recognised. Mind Archive currently reads "
                    "ChatGPT exports — the .zip you get from ChatGPT under "
                    "Settings, Data controls, Export data."
                ),
            )

        validation = importer.validate(upload_path)
        if not validation.ok:
            return ImportSummary(
                ok=False, message=validation.message, source=importer.name
            )

        parsed = importer.parse(upload_path)

        if not parsed.conversations:
            return ImportSummary(
                ok=False,
                message=parsed.summary(),
                source=importer.name,
                skipped=parsed.skipped,
                problems=parsed.problems,
            )

        try:
            settings.ensure_directories()
        except OSError as error:
            # The archive folder is gone, read-only, full, or on a drive that
            # is no longer plugged in. The user needs to know which folder and
            # what to check — not a stack trace.
            logger.error("Cannot write to the archive folder: %s", error)
            return ImportSummary(
                ok=False,
                message=(
                    "Mind Archive could not write to your archive folder "
                    f"({settings.archive_location}). Check that it exists and "
                    "that you have permission to write to it. Nothing was "
                    "imported."
                ),
                source=importer.name,
            )

        writer = ArchiveWriter(settings.archive_dir)
        stored = writer.write_all(parsed.conversations)

        events.publish(
            "archive.imported",
            {
                "source": importer.name,
                "imported": str(stored.written),
                "skipped": str(parsed.skipped + stored.skipped),
            },
        )

        logger.info(
            "Imported from %s: %s new, %s updated, %s unchanged",
            importer.name,
            stored.new,
            stored.updated,
            stored.unchanged,
        )

        total_skipped = parsed.skipped + stored.skipped
        message = stored.summary()
        if total_skipped:
            message = message.rstrip(".")
            message += f", and skipped {total_skipped} that could not be read."

        return ImportSummary(
            ok=True,
            message=message,
            source=importer.name,
            imported=stored.written,
            new=stored.new,
            updated=stored.updated,
            unchanged=stored.unchanged,
            skipped=total_skipped,
            problems=(parsed.problems + stored.problems)[:20],
            archive_location=settings.archive_location,
        )

    finally:
        shutil.rmtree(workspace, ignore_errors=True)


class InboxStatus(BaseModel):
    """Where the inbox is, and what is sitting in it."""

    folder: str
    #: False when the user has pointed the inbox at a folder of their own.
    managed: bool
    #: Whether imported files are tidied away or left where they are.
    moves_files: bool
    waiting: int


class InboxScanResult(BaseModel):
    ok: bool
    message: str
    scanned: int = 0
    imported_files: int = 0
    failed_files: int = 0
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    problems: list[str] = []


@router.get(
    "/api/inbox",
    response_model=InboxStatus,
    summary="Where the inbox is, and what is waiting in it",
)
def inbox_status(
    settings: Annotated[Settings, Depends(get_settings)],
) -> InboxStatus:
    inbox = Inbox(settings)
    return InboxStatus(
        folder=settings.inbox_location,
        managed=settings.inbox_is_managed,
        moves_files=settings.inbox_moves_files,
        waiting=len(inbox.waiting()),
    )


@router.post(
    "/api/inbox/scan",
    response_model=InboxScanResult,
    summary="Import anything waiting in the inbox",
)
def scan_inbox(
    settings: Annotated[Settings, Depends(get_settings)],
) -> InboxScanResult:
    """Import every export sitting in the inbox folder.

    Safe to call whenever. Files already imported are not imported again, and
    re-importing an export you already have changes nothing.
    """
    settings.ensure_directories()
    result = Inbox(settings).scan()

    return InboxScanResult(
        ok=result.failed_files == 0,
        message=result.summary(),
        scanned=result.scanned,
        imported_files=result.imported_files,
        failed_files=result.failed_files,
        new=result.new,
        updated=result.updated,
        unchanged=result.unchanged,
        problems=result.problems,
    )


async def _save_upload(file: UploadFile, destination: Path) -> int:
    """Stream the upload to disk, refusing anything oversized.

    Streamed rather than read whole so a large export does not have to fit in
    memory, and capped so an endless upload cannot fill the disk.
    """
    written = 0

    try:
        with destination.open("wb") as handle:
            while chunk := await file.read(CHUNK_BYTES):
                written += len(chunk)
                if written > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "That file is larger than 1 GB, which is more than "
                            "Mind Archive will accept."
                        ),
                    )
                handle.write(chunk)
    except OSError as error:
        raise HTTPException(
            status_code=500, detail="The upload could not be saved."
        ) from error

    if written == 0:
        raise HTTPException(status_code=400, detail="That file is empty.")

    return written
