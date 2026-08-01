# context/tools.md — Holly Reference

## Active Integrations

---

### Gmail (MCP)
- **Account:** rexhomeservices.co.uk (info@)
- **Purpose:** Rex inbox — read, triage, draft replies
- **MCP server:** gmailmcp.googleapis.com
- **Notes:** Primary email for all Rex client communication. holly@rexhomeservices.co.uk is an alias on this account — check the **To:** field to identify emails directed at Holly. These go into the Notes Inbox (Notion), not directly into tasks.

---

### Google Calendar (MCP)
- **Account:** rexhomeservices.co.uk
- **Purpose:** Rex job scheduling — read and write
- **MCP server:** calendarmcp.googleapis.com
- **Notes:** Jobs are booked here. TPG jobs added in advance by Tonya. ICS URL available for external pulling. Future: replace ICS with Google Service Account for private read/write access.

---

### Outlook / ms365 (MCP)
- **Account:** datavation.co.uk
- **Purpose:** Datavation inbox and calendar — read, triage, draft replies
- **MCP server:** microsoft365.mcp.claude.com
- **Notes:** Also covers Teams if needed. Kings.co.uk (separate tenant) is pending delegation — not yet readable by Holly.

---

### Notion (MCP)
- **Account:** Austen's personal Notion account
- **Purpose:** Master task database and notes inbox — owned and managed by Holly
- **MCP server:** mcp.notion.com
- **Notes:** Holly creates, updates, and closes all tasks. Schema defined below.
- **Operations Hub page:** https://notion.so/36906d59463881dcae2ff3e8ef256bcd
- **Task List database:** https://notion.so/53f84e65b93744818c0cd97ad3207ec3
- **Task List data source ID:** collection://56859bce-e306-4765-a17d-d6fe5f49857c
- **Notes Inbox database:** https://notion.so/4c65fdb5ae464a8f821dfc13f89248f9
- **Notes Inbox data source ID:** collection://0f099081-44e1-4524-bd91-e003976201e4

---

## Notion Task Database Schema

**Database name:** Holly — Task List

| Field | Type | Values / Notes |
|---|---|---|
| Title | Text | Clear action-oriented title |
| Business | Select | Rex / Datavation / Personal |
| Status | Select | Inbox → Active → Waiting → Done → Dropped |
| Priority | Select | Critical / High / Normal / Low |
| Due Date | Date | — |
| Notes | Text | Context, blockers, links |
| Created | Date | Auto |
| Updated | Date | Holly updates on change |

**Status flow:**
- `Inbox` — captured, not yet triaged
- `Active` — in progress
- `Waiting` — blocked on someone else or a future date
- `Done` — completed
- `Dropped` — will not do (always add a note explaining why)

---

## Pending / Not Yet Active

| Tool | Status | Notes |
|---|---|---|
| kings.co.uk (Outlook) | Blocked | Separate tenant — needs delegate calendar access set up |
| WhatsApp Business | Planned | Future: client job confirmations for Rex via Make.com |
| CRM | Planned | Future integration — not yet decided on platform |

---

*Last updated by Holly: [date]*
