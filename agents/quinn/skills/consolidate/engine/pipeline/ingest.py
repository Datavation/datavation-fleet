"""Stage 2 — ingest each inventoried file through its adapter.

Collects RawTxns, statement ControlTotals (for the PDF tie-out), and any notes.
An adapter failure is caught and turned into a note — one bad file never aborts
the whole run.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..adapters import get_adapter


@dataclass
class IngestBundle:
    raw_txns: list = field(default_factory=list)
    control_totals: list = field(default_factory=list)
    notes: list = field(default_factory=list)


def ingest_all(inventory: list, rules) -> IngestBundle:
    bundle = IngestBundle()
    for item in inventory:
        if item.status != "ok":
            continue
        for path in item.files:
            adapter = get_adapter(item.source_row, path)
            if adapter is None:
                bundle.notes.append(f"{path}: no adapter '{item.source_row.adapter}' registered")
                continue
            try:
                result = adapter.ingest(path, item.source_row, rules)
            except Exception as e:  # defensive: never let one file kill the run
                bundle.notes.append(f"{path}: adapter '{adapter.name}' error: {e}")
                continue
            bundle.raw_txns.extend(result.transactions)
            bundle.control_totals.extend(result.control_totals)
            bundle.notes.extend(result.notes)
    return bundle
