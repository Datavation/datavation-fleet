# Routine: cashflow_runway_forecast

**Agent:** Quinn   **Owner:** Austen King / Datavation Ltd
**Version:** 0.1   **Last updated:** 2026-07-13   **Status:** Draft (staged, awaiting promotion)

## Purpose
Produce the 30/60/90-day cash outlook: can Rex cover payroll-equivalents and commitments,
what the runway is at current burn, and the named risks inside the window.
It deliberately does **NOT** move money, promise precision it doesn't have (assumptions are
stated), or give regulated investment advice.

## Trigger
**Type:** Scheduled / trigger phrase.
**Fires when:** monthly, in the session after `month_end_close` completes, or Rex asks
("forecast", "runway", "can I cover…").

## Source of Truth
The workdir ledger + views (trailing actuals: monthly in/out, burn) and the recurring
commitments table (`rules\recurring.csv`) — per `skills\cash-flow-forecast\SKILL.md`.
Rex-facing output through the board; the forecast file lives in `output\reviews\`.

## Ownership & Scope
Per-agent (single-instance).

## Preconditions  (fail loud — if any fails, STOP and say so; never return an empty "all-clear")
1. Workdir resolves; ledger exists and spans ≥ 60 days (a forecast off less history is
   rendered but explicitly downgraded to "indicative only — <n> days of history").
2. `rules\recurring.csv` is readable (the commitments list is the forecast's backbone).
3. The latest consolidation is ≤ 7 days old — else run `consolidate` first.

## Steps  (one action each; mark each [mechanical] or [judgment])
1. [mechanical] **Compute the baseline** — trailing 3-month averages: income by world,
   spend by category, net burn; current liquid position from the consolidated view.
2. [mechanical] **Lay the commitments calendar** — recurring.csv items with expected
   amounts/cadence placed across the next 90 days; known one-offs from open_items answers.
3. [judgment]  **Project 30/60/90** — named criteria: (a) baseline net per month applied
   forward, (b) commitments placed on their dates, (c) receivables due inside the window
   counted only at a stated confidence (aged >60 days = not counted), (d) a low-case using
   the worst trailing month, not just the average.
4. [judgment]  **Name the risks** — named criteria: (a) any projected liquid dip below one
   month's committed spend ("the payroll test" — the explicit "can I cover payroll &
   commitments" verdict), (b) lumpy items inside the window (VAT/tax quarters, insurance
   renewals, the mortgage), (c) concentration: any single expected receipt > 25% of the
   window's income, (d) staleness of any source feeding the baseline.
5. **Render** using the Output Contract. File to `output\reviews\<YYYY-MM-DD>-forecast.md`.
6. [mechanical] **Post one Board record** — Conclusion: "30/60/90 forecast ready — <covered
   comfortably | tight at day N | shortfall risk flagged>" (no figures); 🔴 Rex only on a
   shortfall risk; Link = the forecast file.
7. **Stop.** No advice on where to invest a surplus; surface the surplus and stop.

## Output Contract  (the exact shape — this is the test)
```
# Cash-Flow & Runway Forecast — <YYYY-MM-DD> (30/60/90 days)
Basis: <n> days of actuals · baseline = trailing 3-month · assumptions stated inline
Confidence: NORMAL | INDICATIVE ONLY (<reason>)

## The payroll test
<one line: "Committed outgoings covered through day 90 in both cases" | "Low case dips below
committed spend at ~day <N> — see risk 1">

## Projection
| Horizon | Expected liquid | Low case | Committed out in window |
|---|---|---|---|
| +30d | £X | £Y | £Z |
| +60d | … | … | … |
| +90d | … | … | … |
Runway at current burn: <months, one decimal> (low case: <months>)

## Named risks
1. <risk — criterion — the date it bites — the human action that defuses it>
...

## Assumptions
<numbered; every number that isn't an actual has its assumption here>
```
Empty case (explicit, distinct):
```
Forecast NOT produced: <precondition that failed>. The last forecast (<date>) remains the
standing view and may be stale.
```

## Abort conditions
- Ledger < 60 days and no recurring.csv content → refuse a numeric projection entirely;
  output the empty case recommending the commitments table be filled first.
- Consolidation stale and refresh fails → empty case with the engine error verbatim.

## Change log
| Date | Version | Change |
|---|---|---|
| 2026-07-13 | 0.1 | Created. Staged under Builds\quinn-cfo-v1 by Cody per the 2026-07-11 Quinn commission (§4.3), conforming to Agent-Routine-Standard-v0_1. |
