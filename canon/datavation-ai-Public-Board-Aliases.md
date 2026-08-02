---
id: datavation-ai-Public-Board-Aliases
title: datavation.ai — Public Board Alias Register
domain: architecture
trust_class: canon
owner_seat: Architectus (Archy)
version: v0_1
status: ratified
date: 2026-07-07
provenance: Austen King (Rex) + Archy, live naming session 7 July 2026. Ratified by Rex.
supersedes: "Builds/fable-window/CONTEXT.md:30 — the 6-agent operational roster as the public face"
related: [Agent-Roster-and-Name-Bank-v0_1, Agent-Architecture-Roles]
labels: [datavation-ai, public-aliases, board, round-table, reserved-names, embodiment]
---

# datavation.ai — Public Board Alias Register v0.1

**Status:** Ratified by Austen King (Rex), 7 July 2026. Canon document. Owned by
Archy (Architectus).

> **This document does one job:** it holds the **public alias** each C-suite board
> seat wears on **datavation.ai** and any client-facing surface, and the **embodiment
> state** that drives the round-table visualization. It is not the seat register —
> that is **`Agent-Architecture-Roles.md`** (which masters who exists and is
> accountable). Where this and Roles disagree on a *seat*, Roles wins. This document
> is authoritative only for the **public alias** and **embodiment** of each seat.

The public face of datavation.ai is the full **13-member C-suite board**, presented
as a **round table of individuals** (Sintra-style). Operational sub-agents
(Cody/Marshall/Quill/Ivy/Libby) are backstage and do not appear on the public board.

---

## 1. Reserved-word policy (internal — the reason this register exists)

The Court of Rex **friendly names** (Rex, Hobbs, Holly, Sawyer, Parker, Quinn, Mason,
Cyrus, Archy, Dex, Oscar, Lincoln, Victor) **and** the **Latin canonical keys** (Rex,
Consilium, Praetor, Explorator, Praefectus, Quaestor, Mercator, Custos, Architectus,
Datum, Orator, Legatus, Vigil) are **reserved words — internal-only.** They never
appear on datavation.ai or any public/client surface. The public product knows the
board **only by the aliases below.** Any public artifact (e.g. the site's
`board.json`) is built to **exclude** internal names and Latin keys so they cannot
leak — enforced structurally, not by instruction.

## 2. Embodiment model (per seat — drives the viz)

| State | Icon | Meaning |
|---|---|---|
| **Person** | 👤 | A real human occupies the seat |
| **Augmented** | 👤⚡ | A person **plus** a bank of AI elements/tools behind them |
| **Agent** | 🤖 | Fully autonomous AI |

Embodiment is per-seat and may change over time (a seat can graduate Person →
Augmented → Agent).

## 3. The board

| # | C-suite | Public alias | Function (public one-liner) | Embodiment | Internal *(reserved — not public)* |
|---|---|---|---|---|---|
| 1 | **CEO** | **You** *(the viewer)* | Sets direction; owns the table | 👤 Person | Austen · Rex *(this instance only)* |
| 2 | **CSO** Strategy | **Lore** | Reads the board, calls the moves | 👤⚡ Augmented | Hobbs · Consilium |
| 3 | **Chief of Staff** | **Relay** | Routes the work, keeps the table moving | 🤖 Agent | Holly · Praetor |
| 4 | **CINO** Intelligence | **Argus** | Scouts the market, brings back signal | 🤖 Agent | Sawyer · Explorator |
| 5 | **COO** Operations | **Gear** | Runs delivery day to day | 👤⚡ Augmented | Parker · Praefectus |
| 6 | **CFO** Finance | **Tally** | Holds the money, keeps the books straight | 👤⚡ Augmented | Quinn · Quaestor |
| 7 | **CRO** Revenue | **Surge** | Wins and grows the revenue | 👤⚡ Augmented | Mason · Mercator |
| 8 | **CIO** Information | **Forge** | Guards the systems and the stack | 🤖 Agent | Cyrus · Custos |
| 9 | **CTO** Technology | **Arc** | Sets and holds the build standard | 🤖 Agent | Archy · Architectus |
| 10 | **CDO** Data | **Veda** | Owns the data as an asset | 🤖 Agent | Dex · Datum |
| 11 | **CMO** Marketing | **Vox** | Shapes the story and the demand | 🤖 Agent | Oscar · Orator |
| 12 | **CCO** Communications | **Herald** | Carries the message in and out | 🤖 Agent | Lincoln · Legatus |
| 13 | **CRiO** Risk & Governance | **Lumen** | Watches the downside, holds the line | 🤖 Agent | Victor · Vigil |

## 4. Seat 1 is the instance variable

The CEO seat renders as **"You"** — the person viewing/hiring the fleet, at the head
of *their own* board. It is the **only client-parameterized seat**: Iain Jack for an
IHS instance, Dan Keane for ECC, Austen for Datavation's own. The other twelve are the
**fixed, portable product**. This is Principle 8 expressed in the UI — the board is
the template; the CEO chair is the instance variable. Never hardcode a name in the CEO
seat.

## 5. Where this surfaces

- **datavation.ai** — the round-table visualization (Cody build; source of truth
  `board.json`). Supersedes the old 6-agent "meet the fleet".
- **Notion** — the *Court of Rex — Agent Register* database carries `Public Alias` +
  `Embodiment` per seat.
- **Aliases drawn from the bank** — Lore, Veda et al. originate in the Datavation-IP
  set of `Agent-Roster-and-Name-Bank-v0_1.md` Part C; drawing them here removes them
  from the available pool (the bank's no-double-assign rule).

---

*Canon. Ratified by Austen King (Rex), 7 July 2026.*
*Seat authority remains Agent-Architecture-Roles.md — this is the public-alias +
embodiment register. Internal names + Latin keys held reserved.*
*Next review: at next Memory Audit, or when a seat is added/renamed/re-aliased.*
