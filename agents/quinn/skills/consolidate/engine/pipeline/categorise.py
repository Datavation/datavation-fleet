"""Stage 5 — categorise by the rulebook (rules/categories.csv), in order.

First matching rule wins (rules are pre-sorted by `order`). Match is substring
(case-insensitive) or regex on the description. Unmatched -> 'uncategorised',
counted and surfaced — never invented. A rule may also set scope (e.g. force a
mortgage payment to Personal).
"""

from __future__ import annotations

import re


def _matches(rule, description: str) -> bool:
    desc = description.lower()
    pat = rule.pattern or ""
    if not pat:
        return False
    if rule.match_type == "regex":
        try:
            return re.search(pat, description, re.I) is not None
        except re.error:
            return False
    return pat.lower() in desc


def categorise(txns: list, rules) -> int:
    """Mutate txns in place; return count still uncategorised."""
    uncategorised = 0
    for t in txns:
        matched = False
        for rule in rules.categories:
            if _matches(rule, t.description):
                t.category = rule.category or "uncategorised"
                t.subcategory = rule.subcategory
                if rule.scope:
                    t.scope = rule.scope
                matched = True
                break
        if not matched:
            t.category = "uncategorised"
            uncategorised += 1
    return uncategorised
