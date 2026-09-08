"""Importing a provider export.

Two endpoints:

- ``GET  /api/importers`` — which providers are supported
- ``POST /api/import``    — upload an export and archive it

The uploaded file is written to a temporary location, read, and deleted. It is
never stored in the archive folder: the archive holds readable conversations,
not provider zips.

**The upload is untrusted.** It is size-capped on the way in, and the importer
treats its contents as hostile throughout. See `docs/SECURITY.md`.
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
    imported: int = 0
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

        logger.info("Imported %s conversations from %s", stored.written, importer.name)

        total_skipped = parsed.skipped + stored.skipped
        message = f"Imported {stored.written} " + (
            "conversation" if stored.written == 1 else "conversations"
        )
        if total_skipped:
            message += f", skipped {total_skipped} that could not be read"
        message += "."

        return ImportSummary(
            ok=True,
            message=message,
            source=importer.name,
            imported=stored.written,
            skipped=total_skipped,
            problems=(parsed.problems + stored.problems)[:20],
            archive_location=settings.archive_location,
        )

    finally:
        shutil.rmtree(workspace, ignore_errors=True)


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
