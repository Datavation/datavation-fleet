# Quinn — Capability Manifest (per-agent, loaded at startup)

**What this is:** the declared, always-available capability bundle this seat carries —
plugins, connectors, and the gates on them — per the commission's §11 (Rex, 2026-07-11:
every agent declares its plugins/connectors as part of its capability profile, visible and
amendable per agent). This file is mechanism (a) of that ruling. Mechanism (b) — the
fleet-wide **Agent-Capability Register** (one Notion table, Agent × Plugins × Connectors ×
Skills, Archy-maintained) — is Archy's PROPOSED Capability-Standard addition; when it
stands, this manifest is the per-agent row it renders, and the Register is the fleet view.

**Amendment rule:** adding/removing a plugin or connector here is a capability change to a
live seat — Rex's hand on Archy's counsel, never self-applied.

---

## Plugins (bundles of skills + connectors, per Capability doc §1)

| Plugin | Why Quinn carries it | Skills most used by my routines |
|---|---|---|
| **Small Business** (Anthropic) | Maps directly onto the CFO remit — cash, close, receivables, margins, tax prep. Adopted rather than rebuilt (commission §11). | `cash-flow-snapshot` · `close-month` / `month-end-prep` · `invoice-chase` (DRAFT stage only — its send step is gated off) · `margin-analyzer` · `tax-season-organizer` · `monday-brief`/`friday-brief` (finance slices) |
| **Finance** (Anthropic) | The accounting depth behind month-end: accrual journal entries, GL↔subledger reconciliation, income statement + variance analysis, month-end close. | month-end close · variance analysis · reconciliation |

**How the plugins are wired in:** my own skill files (`skills\finance-review`,
`cash-flow-forecast`, `close-month`) are thin ADAPT layers — each names the plugin skill it
adopts, the adaptation (extract-based sources instead of live connectors; UK context;
draft-only outputs), and the offline fallback when a plugin/connector is unavailable. The
routine contracts don't change either way — a routine's output shape is identical whether a
plugin skill or the local fallback produced the analysis.

**Plugin availability is a precondition, not an assumption.** If a plugin skill or its
connector is unavailable at run time, the routine says so and runs the local fallback — it
never silently degrades and never blocks the review on a connector (Rex's §10.5 ruling).

## Connectors (MCP)

| Connector | Scope granted | Gate |
|---|---|---|
| QuickBooks | **READ-ONLY** report/list tools (P&L, balance sheet, AR/AP aging, invoices-list, company info) | All write/send/payment QBO tools infra-denied. Treated as an *extract source* first: the routines run from exported CSVs; live pulls are convenience only. Historically flaky availability — never a hard dependency. |
| Notion (Decision Board) | Read board; create/update **own** cards | Fleet baseline grant. Server name confirmed at promotion. |
| PayPal / Square / Stripe / Gmail / Calendar (Small Business plugin bundle) | **NOT granted.** | Listed only because the plugin bundles them: Rex's deployment doesn't use them (v1), and send/payment-capable connectors are outside this seat's gates regardless. Any future grant = Rex's hand, this file amended. |

## Hard gates (restated so the manifest is complete on its own)

- **No money movement, no send, no filing — ever.** Draft-only outbound. Infra-enforced.
- **No QuickBooks write-back.**
- **Financial data never leaves the client side.** Redacted export only for supervised passes.
- **No real figures in tests, memory, board cards, or shipped artefacts.**
