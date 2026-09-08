"""Is the backend running?"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from mind_archive import __version__

router = APIRouter(tags=["health"])


class Health(BaseModel):
    """A plain answer to 'is it working?'."""

    status: str
    version: str
    message: str


@router.get("/api/health", response_model=Health, summary="Check the backend")
def get_health() -> Health:
    return Health(
        status="ok",
        version=__version__,
        message="Mind Archive is running.",
    )
