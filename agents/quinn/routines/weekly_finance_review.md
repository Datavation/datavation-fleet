# Routine: weekly_finance_review

**Agent:** Quinn   **Owner:** Austen King / Datavation Ltd
**Version:** 0.1   **Last updated:** 2026-07-13   **Status:** Draft (staged, awaiting promotion)

## Purpose
Produce the standing weekly review — cash position, money in and out this week, receivables
and payables headlines, anything unusual — as one plain summary with "3 things to look at."
It deliberately does **NOT** move money, send anything, forecast (that is
`cashflow_runway_forecast`), or close a period (that is `month_end_close`).

## Trigger
**Type:** Scheduled / trigger phrase.
**Fires when:** Monday morning session (first Quinn session of the ISO week), or Rex asks
("weekly review", "how are the finances", "finance review").

## Source of Truth
The consolidated ledger the `consolidate` skill produces in the workdir declared in
`context\client-config.md` — `transactions.csv` + the computed views (dashboard JSON) +
`open_items.csv`. Receivables headline comes from `receivables_watch`'s source (the AR
aging extract), never a private re-derivation. Rex-facing surfacing goes through the
Decision Board Output Record — no private list.

## Ownership & Scope
Per-agent (single-instance: Quinn is the one CFO seat; no other seat renders a finance
review).

## Preconditions  (fail loud — if any fails, STOP and say so; never return an empty "all-clear")
1. `context\client-config.md` resolves and its `Workdir` exists with a `rules\` folder.
2. Python can run the consolidate engine (`python -m engine --workdir <Workdir> --inventory-only` exits 0).
3. Today's date is known (decides "this week" = the 7 days ending today).

## Steps  (one action each; mark each [mechanical] or [judgment])
1. [mechanical] **Run the consolidation** — `skills\consolidate\` per its SKILL.md (full
   run, not inventory-only). This also refreshes `Finance-Dashboard.html`.
2. [mechanical] **Read the refreshed views** — consolidated position, this week's
   transactions (date within the last 7 days), open_items rows without an answer, and any
   run notes (adapter failures, tie-out flags, stale sources per client-config §5).
3. [judgment]  **Identify "anything unusual"** — named criteria: (a) a transaction > 3× the
   trailing-month median for its category, (b) a new merchant above a week's typical spend,
   (c) a recurring commitment that fired twice or not at all, (d) a tie-out or ingest flag,
   (e) a source past its staleness threshold.
4. [judgment]  **Rank "3 things to look at"** by cost-to-leave: (a) blocks money arriving
   (an overdue receivable), (b) time-decaying (a charge still disputable), (c) recurring —
   fixing it once saves every month, (d) unanswered open_items blocking categorisation.
   State the human action, not board jargon.
5. **Render** using the Output Contract. File to `output\reviews\<YYYY-MM-DD>-weekly-review.md`.
6. [mechanical] **Post one Board record** — Conclusion: "Weekly finance review ready" + the
   three headlines *described without figures*; Action Required = ⚪ None (🔴 Rex only if
   something genuinely needs his hand this week); Link = the review file.
7. **Stop.** Do not draft chases here (receivables_watch owns that), do not forecast, do
   not re-categorise history without logging it.

## Output Contract  (the exact shape — this is the test)
```
# Weekly Finance Review — week ending <YYYY-MM-DD>
Dashboard refreshed: <path>  ·  Ledger span: <from> → <to>  ·  Sources: <n> ok / <n> stale / <n> failed

## Position
<one line: liquid, net position, direction vs last week>

## This week
In: <£X from N receipts>   Out: <£Y across M payments>   Net: <£Z>
<2–4 lines of what moved and why>

## Receivables / payables headline
<one line each, or "No AR extract this week — receivables not reviewed (see receivables_watch)">

## Unusual
<bullet list from step 3, each with the criterion that flagged it — or "Nothing unusual this week.">

## 3 things to look at
1. <thing — the specific human action>
2. <thing>
3. <thing>

## Needs your answer
<open_items without answers, or "Nothing waiting on you.">
```
Empty case (explicit, distinct):
```
Weekly review NOT run: <precondition that failed, verbatim>. Nothing was consolidated; the
dashboard is unchanged from <last refresh date>.
```

## Abort conditions
- Consolidation exits non-zero → output the empty case with the engine's error verbatim;
  board record 🔴 Rex only if the failure needs his hand (e.g. workdir missing), else fix-and-rerun.
- Every source stale beyond threshold → the review still renders but opens with a named
  staleness warning; never presents stale figures as current.
- Tie-out flags present → surfaced under "Unusual" as trust-the-numbers-carefully warnings;
  the review says which account's figures are affected.

## Change log
| Date | Version | Change |
|---|---|---|
| 2026-07-13 | 0.1 | Created. Staged under Builds\quinn-cfo-v1 by Cody per the 2026-07-11 Quinn commission (§4.1), conforming to Agent-Routine-Standard-v0_1. |
