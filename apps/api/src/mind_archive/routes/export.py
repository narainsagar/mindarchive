"""Taking your whole archive with you.

- ``GET /api/export`` — download everything as one zip

This exists because of a promise the project makes on its front page: your
conversations are yours, and Mind Archive is not allowed to become the only
place they can be read. An export button is what makes that true rather than
merely stated.

What comes out is not a proprietary bundle. It is exactly the folder from your
disk — the same Markdown and JSON files, in the same layout — so it can be
unzipped and read with nothing but a text editor, forever.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from mind_archive.config import Settings, get_settings
from mind_archive.events import events

logger = logging.getLogger(__name__)

router = APIRouter(tags=["export"])


@router.get(
    "/api/export",
    summary="Download your whole archive as a zip",
    response_class=FileResponse,
)
def export_archive(
    settings: Annotated[Settings, Depends(get_settings)],
) -> FileResponse:
    """Zip the archive folder and hand it over.

    Built to a temporary file rather than streamed: a personal archive is
    megabytes, the code is simpler, and a partially written stream that fails
    halfway would hand someone a corrupt archive of their own conversations.
    The temporary file is removed once the download finishes.
    """
    archive_dir = settings.archive_dir

    if not archive_dir.is_dir() or not any(archive_dir.rglob("*.md")):
        raise HTTPException(
            status_code=404,
            detail="There is nothing in your archive to export yet.",
        )

    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    filename = f"mindarchive-{stamp}.zip"

    workspace = Path(tempfile.mkdtemp(prefix="mindarchive-export-"))
    bundle = workspace / filename

    try:
        count = _write_bundle(archive_dir, bundle)
    except OSError as error:
        shutil.rmtree(workspace, ignore_errors=True)
        logger.error("Could not build the export: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Your archive could not be packaged up. Check the logs.",
        ) from error

    # Counts, never content.
    logger.info("Exported %s files from the archive", count)
    events.publish("archive.exported", {"files": str(count)})

    return FileResponse(
        bundle,
        media_type="application/zip",
        filename=filename,
        # Clean up once the response has been sent, however that goes.
        background=BackgroundTask(shutil.rmtree, workspace, ignore_errors=True),
    )


def _write_bundle(archive_dir: Path, destination: Path) -> int:
    """Zip every file in the archive, preserving the folder layout.

    Deflated rather than stored: Markdown compresses very well, and a smaller
    file is easier to keep somewhere safe.
    """
    count = 0

    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(archive_dir.rglob("*")):
            if not path.is_file():
                continue

            # Relative paths keep the archive/<source>/<conversation>/ shape,
            # so unzipping it anywhere reproduces exactly what is on disk.
            bundle.write(path, path.relative_to(archive_dir).as_posix())
            count += 1

        bundle.writestr("README.txt", _readme(count))

    return count


def _readme(count: int) -> str:
    """A note to whoever opens this in five years, possibly without us."""
    return f"""Mind Archive export
===================

Exported {datetime.now(UTC).strftime("%d %B %Y")} — {count} files.

This is your archive, exactly as it sits on disk. Nothing here needs Mind
Archive to read it.

  <provider>/<date-and-title>/conversation.md   the conversation, as Markdown
  <provider>/<date-and-title>/metadata.json     title, dates, tags

Open any conversation.md in a text editor, a Markdown viewer, or a notes
application. The metadata.json beside it holds the same information a machine
would want, including any tags you added.

There is no database in here, and nothing is missing because of that: Mind
Archive's search index is built from these files and can always be rebuilt
from them.
"""
