"""Adapter base class + registry + selection logic."""

from __future__ import annotations

import os
from typing import Optional

from ..model import IngestResult


ADAPTERS: dict = {}


def register(adapter: "Adapter") -> "Adapter":
    ADAPTERS[adapter.name] = adapter
    return adapter


class Adapter:
    """Base adapter. Subclasses set `name` and implement detect()/ingest()."""

    name = "base"
    #: file extensions this adapter can read (lowercase, with dot)
    extensions: tuple = ()

    def detect(self, path: str) -> bool:
        """Return True if this adapter recognises the file at `path`.

        Used only when sources.csv leaves the adapter column blank. Should be
        cheap and side-effect-free (peek at header, not parse the whole file).
        """
        return False

    def ingest(self, path: str, source_row, rules) -> IngestResult:  # pragma: no cover
        raise NotImplementedError


def get_adapter(source_row, path: str) -> Optional["Adapter"]:
    """Pick the adapter for a source file.

    Explicit `adapter` name in sources.csv wins. Otherwise auto-detect by asking
    each registered adapter (except the generic fallback) whether it recognises
    the file. If none do, return the generic adapter so the file is flagged, not
    silently dropped.
    """
    explicit = (getattr(source_row, "adapter", "") or "").strip()
    if explicit:
        return ADAPTERS.get(explicit)

    ext = os.path.splitext(path)[1].lower()
    for name, adapter in ADAPTERS.items():
        if name == "generic":
            continue
        if adapter.extensions and ext not in adapter.extensions:
            continue
        try:
            if adapter.detect(path):
                return adapter
        except Exception:
            # A detection probe must never crash the run; treat as "not mine".
            continue
    return ADAPTERS.get("generic")
