"""The importer interface.

Every AI provider is an adapter behind this interface. Core code never imports a
provider-specific module — it asks the registry which importer can handle a
file, and gets one of these back.

The interface is kept small on purpose. It will be generalised properly in
Milestone 5, against a genuine second implementation rather than a guess at what
a second one might need.

**Everything an importer receives is untrusted.** Provider exports are files
from outside the application, and from here on they are parsed. See
`docs/SECURITY.md`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

from mind_archive.models import Conversation


@dataclass
class ValidationResult:
    """Whether a file can be imported, in language a person can read."""

    ok: bool
    message: str

    #: How many conversations were found, when that is known before importing.
    conversation_count: int | None = None

    @classmethod
    def valid(cls, message: str, count: int | None = None) -> ValidationResult:
        return cls(ok=True, message=message, conversation_count=count)

    @classmethod
    def invalid(cls, message: str) -> ValidationResult:
        return cls(ok=False, message=message)


@dataclass
class ImportResult:
    """What happened during an import.

    ``skipped`` and ``problems`` matter as much as ``imported``. A real export
    will contain things we cannot parse, and quietly dropping them would be
    worse than saying so.

    Problems describe the *shape* of what went wrong, never the content of a
    conversation.
    """

    imported: int = 0
    skipped: int = 0
    problems: list[str] = field(default_factory=list)
    conversations: list[Conversation] = field(default_factory=list)

    def note_problem(self, problem: str) -> None:
        self.skipped += 1
        # Bound the list: a corrupt export could otherwise produce one problem
        # per conversation and a report nobody can read.
        if len(self.problems) < 50:
            self.problems.append(problem)

    def summary(self) -> str:
        """A plain-language summary, for the interface to show."""
        if self.imported == 0 and self.skipped == 0:
            return "No conversations were found in that file."

        parts = [
            f"Imported {self.imported} "
            f"{'conversation' if self.imported == 1 else 'conversations'}"
        ]
        if self.skipped:
            parts.append(f"skipped {self.skipped} that could not be read")
        return ", ".join(parts) + "."


@runtime_checkable
class Importer(Protocol):
    """What every provider adapter must offer."""

    #: Short lowercase identifier, stored on each conversation: "chatgpt".
    name: str

    #: Human-readable, for the interface: "ChatGPT".
    display_name: str

    #: File extensions this importer can open: [".zip", ".json"].
    supported_formats: list[str]

    def detect(self, path: Path) -> bool:
        """Does this file look like it belongs to this provider?

        Cheap and non-destructive. Never raises — a file it cannot read is
        simply not a match.
        """
        ...

    def validate(self, path: Path) -> ValidationResult:
        """Can this file be imported, and roughly what is in it?

        Runs before importing so the user finds out about a problem before
        anything is written to disk.
        """
        ...

    def parse(self, path: Path) -> ImportResult:
        """Read the file and normalise it into `Conversation` objects.

        Does not write anything. Storing what comes back is the archive's job,
        which keeps parsing testable without touching the filesystem.
        """
        ...
