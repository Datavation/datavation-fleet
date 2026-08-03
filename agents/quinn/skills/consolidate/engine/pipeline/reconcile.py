"""Stage 6 — reconcile internal transfers between Austen's own accounts (§4.6).

Match opposite-signed amounts of equal magnitude across two different own
accounts within a +/-N-day window; mark both is_internal_transfer=Y with a
shared transfer_group. These are excluded from every spend/burn total (else the
numbers lie — a card payment or an account top-up is not spending).

Ambiguity discipline (never fabricates): if an outflow has exactly one valid
counterpart it is auto-matched; if it has several, nothing is marked and the
case is flagged to open_items for Austen to confirm.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import date


def _d(iso: str) -> date:
    return date.fromisoformat(iso)


def _group_id(a_id: str, b_id: str) -> str:
    key = "|".join(sorted([a_id, b_id]))
    return "T" + hashlib.sha1(key.encode()).hexdigest()[:8]


def reconcile(txns: list, window_days: int, rules) -> tuple[int, list]:
    """Return (n_transfer_pairs, open_item_rows). Mutates txns in place."""
    own = set(rules.accounts.keys())
    open_items = []
    used = set()

    by_mag = defaultdict(list)
    for t in txns:
        if t.account_id in own or not own:  # if no accounts.csv, treat all as own
            by_mag[abs(t.amount)].append(t)

    pairs = 0
    for mag, group in sorted(by_mag.items()):
        if mag == 0:
            continue
        outs = [t for t in group if t.amount < 0]
        ins = [t for t in group if t.amount > 0]
        for o in sorted(outs, key=lambda t: (t.date, t.txn_id)):
            if o.txn_id in used:
                continue
            matches = [
                i for i in ins
                if i.txn_id not in used
                and i.account_id != o.account_id
                and abs((_d(i.date) - _d(o.date)).days) <= window_days
            ]
            if len(matches) == 1:
                i = matches[0]
                gid = _group_id(o.txn_id, i.txn_id)
                for side in (o, i):
                    side.is_internal_transfer = "Y"
                    side.transfer_group = gid
                used.add(o.txn_id)
                used.add(i.txn_id)
                pairs += 1
            elif len(matches) > 1:
                open_items.append({
                    "type": "transfer_ambiguous",
                    "account_id": o.account_id,
                    "detail": (f"Possible internal transfer of {abs(o.amount)} on "
                               f"{o.date} ('{o.description}') has {len(matches)} candidate "
                               f"counterparts within {window_days}d — confirm which, if any."),
                })
    return pairs, open_items
