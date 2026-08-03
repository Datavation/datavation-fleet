"""Load the human-owned rules tables (rules/*.csv).

These are the files Austen edits by hand between runs. The engine reads them,
never rewrites them (except open_items.csv, which it APPENDS to — the one
machine-touched human table, and even then it only adds question rows; the
`answer` column is Austen's).

Pure stdlib csv. No pandas.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from .model import money


@dataclass
class SourceRow:
    world: str
    account_id: str
    adapter: str
    path: str
    kind: str = "glob"      # file | glob | dir
    enabled: str = "Y"
    note: str = ""

    @property
    def is_enabled(self) -> bool:
        return self.enabled.strip().upper() not in ("N", "NO", "0", "FALSE", "")


@dataclass
class AccountRow:
    account_id: str
    name: str
    world: str
    type: str = "current"       # current | savings | credit_card | mortgage | asset | ...
    scope: str = "Personal"     # default scope for txns on this account
    custodial: str = "N"        # Y -> excluded from net worth & burn (held for family)
    account_number: str = ""    # LOCAL ONLY; masked in every export
    opening_balance: str = ""
    note: str = ""

    @property
    def is_custodial(self) -> bool:
        return self.custodial.strip().upper() in ("Y", "YES", "1", "TRUE")

    @property
    def is_liability(self) -> bool:
        return self.type.strip().lower() in ("credit_card", "mortgage", "loan", "liability")

    @property
    def is_asset(self) -> bool:
        # Illiquid holdings declared as manual config lines (the house, premium
        # bonds held long-term). In net worth, never in liquid/cash totals.
        return self.type.strip().lower() in ("asset", "property", "house", "investment")


@dataclass
class CategoryRule:
    order: int
    match_type: str    # substring | regex
    pattern: str
    category: str
    subcategory: str = ""
    scope: str = ""


@dataclass
class RecurringRule:
    pattern: str
    label: str
    match_type: str = "substring"
    expected_amount: str = ""
    cadence: str = ""


@dataclass
class Rules:
    sources: list          # list[SourceRow]
    accounts: dict         # account_id -> AccountRow
    account_by_number: dict  # account_number -> AccountRow (for the Barclays split)
    categories: list       # list[CategoryRule] in order
    recurring: list        # list[RecurringRule]
    rules_dir: str


def _read_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        first = reader.fieldnames[0] if reader.fieldnames else None
        rows = []
        for row in reader:
            # allow '#'-prefixed comment lines in the hand-edited CSVs
            if first and (row.get(first) or "").strip().startswith("#"):
                continue
            rows.append({(k or "").strip(): (v or "").strip() for k, v in row.items()})
        return rows


def load_rules(rules_dir: str) -> Rules:
    sources = [
        SourceRow(
            world=r.get("world", ""),
            account_id=r.get("account_id", ""),
            adapter=r.get("adapter", ""),
            path=r.get("path", ""),
            kind=r.get("kind", "glob") or "glob",
            enabled=r.get("enabled", "Y") or "Y",
            note=r.get("note", ""),
        )
        for r in _read_csv(os.path.join(rules_dir, "sources.csv"))
    ]

    accounts: dict = {}
    account_by_number: dict = {}
    for r in _read_csv(os.path.join(rules_dir, "accounts.csv")):
        acc = AccountRow(
            account_id=r.get("account_id", ""),
            name=r.get("name", ""),
            world=r.get("world", ""),
            type=r.get("type", "current") or "current",
            scope=r.get("scope", "Personal") or "Personal",
            custodial=r.get("custodial", "N") or "N",
            account_number=r.get("account_number", ""),
            opening_balance=r.get("opening_balance", ""),
            note=r.get("note", ""),
        )
        if acc.account_id:
            accounts[acc.account_id] = acc
        if acc.account_number:
            account_by_number[acc.account_number.strip()] = acc

    categories: list = []
    for r in _read_csv(os.path.join(rules_dir, "categories.csv")):
        try:
            order = int(r.get("order", "0") or "0")
        except ValueError:
            order = 0
        categories.append(CategoryRule(
            order=order,
            match_type=(r.get("match_type", "substring") or "substring").lower(),
            pattern=r.get("pattern", ""),
            category=r.get("category", "uncategorised"),
            subcategory=r.get("subcategory", ""),
            scope=r.get("scope", ""),
        ))
    categories.sort(key=lambda c: c.order)

    recurring = [
        RecurringRule(
            pattern=r.get("pattern", ""),
            label=r.get("label", ""),
            match_type=(r.get("match_type", "substring") or "substring").lower(),
            expected_amount=r.get("expected_amount", ""),
            cadence=r.get("cadence", ""),
        )
        for r in _read_csv(os.path.join(rules_dir, "recurring.csv"))
    ]

    return Rules(
        sources=sources,
        accounts=accounts,
        account_by_number=account_by_number,
        categories=categories,
        recurring=recurring,
        rules_dir=rules_dir,
    )
