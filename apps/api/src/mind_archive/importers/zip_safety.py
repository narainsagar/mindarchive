"""Reading zip archives that someone else produced.

A provider export is a file from outside the application. Even when it really
did come from ChatGPT, it reached us through a download folder, so it has to be
treated as though someone hostile wrote it.

The three things that go wrong with zip files:

**Zip slip.** An entry named ``../../.ssh/authorized_keys`` writes outside the
directory you meant. We never extract to a path derived from an entry name — we
read named members into memory and nothing else.

**Zip bombs.** A few kilobytes that decompress into many gigabytes. We check the
declared uncompressed size before reading, cap what we will read, and refuse
absurd compression ratios.

**Sheer size.** An export with a million entries, or one 4 GB member, exhausts
memory. Everything is bounded.

See `docs/SECURITY.md`.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

#: An export with more entries than this is not something we will process.
MAX_ENTRIES = 50_000

#: Largest single member we will read into memory.
MAX_MEMBER_BYTES = 500 * 1024 * 1024  # 500 MB

#: Largest total uncompressed size we will accept across the archive.
MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB

#: A member compressing better than this is treated as a bomb. Real JSON
#: compresses around 10-20x; 200x is not a real export.
MAX_COMPRESSION_RATIO = 200


class UnsafeArchiveError(Exception):
    """The archive is malformed, hostile, or too large to process safely."""


def _entry_is_suspicious(name: str) -> bool:
    """Reject entry names that try to escape, before they are ever used."""
    if not name or name.endswith("/"):
        return False  # Directories are harmless; we never extract them.
    if name.startswith("/") or name.startswith("\\"):
        return True
    if ".." in Path(name.replace("\\", "/")).parts:
        return True
    if "\x00" in name:
        return True
    # Windows drive letters, e.g. "C:/passwords.txt"
    return len(name) > 1 and name[1] == ":"


def inspect(path: Path) -> zipfile.ZipFile:
    """Open a zip file and check it is safe to read.

    Returns the open archive; the caller is responsible for closing it, which
    `read_member` and `find_member` handle when used with a context manager.

    Raises `UnsafeArchiveError` if the archive is not something we will touch.
    """
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile as error:
        raise UnsafeArchiveError("That file is not a valid zip archive.") from error
    except OSError as error:
        raise UnsafeArchiveError("That file could not be opened.") from error

    try:
        entries = archive.infolist()
    except Exception as error:  # noqa: BLE001 - malformed central directory
        archive.close()
        raise UnsafeArchiveError(
            "That archive's contents could not be read."
        ) from error

    if len(entries) > MAX_ENTRIES:
        archive.close()
        raise UnsafeArchiveError(
            f"That archive has {len(entries)} entries, which is more than "
            f"Mind Archive will process ({MAX_ENTRIES})."
        )

    total = 0
    for entry in entries:
        if _entry_is_suspicious(entry.filename):
            archive.close()
            raise UnsafeArchiveError(
                "That archive contains a file path that tries to write outside "
                "the folder it was extracted to. It has not been imported."
            )

        total += entry.file_size
        if total > MAX_TOTAL_BYTES:
            archive.close()
            raise UnsafeArchiveError(
                "That archive is larger uncompressed than Mind Archive will "
                "process (2 GB)."
            )

        if entry.compress_size > 0:
            ratio = entry.file_size / entry.compress_size
            if ratio > MAX_COMPRESSION_RATIO and entry.file_size > 10 * 1024 * 1024:
                archive.close()
                raise UnsafeArchiveError(
                    "That archive contains a file that expands far more than a "
                    "real export would. It has not been imported."
                )

    return archive


def safety_problem(path: Path) -> str | None:
    """Why this archive was refused, if it was — otherwise `None`.

    `Importer.detect` deliberately never raises, so a hostile archive simply
    fails to match any importer. Without this, the user would be told their
    file was "not recognised", which is both unhelpful and untrue: it was
    recognised and rejected. Being told *why* is the difference between a
    confusing dead end and a clear answer.
    """
    if path.suffix.lower() != ".zip":
        return None

    try:
        with inspect(path):
            return None
    except UnsafeArchiveError as error:
        return str(error)


def find_member(archive: zipfile.ZipFile, filename: str) -> str | None:
    """Locate a member by filename, at the root or one folder down.

    ChatGPT exports sometimes wrap everything in a folder named after the
    export date, so `conversations.json` is not always at the top level.
    """
    candidates = [
        entry.filename
        for entry in archive.infolist()
        if not entry.is_dir()
        and Path(entry.filename.replace("\\", "/")).name == filename
    ]
    if not candidates:
        return None

    # Prefer the shallowest match, so a stray copy in a subfolder does not win.
    return min(candidates, key=lambda name: name.count("/"))


def read_member(archive: zipfile.ZipFile, member: str) -> bytes:
    """Read one member into memory, bounded.

    The declared size is checked first, then the read itself is capped — a
    malformed archive can declare one size and contain another.
    """
    try:
        info = archive.getinfo(member)
    except KeyError as error:
        raise UnsafeArchiveError(f"'{member}' is not in that archive.") from error

    if info.file_size > MAX_MEMBER_BYTES:
        raise UnsafeArchiveError(
            f"'{Path(member).name}' is larger than Mind Archive will read "
            f"({MAX_MEMBER_BYTES // (1024 * 1024)} MB)."
        )

    try:
        with archive.open(member) as handle:
            data = handle.read(MAX_MEMBER_BYTES + 1)
    except (zipfile.BadZipFile, OSError, EOFError) as error:
        raise UnsafeArchiveError(
            f"'{Path(member).name}' could not be read from that archive."
        ) from error

    if len(data) > MAX_MEMBER_BYTES:
        raise UnsafeArchiveError(
            f"'{Path(member).name}' is larger than it claimed to be, and has "
            "not been read."
        )

    return data
