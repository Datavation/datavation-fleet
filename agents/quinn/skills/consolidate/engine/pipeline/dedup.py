"""Stage 4 — idempotent dedup (§4.4, the Holly-webhook lesson).

The goal is two-sided:
  * a re-dropped / overlapping statement must NOT double-count the same txn, but
  * two genuinely-identical transactions (same day, amount, merchant) must BOTH
    survive — otherwise real spend is understated.

The plain content key (date+amount+description+account) can't tell those apart.
So we disambiguate:
  * if the source gives a native transaction id (e.g. Monzo's), key on that — it
    dedups overlapping exports and keeps genuine repeats automatically;
  * otherwise, append an occurrence ordinal WITHIN a source file, so a second
    identical line in the same statement is kept, while re-dropping that exact
    file reproduces the same ordinals and still dedups.

Output is sorted (date, id) so a re-run is byte-identical regardless of read order.
"""

from __future__ import annotations

from collections import defaultdict


def dedup(txns: list) -> tuple[list, int]:
    """Return (deduped_sorted_txns, n_duplicates_removed)."""
    seen = {}
    duplicates = 0
    occurrence = defaultdict(int)   # (source_file, base_key) -> count seen so far
    for t in txns:
        base = t.base_key()
        if t.ext_id:
            key = f"id:{t.account_id}:{t.ext_id}"
        else:
            n = occurrence[(t.source_file, base)]
            occurrence[(t.source_file, base)] += 1
            key = f"{base}|{t.source_file}|{n}"
        if key in seen:
            duplicates += 1
            continue
        t.compute_id(key)
        seen[key] = t
    ordered = sorted(seen.values(), key=lambda t: (t.date, t.txn_id))
    return ordered, duplicates
