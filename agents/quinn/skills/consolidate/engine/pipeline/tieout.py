"""Stage 6b — tie parsed PDF transactions back to each statement's own stated
totals (§5b). This is the accountant's "tie out to the statement" discipline,
enforced in code: a mismatch is FLAGGED to open_items, never silently accepted.

For a Barclaycard statement we check:
  * sum of parsed charges      ~= stated new spend
  * sum of parsed credits      ~= stated payments & credits
  * opening + spend - payments ~= closing balance
Any of these missing on the statement is simply skipped (not a failure).
"""

from __future__ import annotations

import re
from decimal import Decimal

from ..model import money

TOLERANCE = money("0.01")

# A positive amount on a card statement is EITHER a payment toward the card
# (reduces the balance, counted in "payments towards your account") OR a refund
# from a merchant (a reversal of spend, part of net purchases). They must be
# told apart or the tie-out double-counts refunds as payments.
_PAYMENT = re.compile(r"^payment\b|direct debit|thank you", re.I)


def _sum(txns, predicate):
    total = Decimal("0.00")
    for t in txns:
        if predicate(t):
            total += t.amount
    return money(total)


def tieout(txns: list, control_totals: list) -> list:
    """Return open_item rows for any statement whose parse fails its own totals."""
    open_items = []
    for ct in control_totals:
        stmt_txns = [t for t in txns if t.source_file == ct.source_file
                     and t.account_id == ct.account_id]

        # payments (reduce balance) vs refunds (reverse spend) — split by keyword
        parsed_charges = money(-_sum(stmt_txns, lambda t: t.amount < 0))
        parsed_payments = _sum(stmt_txns, lambda t: t.amount > 0 and bool(_PAYMENT.search(t.description)))
        parsed_refunds = _sum(stmt_txns, lambda t: t.amount > 0 and not _PAYMENT.search(t.description))
        # net purchases = gross charges less any refunds
        parsed_spend = money(parsed_charges - parsed_refunds)

        # prefer the purchases-only subtotal where the statement prints it (the
        # "total_spend" figure also includes interest/fees, which aren't line items)
        spend_target = ct.purchases_only if ct.purchases_only is not None else ct.total_spend
        if spend_target is not None and abs(parsed_spend - spend_target) > TOLERANCE:
            open_items.append({
                "type": "tieout_spend",
                "account_id": ct.account_id,
                "detail": (f"{ct.source_file}: parsed purchases {parsed_spend} != stated "
                           f"{spend_target} (diff {parsed_spend - spend_target}). "
                           f"PDF parse suspect — verify before trusting."),
            })
        if ct.total_payments is not None and abs(parsed_payments - ct.total_payments) > TOLERANCE:
            open_items.append({
                "type": "tieout_payments",
                "account_id": ct.account_id,
                "detail": (f"{ct.source_file}: parsed payments {parsed_payments} != stated "
                           f"payments/credits {ct.total_payments} "
                           f"(diff {parsed_payments - ct.total_payments})."),
            })
        if ct.opening_balance is not None and ct.closing_balance is not None:
            spend = ct.total_spend if ct.total_spend is not None else parsed_spend
            pays = ct.total_payments if ct.total_payments is not None else parsed_payments
            expected_close = money(ct.opening_balance + spend - pays)
            if abs(expected_close - ct.closing_balance) > TOLERANCE:
                open_items.append({
                    "type": "tieout_balance",
                    "account_id": ct.account_id,
                    "detail": (f"{ct.source_file}: opening {ct.opening_balance} + spend {spend} "
                               f"- payments {pays} = {expected_close} != stated closing "
                               f"{ct.closing_balance} (diff {expected_close - ct.closing_balance})."),
                })
    return open_items
