"""The Mind Archive backend.

Run it:

    uvicorn mind_archive.main:app --reload

Interactive documentation is at http://localhost:8000/docs
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mind_archive import __version__
from mind_archive.config import Settings, get_settings
from mind_archive.events import Event, events
from mind_archive.index import Indexer, supports_fts5
from mind_archive.paths import safe_join
from mind_archive.routes import config as config_routes
from mind_archive.routes import conversations as conversation_routes
from mind_archive.routes import health as health_routes
from mind_archive.routes import import_ as import_routes

logger = logging.getLogger("mind_archive")


def _make_index_handler(settings: Settings) -> Callable[[Event], None]:
    """Build the handler that indexes a freshly imported conversation.

    Subscribed rather than called directly, so importing does not need to know
    that an index exists. That is what the event bus is for (D-009).

    The settings are bound here rather than looked up inside the handler.
    `get_settings` is cached, so a handler that called it would ignore any
    override and write to the real archive — which would be wrong in a test and
    surprising anywhere else. A handler should act on the configuration its
    application was started with.
    """

    def handle(event: Event) -> None:
        path = event.payload.get("path")
        if not isinstance(path, str) or not path:
            return

        try:
            folder = safe_join(settings.archive_dir, *path.split("/"))
            Indexer(settings.archive_dir, settings.database_path).index_one(folder)
        except Exception:  # noqa: BLE001 - never fail an import over the index
            logger.exception("Could not index a conversation; rebuild to recover")

    return handle


def _settings_for(app: FastAPI) -> Settings:
    """The settings this application instance is actually running with.

    Routes receive settings through `Depends(get_settings)`, which respects
    `dependency_overrides`. Startup has no dependency injection, so it has to
    consult the same override itself — otherwise the routes and the startup
    code would be configured differently, which is a confusing way to fail.
    """
    override = app.dependency_overrides.get(get_settings)
    return override() if override else get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Start up and shut down."""
    settings = _settings_for(app)

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s  %(levelname)-7s  %(message)s",
    )

    try:
        settings.ensure_directories()
    except OSError as error:
        # A misconfigured or unavailable archive folder — an unplugged drive, a
        # path that is actually a file, a permissions problem. Start anyway and
        # say so: the interface can then explain it, and the user can fix the
        # setting without the application refusing to run.
        logger.error(
            "Cannot use the archive folder %s: %s", settings.archive_dir, error
        )

    # Log where the data is, never what is in it. See docs/SECURITY.md.
    logger.info("Mind Archive %s starting", __version__)
    logger.info("Archive folder: %s", settings.archive_dir)
    logger.info(
        "Cloud storage: %s", "enabled" if settings.cloud_enabled else "disabled"
    )

    if not supports_fts5():
        # Standard Python builds include FTS5. Saying so now beats an obscure
        # error the first time someone searches.
        logger.warning(
            "This SQLite build has no FTS5 support, so search will find nothing."
        )

    # Index anything on disk that is not in the index yet. This is what makes
    # the archive portable: copy the folder to another machine, or delete
    # mind_archive.db, and everything is rebuilt from the files.
    indexer = Indexer(settings.archive_dir, settings.database_path)
    try:
        rebuilt = indexer.ensure_built()
        if rebuilt:
            logger.info("Rebuilt the index from disk: %s conversations", rebuilt)
    except Exception:  # noqa: BLE001 - a broken index must not stop the app
        logger.exception("Could not build the search index")

    # Keep the index in step with imports.
    index_handler = _make_index_handler(settings)
    events.subscribe("conversation.created", index_handler)

    events.publish("application.started", {"version": __version__})

    yield

    events.unsubscribe("conversation.created", index_handler)

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
app.include_router(import_routes.router)
app.include_router(conversation_routes.router)


@app.get("/", tags=["health"], summary="What this is")
def root() -> dict[str, str]:
    return {
        "name": "Mind Archive",
        "tagline": "Your Personal AI Mind Archive.",
        "version": __version__,
        "documentation": "/docs",
    }
