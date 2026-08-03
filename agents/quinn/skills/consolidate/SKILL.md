---
name: consolidate
description: >
  Deterministic multi-source finance consolidation: ingest declared extracts (QuickBooks
  CSV, Monzo CSV, Barclays XLSX, Barclaycard/mortgage PDFs) plus manual config lines into
  one honest ledger, then render the report, redacted export, and the private HTML
  dashboard. Use whenever a routine needs fresh consolidated numbers, a new extract has
  landed, or Rex asks for a refresh/net-worth view. Do NOT use it to fetch anything live —
  it reads local files only, by design.
---

# consolidate — the deterministic engine behind Quinn's numbers

**Provenance:** salvaged from `Builds\finance-engine\` (2026-07-06, 12/12 self-tested,
Archy-gated) per the Quinn commission §8: the consolidation logic was right; the
double-click `refresh.bat` interface was the wrong shape and is **dropped** — this engine
is a skill Quinn's routines drive, never a launcher a human runs. Extended for Quinn v1:
`quickbooks_csv` adapter (QB-extract ingest, §10.2), the `asset` account class + net-worth
roll-up (manual config lines: savings / mortgage / the house), dashboard v2 (net worth,
Quinn-branded), launchers removed. Self-test: `tests\run_selftest.py`, 17/17.

## Guardrails (built at the capability layer, test-enforced)

- **No network, no send, no credentials** — the engine imports nothing that can reach a
  network/bank/mail server (test: `no_network_imports`). It cannot move money.
- **Read-only sources; writes only inside the workdir.**
- **Never fabricates** — unknown → `uncategorised` (counted) or an `open_items` question.
- **Redaction before any model pass** — `_redacted\transactions_redacted.csv` is the ONLY
  file a supervised Layer-B pass may read (masks sort codes / long numbers, drops raw
  descriptions).
- **Deterministic** — Decimal money, sorted dedup; re-runs are byte-identical.
- **Tie-out** — PDF statement parses are checked against the statement's own stated totals;
  mismatches FLAG to open_items, never silently accepted.
- **Custodial separated** — `custodial=Y` accounts sit outside net worth and burn entirely.

## How to run it (Quinn's routines do this; a human never has to)

```
cd skills\consolidate
python -m engine --workdir <Workdir> --inventory-only   # dry run: every source resolves?
python -m engine --workdir <Workdir>                    # full pipeline + dashboard refresh
python -m engine --init <Workdir>                       # seed a fresh workdir's rules\ skeleton
python -m engine --template <dir>                       # data-stripped shippable bundle (fleet IP)
```

`<Workdir>` comes from `context\client-config.md` §1. Exit code non-zero = fail loud:
surface the error verbatim, never proceed on partial output.

## The workdir contract

- **Human-owned (hand-edited between runs):** `rules\sources.csv` (source → adapter map),
  `rules\accounts.csv` (accounts + manual/config lines via `opening_balance`; the ONLY
  place account numbers live), `rules\categories.csv`, `rules\recurring.csv`, and the
  `answer` column of `open_items.csv`.
- **Machine-owned (never hand-edit):** `transactions.csv` (regenerated every run),
  `Finance-Report.xlsx`, `Finance-Dashboard.html`, `_redacted\`.
- **Manual/config lines:** an `accounts.csv` row with `opening_balance` and no source row.
  `type=asset` → illiquid (net worth only); `type=savings` non-custodial → liquid;
  `type=mortgage` → liability (auto-overridden by the letter balance when a mortgage PDF
  is ingested).

## Adapters (the ingest methods of client-config §2)

`quickbooks_csv` (QB transaction export — READ-ONLY extract; handles title rows, signed or
debit/credit amounts, skips dateless total rows, keeps split lines) · `monzo_csv` ·
`barclays_xlsx` (Personal/Joint split on account number) · `barclaycard_pdf` (tie-out) ·
`mortgage_pdf` (balance letter) · `generic` (unknown files are flagged, never guessed).

## Judgment layer on top (Quinn, not the engine)

After a run, Quinn — not the engine — reads the console notes and open_items and decides
what is worth surfacing (the routines' judgment steps). The optional supervised
"accountant" pass (`layer-b\accountant-prompt.md`) reads ONLY the redacted export and is
never required for the engine to complete.

## Self-test (synthetic, figure-free — never real data)

```
python tests\run_selftest.py     # 17/17 — includes QB adapter, split-line dedup,
                                 # manual-line net-worth roll-up, no-launcher template
```
