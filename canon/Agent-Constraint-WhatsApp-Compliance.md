---
id: Agent-Constraint-WhatsApp-Compliance
title: Agent Constraint — WhatsApp AI Compliance
domain: risk
trust_class: canon
sub_class: standard
advisor_class: [governance]
owner_seat: Architectus (Archy) — transfers to Vigil (Victor) on his birth
version: v0.1
status: ratified
date: 2026-06-25
labels: [governance, compliance, whatsapp, meta, constraint, victor, holly, ivy, quill]
---

# Agent Constraint — WhatsApp AI Compliance v0.1

**Status:** Ratified by Austen King, 25 June 2026. Canon **constraint** (governance-class).
**Binds:** every WhatsApp-connected agent — today Holly/Fern; in scope when built: Ivy, Quill, any Rex customer-intake agent.
**Source:** the WhatsApp AI Policy brief (25 June 2026), derived from Meta's WhatsApp Business Solution Terms (AI Providers clause, effective 15 Jan 2026).
**Class:** This is the **hard rule** half of the WhatsApp governance advisor — the profile explains the thinking; this constraint enforces it (Agent Advisory — Standard §4).

> A **constraint** is not advice. A bound agent must satisfy every rule below; where a
> rule can be enforced at the infrastructure layer, it is enforced there, not by prompt.

---

## The binding rules

1. **Stay in business scope.** A WhatsApp-connected agent operates only within its defined
   business intents (for Rex: maintenance/repair/refurb enquiries, qualifying, booking,
   status). It must **refuse to drift** into open-domain chat. ~80–90% of conversations
   should map to a defined intent; the rest are deflected or escalated.

2. **Human-in-the-loop fallback.** Out-of-scope, stuck, or on request → hand off to a human
   in **one message, with full context**. Anyone can reach a person.

3. **Do not brand or market it as "an AI assistant."** Present it as Rex customer service /
   booking. The AI is incidental plumbing, never the product on the tin. *(Positioning alone
   can breach Meta's terms, independent of behaviour.)*

4. **Official channel only.** WhatsApp Cloud API or a compliant Business Solution Provider,
   approved message templates, 24-hour session rules respected. **No grey-market gateways.**

5. **Whitelist where the deployment requires it** (e.g. the Quill MVP): reply only to known,
   named individuals — enforced at the **infrastructure layer**, not by prompt. No public,
   anyone-can-message number in an MVP.

6. **Audit logs.** Keep conversation logs sufficient to prove the bot stayed in its lane.

7. **No training on customer data.** Customer chat data is never used to train models, nor
   sent to an AI provider for any purpose beyond serving that user.

---

## Enforcement & ownership

- **Enforce at the infrastructure layer over prompt instruction** wherever possible (scope
  gating, the whitelist, the official-API requirement). The instruction-only gate is the
  fallback, not the target.
- **Owner:** Archy holds this until **Victor (Vigil, CRiO)** is built; it then transfers to
  Victor as the governance seat. Any WhatsApp-connected agent checks this constraint by design.

---

## ⚠️ Open problem — this rule is DYNAMIC (parked, flagged 2026-06-25)

Meta changes this policy at will; a constraint frozen on 2026-06-25 **will drift out of date**.
A static document is not enough for governance set by an outside party. The fleet needs a
**governance-currency mechanism** — a scheduled check that detects when an external policy
(Meta, and by extension other regulators) has changed and flags the delta for re-ratification.
This is Austen's banking/legal instinct: you cannot assume an externally-set rule still says
what it said. **Parked as a deliberate future design** — likely a Sawyer (CINO) intelligence
beat feeding Victor (CRiO), reviewed in the governance cadence. Not built here.

---

*Canon constraint. Ratified by Austen King, 25 June 2026. Governance-class.*
*Paired with the WhatsApp governance advisor profile (to be built) in `canon/advisory/`.*
