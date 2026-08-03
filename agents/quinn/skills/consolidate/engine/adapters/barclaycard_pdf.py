"""Barclaycard PDF adapter — the fragile path, so it is self-checking (§5b).

PDF parsing is error-prone, so we never trust it blind. Each statement prints
its own control totals (previous balance, payments & credits, new spend, new
balance). The parser captures both the transactions AND those stated totals;
the tie-out step (pipeline/tieout.py) reconciles them and FLAGS a mismatch to
open_items rather than silently accepting a bad parse.

The text-extraction (pdfplumber) is kept as a thin shim so the parse logic can
be unit-tested on captured text without shipping binary PDF fixtures.

Sign convention (card = liability, "out negative / in positive"):
  * a purchase / charge  -> money out -> NEGATIVE
  * a payment / credit (CR on the statement) -> money in -> POSITIVE
A payment to the card FROM the current account is the internal-transfer contra
side; reconcile nets it so it is not counted as spend.
"""

from __future__ import annotations

import os
import re

from ..model import RawTxn, ControlTotals, IngestResult, money, parse_date
from .base import Adapter, register


_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}

_AMOUNT = r"[\d,]+\.\d{2}"
# a dated transaction line: "19 Nov 123 AMAZON* ..., London 24.99"  (amount at end,
# optional CR). Date is 'DD Mon' with NO year — the year comes from the statement period.
_TXN_RE = re.compile(r"^\s*(\d{1,2})\s+([A-Za-z]{3})\s+(.+?)\s+£?\s*(" + _AMOUNT + r")\s*(CR)?\s*$")
_LEAD_REF = re.compile(r"^\d{1,4}\s+")          # strip a leading transaction reference
_YEAR_IN_TEXT = re.compile(r"20\d{2}")
# A genuine payment TO the card starts with "Payment" or is a direct debit / "thank
# you" line. A merchant whose name merely ENDS in "payment" (e.g. "Creation Card
# Payment") is a purchase, not a payment — so anchor on ^payment, don't match anywhere.
_PAYMENT_HINT = re.compile(r"^payment\b|direct debit|thank you", re.I)
_REFUND_HINT = re.compile(r"refund|reversal", re.I)
# finance-cost lines that are summarised in the totals, not spending line items —
# excluded from the transaction list so parsed purchases tie to 'how you've used your card'
_SKIP_TXN = re.compile(r"interest|instalment plan fee|over credit|returned payment|"
                       r"late payment|non-sterling transaction fee|account maintenance", re.I)

# control-total label -> field. We take the FIRST amount after the label (some lines
# carry a second, unrelated amount such as the credit limit).
_CTRL = [
    ("opening_balance", "your previous balance"),
    ("closing_balance", "your new balance"),
    ("total_payments", "payments towards your account"),
    ("total_spend", "transactions, interest and charges"),
    ("purchases_only", "how you've used your card"),
]


def _norm(text):
    # pdfplumber decodes the '£' glyph as U+FFFD on these statements
    return (text or "").replace("�", "£")


def _statement_period(source_file, text):
    """(year, month) the statement covers — from the filename ('..._19-DEC-25 ...')
    or, failing that, any 4-digit year in the text. Month may be None."""
    m = re.search(r"(\d{1,2})-([A-Za-z]{3})-(\d{2,4})", source_file or "")
    if m:
        yr = int(m.group(3))
        yr = yr + 2000 if yr < 100 else yr
        return yr, _MONTHS.get(m.group(2).lower()[:3])
    m = _YEAR_IN_TEXT.search(text)
    return (int(m.group()) if m else None), None


def _amount_after(line, label):
    i = line.lower().find(label)
    if i < 0:
        return None
    m = re.search(_AMOUNT, line[i + len(label):])
    return money(m.group()) if m else None


def _iso(day, mon3, styr, stmon):
    mn = _MONTHS.get(mon3.lower())
    if not mn or not styr:
        return None
    # a statement covers ~the prior month, so a txn month later than the statement
    # month belongs to the previous year (e.g. Dec txns on a January statement)
    yr = styr - 1 if (stmon and mn > stmon) else styr
    return f"{yr:04d}-{mn:02d}-{int(day):02d}"


def parse_barclaycard_text(text, account_id, world, source_file):
    """Pure parser for the Barclaycard MONTHLY statement layout.

    Dated 'DD Mon' lines with the amount at the end. Credits (payments) and
    charges (purchases) are separated by section headers, not a CR marker.
    Control totals are read from their labels for the §5b tie-out. Deterministic
    and side-effect free — the unit-testable heart of the fragile PDF path.
    """
    text = _norm(text)
    txns, notes = [], []
    ct = ControlTotals(account_id=account_id, source_file=source_file)
    styr, stmon = _statement_period(source_file, text)

    if re.search(r"annual\s+statement", text, re.I) and "your transactions" not in text.lower():
        return [], ct, [f"{source_file}: annual summary (no line items) — skipped"]

    # control totals: first amount after each label (first occurrence wins)
    for line in text.splitlines():
        low = line.lower()
        for field, label in _CTRL:
            if getattr(ct, field) is None and label in low:
                v = _amount_after(line, label)
                if v is not None:
                    setattr(ct, field, v)

    # Sign is decided by keyword, NOT by statement section: column-aware
    # extraction separates a section header from its transactions (they can be
    # in different columns), so section state is unreliable. Purchases never
    # match the credit keywords, so they stay charges; only explicit payments/
    # refunds/credits go positive.
    for line in text.splitlines():
        m = _TXN_RE.match(line)
        if not m:
            continue
        day, mon, desc, amt, cr = m.groups()
        iso = _iso(day, mon, styr, stmon)
        if iso is None:
            continue
        if _SKIP_TXN.search(desc):
            continue  # interest / fees — summarised in the totals, not a purchase
        clean = _LEAD_REF.sub("", desc.strip()) or "(no description)"
        is_credit = bool(cr) or bool(_PAYMENT_HINT.search(clean)) or bool(_REFUND_HINT.search(clean))
        amount = money(amt)
        amount = abs(amount) if is_credit else -abs(amount)
        txns.append(RawTxn(
            date=iso, amount=amount, description=clean,
            account_id=account_id, world=world,
            source_file=source_file, adapter="barclaycard_pdf",
        ))

    if not txns:
        notes.append(f"{source_file}: no transactions parsed — check the layout/regex")
    return txns, ct, notes


def extract_text(path: str):
    """Thin pdfplumber shim. Returns (text, error). Degrades loudly."""
    try:
        import pdfplumber
    except ImportError:
        return None, ("pdfplumber not installed — cannot read PDF statements "
                      "(pip install pdfplumber)")
    parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts), None


def extract_text_columns(path: str, split_ratio: float = 0.5):
    """Column-aware extraction for the two-column statement layout.

    Barclaycard statements print two columns; the default extractor merges them
    onto one physical line, which corrupts amounts (a left-column transaction
    ends up carrying the right column's figure). We split each page's words by
    x-position and read each column top-to-bottom separately, so every output
    line belongs to exactly one column.
    """
    try:
        import pdfplumber
    except ImportError:
        return None, ("pdfplumber not installed — cannot read PDF statements "
                      "(pip install pdfplumber)")
    out = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
            if not words:
                continue
            mid = page.width * split_ratio
            left = [w for w in words if (w["x0"] + w["x1"]) / 2.0 < mid]
            right = [w for w in words if (w["x0"] + w["x1"]) / 2.0 >= mid]
            for col in (left, right):
                rows = {}
                for w in col:
                    rows.setdefault(round(w["top"] / 3.0), []).append((w["x0"], w["text"]))
                for key in sorted(rows):
                    out.append(" ".join(t for _, t in sorted(rows[key])))
    return "\n".join(out), None


class BarclaycardPdfAdapter(Adapter):
    name = "barclaycard_pdf"
    extensions = (".pdf",)

    def detect(self, path: str) -> bool:
        text, err = extract_text(path)
        if err or not text:
            return False
        return bool(re.search(r"barclaycard", text, re.I))

    def ingest(self, path, source_row, rules) -> IngestResult:
        base = os.path.basename(path)
        text, err = extract_text_columns(path)   # two-column-aware (see above)
        if err:
            return IngestResult([], [], [f"{base}: {err}"])
        txns, ct, notes = parse_barclaycard_text(
            text, source_row.account_id, source_row.world, base)
        return IngestResult(transactions=txns, control_totals=[ct], notes=notes)


register(BarclaycardPdfAdapter())
