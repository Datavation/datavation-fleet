"""Canonical data model + deterministic helpers.

Money is carried as Decimal and quantised to 2dp so that a re-run produces
byte-identical output (a float would drift). Dates are ISO strings once
normalised. Nothing here touches the network or the filesystem.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from typing import Optional


TWOPLACES = Decimal("0.01")


def money(value) -> Decimal:
    """Coerce anything numeric-ish to a 2dp Decimal, deterministically.

    Accepts Decimal / int / float / str. Strips currency symbols, thousands
    separators, and parenthesised-negative accounting notation ("(1,234.56)").
    Raises ValueError on genuinely unparseable input rather than guessing.
    """
    if isinstance(value, Decimal):
        d = value
    else:
        s = str(value).strip()
        if not s:
            raise ValueError("empty money value")
        negative = False
        if s.startswith("(") and s.endswith(")"):
            negative = True
            s = s[1:-1]
        # drop currency symbols, spaces and thousands separators
        for ch in ("£", "$", "€", ",", " ", " "):
            s = s.replace(ch, "")
        if s.startswith("+"):
            s = s[1:]
        if s in ("", "-", "."):
            raise ValueError(f"unparseable money value: {value!r}")
        d = Decimal(s)
        if negative:
            d = -d
    return d.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def parse_date(value, fmts: Optional[list[str]] = None) -> str:
    """Normalise a date to ISO 'YYYY-MM-DD'. Never guesses a locale silently.

    If `fmts` is given, only those formats are tried (adapter-driven). Otherwise
    a small, unambiguous set is tried, plus ISO. Raises ValueError if none match.
    """
    if isinstance(value, (datetime, date)):
        d = value.date() if isinstance(value, datetime) else value
        return d.isoformat()
    s = str(value).strip()
    if not s:
        raise ValueError("empty date value")
    candidates = fmts or [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%d %b %y",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"unparseable date {value!r} (tried {candidates})")


@dataclass
class RawTxn:
    """What an adapter emits, before normalise/dedup/categorise.

    An adapter's ONLY job is to map its native format onto this shape. It sets
    world/account_id from the source row and leaves category/scope blank.
    """
    date: str                       # ISO after normalise; adapter may pass native then normalise
    amount: Decimal                 # signed: out negative, in positive
    description: str
    account_id: str
    world: str
    source_file: str
    adapter: str
    raw_description: str = ""
    currency: str = "GBP"
    ext_id: str = ""          # native per-transaction id where the source provides one

    def __post_init__(self):
        if not self.raw_description:
            self.raw_description = self.description


# Canonical column order for transactions.csv (machine-owned master ledger).
TXN_COLUMNS = [
    "txn_id",
    "date",
    "amount",
    "currency",
    "description",
    "raw_description",
    "account_id",
    "world",
    "scope",
    "category",
    "subcategory",
    "is_internal_transfer",
    "transfer_group",
    "source_file",
    "adapter",
]


@dataclass
class Txn:
    """A fully-processed ledger row."""
    date: str
    amount: Decimal
    description: str
    raw_description: str
    account_id: str
    world: str
    source_file: str
    adapter: str
    currency: str = "GBP"
    scope: str = ""
    category: str = "uncategorised"
    subcategory: str = ""
    is_internal_transfer: str = "N"
    transfer_group: str = ""
    ext_id: str = ""
    txn_id: str = ""

    @classmethod
    def from_raw(cls, r: RawTxn) -> "Txn":
        return cls(
            date=r.date,
            amount=r.amount,
            description=r.description,
            raw_description=r.raw_description,
            account_id=r.account_id,
            world=r.world,
            source_file=r.source_file,
            adapter=r.adapter,
            currency=r.currency,
            ext_id=r.ext_id,
        )

    def base_key(self) -> str:
        """Composite content key: date + amount + description + account. Two
        genuinely-identical transactions share this; dedup disambiguates them
        with a native id or an occurrence ordinal (see pipeline/dedup.py)."""
        return "|".join([
            self.date,
            f"{self.amount:.2f}",
            self.raw_description.strip().lower(),
            self.account_id,
        ])

    def compute_id(self, unique_key: str = "") -> str:
        """Set and return txn_id. `unique_key` is the fully-disambiguated dedup
        key (with id/ordinal); if omitted, the plain content key is used."""
        self.txn_id = hashlib.sha1((unique_key or self.base_key()).encode("utf-8")).hexdigest()[:16]
        return self.txn_id

    def as_row(self) -> dict:
        d = asdict(self)
        d["amount"] = f"{self.amount:.2f}"
        return {c: d[c] for c in TXN_COLUMNS}


@dataclass
class ControlTotals:
    """Statement-stated totals for the PDF tie-out (§5b).

    Any field left None is simply not checked. The reconcile step compares the
    parsed transactions against whichever of these the statement actually prints.
    """
    account_id: str
    source_file: str
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    total_payments: Optional[Decimal] = None      # money IN to the card / credits
    total_spend: Optional[Decimal] = None         # everything that increased the balance (purchases + interest + fees)
    purchases_only: Optional[Decimal] = None      # dated purchases subtotal (excl. interest/fees), for the line-parse check
    stated_txn_count: Optional[int] = None
    extras: dict = field(default_factory=dict)    # e.g. mortgage: payments_made, balance


@dataclass
class IngestResult:
    transactions: list          # list[RawTxn]
    control_totals: list        # list[ControlTotals]
    notes: list                 # list[str] human-readable, surfaced in console
