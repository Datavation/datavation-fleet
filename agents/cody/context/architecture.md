# context/architecture.md — Austen King Agent Fleet

Living architecture document. Updated as the design evolves.

---

## Principle

One infrastructure pattern, multiple business instances. Every agent, contact store,
and channel is built to the same template so adding a new business means deploying
a known pattern — not designing a new one.

Holly sits above all businesses. She can see across all contact stores and all agents.
Individual agents own their own data but Holly is the aggregator.

---

## Fleet Structure

```
Holly (EA / Chief of Staff)
│
├── Rex Home Services
│   ├── WhatsApp line: +44 7376 475910
│   ├── Agent: Ivy (customer-facing — in build)
│   ├── Contact store: Rex Contacts (Notion DB — in build)
│   └── Channels: WhatsApp (live), web enquiry (future), email (future)
│
├── [Future business — e.g. Ian Jack / AHS]
│   ├── WhatsApp line: [separate number]
│   ├── Agent: [separate agent]
│   ├── Contact store: [separate Notion DB]
│   └── Channels: WhatsApp, SMS, web (future)
│
└── Datavation Ltd
    └── [TBD — separate scoping required]
```

---

## Per-Business Pattern

Each business gets:
- **One WhatsApp number** — dedicated line, not shared
- **One customer-facing agent** — handles inbound, books jobs, manages enquiries
- **One contact store** — scoped to that business, owned by that agent
- **One deployment** — separate Railway service (or route within shared service)

Holly has read access to all contact stores. She never owns customer contacts directly
but can query and collate across all businesses.

---

## Contact Data Model

Standard across all businesses and channels. Every contact record contains:

| Field | Type | Notes |
|---|---|---|
| `id` | string | UUID — generated on first contact |
| `phone_number` | string | E.164 format without + (e.g. `447771621677`) |
| `name` | string / null | Populated when identified |
| `business` | string | `Rex`, `Datavation`, `AHS`, etc. |
| `channel` | string | `whatsapp`, `web`, `email`, `sms` |
| `status` | string | `unknown`, `prospect`, `client`, `customer` |
| `first_contact` | ISO8601 | Timestamp of first inbound message |
| `last_contact` | ISO8601 | Timestamp of most recent message |
| `notes` | string / null | Free text — agent-populated |

**Status definitions:**
- `unknown` — number logged, identity not yet confirmed
- `prospect` — first-time enquiry, no prior business relationship
- `client` — active commercial relationship (e.g. ECC, Equans)
- `customer` — residential/one-off customer

---

## Channel Abstraction

All inbound contact channels feed the same contact record. When a number that
previously messaged via WhatsApp submits a web enquiry, they're the same contact —
not a duplicate.

Channel is recorded per interaction, not per contact. A contact can have interactions
across multiple channels.

**Current state:** WhatsApp only.
**Planned:** Web enquiry form → webhook → same contact store. Email → same.

---

## Ivy — Customer-Facing Agent (Rex)

Ivy handles all inbound enquiries to the Rex WhatsApp line. Her behaviour is modelled
on the Holly/Peta exchange of 5 June 2026 — that exchange is the reference template.

**Booking autonomy rule:**
- Weekday (Mon–Fri) + diary clear for requested date → Ivy books autonomously
- Diary has conflict, date unclear, or outside normal parameters → Ivy flags to Austen
- Austen's side of the contract: keep the Rex calendar accurate

**Ivy's job booking flow (target):**
1. Receive enquiry — take date, address, scope
2. Check Rex calendar for availability
3. If clear and within autonomy parameters: confirm booking, create calendar entry, send client confirmation
4. If unclear: flag to Austen → "Peta Keen — clearance, Hayes Road Clacton, 17 June. Looks clear. Confirm?"
5. Austen replies "Confirm" → Ivy creates entry and sends confirmation

**Contact handling:**
- Every inbound number is logged to Rex Contacts on first message
- Ivy populates name and status as the conversation provides detail
- Holly can query Rex Contacts when briefing Austen on Rex work

---

## Holly — Aggregator Role

Holly is not a customer-facing agent for any business. Her role in the contact layer:
- Receives notifications of all inbound messages (currently active for Rex)
- Can query any business contact store when briefing Austen
- Can collate across businesses (e.g. "Anyone from ECC contacted either line this week?")
- Never responds to customer messages directly

Holly's WhatsApp channel (+44 7376 475910) is the Rex business line — she receives
notifications on it but Austen is the only sender she responds to.

---

## Infrastructure

| Layer | Current | Notes |
|---|---|---|
| Webhook host | Railway (EU West) | Holly webhook live. Ivy will share platform or get own service. |
| Contact store | JSONL on Railway volume (interim) | Migration to Notion DB when Ivy is built |
| Calendar | Google Calendar read via ICS | Write access in build (OAuth2 — see below) |
| Messaging | Meta Cloud API | One WABA, separate phone number IDs per business |

---

## Google Calendar Write (in build)

Current state: Holly can read the Rex Google Calendar via a public ICS URL (read-only).

Target: Holly can create, read, and query calendar events — specifically to:
- Book Rex jobs when Austen or Ivy confirms
- Add personal appointments and reminders
- Support Ivy's autonomous booking flow

Requires: Google Cloud project with Calendar API, OAuth2 credentials, refresh token
stored in Railway env vars.

**Scope for initial build:** Austen's personal Rex Google Calendar only.
Outlook calendar: separate build, not in current scope.

---

*Last updated: 2026-06-05*
*Maintained by Cody*
