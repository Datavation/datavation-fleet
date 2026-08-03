# Routine: month_end_close

**Agent:** Quinn   **Owner:** Austen King / Datavation Ltd
**Version:** 0.1   **Last updated:** 2026-07-13   **Status:** Draft (staged, awaiting promotion)

## Purpose
Close the prior month: reconcile the consolidated ledger against each source's own totals,
write the P&L narrative with variance vs the prior month, and file a close packet.
It deliberately does **NOT** post journal entries anywhere, write back to QuickBooks, file
anything with HMRC, or send anything to the accountant — the packet is a draft handoff Rex
sends.

## Trigger
**Type:** Scheduled / trigger phrase.
**Fires when:** first Quinn session on or after the 1st of a month (closing the month just
ended), or Rex asks ("close the month", "month-end", "close May").

## Source of Truth
The workdir ledger (`transactions.csv` + views) as produced by `consolidate`, checked
against **each source's own stated totals** (statement tie-outs; QB extract totals). The
close packet lands in `output\reviews\`; the board carries the Output Record.

## Ownership & Scope
Per-agent (single-instance — one CFO seat closes the books).

## Preconditions  (fail loud — if any fails, STOP and say so; never return an empty "all-clear")
1. Workdir + rules resolve (as weekly_finance_review).
2. **Every enabled source has an extract covering the full month being closed** — a month
   cannot close on partial data. Missing coverage = a named gap, and the close is BLOCKED,
   not approximated.
3. The prior month's close packet exists (for variance), or this is flagged as the first close.

## Steps  (one action each; mark each [mechanical] or [judgment])
1. [mechanical] **Run the consolidation** (full run; refreshes dashboard).
2. [mechanical] **Check coverage** — for the close month, each enabled source has ≥1 ingested
   file whose transactions span it (QB extract for RHS, Monzo for Datavation, Barclays for
   personal). List any gap by source name.
3. [mechanical] **Reconcile** — per `skills\close-month\SKILL.md`: engine tie-out flags,
   uncategorised count for the month, unmatched internal transfers, and (where the extract
   states its own period totals) parsed-vs-stated totals per account.
4. [judgment]  **Write the P&L narrative** — named criteria: (a) income vs prior month and
   why, (b) top 3 spend movements by category with cause where knowable, (c) business
   (per-world) vs personal clearly separated, (d) one-line margin/health verdict per world.
   Never smooth: an unexplained variance is stated as unexplained.
5. [mechanical] **Assemble the close packet** in `output\reviews\<YYYY-MM>-close\`:
   `close-narrative.md` (the narrative + reconciliation results + open questions) and a
   copy of `Finance-Report.xlsx` for the month context. Real figures live in the packet —
   the packet stays in the private tree / workdir, per the data boundary.
6. [judgment]  **Flag what needs Rex** — unanswered open_items blocking a clean close,
   uncategorised above 5% of the month's spend, any reconciliation break.
7. [mechanical] **Post one Board record** — Conclusion: "<Month> close ready — clean" or
   "<Month> close ready — N items need your answer" (no figures); Action Required = 🔴 Rex
   if answers/decisions are needed, else ⚪ None; Link = the packet.
8. **Stop.** Do not carry corrections into rules files without logging each change; do not
   touch QuickBooks.

## Output Contract  (the exact shape — this is the test)
```
# Month-End Close — <YYYY-MM>
Status: CLEAN | N OPEN ITEMS | BLOCKED (coverage gap: <sources>)
Coverage: <source: full/partial/missing, one per enabled source>
Reconciliation: <per account: OK | break (parsed vs stated, difference)>
Uncategorised this month: <n> transactions (<x>% of spend)

## P&L narrative
<step-4 narrative>

## Variance vs <prior YYYY-MM>
<income delta, top spend movements — or "First close: no prior month.">

## Open questions for Rex
<numbered, each one answerable in a sentence — or "None.">

Packet: output\reviews\<YYYY-MM>-close\
```
Empty case (explicit, distinct):
```
Month-end close NOT run for <YYYY-MM>: <precondition/coverage failure, named per source>.
No packet was produced. The close stays open until the gap is filled.
```

## Abort conditions
- Coverage gap (precondition 2) → the explicit empty case, board record 🔴 Rex naming
  exactly which export to drop in (that is his one action).
- Reconciliation break the tie-out flags → close renders with Status "N OPEN ITEMS", never
  silently CLEAN; the break is question #1 for Rex.
- Engine failure → empty case with the error verbatim.

## Change log
| Date | Version | Change |
|---|---|---|
| 2026-07-13 | 0.1 | Created. Staged under Builds\quinn-cfo-v1 by Cody per the 2026-07-11 Quinn commission (§4.2), conforming to Agent-Routine-Standard-v0_1. |
