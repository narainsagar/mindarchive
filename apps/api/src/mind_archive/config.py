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
        # A field with an explicit alias skips the prefix, so it can still be
        # set by its own name in code and in tests.
        populate_by_name=True,
    )

    # Where the user's archive lives.
    data_dir: Path = Field(
        default=REPO_ROOT / "data",
        description="Folder holding the archive and the metadata database.",
    )

    # A folder Mind Archive watches for provider exports. Anything dropped in
    # is imported.
    #
    # Empty means `data/inbox`, a folder Mind Archive owns. You can point this
    # at a folder you already keep exports in — but then Mind Archive reads
    # that folder, so choose it deliberately. Only .zip and .json files are
    # ever opened. See project-memory/DECISIONS.md D-023.
    inbox_dir_setting: str = Field(
        default="",
        alias="MIND_ARCHIVE_INBOX_DIR",
        description="Folder watched for exports. Empty means data/inbox.",
    )

    # Leave imported files where they are instead of moving them into
    # `imported/`.
    #
    # Turn this on if the inbox is a folder you use for other things — moving
    # files out of somebody's Downloads folder would be rude. A small ledger
    # then records what has already been imported so nothing is done twice.
    inbox_keep_files: bool = False

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
    # See project-memory/DECISIONS.md D-011.
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
    def inbox_dir(self) -> Path:
        """The folder watched for provider exports.

        Defaults to `data/inbox`. A configured relative path is resolved from
        the repository root, the same as `data_dir`.
        """
        if not self.inbox_dir_setting.strip():
            return self.data_dir / "inbox"

        configured = Path(self.inbox_dir_setting.strip()).expanduser()
        if not configured.is_absolute():
            configured = REPO_ROOT / configured
        return configured

    @property
    def inbox_is_managed(self) -> bool:
        """Is the inbox a folder Mind Archive owns?

        When it is, imported files are tidied into `imported/`. When the user
        has pointed it somewhere of their own, files are left alone unless they
        ask otherwise.
        """
        return not self.inbox_dir_setting.strip()

    @property
    def inbox_moves_files(self) -> bool:
        return self.inbox_is_managed and not self.inbox_keep_files

    @property
    def inbox_location(self) -> str:
        """Where the inbox is, described so the user can actually find it.

        Same reasoning as `archive_location`: inside a container the inbox is
        at /data/inbox, but the folder the person can drop a file into is
        ./data/inbox on their own machine.
        """
        if self.display_data_dir and self.inbox_is_managed:
            return f"{self.display_data_dir.rstrip('/')}/inbox"
        return str(self.inbox_dir)

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
        """Create the archive directories if they are not there yet.

        The inbox is only created when Mind Archive owns it. If the user has
        pointed it at a folder of their own, it is theirs to create — silently
        making directories somewhere a person chose is not our business.
        """
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        if self.inbox_is_managed:
            self.inbox_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """The settings singleton. Cached, so the environment is read once."""
    return Settings()
