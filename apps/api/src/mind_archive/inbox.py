"""The inbox: a folder you drop exports into.

Getting an export out of ChatGPT is slow — OpenAI's own email says it "may take
a few days" — so the least Mind Archive can do is make the moment it finally
arrives effortless. Save the file into the inbox and it imports itself. No
upload, no browser, no clicking.

Two shapes, chosen by configuration:

**A folder Mind Archive owns** (the default, `data/inbox`). Imported files are
tidied into `imported/`, failures into `failed/` with a note saying why. Moving
them is the feedback: an empty inbox means everything is in.

**A folder you already keep exports in** (`MIND_ARCHIVE_INBOX_DIR`). Files are
left exactly where they are — moving things out of somebody's Downloads folder
would be rude — and a small ledger records what has already been imported so
nothing is done twice.

**Everything in the inbox is untrusted**, exactly like an upload. Same
importers, same zip-safety checks, same size caps. A folder on someone's
computer is not a promise about what is in it.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from mind_archive.archive import ArchiveWriter
from mind_archive.config import Settings
from mind_archive.importers import find_importer
from mind_archive.importers.zip_safety import safety_problem

logger = logging.getLogger(__name__)

#: Files we will even look at. Anything else in the folder is not ours.
IMPORTABLE_SUFFIXES = {".zip", ".json"}

#: Where imported and failed files are moved, when we are moving them.
IMPORTED_DIR = "imported"
FAILED_DIR = "failed"

#: Records what has already been imported when files are left in place.
LEDGER_FILE = ".mind-archive-imported.json"

#: Largest file the inbox will open, matching the upload limit.
MAX_FILE_BYTES = 1024 * 1024 * 1024  # 1 GB

#: A file still being written to has no business being imported. Give a
#: download a moment to finish before touching it.
SETTLE_SECONDS = 2.0


@dataclass
class InboxResult:
    """What the inbox did, in terms the interface can show."""

    scanned: int = 0
    imported_files: int = 0
    failed_files: int = 0
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    problems: list[str] = field(default_factory=list)

    def note_problem(self, problem: str) -> None:
        if len(self.problems) < 20:
            self.problems.append(problem)

    def summary(self) -> str:
        if self.scanned == 0:
            return "Nothing new in your inbox."

        if self.imported_files == 0:
            return (
                f"Could not read {self.failed_files} "
                f"{'file' if self.failed_files == 1 else 'files'} in your inbox."
            )

        parts: list[str] = []
        if self.new:
            parts.append(f"{self.new} new")
        if self.updated:
            parts.append(f"{self.updated} updated")
        if self.unchanged:
            parts.append(f"{self.unchanged} already in your archive")

        files = (
            f"{self.imported_files} {'file' if self.imported_files == 1 else 'files'}"
        )
        if not parts:
            return f"Read {files}, but found no conversations."
        return f"Read {files}: " + ", ".join(parts) + "."


class Inbox:
    """Imports whatever appears in the watched folder."""

    def __init__(self, settings: Settings, settle_seconds: float | None = None) -> None:
        self.settings = settings
        self.folder = settings.inbox_dir
        self.moves_files = settings.inbox_moves_files
        # Injectable so tests do not spend two seconds per file waiting for a
        # download that was never happening.
        self.settle_seconds = (
            SETTLE_SECONDS if settle_seconds is None else settle_seconds
        )

    # -- Scanning -----------------------------------------------------------

    def waiting(self) -> list[Path]:
        """Files that look importable and have not been imported yet."""
        if not self.folder.is_dir():
            return []

        ledger = self._read_ledger()
        found: list[Path] = []

        try:
            entries = sorted(self.folder.iterdir())
        except OSError as error:
            logger.warning("Could not read the inbox: %s", error)
            return []

        for path in entries:
            if not path.is_file():
                continue
            if path.suffix.lower() not in IMPORTABLE_SUFFIXES:
                continue
            if path.name.startswith("."):
                continue
            if self._ledger_key(path) in ledger:
                continue
            found.append(path)

        return found

    def scan(self) -> InboxResult:
        """Import everything waiting. Never raises."""
        result = InboxResult()

        for path in self.waiting():
            if not self._has_settled(path):
                # Probably still downloading. It will be picked up next scan.
                logger.info("Skipping a file that is still being written")
                continue

            result.scanned += 1
            try:
                self._import_file(path, result)
            except Exception as error:  # noqa: BLE001 - one file, not the scan
                logger.exception("Unexpected failure importing an inbox file")
                result.failed_files += 1
                result.note_problem(
                    f"{path.name} could not be imported ({type(error).__name__})."
                )
                self._move(path, FAILED_DIR, reason=str(error))

        return result

    # -- Importing one file -------------------------------------------------

    def _import_file(self, path: Path, result: InboxResult) -> None:
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                self._fail(path, result, f"{path.name} is larger than 1 GB.")
                return
        except OSError:
            self._fail(path, result, f"{path.name} could not be read.")
            return

        importer = find_importer(path)
        if importer is None:
            refusal = safety_problem(path)
            self._fail(
                path,
                result,
                refusal or f"{path.name} is not an export Mind Archive recognises.",
            )
            return

        validation = importer.validate(path)
        if not validation.ok:
            self._fail(path, result, f"{path.name}: {validation.message}")
            return

        parsed = importer.parse(path)
        if not parsed.conversations:
            self._fail(path, result, f"{path.name}: {parsed.summary()}")
            return

        self.settings.ensure_directories()
        stored = ArchiveWriter(self.settings.archive_dir).write_all(
            parsed.conversations
        )

        result.imported_files += 1
        result.new += stored.new
        result.updated += stored.updated
        result.unchanged += stored.unchanged

        for problem in (parsed.problems + stored.problems)[:5]:
            result.note_problem(problem)

        # Counts and the file name, never conversation content.
        logger.info(
            "Imported an inbox file: %s new, %s updated, %s unchanged",
            stored.new,
            stored.updated,
            stored.unchanged,
        )

        self._finish(path, IMPORTED_DIR)

    def _fail(self, path: Path, result: InboxResult, message: str) -> None:
        logger.warning("Inbox file rejected: %s", message)
        result.failed_files += 1
        result.note_problem(message)
        self._move(path, FAILED_DIR, reason=message)

    # -- Moving, or remembering ---------------------------------------------

    def _finish(self, path: Path, destination: str) -> None:
        if self.moves_files:
            self._move(path, destination)
        else:
            self._remember(path)

    def _move(self, path: Path, destination: str, reason: str | None = None) -> None:
        """Tidy a file away, or remember it if we are not moving things."""
        if not self.moves_files:
            self._remember(path)
            return

        target_dir = self.folder / destination
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            target = _free_name(target_dir / path.name)
            path.rename(target)

            if reason:
                target.with_suffix(target.suffix + ".txt").write_text(
                    reason + "\n", encoding="utf-8"
                )
        except OSError as error:
            # Failing to tidy up must not fail the import. Remember the file
            # instead so the next scan does not repeat the work.
            logger.warning("Could not move an inbox file: %s", error)
            self._remember(path)

    def _remember(self, path: Path) -> None:
        ledger = self._read_ledger()
        ledger[self._ledger_key(path)] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._write_ledger(ledger)

    def _ledger_key(self, path: Path) -> str:
        """Identify a file well enough to not import it twice.

        Name, size and modification time. Not a hash: hashing a gigabyte on
        every scan to detect a case that barely happens is a poor trade, and
        the consequence of being wrong is a re-import, which is now harmless —
        unchanged conversations are skipped.
        """
        try:
            stat = path.stat()
            return f"{path.name}:{stat.st_size}:{int(stat.st_mtime)}"
        except OSError:
            return path.name

    def _read_ledger(self) -> dict[str, str]:
        if self.moves_files:
            return {}

        ledger_path = self.folder / LEDGER_FILE
        try:
            data = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return {}

        return data if isinstance(data, dict) else {}

    def _write_ledger(self, ledger: dict[str, str]) -> None:
        try:
            (self.folder / LEDGER_FILE).write_text(
                json.dumps(ledger, indent=2) + "\n", encoding="utf-8"
            )
        except OSError as error:
            logger.warning("Could not update the inbox ledger: %s", error)

    def _has_settled(self, path: Path) -> bool:
        """Has this file finished being written?

        A download in progress grows. Comparing size across a short pause is
        crude but costs nothing and avoids importing half a zip.
        """
        if self.settle_seconds <= 0:
            return True

        try:
            first = path.stat().st_size
            time.sleep(self.settle_seconds)
            return path.stat().st_size == first
        except OSError:
            return False


def _free_name(target: Path) -> Path:
    """A path that does not already exist, suffixing if it does."""
    if not target.exists():
        return target

    for number in range(2, 1000):
        candidate = target.with_name(f"{target.stem}-{number}{target.suffix}")
        if not candidate.exists():
            return candidate

    return target.with_name(f"{target.stem}-{int(time.time())}{target.suffix}")
