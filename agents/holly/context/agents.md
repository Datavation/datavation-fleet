# context/agents.md — Holly Reference

## Agent Register & Roster

Outline of Austen's agent fleet. Source: *Datavation Agent Roster and Agent Name
Bank.docx* (Draft v0.2), reconciled with what Holly can verify live.
Naming convention: `[Business / Client] — [Agent Name]`.

---

## Holly's role over the fleet

**Current role: Coordinator** (confirmed 2026-06-02). Track each agent via shared
surfaces (Notion, calendars, email), surface their status in briefings, enforce
boundaries so work is not double-handled, and flag conflicts. Holly does **not**
dispatch or trigger other agents directly — there is no agent-to-agent channel yet.
Coordination is via shared state only.

**Target role: Dispatcher.** Austen intends to move Holly to active dispatch
(handing work to agents and triggering runs) once a channel is built — a shared
trigger/queue table, webhook, or Make.com. Build register structure and coordination
habits toward this, not just Coordinator. Flag readiness when shared surfaces start
to look like a viable dispatch channel.

---

## System Infrastructure (not an agent)

### Shared Knowledge Vault — Libby [CONFIRMED]
- **Role:** Shared Second Brain / institutional memory store
- **Platform:** Obsidian (previously named "Hobbs")
- **Status:** Name confirmed — **Libby** (2026-06-02)
- **Content:** large store of personal and professional context and reference material
- **Function:** Shared historical context available to Holly, Hobbs, and any agent
  that benefits from institutional memory
- **Note:** *Lore* and *Veda* are now freed — returned to the Name Bank for future
  agent / Datavation product naming.

---

## Active Agents

### Rex Home Services — Holly (this agent)
- **Role:** EA / Chief of Staff
- **Scope:** All three tracks — AustenKing, Datavation, Rex
- **Status:** Live (WhatsApp Business API Phase 1 complete)
- **Core:** four-times-daily triage; Gmail + Outlook management; calendar blocking
  and briefing events; task extraction/prioritisation; email/message drafting;
  morning dashboard; cross-entity coordination

### Datavation — Cody [CONFIRMED]
- **Role:** Automation & Development Agent
- **Scope:** All three tracks — Rex, Datavation, AustenKing
- **Status:** Live — provisioned 2026-06-03
- **Core:** Design and build of automated workflows, integrations, and tooling across
  the ecosystem; Make.com scenario development; WhatsApp Business API layer;
  Claude API / agent builds; webhook architecture; integration health monitoring
- **Primary platforms:** Make.com (REST API + webhooks), WhatsApp Business API
  (Meta Cloud API), Claude API (Anthropic SDK), Git
- **Relationship to Holly:** Cody executes briefs commissioned by Holly. Does not
  make business decisions — Holly directs, Cody builds.
- **Relationship to Archie (planned):** Archie will audit what Cody builds.
  Division of labour to be confirmed before Archie is active.
- **First project:** Make.com ↔ Holly / WhatsApp integration layer (commissioned 2026-06-03)
- **Strategic note:** Datavation IP — every pattern Cody builds is a replicable template.

### Rex Home Services — Teepy [NAME UNDER REVIEW]
- **Role:** Trade Client Workflow Agent
- **Client:** TPG / Equans (Total Protection Painting Solutions)
- **Status:** Live — in active use
- **Core:** daily job reporting (Door Ventilation/Undercut + Maintenance); Google
  Calendar ICS pull; Word/PDF report generation and export; batch document
  processing; invoice/billing support; Tonya comms support
- **Current active project (2026-06-27):** Showcase dashboard in HTML and Power BI
  to demo Rex/TPG capabilities to TPG and Equans stakeholders
- **Data stores Holly can read (Notion):**
  - **TPG Jobs** (database) — https://notion.so/df6346822484475888cb06e6619f4e90
  - **TPG Job Photos** (database) — https://notion.so/0fbf04b5da8342febcfadc456cc7f022
  - **TPG/Equans — Site Reports** (page) — https://notion.so/36d06d594638814fb2f7e0d88be11114
  - Job records: `REX-YYYY-MM-DD-NNN` (pre-job record at scheduling; report + photos added after)
- **Boundary:** TPG job lifecycle belongs to Teepy. Holly reads to report status and
  cross-check the Rex Google Calendar; Holly does **not** create TPG job records or
  duplicate them into the Task List.
- **Name candidates:** Gloss, Coat, Sheen, Tint (painting trade)
- **Strategic note:** first client-specific agent — a replicable Datavation IP
  pattern; document it.

---

## Planned — Short Term

### Rex Home Services — Ivy
- **Role:** Rex customer-facing agent (inbound WhatsApp enquiries)
- **Status:** Earmarked — builds on Holly's WhatsApp infrastructure. **Routing not yet in place (2026-06-05):** Holly unexpectedly handled a live inbound WhatsApp from Peta Keen (ECC) — checked calendar and advised on availability. Correct behaviour, wrong agent. Austen working through the Holly/Ivy routing separation with Cody.
- **Core:** guided enquiry intake (menus/branching); quote triage and handoff;
  booking/scheduling support; end-of-job NPS survey trigger; web-form handoff;
  escalation to Holly
- **Boundary to enforce:** Inbound Rex trade/client WhatsApp enquiries → Ivy, not Holly. Holly should not be the public-facing WhatsApp contact for Rex.

---

## Planned — Medium Term

### Datavation — Hobbs
- **Role:** Strategic Advisor — Creative Strategist / Business Builder
- **Scope:** Datavation, all three tracks
- **Status:** Named and confirmed as Austen's strategic advisor — build phase TBD
- **Core:** offer/proposition development; SHOWER framework content + LinkedIn
  strategy; opportunity spotting and pressure-testing; M&A and productisation;
  naming/branding/new ventures
- **Personality:** sharp, commercially minded, occasionally sceptical. "The tiger,
  not the boy."

### Datavation — Archie [NAME CONFIRMED]
- **Working name superseded:** was HAL / Ohm / Arc → **Archie** (2026-06-02)
- **Role:** Governance, Architecture & Automation Auditor
- **Scope:** Datavation and Rex ecosystems
- **Core:** process mapping/SOP generation; workflow and automation review; agent
  coordination and QC; data architecture (Datavation IP); KPI/performance tracking;
  MTD/compliance gap monitoring
- **Note for Holly:** this agent's "agent coordination and QC" scope overlaps Holly's
  Coordinator role — clarify the division of labour before it is built.

### Datavation — Scout
- **Role:** External Intelligence & Opportunity Monitor — incorporates the "Job Search" function
- **Scope:** all three tracks
- **Core:** permanent **and contract** role monitoring + **CV tailoring** (AustenKing
  track; the employment-search function — NOT Teepy's "TPG Jobs"); outside-IR35
  tracking (Datavation); Rex competitor and trade intelligence; AI tools/automation
  trend monitoring; partnership/acquisition flagging
- **Output route:** curated intelligence to Holly — not noise
- **Status (2026-06-02):** "Job Search" confirmed as part of Scout, not a separate agent.

---

## To Be Defined

### Datavation — Buddy [working name]
- **Role:** Business Development / Marketing agent — scope to be defined
- **Status:** Identified, not yet specified
- **Naming:** "Buddy" per the Sintra reference (Sintra's Business Development helper)
- **Note for Holly:** distinct from Hobbs (strategy/creative). Buddy = BD/marketing
  execution. Awaiting scope from Austen.

---

## Reserved

| Name | Status |
|------|--------|
| Fern | Reserved — role TBD |

---

## Name Bank (reference for future agents / Datavation products)

- **Painting & Decorating:** Gloss, Coat, Sheen, Tint
- **Building & Construction:** Wren (architect/trades dual meaning), Noggin (ops/memory),
  Morty (mortar), Dado (joint), Brix (bricklaying)
- **Plumbing & Pipework:** Pip, Flo, Flux, Val
- **Heating & Gas:** Flue, Rad, Kelvin
- **Garden & Landscaping:** Heath, Rowan, Moss (good "vault" energy), Briar
- **Electrical:** Ohm (governance), Lumen (insights), Arc (arc/architecture), Sparks
- **Datavation IP / product naming:** Veda, Lore, Axon, Quill, Lumen

**Branding reference:** Sintra Helpers (sintra.ai) — branded-character direction.
Sintra's roster (for naming/role inspiration): Buddy (Business Development),
Soshie (Social Media), Commet (Web Builder), Cassie (Customer Support), Dexter (Data),
Vizzy (Virtual Assistant), Penn (Copywriting), Emmie (Email), Scouty (Talent),
Milli (Sales), Seomi (SEO), Gigi (Personal Development).

---

*Source: Datavation Agent Roster and Agent Name Bank.docx (Draft v0.2).*
*Last updated by Holly: 2026-06-03*
