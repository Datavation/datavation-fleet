"""Stage 1 — inventory the configured sources BEFORE doing anything (Hobbs §5).

Report exactly what was found in each source folder/file, which adapter will
handle it, and any gaps ("folder empty / not found"), so a wrong path shows up
immediately rather than as a silent zero.

Sources are opened read-only. This stage never writes.
"""

from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field

from ..adapters import get_adapter


@dataclass
class SourceInventory:
    source_row: object
    files: list = field(default_factory=list)      # list[str] absolute resolved paths
    adapter_names: dict = field(default_factory=dict)  # path -> adapter name
    status: str = "ok"                             # ok | empty | not_found | disabled
    detail: str = ""


def _resolve(path: str, base_dir: str) -> str:
    path = os.path.expanduser(os.path.expandvars(path))
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    return os.path.normpath(path)


def resolve_source_files(source_row, base_dir: str) -> tuple[list, str, str]:
    """Return (files, status, detail) for one source row without ingesting."""
    if not source_row.is_enabled:
        return [], "disabled", "enabled=N"
    raw = _resolve(source_row.path, base_dir)
    kind = (source_row.kind or "glob").lower()

    if kind == "file":
        return ([raw], "ok", "") if os.path.isfile(raw) else ([], "not_found", raw)
    if kind == "dir":
        if not os.path.isdir(raw):
            return [], "not_found", raw
        files = sorted(
            os.path.join(raw, f) for f in os.listdir(raw)
            if os.path.isfile(os.path.join(raw, f)) and not f.startswith(".")
        )
        return (files, "ok", "") if files else ([], "empty", raw)
    # glob (default) — also handles a literal path with no wildcard
    matches = sorted(glob.glob(raw)) if any(c in raw for c in "*?[") else (
        [raw] if os.path.exists(raw) else [])
    if not matches:
        return [], ("not_found" if not any(c in raw for c in "*?[") else "empty"), raw
    files = [m for m in matches if os.path.isfile(m)]
    return (files, "ok", "") if files else ([], "empty", raw)


def build_inventory(rules, base_dir: str) -> list:
    inv = []
    for src in rules.sources:
        files, status, detail = resolve_source_files(src, base_dir)
        item = SourceInventory(source_row=src, files=files, status=status, detail=detail)
        for f in files:
            adapter = get_adapter(src, f)
            item.adapter_names[f] = adapter.name if adapter else "generic"
        inv.append(item)
    return inv


def format_inventory(inv: list) -> str:
    lines = ["Source inventory:"]
    for item in inv:
        src = item.source_row
        tag = f"[{src.world}/{src.account_id}]"
        if item.status != "ok":
            lines.append(f"  {tag} {item.status.upper()}: {item.detail or src.path}")
            continue
        lines.append(f"  {tag} {len(item.files)} file(s):")
        for f in item.files:
            lines.append(f"      - {os.path.basename(f)}  ({item.adapter_names.get(f)})")
    return "\n".join(lines)
