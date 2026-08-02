---
id: Agent-Roster-and-Name-Bank-v0_1
title: Agent Roster Index & Name Bank
domain: architecture
trust_class: canon
owner_seat: Architectus (Archy)
version: v0_1
status: ratified
date: 2026-06-25
provenance: Austen King + Archy, consolidation session 25 June 2026. Merged from three superseded Word drafts (The Court of Rex; Agent Roster and Agent Name Bank; Agent Roster) now archived.
labels: [roster, names, name-bank, register, court-of-rex, reserved-names, partner-fleet]
---

# Agent Roster Index & Name Bank v0.1

**Status:** Ratified by Austen King, 25 June 2026. Canon document. Owned by Archy (Architectus).

> **This document is NOT the seat register.** The authoritative roster of seats —
> who exists, who is accountable, each role's full definition and status — is
> **`Agent-Architecture-Roles.md`**. Where this document and Roles ever
> disagree, **Roles wins.**
>
> This document does one job Roles does not: it is the **name register** — the
> single place that tracks every *name* in the fleet's universe. Three kinds:
> **assigned** (a name in use, pointing to where its seat is defined),
> **reserved** (held, not yet assigned), and **available** (the name bank for
> future agents and partner deployments). Its purpose is to stop name collisions
> and stop Austen re-deriving names he has already chosen.

---

## Part A — Assigned Names (index, not definitions)

This is a thin pointer index. It carries only the stable facts: the friendly
name, the Latin canonical key (which never moves — see Roles, Part 2), the seat
or function, and **which Canon document defines it in full**. It deliberately
carries **no status field** — live status lives in the Notion *Court of Rex —
Agent Register* (the queryable view) and seat status is mastered in Roles. Adding
status here would create a third master that drifts.

### Court of Rex — board seats

| Friendly | Latin key | Seat / Function | Defined in |
|---|---|---|---|
| Austen | Rex | CEO | Agent-Architecture-Roles |
| Hobbs | Consilium | CSO — Strategy | Agent-Architecture-Roles · Agent-Strategy-Seat-Definition-v0_4 |
| Holly | Praetor | Chief of Staff (root agent) | Agent-Architecture-Roles |
| Sawyer | Explorator | CINO — Intelligence | Agent-Architecture-Roles |
| Parker | Praefectus | COO — Operations | Agent-Architecture-Roles |
| Quinn | Quaestor | CFO — Finance | Agent-Architecture-Roles |
| Mason | Mercator | CRO — Revenue | Agent-Architecture-Roles |
| Cyrus | Custos | CIO — Information | Agent-Architecture-Roles |
| Archy | Architectus | CTO — Technology *(peer of CIO/CDO, not subordinate)* | Agent-Architecture-Roles |
| Dex | Datum | CDO — Data *(peer of CIO/CTO, not subordinate)* | Agent-Architecture-Roles |
| Oscar | Orator | CMO — Marketing | Agent-Architecture-Roles |
| Lincoln | Legatus | CCO — Communications | Agent-Architecture-Roles |
| Victor | Vigil | CRiO — Risk & Governance | Agent-Architecture-Roles |

### Sub-agents and operational agents (report into a seat)

| Friendly | Latin key | Role | Reports to | Defined in |
|---|---|---|---|---|
| Marshall | Cursor | Client-workflow agent (TPG/Equans) | Parker (COO) | Agent-Architecture-Roles |
| Cody | — *(Faber proposed, not ratified)* | Engineering agent | Archy (CTO) | Agent-Architecture-Roles |
| Tessa | Probator | QA / testing agent — independent build verification (born + ratified 2026-07-11) | Archy (CTO) | Agent-Architecture-Roles |
| Ivy | — | Customer Services agent | Lincoln (CCO) | Agent-Architecture-Roles |
| Quill | — *(pending)* | Personal Assistant (MVP) | Holly (Chief of Staff) | **This document, §A.1 — seat PROPOSED for Roles v0.4** |
| Libby | Curatrix | Tabularium curator & knowledge-engineering engine (born 2026-07-05, Live) — reusable per-vault (Datavation IP) | **Cyrus (CIO)** | Agent-Library-Filing-Standard-v0_1 · Agent-Architecture-Capability-v0_3 |

### Infrastructure roles (parked off the org chart — they are not board seats)

| Friendly | Latin key | What it is | Defined in |
|---|---|---|---|
| Tabularium | — | The library *institution* (the room, a tool — not an agent) | Agent-Library-Filing-Standard-v0_1 |

> **Three corrections banked here against the superseded Word drafts** (Canon was
> already right on all three; the drafts were wrong):
> 1. **Libby is *Curatrix*, not "Librarius", and is NOT a board *seat*.**
>    Originally parked off-chart as infrastructure; **re-decided 2026-07-05** (Rex) once
>    she was built — she is now a **live sub-agent under Cyrus (CIO)**, on the org chart
>    below the CIO like Cody below the CTO. Still not a board seat (Roles v0.5 org chart
>    + sub-agents table; Filing Standard §6).
> 2. **Archy (CTO) and Dex (CDO) are full peer board seats — NOT subordinate to
>    Cyrus (CIO).** Technology, Data and Information are three equal officers
>    (Roles, "Collisions resolved" §4).
> 3. **Marshall's Latin key is *Cursor* and he reports to Parker (COO) only** —
>    not to Holly (Roles, sub-agents table).

### §A.1 — Quill (Personal Assistant, MVP) — interim definition

**Quill** is the friendly name now assigned to the personal-assistant agent that
was being scoped under the working label "Dex" in the build briefs. That label
was a collision: **Dex is the reserved key for the CDO seat (Datum)** and cannot
be reused. Quill takes its place.

- **Origin of the name:** *Quill* — writing, recording, capturing and returning
  knowledge. Drawn from the Datavation IP name bank (Part C); now removed from
  the available pool.
- **Role:** A channel-agnostic personal assistant — holds knowledge, returns it
  on demand, manages reminders and bookings for Austen. WhatsApp is the *proving
  channel* for the MVP, not the product; the engine must not be welded to it.
- **Reports to:** Holly (Chief of Staff), as a personal-productivity agent.
- **Status:** Name **assigned**. Seat **PROPOSED** for inclusion in Roles v0.4 —
  not yet a ratified seat. Held here as the interim home until Austen ratifies
  the Roles update. The MVP build (three-gate sequence) is specced separately in
  the build brief and is **not** authorised by this document.

---

## Part B — Internal Fleet Names: Reserved & Available

Names held for future internal Court of Rex agents. Not for partner deployments
without first being released here.

| Name | State | Notes |
|---|---|---|
| **Fern** | Reserved | Held for a future role; no current seat. Do not assign. (Roles, "Collisions resolved" §8 — Fern retired/reserved.) |
| **Kelvin** | Available | Temperature unit; unexpectedly sophisticated. Carries a quiet **Calvin and Hobbes** echo — fitting, given Hobbs (the tiger, not the boy) is already a seat. Strong candidate for a future internal agent. *(Note: the superseded drafts read "Kelvin and Hobbes" — that was a Wispr transcription of "Calvin and Hobbes". The name origin of the Hobbs seat is Calvin and Hobbes; "Kelvin" survives here only as an available, unrelated name.)* |

---

## Part C — Partner Fleet Name Bank (Trades)

For use when Datavation builds agent fleets for **partner businesses** (e.g.
Iain Jack / AHS). These are not Court of Rex seats — they are a ready pool so
Austen can offer a named character quickly without re-brainstorming. Organised by
trade so a name can be matched to a client's sector.

> **Rule:** if a name is drawn from this bank for any agent, **remove it from the
> bank in the same edit** to prevent double-assignment. (Quill has already been
> drawn from the Datavation IP set below and removed.)

### Painting & Decorating
| Name | Origin | Notes |
|---|---|---|
| Gloss | Paint finish | Maps to report generation / surface processing |
| Coat | Coat of paint | Direct, trade-facing |
| Sheen | Paint sheen | Sounds like a real name, trade-relevant |
| Tint | Colour tint | Minimal, sharp |

### Building & Construction
| Name | Origin | Notes |
|---|---|---|
| Wren | Sir Christopher Wren + small bird | Strong dual meaning — architect/trades. Distinctly British |
| Noggin | Timber-framing term + British slang for head/brain | Excellent for an ops or memory agent |
| Morty | Mortar | Memorable, pop-culture adjacent |
| Dado | Carpentry joint | Sophisticated, understated |
| Brix | Bricklaying | Punchy, brandable |

### Plumbing & Pipework
| Name | Origin | Notes |
|---|---|---|
| Pip | Pipe + seed/beginning | Short, British, great on voice |
| Flo | Flow | Clean, widely understood |
| Flux | Soldering flux | Implies movement — good agent energy |
| Val | Valve | Understated, works as a human name |

### Heating & Gas
| Name | Origin | Notes |
|---|---|---|
| Flue | Flue pipe | Implies direction / output |
| Rad | Radiator | Self-aware — "rad" also means cool |
| Kelvin | Temperature unit | **Also held in the internal bank (Part B)** — do not double-assign |

### Garden & Landscaping
| Name | Origin | Notes |
|---|---|---|
| Heath | Heathland | Very English, strong |
| Rowan | Rowan tree | Proper name, works naturally |
| Moss | Garden moss | Quiet, present — good "vault" energy. Note: IT Crowd association |
| Briar | Briar plant | Character and edge |

### Electrical
| Name | Origin | Notes |
|---|---|---|
| Ohm | Unit of resistance | Almost meditative — suits a governance agent |
| Lumen | Unit of light | Perfect for an insights / intelligence agent |
| Arc | Electrical arc + architecture | Dual-meaning potential |
| Sparks | Electrician slang | Friendly, immediately recognisable |

### Datavation IP / Product Naming
| Name | Origin | Notes |
|---|---|---|
| Veda | Sanskrit: knowledge / wisdom | Datavation-brand aligned; product-naming potential |
| Lore | Institutional knowledge / deliberate misspelling of *Law* | Legal-AI product potential |
| Axon | Neural pathway, data flow | Very Datavation; zero ambiguity about being AI |
| ~~Quill~~ | Writing, recording, data capture | **DRAWN — assigned to the Personal Assistant MVP (§A.1). Removed from pool.** |
| Lumen | Light / insight | Crossover from electrical — works for analytics |

---

## Part D — The Notion ↔ Tabularium pattern (how this document is surfaced)

Confirmed with Austen, 25 June 2026, as the standard pattern for fleet registers:

- **Notion holds the headline, queryable layer** — one row per agent / name, with
  the fields needed to answer "does this exist, what is it, what's its status" at
  a glance, and to drive a dashboard.
- **Each Notion row carries a *Canon Document* link** pointing to the authoritative
  Tabularium markdown where the full detail lives — this document, or Roles, or
  the relevant seat-definition doc.
- **The markdown in the Tabularium is the source of truth**; Notion is a view.
  Detail is read (and, when agreed, edited) in the markdown; status is tracked in
  Notion.
- **Readability:** these Canon markdown files can be rendered to HTML (as the
  fleet dashboards already are) when a more readable reference surface is wanted.
  Logged as a future option, not built here.

The Notion database for this register is **Court of Rex — Agent Register**, under
the *Archy — Architecture Governance* page.

---

*Canon. Ratified by Austen King, 25 June 2026.*
*Authoritative seat register remains Agent-Architecture-Roles.md — this is the name register and a pointer index.*
*Next review: at next Memory Audit, when a seat is added/renamed, or when Roles v0.4 ratifies the Quill seat.*
