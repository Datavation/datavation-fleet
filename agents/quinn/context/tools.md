# Quinn — Tools & Integrations

| Tool | Access | Purpose |
|---|---|---|
| Local filesystem | read fleet-wide; write own tree + the declared finance workdir only | Read extracts/rules in the workdir (`context\client-config.md` names it); write the ledger, report, dashboard there; write reviews/drafts to `output\`. |
| Python | run | Drives `skills\consolidate\engine\` — the deterministic consolidation. Optional deps `openpyxl` (xlsx) and `pdfplumber` (PDF) degrade loudly if absent. |
| QuickBooks | **read-only, extract-first** | Primary business source for Rex Home Services. A human exports the transaction CSV into the workdir's extracts folder; the `quickbooks_csv` adapter ingests it. The live QB MCP connector, where granted and working, may be used for read-only convenience pulls (P&L, AR aging) — never as a hard dependency, never any `create/update/delete/send` tool (infra-denied). |
| Notion board MCP | read board; write own cards | The Output Record (§9 of CLAUDE.md). Grant to be confirmed on promotion — same server-name open item as every seat since the fleet permissions baseline. |
| HTML dashboard | write (workdir only) | `Finance-Dashboard.html` — Rex's read-only review surface, refreshed by routines, private on OneDrive, never published. |

**Deliberately withheld (control gates, infra-enforced in settings):** any payment,
transfer, or banking capability; any send capability (email, WhatsApp, publish); QuickBooks
write-back; writes to the Tabularium, `Builds\`, or any peer agent's tree. Capability is
granted in units when a real problem demands it (Principle 6) — and the money/send units
are never granted to this seat by design.
