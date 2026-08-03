"""Stage 3 — normalise RawTxns into canonical Txns.

Collapse whitespace in descriptions, apply the account's default scope, and
carry the (already 2dp Decimal, already ISO-date) values through. Deterministic.
"""

from __future__ import annotations

import re

from ..model import Txn

_WS = re.compile(r"\s+")


def normalise(raw_txns: list, rules) -> list:
    out = []
    for r in raw_txns:
        t = Txn.from_raw(r)
        t.description = _WS.sub(" ", t.description).strip()
        t.raw_description = _WS.sub(" ", t.raw_description).strip()
        acc = rules.accounts.get(t.account_id)
        if acc:
            t.scope = acc.scope
            if not t.world:
                t.world = acc.world
        out.append(t)
    return out
