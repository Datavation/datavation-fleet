"""Compute the six dashboard views from the ledger. Deterministic, no I/O.

Every total nets out internal transfers (is_internal_transfer=Y) — a transfer
between Austen's own accounts is not income and not spend. Custodial accounts
(held for family) are excluded from net worth and from all burn/cash totals and
shown on a separate "held in safekeeping" line, per §6.

Money is Decimal internally; serialised to 2dp strings for JSON so the embedded
dashboard data is byte-stable across re-runs.
"""

from __future__ import annotations

from collections import defaultdict, OrderedDict
from datetime import date
from decimal import Decimal

from .model import money

ZERO = Decimal("0.00")


def _s(d: Decimal) -> str:
    return f"{money(d):.2f}"


def _real(txns):
    """Transactions that count toward income/spend: exclude internal transfers."""
    return [t for t in txns if t.is_internal_transfer != "Y"]


def _month(iso: str) -> str:
    return iso[:7]


def compute(txns, rules, mortgage_balances=None, open_items=None):
    """Return a JSON-serialisable dict with all six views."""
    mortgage_balances = mortgage_balances or {}
    open_items = open_items or []
    accounts = rules.accounts

    real = _real(txns)
    dates = sorted(t.date for t in txns)
    span = {"from": dates[0], "to": dates[-1]} if dates else {"from": None, "to": None}

    # ---- per-account balances -------------------------------------------------
    flow = defaultdict(lambda: ZERO)
    for t in txns:  # balances include transfers (they move real money)
        flow[t.account_id] += t.amount

    account_rows = []
    liquid_total = ZERO
    asset_total = ZERO
    liability_total = ZERO
    custodial_total = ZERO
    for acc_id, acc in accounts.items():
        opening = money(acc.opening_balance) if acc.opening_balance else ZERO
        computed = money(opening + flow.get(acc_id, ZERO))
        # prefer an authoritative statement balance where we have one
        if acc.type == "mortgage" and acc_id in mortgage_balances:
            balance = money(-abs(money(mortgage_balances[acc_id])))
        else:
            balance = computed
        if acc.is_custodial:
            cls = "custodial"
        elif acc.is_liability:
            cls = "liability"
        elif acc.is_asset:
            cls = "asset"
        else:
            cls = "liquid"
        account_rows.append({
            "account_id": acc_id, "name": acc.name, "world": acc.world,
            "type": acc.type, "class": cls, "balance": _s(balance),
            "custodial": "Y" if acc.is_custodial else "N",
        })
        if cls == "custodial":
            custodial_total += balance
        elif cls == "liability":
            liability_total += balance
        elif cls == "asset":
            asset_total += balance
        else:
            liquid_total += balance

    net_position = money(liquid_total + liability_total)  # liabilities already negative
    net_worth = money(liquid_total + asset_total + liability_total)

    consolidated = {
        "accounts": account_rows,
        "liquid_total": _s(liquid_total),
        "asset_total": _s(asset_total),
        "liability_total": _s(liability_total),
        "custodial_total": _s(custodial_total),
        "net_position": _s(net_position),
        "net_worth": _s(net_worth),
        "note": ("Net position = liquid + liabilities (cash view). Net worth adds "
                 "illiquid assets. Custodial holdings excluded from both."),
    }

    # ---- cash flow: monthly + headline burn ----------------------------------
    by_month_out = defaultdict(lambda: ZERO)
    by_month_in = defaultdict(lambda: ZERO)
    total_out = ZERO
    total_in = ZERO
    for t in real:
        if t.amount < 0:
            by_month_out[_month(t.date)] += -t.amount
            total_out += -t.amount
        else:
            by_month_in[_month(t.date)] += t.amount
            total_in += t.amount
    months = sorted(set(by_month_out) | set(by_month_in))
    monthly = [
        {"month": m, "out": _s(by_month_out[m]), "in": _s(by_month_in[m]),
         "net": _s(by_month_in[m] - by_month_out[m])}
        for m in months
    ]
    n_days = (date.fromisoformat(span["to"]) - date.fromisoformat(span["from"])).days + 1 \
        if span["from"] else 0
    weekly_burn = money(total_out / Decimal(n_days) * 7) if n_days else ZERO
    daily_burn = money(total_out / Decimal(n_days)) if n_days else ZERO
    cashflow = {
        "monthly": monthly,
        "total_out": _s(total_out), "total_in": _s(total_in),
        "net": _s(total_in - total_out),
        "weekly_burn": _s(weekly_burn), "daily_burn": _s(daily_burn),
        "span_days": n_days,
    }

    # ---- spend by category ----------------------------------------------------
    by_cat = defaultdict(lambda: ZERO)
    for t in real:
        if t.amount < 0:
            by_cat[t.category or "uncategorised"] += -t.amount
    spend_by_category = [
        {"category": c, "amount": _s(v)}
        for c, v in sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True)
    ]
    uncategorised_total = _s(by_cat.get("uncategorised", ZERO))

    # ---- recurring commitments / leak list -----------------------------------
    recurring_rows = []
    for rule in rules.recurring:
        hits = [t for t in real if rule.pattern and (
            rule.pattern.lower() in t.description.lower())]
        if hits:
            spent = money(sum((-t.amount for t in hits if t.amount < 0), ZERO))
            recurring_rows.append({
                "label": rule.label or rule.pattern,
                "cadence": rule.cadence, "hits": len(hits),
                "total": _s(spent),
                "expected": rule.expected_amount,
            })
    recurring_rows.sort(key=lambda r: money(r["total"]), reverse=True)

    # ---- business vs personal -------------------------------------------------
    by_scope_out = defaultdict(lambda: ZERO)
    by_scope_in = defaultdict(lambda: ZERO)
    for t in real:
        key = t.scope or "Unscoped"
        if t.amount < 0:
            by_scope_out[key] += -t.amount
        else:
            by_scope_in[key] += t.amount
    by_world_out = defaultdict(lambda: ZERO)
    for t in real:
        if t.amount < 0:
            by_world_out[t.world or "Unknown"] += -t.amount
    scopes = sorted(set(by_scope_out) | set(by_scope_in))
    business_personal = {
        "by_scope": [
            {"scope": s, "out": _s(by_scope_out[s]), "in": _s(by_scope_in[s])}
            for s in scopes
        ],
        "by_world": [
            {"world": w, "out": _s(v)}
            for w, v in sorted(by_world_out.items(), key=lambda kv: kv[1], reverse=True)
        ],
    }

    # ---- open questions -------------------------------------------------------
    questions = [
        {"id": oi.get("id", ""), "type": oi.get("type", ""),
         "account_id": oi.get("account_id", ""), "detail": oi.get("detail", ""),
         "answer": oi.get("answer", "")}
        for oi in open_items
    ]

    return OrderedDict([
        ("generated_span", span),
        ("txn_count", len(txns)),
        ("consolidated", consolidated),
        ("cashflow", cashflow),
        ("spend_by_category", spend_by_category),
        ("uncategorised_total", uncategorised_total),
        ("recurring", recurring_rows),
        ("business_personal", business_personal),
        ("open_questions", questions),
    ])
