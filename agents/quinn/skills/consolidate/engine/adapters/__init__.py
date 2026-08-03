"""Adapter registry.

Each adapter maps ONE native statement format onto the canonical RawTxn shape.
Adapters are selected by the explicit `adapter` column in sources.csv; if that
column is blank the registry falls back to header-signature auto-detection.
An unknown format is never guessed at — the generic adapter flags it.
"""

from __future__ import annotations

from .base import Adapter, register, get_adapter, ADAPTERS
from . import barclays_xlsx      # noqa: F401  (import registers the adapter)
from . import monzo_csv          # noqa: F401
from . import quickbooks_csv     # noqa: F401
from . import barclaycard_pdf    # noqa: F401
from . import mortgage_pdf       # noqa: F401
from . import generic            # noqa: F401

__all__ = ["Adapter", "register", "get_adapter", "ADAPTERS"]
