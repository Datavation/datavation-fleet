"""Build a synthetic workdir with figure-free FAKE statements for self-testing.

None of this is real financial data — invented merchants, invented amounts,
invented account numbers. It exercises every code path: two accounts split from
one Barclays workbook, a Monzo CSV, a QuickBooks transaction-export CSV, an
internal transfer between two own accounts, a normal spend/income, an
uncategorised row, and the manual/config lines (a savings line and an illiquid
asset) that complete the net-worth roll-up.
"""

from __future__ import annotations

import os


SOURCES = (
    "world,account_id,adapter,path,kind,enabled,note\n"
    "Personal,barclays_personal,barclays_xlsx,statements/barclays.xlsx,file,Y,\n"
    "Datavation,datavation_monzo,monzo_csv,statements/monzo.csv,file,Y,\n"
    "RexHomeServices,rhs_quickbooks,quickbooks_csv,statements/qb_rhs.csv,file,Y,QB extract — read-only\n"
)

# account numbers here are FAKE and map the two Barclays worlds
ACCOUNTS = (
    "account_id,name,world,type,scope,custodial,account_number,opening_balance,note\n"
    "barclays_personal,Barclays Personal,Personal,current,Personal,N,11110000,1000.00,\n"
    "barclays_joint,Barclays Joint,Joint,current,Family,N,22220000,500.00,\n"
    "datavation_monzo,Datavation,Datavation,current,Business,N,,0.00,\n"
    "rhs_quickbooks,Rex Home Services,RexHomeServices,current,Business,N,,0.00,\n"
    "savings_bond,Test Bond,Personal,savings,Personal,Y,,50000.00,Custodial — held for family\n"
    "ns_savings,Test Premium Bonds,Personal,savings,Personal,N,,10000.00,Manual line — no transactions\n"
    "house,Test House,Personal,asset,Family,N,,250000.00,Manual line — illiquid asset\n"
)

CATEGORIES = (
    "order,match_type,pattern,category,subcategory,scope\n"
    "10,substring,tesco,Groceries,,\n"
    "20,substring,salary,Income,Salary,\n"
    "30,substring,transfer,Transfers,,\n"
)

RECURRING = (
    "pattern,label,match_type,expected_amount,cadence\n"
    "netflix,Netflix,substring,,monthly\n"
)

MONZO_CSV = (
    "Transaction ID,Date,Time,Type,Name,Amount,Currency,Category,Money Out,Money In,Description\n"
    "tx_001,01/05/2025,09:00:00,Card,NETFLIX,-9.99,GBP,Entertainment,9.99,,Netflix monthly\n"
    "tx_002,03/05/2025,10:00:00,Faster payment,CLIENT LTD,1500.00,GBP,Income,,1500.00,Invoice 42\n"
    "tx_003,05/05/2025,11:00:00,Card,MYSTERY VENDOR,-40.00,GBP,General,40.00,,Unknown thing\n"
)

# QuickBooks Online transaction-list export shape: leading title rows, then the
# header, signed Amount, a footer TOTAL row with no date (must be skipped), and
# two split lines sharing one document Num (both must survive dedup).
QB_CSV = (
    "Test Trading Ltd\n"
    "Transaction Report,,,,,,,\n"
    "Date,Transaction Type,Num,Name,Memo/Description,Account,Split,Amount\n"
    "02/05/2025,Invoice,1001,CUSTOMER A,Boiler service,Debtors,Sales,350.00\n"
    "04/05/2025,Expense,,TRADE SUPPLIES CO,Copper pipe,Monzo,Materials,-85.25\n"
    "08/05/2025,Invoice,1002,CUSTOMER B,Split line one,Debtors,Sales,120.00\n"
    "08/05/2025,Invoice,1002,CUSTOMER B,Split line one,Debtors,Sales,120.00\n"
    ",,,,,,TOTAL,504.75\n"
)


def _barclays_rows():
    # (date, account_number, amount, memo)
    return [
        ("02/05/2025", "11110000", "-45.50", "TESCO STORES 1234"),
        ("03/05/2025", "11110000", "2000.00", "ACME LTD SALARY"),
        ("06/05/2025", "11110000", "-300.00", "TRANSFER TO JOINT 22-22-00 22220000"),
        ("06/05/2025", "22220000", "300.00", "TRANSFER FROM PERSONAL"),
        ("07/05/2025", "22220000", "-80.00", "TESCO STORES 5678"),
    ]


def write_barclays_xlsx(path: str) -> bool:
    """Write the synthetic Barclays workbook. Returns False if openpyxl absent."""
    try:
        from openpyxl import Workbook
    except ImportError:
        return False
    wb = Workbook()
    ws = wb.active
    ws.append(["Date", "Account Number", "Amount", "Memo"])
    for row in _barclays_rows():
        ws.append([row[0], row[1], float(row[2]), row[3]])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    return True


def build_workdir(workdir: str) -> dict:
    """Create rules/ + statements/ under workdir. Returns a dict of facts tests assert on."""
    rules = os.path.join(workdir, "rules")
    stmts = os.path.join(workdir, "statements")
    os.makedirs(rules, exist_ok=True)
    os.makedirs(stmts, exist_ok=True)

    for name, content in [
        ("sources.csv", SOURCES), ("accounts.csv", ACCOUNTS),
        ("categories.csv", CATEGORIES), ("recurring.csv", RECURRING),
    ]:
        with open(os.path.join(rules, name), "w", encoding="utf-8") as fh:
            fh.write(content)

    with open(os.path.join(stmts, "monzo.csv"), "w", encoding="utf-8") as fh:
        fh.write(MONZO_CSV)

    with open(os.path.join(stmts, "qb_rhs.csv"), "w", encoding="utf-8") as fh:
        fh.write(QB_CSV)

    has_xlsx = write_barclays_xlsx(os.path.join(stmts, "barclays.xlsx"))

    return {
        "rules": rules,
        "statements": stmts,
        "has_xlsx": has_xlsx,
        # if xlsx present: 5 barclays + 3 monzo + 4 QB = 12 rows; internal transfer = 1 pair
        "expected_txn_min": 12 if has_xlsx else 7,
        "expected_transfer_pairs": 1 if has_xlsx else 0,
        # manual/config lines the net-worth roll-up must show
        "asset_total": "250000.00",
        "manual_savings": "10000.00",
    }


# --- synthetic Barclaycard statement TEXT (for the pure-parser tie-out test) ---
# Real Barclaycard MONTHLY layout: DD Mon dates (no year), section-separated
# credits/charges, control totals by label. Filename carries the statement period.
BARCLAYCARD_FILE = "Monthly BarclayCard Statement_19-DEC-25.pdf"
BARCLAYCARD_TEXT_GOOD = """Your Platinum Visa monthly statement
Your previous balance: £200.00
Payments towards your account: £100.00
Your new balance: £174.99
Your transactions
Payments towards your account £100.00
19 Dec Payment, Thank You £100.00
Transactions, interest and charges £74.99
How you've used your card £74.99 limit of £5,000.00
05 Dec 123 AMAZON* ABC, London £24.99
06 Dec 456 SHELL FUEL, Colchester £50.00
"""

# same statement but the stated purchases subtotal is wrong (should be 74.99)
BARCLAYCARD_TEXT_BAD = BARCLAYCARD_TEXT_GOOD.replace(
    "How you've used your card £74.99", "How you've used your card £99.99")

MORTGAGE_TEXT = """Your Mortgage Statement
Outstanding balance 150000.00
Monthly payment 800.00
Number of payments made 12
Total amount paid 9600.00
Interest rate 4.50 %
"""
