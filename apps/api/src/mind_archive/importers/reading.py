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
import re
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


#: The file an export uses to describe its own contents, if it has one.
EXPORT_MANIFEST = "export_manifest.json"

#: A shard of a logical file: `conversations-000.json` for `conversations.json`.
_SHARD = re.compile(r"^(?P<stem>.+)-(?P<index>\d{3,})\.json$", re.IGNORECASE)


def _manifest_shards(archive: zipfile.ZipFile, filename: str) -> list[str] | None:
    """The members a manifest says make up `filename`, in its own order.

    ChatGPT exports carry `export_manifest.json` with:

        "logical_files": {
          "conversations.json": {
            "files": ["conversations-000.json", ...],
            "shard_count": 3,
            "sharded": true
          }
        }

    Reading that is always better than guessing from filenames — the export is
    telling us the answer. Same principle as detecting by shape (D-027).
    """
    member = find_member(archive, EXPORT_MANIFEST)
    if member is None:
        return None

    try:
        manifest = json.loads(read_member(archive, member).decode("utf-8"))
    except (UnsafeArchiveError, ValueError, UnicodeDecodeError):
        return None

    entry = as_dict(as_dict(as_dict(manifest).get("logical_files")).get(filename))
    if not entry.get("sharded"):
        return None

    files = [name for name in as_list(entry.get("files")) if isinstance(name, str)]
    return [name for name in files if find_member(archive, name)] or None


def _guessed_shards(archive: zipfile.ZipFile, filename: str) -> list[str]:
    """Shards found by name, for an export with no manifest.

    Sorted by the numeric index rather than as text, so a hypothetical
    `-010.json` lands after `-009.json` instead of after `-001.json`.
    """
    stem = filename[: -len(".json")] if filename.lower().endswith(".json") else filename

    found: list[tuple[int, str]] = []
    for name in archive.namelist():
        match = _SHARD.match(name.rsplit("/", 1)[-1])
        if match and match.group("stem").lower() == stem.lower():
            found.append((int(match.group("index")), name))

    return [name for _, name in sorted(found)]


def conversation_members(path: Path, filename: str) -> list[str]:
    """Which members of this export hold `filename`.

    OpenAI no longer ships a single `conversations.json`. A real export now
    contains `conversations-000.json`, `-001`, `-002` and declares the mapping
    in `export_manifest.json`. Looking only for the plain name found nothing,
    so a 204-conversation export was reported as "not recognised" (D-042).

    Returns `[filename]` for the plain single-file form, so nothing about the
    old shape changes.
    """
    suffix = path.suffix.lower()

    if suffix == ".json":
        # A bare export: the file is its own only member.
        return [filename]

    if suffix != ".zip":
        # Not something that could hold conversations at all. Returning the
        # filename here made `detect` claim any file, including notes.txt.
        return []

    try:
        with inspect(path) as archive:
            if find_member(archive, filename) is not None:
                return [filename]
            return _manifest_shards(archive, filename) or _guessed_shards(
                archive, filename
            )
    except (UnsafeArchiveError, OSError, zipfile.BadZipFile):
        return []


def load_conversations(path: Path, filename: str, provider: str) -> Any:
    """Read `filename`, joining its shards if the export split it up.

    Returns the concatenated list when sharded, so every caller downstream sees
    the single list it always expected.
    """
    members = conversation_members(path, filename)

    if len(members) <= 1:
        return load_json_member(path, members[0] if members else filename, provider)

    joined: list[Any] = []
    for member in members:
        payload = load_json_member(path, member, provider)
        if not isinstance(payload, list):
            raise ImportProblem(
                f"{member} should contain a list of conversations, but it does not."
            )
        joined.extend(payload)

    return joined


def looks_like_download_manifest(payload: Any) -> bool:
    """Is this JSON a list of download links rather than conversation data?

    Claude hands you one of these instead of your conversations:

        {"version": "1.0", "total_files": 3,
         "data_files": [{"category": "conversations",
                         "filename": "conversations-000.zip",
                         "export_url": "https://claude.ai/..."}]}

    It lives here rather than in `claude.py` because **two** importers need it,
    and an adapter must never import another adapter. Claude uses it to explain
    what to download; ChatGPT uses it to decline a file that is plainly not
    its own (D-042).
    """
    entries = as_list(as_dict(payload).get("data_files"))
    if not entries:
        return False

    return any(
        as_text(as_dict(entry).get("export_url")) and as_dict(entry).get("filename")
        for entry in entries[:20]
    )


def read_download_manifest(path: Path) -> Any | None:
    """The parsed manifest if this file is one, else None. Never raises."""
    if path.suffix.lower() != ".json":
        return None
    try:
        payload = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, ValueError):
        return None
    return payload if looks_like_download_manifest(payload) else None


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

    Sharded exports are joined here too. Detection has to see the same thing
    the import will, or a real export is refused as "not recognised" while
    holding hundreds of conversations (D-042).
    """
    try:
        if path.suffix.lower() == ".zip":
            members = conversation_members(path, filename)
            if not members:
                return None

            joined: list[Any] = []
            with inspect(path) as archive:
                for name in members:
                    member = find_member(archive, name)
                    if member is None:
                        return None
                    payload = json.loads(read_member(archive, member).decode("utf-8"))
                    if not isinstance(payload, list):
                        return None
                    joined.extend(payload)
            return joined

        if path.suffix.lower() == ".json":
            data = path.read_bytes()
        else:
            return None

        payload = json.loads(data.decode("utf-8"))
    except (UnsafeArchiveError, OSError, ValueError, zipfile.BadZipFile):
        return None

    return payload if isinstance(payload, list) else None
