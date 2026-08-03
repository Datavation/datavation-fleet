# Tessa — Tools & Integrations

| Tool | Account | Purpose |
|---|---|---|
| Local filesystem | — | Read a build under test (`Builds\<name>\`) and its commission/handoff; read Canon (Tabularium, read-only) to know what "done" means; read/write only her own `Agents\Tessa\` tree. |
| Python | — | Runs `skills\qa-verify\scripts\qa_verify.py` — the self-test runner + clean-environment check. No other runtime is assumed; a build that ships PowerShell tests is invoked as a subprocess the same way. |
| Notion board MCP | Datavation workspace | Read the Decision Board; write/advance only cards where `To = Tessa`. Not yet granted — add on promotion once the MCP server name is confirmed (see Cody's own `_mcp_note` pattern). |

Capability is granted in units when a real problem demands it (Principle 6, rails before freedom). Tessa holds no Bash beyond what running a build's own self-test requires (`python`, `pip install` for a build's declared test dependencies) — no `git push`, no network tools, no send/publish capability of any kind.
