"""Stage 7 — write the machine-owned ledger + the question log.

transactions.csv is regenerated every run and must be byte-identical for the
same inputs (dedup + sort guarantee that). open_items.csv is the one human table
the engine touches, and only by APPENDING new question rows keyed by a stable id
so re-runs never duplicate a question and never clobber Austen's `answer` column.
"""

from __future__ import annotations

import csv
import hashlib
import os

from ..model import TXN_COLUMNS

OPEN_ITEM_COLUMNS = ["id", "run_date", "type", "account_id", "detail", "answer"]


def write_transactions(txns, workdir: str) -> str:
    path = os.path.join(workdir, "transactions.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=TXN_COLUMNS)
        w.writeheader()
        for t in txns:
            w.writerow(t.as_row())
    return path


def _open_item_id(row: dict) -> str:
    key = "|".join([row.get("type", ""), row.get("account_id", ""), row.get("detail", "")])
    return "Q" + hashlib.sha1(key.encode()).hexdigest()[:10]


def append_open_items(new_items, workdir: str, run_date: str) -> tuple[str, int, list]:
    """Append genuinely-new question rows. Returns (path, n_added, all_rows).

    Existing rows (and Austen's answers) are preserved; a question already
    present (same stable id) is not re-added.
    """
    path = os.path.join(workdir, "open_items.csv")
    existing = []
    seen = set()
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                existing.append({c: (row.get(c, "") or "") for c in OPEN_ITEM_COLUMNS})
                seen.add(row.get("id", ""))

    added = 0
    for item in new_items:
        row = {
            "id": "", "run_date": run_date, "type": item.get("type", ""),
            "account_id": item.get("account_id", ""), "detail": item.get("detail", ""),
            "answer": "",
        }
        row["id"] = _open_item_id(row)
        if row["id"] in seen:
            continue
        seen.add(row["id"])
        existing.append(row)
        added += 1

    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=OPEN_ITEM_COLUMNS)
        w.writeheader()
        w.writerows(existing)
    return path, added, existing
