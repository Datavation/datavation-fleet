# Routine: consolidated_view

**Agent:** Quinn   **Owner:** Austen King / Datavation Ltd
**Version:** 0.1   **Last updated:** 2026-07-13   **Status:** Draft (staged, awaiting promotion)

## Purpose
Keep the standing personal + business consolidated view current: every declared source
ingested, both worlds clearly separated, one net-worth roll-up (liquid / illiquid assets /
liabilities / custodial), rendered on the private HTML dashboard. This is the commission's
standing "personal/business finance consolidation" need (§4.5) and the dashboard ruling
(§10.4). It deliberately does **NOT** editorialise (the review routines do that) — it makes
the numbers current and honest, then stops.

## Trigger
**Type:** Event / trigger phrase.
**Fires when:** any other routine needs a fresh consolidation (they call this), a new
extract lands and Rex asks for a refresh, or Rex asks ("refresh the dashboard",
"consolidated view", "net worth").

## Source of Truth
The declared sources in `context\client-config.md` §2–3, ingested by the `consolidate`
skill into the workdir ledger. The rendered surface is `<Workdir>\Finance-Dashboard.html` —
THE one review surface; no second copy is ever written elsewhere (single source, R2).

## Ownership & Scope
Per-agent (single-instance — one dashboard, one owner; another seat wanting finance data
reads the board record or asks Quinn, never renders its own copy).

## Preconditions  (fail loud — if any fails, STOP and say so; never return an empty "all-clear")
1. Workdir + rules resolve.
2. Inventory passes: `python -m engine --workdir <Workdir> --inventory-only` exits 0 and
   every enabled source row resolves to ≥1 file (a source resolving to nothing is a named
   warning, not a silent skip).

## Steps  (one action each; mark each [mechanical] or [judgment])
1. [mechanical] **Run inventory** (dry run) and record per-source file counts.
2. [mechanical] **Run the full consolidation** — ingest → normalise → dedup → categorise →
   reconcile transfers → tie-out → render (ledger, xlsx, redacted export, dashboard).
3. [mechanical] **Verify the render** — `Finance-Dashboard.html` mtime advanced this run;
   the embedded JSON parses; `net_worth`, `asset_total`, `liquid_total`,
   `liability_total`, `custodial_total` all present.
4. [judgment]  **Check the roll-up is honest** — named criteria: (a) every manual line from
   client-config §3 appears with a non-blank balance (a £0 house means the line was lost,
   not that the house is worthless — flag it), (b) both business worlds and Personal appear
   in the by-world view, (c) internal transfers netted (pairs count reported), (d) any
   tie-out flag or stale source named.
5. **Render** the Output Contract (console/summary — the dashboard itself is the artefact).
6. **Stop.** No board record for a routine refresh that another routine triggered (the
   calling routine posts); post one only when Rex asked directly (⚪ None, Link = dashboard path).

## Output Contract  (the exact shape — this is the test)
```
# Consolidated View refreshed — <YYYY-MM-DD HH:MM>
Sources: <world/source: n files ingested, or WARNING none found — one line each>
Ledger: <N> transactions (<from> → <to>) · <d> duplicates dropped · <t> transfer pairs netted
Roll-up: net worth present ✓ · manual lines present: <list> · custodial separated ✓
Flags: <tie-out/stale/uncategorised counts — or "none">
Dashboard: <path> (refreshed ✓)
```
Empty case (explicit, distinct):
```
Consolidation NOT run: <precondition failure / engine error verbatim>. The dashboard still
shows the <date> state — treat it as stale.
```

## Abort conditions
- Inventory failure or engine non-zero exit → empty case with the error verbatim.
- Dashboard file not rewritten (step 3 fails) → report FAILURE even if the ledger wrote —
  a stale dashboard silently presented as fresh is the worst outcome this routine can produce.

## Change log
| Date | Version | Change |
|---|---|---|
| 2026-07-13 | 0.1 | Created. Staged under Builds\quinn-cfo-v1 by Cody per the 2026-07-11 Quinn commission (§4.5, §10.2, §10.4), conforming to Agent-Routine-Standard-v0_1. |
