# context/rex.md — Rex Home Services Operational Reference

## Overview

Rex Home Services is Austen King's sole trader field services business, launched August 2025. It is currently the primary income source during the career transition period. Austen is the sole field operative — all jobs are done by him personally.

Rex serves three purposes simultaneously:
1. **Income** — survival cash flow (~£1,000/week at full capacity)
2. **Automation testbed** — live environment for workflow, AI, and digital tools
3. **Datavation proof of concept** — demonstrates SMB digital transformation to future consulting clients

---

## Rate & Income

| Metric | Detail |
|---|---|
| Day rate | £180–£200/day |
| Weekly target | £1,000 (5 working days) |
| Comparison | Datavation/contract work = £600–£1,000/day |

---

## Services

- Property maintenance and repair
- Garden maintenance
- Home improvement and refurbishment
- Property clearances (via ECC partnership)

---

## Clients

### TPG (TP Group / Total Protection Group) + Equans
- **Type:** Council/property maintenance — painting, decorating, door undercuts, maintenance. Work flows **Equans (principal) → TPG (subcontractor) → Rex**.
- **TPG — commercial/contract layer:**
  - **Jack Darby** (JackD@thetpgroup.co.uk) — day-to-day TPG contact; replaced Sam Bollen.
  - **Will Smith** (wills@thetpgroup.co.uk) — TPG; little direct dealing.
  - **Dan (TPG)** — *not* Dan Keen (ECC); Jack needs to speak to him about future work/margins. Likely to need engaging later.
  - **Emma (+ Summer)** — TPG contracts/admin; sent the 17-page subcontractor contract.
  - **Sam Bollen** — ex-Commercial Director; completed Datavation Digital Business Balance Scorecard (May 2025).
- **Equans — job-detail layer (@equans.com):**
  - **Tonia Weller** (Tonia.Weller@equans.com) — RLO, Suffolk team; sends jobs in advance; key day-to-day liaison. *(Voice-to-text misspells as Tonya/Toni/Tony — not to be confused with Tony Kelly.)*
  - **Gary Wenlock** (gary.wenlock@equans.com) — Site Manager, Suffolk team; job detail on site.
  - **Bradley Anderson** (Bradley.Anderson@equans.com) — Suffolk team; phases, vacant-property + garden maintenance.
  - **Tony Kelly** (tony.kelly@equans.com) — Equans Greenwich; books Austen in for Greenwich work.
- **Notes:** Primary and most reliable client. Jobs pre-booked into Google Calendar by Tonia. PowerShell-based daily reporting workflow exists specifically for TPG (scripts managed via Claude Code). Datavation Discovery Report also delivered to TPG — first SMB proof of concept.

### AHS (Accredited Home Services)
- **Contact:** Iain Jack
- **Notes:** Established Rex client. Iain Jack is also identified as a potential Datavation BYO-AI SMB target.

### ECC (Eastern County Clearances)
- **Contact:** Dan Keen
- **Notes:** Property clearance work. Dan Keen has since established a separate company, Eastern County Contracts. ECC coordination now handled directly by Dan.

---

## Operations

- Jobs booked via **Google Calendar** (rexhomeservices.co.uk account)
- TPG jobs added in advance by Tonya — calendar is primary scheduling tool
- **Invoicing:** Monzo Business
- **Reporting:** PowerShell daily reporting workflow for TPG (Claude Code managed)
- Rex email: info@rexhomeservices.co.uk (Gmail) — primary client communication channel
- Holly's dedicated inbox: holly@rexhomeservices.co.uk (alias on same account)

---

## Automation & Technology

| System | Status | Notes |
|---|---|---|
| PowerShell TPG reporting | Active | Daily report scripts; Claude Code managed |
| Microsoft Fabric analytics | Planned | Rex as live proof of concept for DP-600 use case — not yet delivered |
| Field operations platform | In design | SQLite offline-first store, sync to Fabric when connected; inspired by MyOfficeDiary (MOD) data architecture from 2008–2014 |
| Automated invoicing | In progress | Priority workflow automation |
| WhatsApp Business | Planned | Client job confirmations via Make.com |

---

## Strategic Context

Rex was launched out of necessity, not long-term intent. The honest position:

> Rex generates income but consumes the time required to escape Rex.

The exit path is: secure a Datavation contract or senior leadership role → reduce or automate Rex → Rex either becomes a side experiment or an automated/franchise model.

Every decision about Rex should be evaluated against: *does this move Austen closer to a senior transformation role or a Datavation consulting contract?*

---

## Reference Documents (Google Drive)

- `03 - Business Context.txt` — full three-business system overview
- `MyOfficeDiary Context.txt` — MOD/Vector product history and lessons applied to Rex platform design

---

*Last updated by Holly: 2026-05-25*
