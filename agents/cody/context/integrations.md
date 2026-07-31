# context/integrations.md — Cody Reference

Active integrations, API endpoints, and webhook configurations.
**Credentials are NOT stored here** — they live in environment variables or a local secrets file.

---

## Make.com

- **API base URL:** `https://eu2.make.com/api/v2` (EU region — confirm with account)
- **Authentication:** API key via `Authorization: Token <key>` header
- **Key operations:** `GET /scenarios`, `POST /scenarios/{id}/run`, `GET /scenarios/{id}/executions`
- **Webhook trigger pattern:** POST to `https://hook.eu2.make.com/<webhook-id>` with JSON payload
- **Webhook receive pattern:** Make.com POSTs to an endpoint Cody/the target system exposes; validate with HMAC signature

**Active scenarios:**

| Scenario name | ID | Purpose | Status |
|---|---|---|---|
| Integration WhatsApp Business Cloud | 9326259 | Rex WhatsApp inbound — currently routes to Make.com memory (broken). May be deprecated once Holly webhook handler is live and verified. | Active / partial |

---

## WhatsApp Business API (Meta Cloud API)

- **API base URL:** `https://graph.facebook.com/v19.0`
- **Authentication:** Bearer token (system user access token) — env var `WA_ACCESS_TOKEN`
- **Phone Number ID:** `705501459320704` (Rex number `+44 7376 475910`) — env var `WA_PHONE_NUMBER_ID`
- **WABA ID:** `1240873780546815`
- **Meta App:** RexHomeServices-Holly (App ID `919859944406192`)
- **Webhook verify token:** env var `WA_VERIFY_TOKEN` (value chosen by us, set in Meta Developer Console)
- **Meta App Secret:** env var `META_APP_SECRET` (used to verify inbound webhook signatures — `X-Hub-Signature-256`)
- **Key operations:**
  - Send message: `POST /{phone-number-id}/messages`
  - Template management: `POST /{waba-id}/message_templates`
  - Webhook registration: `POST /{waba-id}/subscribed_apps`

**Webhook handler:** `C:\Users\Austen\OneDrive - Datavation Limited\Agent-Fleet\Agents\Holly\whatsapp\server.py`
**Webhook endpoint:** `/webhook` (GET = Meta verification, POST = inbound messages)

**Outstanding for production:**
- Permanent Meta access token (current is temporary dev token)
- Rex Meta Business verification
- Consolidation of duplicate Datavation portfolios in Meta Business Manager

**Active templates:**

| Template name | Status | Purpose |
|---|---|---|
| — | — | None registered yet |

---

## Claude API (Anthropic)

- **SDK:** `anthropic` (Python) or `@anthropic-ai/sdk` (Node)
- **Default model:** `claude-sonnet-4-6`
- **Base URL:** standard Anthropic API endpoint
- **Auth:** `ANTHROPIC_API_KEY` environment variable
- **Caching:** implement prompt caching on all system prompts and large static context blocks
- **Active key:** `holly-railway-whatsapp` — stored as `ANTHROPIC_API_KEY` in Railway env vars (Holly webhook service). Rotated 2026-06-06; previous key `make-holly-rex` deleted.

---

## RemoteTrigger (Claude Code)

Used to receive triggers from Make.com or external webhooks into Cody.

- **Pattern:** Make.com scenario → HTTP module → POST to RemoteTrigger endpoint
- **Status:** Not yet configured — set up when first dispatch channel is built

---

*Last updated: 2026-06-06*
