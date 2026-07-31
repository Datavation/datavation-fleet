# context/fleet.md — Cody Reference

The agents Cody builds for. What each agent needs from Cody — interfaces, formats, dependencies.
Source of truth for the full fleet: Holly's `context/agents.md`.

---

## Holly — EA / Chief of Staff
- **What she needs from Cody:** Stable webhook endpoints, Make.com scenario IDs, WhatsApp API wrappers, any integration Cody has built that Holly dispatches work through
- **Critical constraint:** Holly's active integrations (Gmail MCP, Google Calendar, Outlook MCP, Notion MCP) are production systems — do not alter without a specific brief and confirmation
- **Dispatch pattern (target):** Holly → Make.com → POST to Cody RemoteTrigger → Cody executes and returns result

---

## Teepy — Trade Client Workflow Agent (Rex / TPG)
- **What they need from Cody:** TBD — job workflow automation not yet scoped for Cody's involvement
- **Data stores:** TPG Jobs DB, TPG Job Photos DB (Notion — read-only for Cody unless briefed otherwise)
- **Note:** Teepy's job lifecycle is its own domain — do not touch without Holly confirming scope

---

## Ivy — Rex Customer-Facing Agent (planned)
- **What they need from Cody:** WhatsApp Business API flows — Make.com scenarios for inbound enquiry handling, guided menus, quote triage, booking triggers, NPS survey sends
- **Status:** Planned — Cody will build the automation layer when Ivy is scoped

---

## Hobbs — Strategic Advisor (planned)
- **What they need from Cody:** TBD

---

## Archie — Governance & Architecture Auditor (planned)
- **Relationship to Cody:** Archie will audit what Cody builds — process maps, workflow reviews, architecture checks. Division of labour to be confirmed before Archie is built.
- **What they need from Cody:** TBD

---

## Scout — External Intelligence Monitor (planned)
- **What they need from Cody:** TBD

---

*Last updated: 2026-06-03*
*Source: Holly context/agents.md (2026-06-02)*
