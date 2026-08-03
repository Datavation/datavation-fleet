---
name: cash-flow-forecast
description: >
  Build the 30/60/90-day cash outlook with a low case, the payroll-test verdict ("can I
  cover commitments"), runway months, and named risks with dates. Use when
  cashflow_runway_forecast fires or Rex asks about runway/coverage. Do NOT use for
  historical review (finance-review) — this is forward-looking only, and it never gives
  regulated investment advice.
---

# cash-flow-forecast — forward view from actuals + commitments

**Adoption note (commission §11):** ADAPTS the Anthropic **Small Business** plugin's
`cash-flow-snapshot` (30/60/90 forecast, confidence bands, named risk flags — the exact
shape Rex ruled for). Adapted: (a) inputs are the consolidated extract ledger + the
recurring-commitments table, not live QuickBooks/Stripe connectors (extract-first, §10.5);
(b) UK cadence — VAT quarters, self-assessment, the mortgage — rather than US payroll
framing (the "payroll test" here = committed personal + business outgoings); (c) output is
the routine's fixed contract, filed locally — no XLSX-to-chat delivery of real figures.
The plugin's live-connector path may enrich the receivables-due input when granted;
convenience, never dependency.

## Method (deterministic where possible, judgment where stated)

1. **Baseline** [mechanical] — trailing 3-month averages from the ledger: income by world,
   spend by category, net burn. Low case = the worst single trailing month.
2. **Commitments calendar** [mechanical] — `rules\recurring.csv` items placed on their
   cadence dates across 90 days; add known one-offs recorded in open_items answers.
3. **Receivables inside the window** [judgment] — count expected receipts only at stated
   confidence; aged > 60 days counts as zero until it actually lands.
4. **Project** [mechanical] — expected and low-case liquid at +30/60/90; runway = liquid ÷
   average monthly net burn (only meaningful when burn is negative — say so when it isn't).
5. **The payroll test** [judgment] — does projected liquid stay above one month's committed
   outgoings at every point in the window, in both cases? One-line verdict, always present.
6. **Risks** [judgment] — per the routine's named criteria (dip points, lumpy items with
   dates, receipt concentration, stale baseline). Each risk = criterion + date it bites +
   the defusing action.
7. **Assumptions block** — every non-actual number gets its assumption listed. A forecast
   with hidden assumptions is a fabrication with extra steps.

Render exactly to `routines\cashflow_runway_forecast.md`'s Output Contract.
