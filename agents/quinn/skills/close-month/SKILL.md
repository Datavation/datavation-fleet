---
name: close-month
description: >
  Close a calendar month: verify full source coverage, reconcile parsed ledger vs each
  source's stated totals, write the P&L narrative with variance vs prior month, assemble
  the close packet. Use when month_end_close fires or Rex says "close the month." Do NOT
  use it to post/adjust anything in QuickBooks (read-only, always) or to send anything to
  the accountant (draft handoff; Rex sends).
---

# close-month — reconcile, narrate, packet

**Adoption note (commission §11):** ADAPTS the Anthropic **Small Business** plugin's
`close-month`/`month-end-prep` (reconcile books vs processor settlements, flag gaps, P&L
narrative, close packet) and carries the **Finance** plugin's month-end discipline
(GL↔subledger-style reconciliation, income-statement variance analysis). Adapted: (a)
reconciliation is extract-vs-extract — the consolidated ledger against each source's own
stated totals (statement tie-outs, QB extract period totals) — not QuickBooks-vs-PayPal
live pulls; (b) no accrual journal entries are *posted* anywhere — accrual-style
observations ("May includes an invoice paid in June") go in the narrative as notes for the
accountant; (c) the packet is filed locally for Rex to send on.

## Procedure

1. **Coverage gate** [mechanical] — every enabled source has extract(s) spanning the close
   month. Any gap → BLOCKED, named per source. A month never closes on partial data.
2. **Fresh consolidation** [mechanical] — full run via `consolidate`.
3. **Reconcile** [mechanical] — collect: engine tie-out results (parsed vs stated totals
   per statement), month's uncategorised count and % of spend, unmatched transfer flags,
   dedup anomalies (a duplicate spike usually means an overlapping export).
4. **Variance analysis** [judgment] — vs prior close: income delta by world with cause;
   top 3 spend movements by category; flag any category ±40% vs its 3-month average with
   an explanation or an explicit "unexplained."
5. **P&L narrative** [judgment] — per the routine's named criteria: business worlds and
   personal clearly separated, one health verdict per world, plain English, no smoothing.
6. **Packet** [mechanical] — `output\reviews\<YYYY-MM>-close\`: `close-narrative.md`
   (narrative + reconciliation + open questions) + the month's `Finance-Report.xlsx` copy.
   Real figures stay in the packet; the board card carries none.
7. **Open questions for Rex** — each answerable in one sentence; his answers land in
   `open_items.csv`'s answer column and improve the rules for next month.

Render exactly to `routines\month_end_close.md`'s Output Contract.
