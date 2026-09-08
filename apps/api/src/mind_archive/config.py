"""Application settings, read once from the environment.

Nothing in the application reads ``os.environ`` directly. Add new settings here
so that every option is typed, documented and discoverable in one place.

No setting in this file is a secret, and nothing here is returned to the browser
without being filtered through ``PublicConfig`` first.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

StorageMode = Literal["local", "cloud", "both"]

# Files that only exist at the top of the repository.
_ROOT_MARKERS = ("project.json", ".git", "docker-compose.yml")


def _find_repo_root() -> Path:
    """Locate the repository root, or fall back to somewhere sensible.

    Counting parent directories does not work here: in a source checkout this
    file is at ``apps/api/src/mind_archive/config.py``, but in the Docker image
    it is at ``/app/src/mind_archive/config.py``. So search upward for a marker
    instead, and fall back to the working directory when there is none — which
    is the normal case inside a container.
    """
    for directory in Path(__file__).resolve().parents:
        if any((directory / marker).exists() for marker in _ROOT_MARKERS):
            return directory
    return Path.cwd()


REPO_ROOT = _find_repo_root()


class Settings(BaseSettings):
    """Everything the backend can be configured with.

    Values come from environment variables prefixed ``MIND_ARCHIVE_``, or from
    a ``.env`` file at the repository root. Every setting has a safe default,
    so Mind Archive runs with no configuration at all.
    """

    model_config = SettingsConfigDict(
        env_prefix="MIND_ARCHIVE_",
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Where the user's archive lives.
    data_dir: Path = Field(
        default=REPO_ROOT / "data",
        description="Folder holding the archive and the metadata database.",
    )

    # What to call the archive's location when telling the user where their
    # conversations went.
    #
    # Inside a container the archive really is at /data, but on the user's own
    # machine it is ./data — and sending someone to a folder that does not
    # exist on their computer is worse than saying nothing. Docker Compose sets
    # this to the host path. Left empty, the real path is used, which is
    # correct when running natively.
    display_data_dir: str = ""

    # The server.
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = False
    log_level: Literal["debug", "info", "warning", "error"] = "info"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Cloud. Off, and it stays off unless the user changes this deliberately.
    # See docs/project-memory/DECISIONS.md D-011.
    cloud_enabled: bool = False
    storage_mode: StorageMode = "local"

    @field_validator("data_dir")
    @classmethod
    def _resolve_data_dir(cls, value: Path) -> Path:
        """Make relative paths absolute, relative to the repository root."""
        if not value.is_absolute():
            value = (REPO_ROOT / value).resolve()
        return value

    @property
    def archive_dir(self) -> Path:
        """Where conversations and documents are written, as readable files."""
        return self.data_dir / "archive"

    @property
    def database_path(self) -> Path:
        """The metadata and search index.

        This file is an index, never the only home of the user's content. It
        must always be rebuildable from the files in ``archive_dir``.
        """
        return self.data_dir / "mind_archive.db"

    @property
    def archive_location(self) -> str:
        """Where the archive is, described so the user can actually find it."""
        if self.display_data_dir:
            return f"{self.display_data_dir.rstrip('/')}/archive"
        return str(self.archive_dir)

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    def ensure_directories(self) -> None:
        """Create the archive directories if they are not there yet."""
        self.archive_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """The settings singleton. Cached, so the environment is read once."""
    return Settings()
