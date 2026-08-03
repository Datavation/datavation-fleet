"""Mortgage letter PDF adapter (§5, §6).

The mortgage letter is NOT a transaction ledger — it is a periodic statement of
the account. We extract the balance-side facts (outstanding balance, payments
made, total paid, monthly payment, interest rate) into the mortgage account's
control totals. The CASH side (the monthly payment leaving the current account)
is captured on the Barclays side and categorised Housing/Mortgage there, so we
do NOT emit spend transactions here — that would double-count the same event.

Self-check (§5b): if the letter states both a payment count and a monthly
amount, we sanity-check count x monthly ~= total paid and flag a mismatch.
"""

from __future__ import annotations

import os
import re

from ..model import ControlTotals, IngestResult, money
from .base import Adapter, register
from .barclaycard_pdf import extract_text


_NUM = r"(\(?[\d,]+\.\d{2}\)?|\d[\d,]*)"

_FIELDS = [
    ("balance", re.compile(r"(?:outstanding|remaining|current)\s+balance[^0-9£]*£?\s*" + _NUM, re.I)),
    ("balance", re.compile(r"(?:amount|balance)\s+(?:you\s+owe|outstanding)[^0-9£]*£?\s*" + _NUM, re.I)),
    ("total_paid", re.compile(r"total\s+(?:amount\s+)?(?:paid|repaid)[^0-9£]*£?\s*" + _NUM, re.I)),
    ("monthly_payment", re.compile(r"(?:monthly\s+payment|payment\s+amount)[^0-9£]*£?\s*" + _NUM, re.I)),
    ("interest_rate", re.compile(r"(?:interest\s+rate|rate\s+of\s+interest)[^0-9%]*" + r"([\d.]+)\s*%", re.I)),
]
_COUNT_RE = re.compile(r"(\d+)\s+payments?\s+(?:made|received)", re.I)
_COUNT_RE2 = re.compile(r"(?:number\s+of\s+payments|payments\s+made)[^0-9]*(\d+)", re.I)


def parse_mortgage_text(text, account_id, source_file):
    """Pure parser: letter text -> (ControlTotals with extras, notes)."""
    ct = ControlTotals(account_id=account_id, source_file=source_file)
    notes = []
    extras = {}

    for name, rx in _FIELDS:
        if name in extras:
            continue
        m = rx.search(text)
        if m:
            val = m.group(1)
            try:
                extras[name] = str(money(val)) if name != "interest_rate" else val
            except Exception:
                extras[name] = val

    for rx in (_COUNT_RE, _COUNT_RE2):
        m = rx.search(text)
        if m:
            extras["payments_made"] = int(m.group(1))
            break

    if "balance" in extras:
        try:
            ct.closing_balance = money(extras["balance"])
        except Exception:
            pass

    # self-check: count x monthly ~= total paid
    if {"payments_made", "monthly_payment", "total_paid"} <= set(extras):
        try:
            expected = money(str(int(extras["payments_made"]) * float(extras["monthly_payment"])))
            actual = money(extras["total_paid"])
            if abs(expected - actual) > money("1.00"):
                notes.append(
                    f"{source_file}: mortgage tie-out — {extras['payments_made']} x "
                    f"{extras['monthly_payment']} = {expected} but letter states total "
                    f"paid {actual} (diff {actual - expected}); verify the parse")
        except Exception:
            pass

    ct.extras = extras
    if not extras:
        notes.append(f"{source_file}: no mortgage fields parsed — check the letter layout")
    return ct, notes


class MortgagePdfAdapter(Adapter):
    name = "mortgage_pdf"
    extensions = (".pdf",)

    def detect(self, path: str) -> bool:
        text, err = extract_text(path)
        if err or not text:
            return False
        return bool(re.search(r"mortgage", text, re.I))

    def ingest(self, path, source_row, rules) -> IngestResult:
        base = os.path.basename(path)
        text, err = extract_text(path)
        if err:
            return IngestResult([], [], [f"{base}: {err}"])
        ct, notes = parse_mortgage_text(text, source_row.account_id, base)
        # No spend transactions emitted (cash side lives on the current account).
        return IngestResult([], [ct], notes)


register(MortgagePdfAdapter())
