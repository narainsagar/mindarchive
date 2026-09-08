"""What the interface is allowed to know about the configuration.

This endpoint exists so Mind Archive can tell the user plainly where their data
is and whether anything is being sent anywhere.

**Never add a secret to this response.** It goes straight to the browser.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from mind_archive import __version__
from mind_archive.config import Settings, get_settings

router = APIRouter(tags=["config"])


class PublicConfig(BaseModel):
    """Configuration that is safe to show in the browser.

    Every field here is deliberately non-sensitive. If you are tempted to add
    something that is not, add it somewhere else.
    """

    version: str
    storage_mode: str
    cloud_enabled: bool
    archive_location: str
    database_location: str
    privacy_note: str


@router.get("/api/config", response_model=PublicConfig, summary="Where your data is")
def get_config(
    settings: Annotated[Settings, Depends(get_settings)],
) -> PublicConfig:
    if settings.cloud_enabled:
        privacy_note = (
            "Cloud storage is enabled. Some of your archive may be copied to the "
            "storage you configured."
        )
    else:
        privacy_note = (
            "Your archive is stored only on this computer. Nothing is uploaded "
            "anywhere."
        )

    return PublicConfig(
        version=__version__,
        storage_mode=settings.storage_mode,
        cloud_enabled=settings.cloud_enabled,
        archive_location=str(settings.archive_dir),
        database_location=str(settings.database_path),
        privacy_note=privacy_note,
    )
