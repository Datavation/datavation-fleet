"""Redaction pass (§2.4, §8) — the ONLY data Layer B may ever read.

Masks anything that looks like an account number or sort code out of the
description before it can reach a model. Keeps date, amount, description
(masked), category, subcategory, scope, world, transfer flag. Drops the raw
description entirely (it is the un-normalised source string most likely to
carry a full number). Account *ids* (e.g. 'barclays_personal') are opaque
labels, not numbers, so they are safe to keep.

The redacted export is written under WORKDIR/_redacted/ and is the single
model-facing artefact.
"""

from __future__ import annotations

import csv
import os
import re

# sort code dd-dd-dd (or dd dd dd), and any run of 6+ digits (account numbers,
# card numbers, long references)
_SORTCODE = re.compile(r"\b\d{2}[-\s]\d{2}[-\s]\d{2}\b")
_LONGNUM = re.compile(r"\d{6,}")

REDACTED_COLUMNS = [
    "date", "amount", "description", "category", "subcategory",
    "scope", "world", "is_internal_transfer",
]


def mask_text(s: str) -> str:
    if not s:
        return s
    s = _SORTCODE.sub("**-**-**", s)
    s = _LONGNUM.sub("######", s)
    return s


def redacted_rows(txns) -> list:
    rows = []
    for t in txns:
        rows.append({
            "date": t.date,
            "amount": f"{t.amount:.2f}",
            "description": mask_text(t.description),
            "category": t.category,
            "subcategory": t.subcategory,
            "scope": t.scope,
            "world": t.world,
            "is_internal_transfer": t.is_internal_transfer,
        })
    return rows


def write_redacted(txns, workdir: str) -> str:
    out_dir = os.path.join(workdir, "_redacted")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "transactions_redacted.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=REDACTED_COLUMNS)
        w.writeheader()
        w.writerows(redacted_rows(txns))
    return path
