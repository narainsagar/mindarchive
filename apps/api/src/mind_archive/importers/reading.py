"""Reading untrusted JSON, shared by every importer.

These helpers were private to the ChatGPT importer until a second provider
needed exactly the same ones. That is the right moment to share code — when
two real callers want it, not when one might.

The rule they all follow: **return a safe default rather than raise.** A
provider export is a file from outside the application, and one odd field
should never take down an import of four hundred conversations. What cannot be
read is skipped and reported.
"""

from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mind_archive.importers.zip_safety import (
    UnsafeArchiveError,
    find_member,
    inspect,
    read_member,
)


class ImportProblem(Exception):
    """Something in the file stopped the import, described for a person."""


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def epoch_to_time(value: Any) -> datetime | None:
    """Convert a Unix timestamp, as ChatGPT uses, or give up.

    A missing or nonsensical timestamp becomes `None`. An archive people will
    read in ten years is better with a gap than with a fabricated date.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=UTC)
    except (ValueError, OSError, OverflowError):
        return None


def iso_to_time(value: Any) -> datetime | None:
    """Convert an ISO 8601 timestamp, as Claude uses, or give up.

    Handles the trailing ``Z`` that `datetime.fromisoformat` refused before
    Python 3.11, and assumes UTC when no offset is given — every provider
    export seen so far is in UTC, and guessing a local zone would be worse
    than assuming the documented one.
    """
    text = as_text(value)
    if not text:
        return None

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None

    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def load_json_member(path: Path, filename: str, provider: str) -> Any:
    """Read one JSON file from an export zip, or from a bare JSON file.

    Shared because every provider so far ships a zip containing a single JSON
    file of conversations, and the reading, size-capping and error wording are
    identical. What is *inside* that JSON is where they differ, and that stays
    in each importer.
    """
    if path.suffix.lower() == ".zip":
        with inspect(path) as archive:
            member = find_member(archive, filename)
            if member is None:
                raise ImportProblem(
                    f"That zip does not contain {filename}, so it is not "
                    f"{provider} export."
                )
            data = read_member(archive, member)
    else:
        try:
            data = path.read_bytes()
        except OSError as error:
            raise ImportProblem("That file could not be read.") from error

    try:
        return json.loads(data.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ImportProblem(f"{filename} is not valid UTF-8 text.") from error
    except json.JSONDecodeError as error:
        raise ImportProblem(
            f"{filename} is not valid JSON (line {error.lineno})."
        ) from error


def has_member(path: Path, filename: str) -> bool:
    """Is this file named, or does this zip contain, `filename`? Never raises.

    Separate from `peek_conversations` so an importer can tell "this is not our
    kind of file" apart from "this is our kind of file and it is broken". The
    second deserves a real explanation rather than "not recognised".
    """
    try:
        if path.suffix.lower() == ".zip":
            with inspect(path) as archive:
                return find_member(archive, filename) is not None
        return path.suffix.lower() == ".json"
    except (UnsafeArchiveError, OSError, zipfile.BadZipFile):
        return False


def peek_conversations(path: Path, filename: str) -> list[Any] | None:
    """Read a conversation list for `detect()`, without ever raising.

    Detection has to look *inside* the file. Two providers now ship a file
    called `conversations.json`, so matching on the name alone would have one
    importer confidently claiming another's export — which is exactly what
    happened before this existed.
    """
    try:
        if path.suffix.lower() == ".zip":
            with inspect(path) as archive:
                member = find_member(archive, filename)
                if member is None:
                    return None
                data = read_member(archive, member)
        elif path.suffix.lower() == ".json":
            data = path.read_bytes()
        else:
            return None

        payload = json.loads(data.decode("utf-8"))
    except (UnsafeArchiveError, OSError, ValueError, zipfile.BadZipFile):
        return None

    return payload if isinstance(payload, list) else None
