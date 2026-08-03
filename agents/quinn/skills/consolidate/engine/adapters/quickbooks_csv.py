"""QuickBooks transaction-export CSV adapter (QB READ-ONLY, as an extract source).

Rex's ruling (Quinn commission §10.5): QuickBooks is treated as one EXPORT
source into the consolidation, never a live-API dependency — a connector gap
must never block the review. This adapter reads the transaction-list /
account-register CSV a human exports from QuickBooks Online.

Two common QBO export shapes are handled:
  - a signed `Amount` column, or
  - separate `Debit`/`Credit` (or `Payment`/`Deposit`) columns.
Dates arrive as DD/MM/YYYY (UK locale) or ISO. Summary/total rows (no date, or
no parseable amount) are skipped with a note, never guessed at. The account is
keyed off the sources.csv row, NOT off anything inside the file.
"""

from __future__ import annotations

import csv

from ..model import RawTxn, IngestResult, money, parse_date
from .base import Adapter, register


class QuickBooksCsvAdapter(Adapter):
    name = "quickbooks_csv"
    extensions = (".csv",)

    # Headers that, together, are unmistakably a QuickBooks export and not a
    # bank CSV: a date plus at least one distinctly-QB column.
    _QB_HINTS = {"transaction type", "memo/description", "split", "posting", "num"}

    def _headers(self, path: str) -> list[str]:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.reader(fh)
            for row in reader:
                # QB report exports sometimes lead with title rows; take the
                # first row that looks like a header (2+ non-empty cells).
                cells = [c.strip().lower() for c in row]
                if sum(1 for c in cells if c) >= 2:
                    return cells
        return []

    def detect(self, path: str) -> bool:
        headers = set(self._headers(path))
        if "date" not in headers:
            return False
        return len(headers & self._QB_HINTS) >= 1

    def ingest(self, path, source_row, rules) -> IngestResult:
        import os
        base = os.path.basename(path)
        txns, notes = [], []
        with open(path, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.reader(fh))
        # locate the header row (QB report exports can lead with title lines)
        header_idx = None
        for i, row in enumerate(rows):
            cells = [c.strip().lower() for c in row]
            if "date" in cells:
                header_idx = i
                break
        if header_idx is None:
            return IngestResult(transactions=[], control_totals=[],
                                notes=[f"{base}: no 'Date' header found — not ingested"])
        header = [c.strip().lower() for c in rows[header_idx]]
        idx = {name: header.index(name) for name in header if name}

        def cell(row, *names):
            for n in names:
                j = idx.get(n)
                if j is not None and j < len(row):
                    v = row[j].strip()
                    if v:
                        return v
            return ""

        for lineno, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
            raw_date = cell(row, "date")
            if not raw_date:
                continue  # subtotal / footer / blank row
            # amount: signed Amount, else Credit - Debit, else Deposit - Payment
            amt_raw = cell(row, "amount")
            try:
                if amt_raw:
                    amount = money(amt_raw)
                else:
                    credit = cell(row, "credit", "deposit")
                    debit = cell(row, "debit", "payment")
                    if credit:
                        amount = money(credit)
                    elif debit:
                        amount = -abs(money(debit))
                    else:
                        notes.append(f"{base} row {lineno}: no amount column value; skipped")
                        continue
            except ValueError as e:
                notes.append(f"{base} row {lineno}: {e}; skipped")
                continue
            try:
                iso = parse_date(raw_date)
            except ValueError as e:
                notes.append(f"{base} row {lineno}: {e}; skipped")
                continue
            name = cell(row, "name", "payee")
            memo = cell(row, "memo/description", "memo", "description")
            ttype = cell(row, "transaction type", "type")
            description = name or memo or ttype or "(no description)"
            if name and memo and memo != name:
                description = f"{name} — {memo}"
            txns.append(RawTxn(
                date=iso,
                amount=amount,
                description=description,
                account_id=source_row.account_id,
                world=source_row.world,
                source_file=base,
                adapter=self.name,
                # QB's "Num" is a document number, shared by every split line of
                # one invoice — NOT a per-row id. Passing it as ext_id would make
                # dedup collapse distinct split lines (dedup keys ext_id as
                # unique-per-transaction). Leave blank: the occurrence ordinal
                # keeps genuine repeats and still dedups a re-dropped file.
                ext_id="",
            ))
        return IngestResult(transactions=txns, control_totals=[], notes=notes)


register(QuickBooksCsvAdapter())
