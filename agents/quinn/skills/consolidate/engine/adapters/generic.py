"""Generic fallback adapter.

When no adapter recognises a file, we do NOT guess a column map — that is how
you silently corrupt a ledger. Instead we flag it: the file is reported as
"no adapter", and Layer B (the accountant pass) is the thing that proposes a
map once, which Austen approves and saves as a real adapter. Never invents.
"""

from __future__ import annotations

import os

from ..model import IngestResult
from .base import Adapter, register


class GenericAdapter(Adapter):
    name = "generic"
    extensions = ()

    def ingest(self, path, source_row, rules) -> IngestResult:
        base = os.path.basename(path)
        note = (f"{base}: NO ADAPTER matched (world='{source_row.world}', "
                f"account='{source_row.account_id}'). File left un-ingested. "
                f"Run Layer B to propose a column map, or set the `adapter` "
                f"column in sources.csv.")
        return IngestResult([], [], [note])


register(GenericAdapter())
