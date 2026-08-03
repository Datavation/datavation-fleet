"""Monzo Business CSV adapter (Rex Home Services + Datavation share this format).

Monzo exports carry a signed `Amount` column (out negative, in positive) plus
`Date` (DD/MM/YYYY), `Name`, and `Description`. We detect on the header
signature so a re-named file still routes correctly, and we key the account off
the sources.csv row (world/account_id), NOT off anything inside the file.
"""

from __future__ import annotations

import csv

from ..model import RawTxn, IngestResult, money, parse_date
from .base import Adapter, register


class MonzoCsvAdapter(Adapter):
    name = "monzo_csv"
    extensions = (".csv",)

    # Columns that, taken together, are unmistakably a Monzo export.
    _SIGNATURE = {"date", "amount"}
    _MONZO_HINTS = {"transaction id", "money out", "money in", "local amount", "emoji"}

    def _headers(self, path: str) -> list[str]:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.reader(fh)
            for row in reader:
                return [c.strip().lower() for c in row]
        return []

    def detect(self, path: str) -> bool:
        headers = set(self._headers(path))
        if not self._SIGNATURE.issubset(headers):
            return False
        # require at least one distinctly-Monzo column to avoid grabbing every CSV
        return bool(headers & self._MONZO_HINTS)

    def ingest(self, path, source_row, rules) -> IngestResult:
        import os
        base = os.path.basename(path)
        txns, notes = [], []
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            cols = {c.strip().lower(): c for c in (reader.fieldnames or [])}
            date_col = cols.get("date")
            amt_col = cols.get("amount")
            name_col = cols.get("name") or cols.get("description")
            desc_col = cols.get("description") or cols.get("name")
            out_col, in_col = cols.get("money out"), cols.get("money in")
            id_col = cols.get("transaction id")
            for i, row in enumerate(reader, start=2):
                raw_date = (row.get(date_col) or "").strip() if date_col else ""
                if not raw_date:
                    continue
                # amount: prefer signed Amount; else derive from Money Out/In
                amt_raw = (row.get(amt_col) or "").strip() if amt_col else ""
                try:
                    if amt_raw:
                        amount = money(amt_raw)
                    elif out_col or in_col:
                        out_v = (row.get(out_col) or "").strip() if out_col else ""
                        in_v = (row.get(in_col) or "").strip() if in_col else ""
                        amount = money(in_v) if in_v else -abs(money(out_v))
                    else:
                        notes.append(f"{base} row {i}: no amount column; skipped")
                        continue
                except ValueError as e:
                    notes.append(f"{base} row {i}: {e}; skipped")
                    continue
                name = (row.get(name_col) or "").strip() if name_col else ""
                desc = (row.get(desc_col) or "").strip() if desc_col else ""
                description = name or desc or "(no description)"
                if name and desc and desc != name:
                    description = f"{name} — {desc}"
                try:
                    iso = parse_date(raw_date)
                except ValueError as e:
                    notes.append(f"{base} row {i}: {e}; skipped")
                    continue
                txns.append(RawTxn(
                    date=iso,
                    amount=amount,
                    description=description,
                    account_id=source_row.account_id,
                    world=source_row.world,
                    source_file=base,
                    adapter=self.name,
                    ext_id=(row.get(id_col) or "").strip() if id_col else "",
                ))
        return IngestResult(transactions=txns, control_totals=[], notes=notes)


register(MonzoCsvAdapter())
