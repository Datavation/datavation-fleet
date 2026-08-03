"""Canonical rules-file skeletons + generic (figure-free) examples.

Used by `--template` (data-stripped shippable bundle) and by `--init` (seed a
fresh workdir). Every example here is generic and contains NO real figures,
account numbers, or family data — those only ever go into the local files by
hand (§11).
"""

from __future__ import annotations

import os

# --- headers (the contract for each human-owned table) --------------------
SOURCES_HEADER = "world,account_id,adapter,path,kind,enabled,note\n"
ACCOUNTS_HEADER = "account_id,name,world,type,scope,custodial,account_number,opening_balance,note\n"
CATEGORIES_HEADER = "order,match_type,pattern,category,subcategory,scope\n"
RECURRING_HEADER = "pattern,label,match_type,expected_amount,cadence\n"
OPEN_ITEMS_HEADER = "id,run_date,type,account_id,detail,answer\n"

# --- generic examples (figure-free, illustrative only) --------------------
SOURCES_EXAMPLE = SOURCES_HEADER + (
    "# One row per source file/folder. adapter: quickbooks_csv|monzo_csv|barclays_xlsx|barclaycard_pdf|mortgage_pdf|generic\n"
    "# kind: file (exact) | glob (wildcards) | dir (all files in a folder)\n"
    "# Manual/config lines (savings, mortgage balance, the house) need NO source row —\n"
    "# declare them in accounts.csv with an opening_balance and no transactions.\n"
    "RexHomeServices,rhs_quickbooks,quickbooks_csv,extracts/qb_rhs_*.csv,glob,Y,QuickBooks transaction export (QB read-only; extract not live API)\n"
    "Datavation,datavation_monzo,monzo_csv,extracts/monzo_datavation_*.csv,glob,Y,Monzo Business export (no QuickBooks)\n"
    "Personal,barclays_personal,barclays_xlsx,extracts/barclays_personal_joint.xlsx,file,Y,Personal+Joint workbook (split on account number)\n"
    "Personal,barclaycard,barclaycard_pdf,extracts/barclaycard_*.pdf,glob,Y,PDF only; tie-out checked\n"
    "Personal,mortgage,mortgage_pdf,extracts/mortgage_*.pdf,glob,Y,Letter; balance not a ledger\n"
)

ACCOUNTS_EXAMPLE = ACCOUNTS_HEADER + (
    "# type: current|savings|credit_card|mortgage|asset   custodial:Y excludes from net worth & burn\n"
    "# asset = illiquid manual line (house, long-term holdings): in net worth, never in liquid/cash\n"
    "# account_number maps a Barclays row to Personal/Joint; it stays LOCAL and is masked in exports\n"
    "rhs_quickbooks,Rex Home Services (QB/Monzo),RexHomeServices,current,Business,N,,,\n"
    "datavation_monzo,Datavation (Monzo),Datavation,current,Business,N,,,\n"
    "barclays_personal,Barclays Personal,Personal,current,Personal,N,,,\n"
    "barclays_joint,Barclays Joint,Joint,current,Family,N,,,Joint account — family data\n"
    "barclaycard,Barclaycard,Personal,credit_card,Personal,N,,,Liability\n"
    "mortgage,Mortgage,Personal,mortgage,Personal,N,,,Liability; balance from letter\n"
    "# manual/config lines — value entered locally by hand, updated between runs, never shipped:\n"
    "# ns_savings,National Savings / Premium Bonds,Personal,savings,Personal,N,,,Manual line — update value by hand\n"
    "# house,House,Personal,asset,Family,N,,,Manual line — illiquid asset, in net worth only\n"
    "# custodial example (held for someone else — excluded from net worth entirely):\n"
    "# family_bond,Family Savings Bond,Personal,savings,Personal,Y,,,Held for family — not my net worth\n"
)

CATEGORIES_EXAMPLE = CATEGORIES_HEADER + (
    "# First matching rule wins (sorted by order). match_type: substring|regex\n"
    "10,substring,mortgage,Housing,Mortgage,Personal\n"
    "20,substring,barclaycard payment,Transfers,Card payment,Personal\n"
    "30,substring,tesco,Groceries,,\n"
    "31,substring,sainsbury,Groceries,,\n"
    "40,substring,shell,Transport,Fuel,\n"
    "50,regex,(gas|electric|octopus|british gas),Utilities,Energy,\n"
    "60,substring,amazon,Shopping,,\n"
)

RECURRING_EXAMPLE = RECURRING_HEADER + (
    "# Commitments to watch for the leak list. expected_amount is illustrative only.\n"
    "netflix,Netflix,substring,,monthly\n"
    "spotify,Spotify,substring,,monthly\n"
    "mortgage,Mortgage payment,substring,,monthly\n"
)

HOW_TO_REFRESH = (
    "HOW YOUR FINANCE VIEW REFRESHES\n"
    "1. Drop each new statement/extract into the folder it belongs to (see rules/sources.csv).\n"
    "2. Quinn's routines run the consolidation for you (or ask Quinn to refresh now).\n"
    "   Under the hood that is: python -m engine --workdir <this folder>\n"
    "3. Open Finance-Dashboard.html (or Finance-Report.xlsx). Check open_items.csv for anything to answer.\n"
    "There is nothing to double-click — the agent runs the engine; you read the dashboard.\n"
)


def write_rules_skeleton(rules_dir: str, with_examples: bool = True):
    os.makedirs(rules_dir, exist_ok=True)
    os.makedirs(os.path.join(rules_dir, "adapters"), exist_ok=True)
    files = {
        "sources.csv": SOURCES_EXAMPLE if with_examples else SOURCES_HEADER,
        "accounts.csv": ACCOUNTS_EXAMPLE if with_examples else ACCOUNTS_HEADER,
        "categories.csv": CATEGORIES_EXAMPLE if with_examples else CATEGORIES_HEADER,
        "recurring.csv": RECURRING_EXAMPLE if with_examples else RECURRING_HEADER,
    }
    for name, content in files.items():
        path = os.path.join(rules_dir, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
    # adapters/ README (the column maps are code; this documents adding one)
    ad_readme = os.path.join(rules_dir, "adapters", "README.txt")
    if not os.path.exists(ad_readme):
        with open(ad_readme, "w", encoding="utf-8") as fh:
            fh.write(
                "Per-bank column maps live in the engine's adapters. To add a new bank:\n"
                "run the engine, let the generic fallback flag the file, then run Layer B\n"
                "(the accountant pass) to propose a column map you approve.\n")
