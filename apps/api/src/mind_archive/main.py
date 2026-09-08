"""The Mind Archive backend.

Run it:

    uvicorn mind_archive.main:app --reload

Interactive documentation is at http://localhost:8000/docs
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mind_archive import __version__
from mind_archive.config import get_settings
from mind_archive.events import events
from mind_archive.routes import config as config_routes
from mind_archive.routes import health as health_routes

logger = logging.getLogger("mind_archive")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Start up and shut down."""
    settings = get_settings()

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s  %(levelname)-7s  %(message)s",
    )

    settings.ensure_directories()

    # Log where the data is, never what is in it. See docs/SECURITY.md.
    logger.info("Mind Archive %s starting", __version__)
    logger.info("Archive folder: %s", settings.archive_dir)
    logger.info(
        "Cloud storage: %s", "enabled" if settings.cloud_enabled else "disabled"
    )

    events.publish("application.started", {"version": __version__})

    yield

    events.publish("application.stopping", {"version": __version__})
    logger.info("Mind Archive stopped")


app = FastAPI(
    title="Mind Archive",
    description=(
        "Your personal AI mind archive. Local-first, privacy-first, and yours.\n\n"
        "This API runs on your own computer. It has no authentication because it "
        "is meant for a single user on localhost — do not expose it to a network "
        "you do not control."
    ),
    version=__version__,
    lifespan=lifespan,
)

# Only the local web interface may call this API. Widening this is a security
# decision, not a convenience one: the API has no authentication.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(health_routes.router)
app.include_router(config_routes.router)


@app.get("/", tags=["health"], summary="What this is")
def root() -> dict[str, str]:
    return {
        "name": "Mind Archive",
        "tagline": "Your Personal AI Mind Archive.",
        "version": __version__,
        "documentation": "/docs",
    }
