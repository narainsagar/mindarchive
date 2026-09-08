"""Provider importers.

Core code never imports a provider module directly. Ask `find_importer` which
adapter can handle a file, or `get_importer` for one by name.

Adding a provider means writing an adapter that satisfies the `Importer`
protocol and adding it to `IMPORTERS`. Nothing else in the application changes.
That is the whole point — see docs/project-memory/DECISIONS.md D-002.
"""

from __future__ import annotations

from pathlib import Path

from mind_archive.importers.base import Importer, ImportResult, ValidationResult
from mind_archive.importers.chatgpt import ChatGPTImporter
from mind_archive.importers.claude import ClaudeImporter

#: Every importer the application knows about.
#:
#: Order does not matter, and that is deliberate: each `detect()` inspects the
#: *shape* of the file rather than its name. Both providers ship a file called
#: `conversations.json`, so an order-dependent registry would quietly hand a
#: Claude export to whichever importer happened to be listed first.
IMPORTERS: list[Importer] = [
    ChatGPTImporter(),
    ClaudeImporter(),
]

__all__ = [
    "IMPORTERS",
    "ImportResult",
    "Importer",
    "ValidationResult",
    "available_importers",
    "find_importer",
    "get_importer",
]


def find_importer(path: Path) -> Importer | None:
    """Which importer can read this file, if any."""
    for importer in IMPORTERS:
        if importer.detect(path):
            return importer
    return None


def get_importer(name: str) -> Importer | None:
    """Look up an importer by its short name, e.g. "chatgpt"."""
    for importer in IMPORTERS:
        if importer.name == name:
            return importer
    return None


def available_importers() -> list[dict[str, object]]:
    """Describe the importers, for the interface to list."""
    return [
        {
            "name": importer.name,
            "display_name": importer.display_name,
            "supported_formats": list(importer.supported_formats),
        }
        for importer in IMPORTERS
    ]
