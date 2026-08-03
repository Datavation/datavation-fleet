# Quinn — Client Configuration (client-0: Rex)

**What this is:** THE single named config seam (the Marshall/Libby pattern, Principle 8) —
every client-coupled value lives here, and swapping client = replacing this file, never the
skills or routines. This fill is **client-0: Rex** (personal + Rex Home Services +
Datavation), per the commission's §10.2 locked ruling: **multi-source, consolidated from
EXTRACTS, not one live API.**

**Data boundary:** this file names *where* data lives and *how* it arrives. It carries **no
figures, no account numbers, no balances** — those live only in the workdir's local rules
files (`accounts.csv`), which never ship, never enter memory, and never reach the board.

**Placeholders:** values marked `<SET-ON-PROMOTION>` are Rex's hand at promotion time —
the build ships figure-free.

---

## 1. The finance workdir (where the data lives)

| Setting | Value |
|---|---|
| `Workdir` | `C:\Users\Austen\OneDrive - Datavation Limited\Accounts\Finance\Quinn-WorkDir` 
— a private OneDrive folder, e.g. `...\Documents\Finance\Quinn-Workdir\` (NOT inside `Agents\Quinn\`) |
| `Extracts` | `<Workdir>\extracts\` 
— where exports are dropped |
| `Rules` | `<Workdir>\rules\` 
— sources.csv · accounts.csv · categories.csv · recurring.csv (seed once with `python -m engine --init <Workdir>`) |
| `Dashboard` | `<Workdir>\Finance-Dashboard.html` — Rex's read-only review surface; private OneDrive, never published (§10.4) |
| Machine-owned outputs | `<Workdir>\transactions.csv`, `Finance-Report.xlsx`, `_redacted\`, `open_items.csv` (engine-written; the `answer` column of open_items is Rex's) |

## 2. Declared sources (each with its ingest method — §10.2)

| # | World | Source | Ingest method | Adapter | Notes |
|---|---|---|---|---|---|
| 1 | RexHomeServices | Rex Home Services — banks on **Monzo**, books in **QuickBooks** | **QB-extract**: transaction CSV exported from QuickBooks (READ-ONLY) into `extracts\qb_rhs_*.csv` | `quickbooks_csv` | QB is the books of record for RHS, so the QB export (not the raw Monzo feed) is the ingested ledger — no double-count. Live QB MCP = convenience only, never a dependency (§10.5). |
| 2 | Datavation | Datavation — **Monzo**, no QuickBooks (low income, mostly outgoings) | **Monzo-export**: CSV into `extracts\monzo_datavation_*.csv` | `monzo_csv` | |
| 3 | Personal | **Barclays personal + joint** accounts | **Barclays-export**: XLSX workbook into `extracts\` | `barclays_xlsx` | Personal/Joint split on account number — the number map lives ONLY in the local `accounts.csv`. |
| 4 | Personal | Barclaycard | PDF statement into `extracts\` | `barclaycard_pdf` | Tie-out checked against the statement's own totals. |
| 5 | Personal | Mortgage letter | PDF into `extracts\` | `mortgage_pdf` | A balance statement, not a ledger — feeds the liability line. |

## 3. Manual / config lines (no source file — declared in `accounts.csv`, updated by hand)

These complete the net-worth roll-up (§10.2 item 4). Each is one row in the workdir's
`accounts.csv` with an `opening_balance` Rex maintains by hand and no transactions:

| Line | `type` | Roll-up bucket |
|---|---|---|
| National Savings / Premium Bonds | `savings` | Liquid (non-custodial) |
| Mortgage | `mortgage` | Liability (balance auto-overridden by the letter when a mortgage PDF is ingested) |
| The house | `asset` | Illiquid assets — in **net worth**, never in liquid/cash or net position |

## 4. Receivables source (for `routines\receivables_watch.md`)

| Setting | Value |
|---|---|
| AR aging extract | `<Workdir>\extracts\qb_ar_aging_*.csv` — QuickBooks AR-aging report export (READ-ONLY), dropped alongside the transaction extract |
| Fallback | If no AR extract exists, the routine says so and stops — it never infers receivables from the transaction ledger. |

## 5. Cadence & freshness expectations

| Source | Expected refresh | Staleness threshold (routine warns) |
|---|---|---|
| QB extract (RHS) | weekly | > 14 days old |
| Monzo export (Datavation) | monthly | > 45 days |
| Barclays export | monthly | > 45 days |
| Barclaycard / mortgage PDFs | on statement arrival | — |
| Manual lines | Rex updates when values change | reviewed at month-end |

A stale source is a **named warning in the review output** ("Datavation figures are 7 weeks
old"), never a silent gap — and never a fabricated fill-in.

## 6. What ships to another client

The seat (skills + routines + engine + this file's *structure*). What never ships: this
file's *values*, the workdir, the rules CSVs, any extract, any figure. A new deployment
gets a fresh client-config naming *their* sources against the same seams.
