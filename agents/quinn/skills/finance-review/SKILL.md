---
name: finance-review
description: >
  Turn a fresh consolidation into the weekly finance review: position, week's movements,
  receivables/payables headline, "anything unusual," and the ranked 3-things-to-look-at.
  Use when weekly_finance_review fires or Rex asks how the finances look. Do NOT use for
  period close (close-month) or projections (cash-flow-forecast).
---

# finance-review — the judgment pass over the consolidated ledger

**Adoption note (commission §11):** ADAPTS the Anthropic **Small Business** plugin's
business-pulse/brief pattern (`business-pulse`, `monday-brief` — cash position, watch-list,
"the one thing needing attention"). Adapted because Rex's deployment is **extract-based**:
the plugin skills assume live connectors (QuickBooks/PayPal/HubSpot MCP); Quinn's client-0
reads consolidated extracts. Where those connectors ARE live and granted read-only, the
plugin skills may enrich this review (e.g. a live AR-aging pull) — as convenience, never a
dependency. The output contract is `routines\weekly_finance_review.md`'s either way.

## Procedure

1. **Require a fresh consolidation** (≤ 1 day old, else run `consolidate` first). Inputs:
   the dashboard JSON views, this week's ledger slice, `open_items.csv`, run notes.
2. **Position** — liquid, net position, direction vs prior week (compare against the prior
   review file in `output\reviews\`, if present).
3. **Movements** — in/out/net for the 7-day window; name the drivers (top receipts, top
   payments) rather than restating totals.
4. **Unusual** — apply the routine's named criteria (3× category median; new large
   merchant; recurring misfire; tie-out/ingest flags; stale sources). Every flag cites its
   criterion — auditable judgment, not vibes (Routine Standard R1).
5. **3 things** — rank by cost-to-leave (blocks money in > time-decaying > recurring >
   blocking-answers). Phrase each as the human action ("Answer the two categorisation
   questions" — not "review open_items").
6. **Render** the routine's Output Contract exactly. File it; post the board record
   (no figures on the card).

## Tone

CFO-honest: no smoothing, no premature reassurance, no figure without a source. "I don't
know yet — it's uncategorised" is a valid and required answer.
