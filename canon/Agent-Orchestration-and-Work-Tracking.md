---
id: Agent-Orchestration-and-Work-Tracking
title: Agent Architecture — Orchestration & Work-Tracking
domain: architecture
trust_class: canon
sub_class: standard
advisor_class: []
owner_seat: Architectus (Archy) — CTO
version: v0.3
status: ratified
date: 2026-07-02
labels: [architecture, orchestration, pmo, decision-board, routines, remote-control, voice, dashboard, autonomy, safety, holly, cody, telegram, epic-timeline, evaluation-harness, model-tiering, raci]
---

# Agent Architecture — Orchestration & Work-Tracking (v0.3)

**Status:** RATIFIED by Austen King, 2026-06-27 (v0.2); **v0.3 additions ratified 2026-07-02.**
The fourth Agent Architecture standard. Filed version-less in Canon per the Filing Standard.
(Provenance: drafted + revised as
`Agents/Archy/output/proposals/Agent-Orchestration-and-Work-Tracking-Standard-PROPOSAL.md`;
v0.3 merges the ratified "How" proposal reviewed in
`Agents/Archy/output/2026-07-02-Strategic-Architecture-Review-and-Merge-Plan.md`.)

**v0.3 changelog (ratify-and-merge of the "Strategic Architecture & Epic Timeline" proposal, 2026-07-02):**
Merges the external "How" document (an independent sense-check, ~85% confirming existing Canon)
into this standard rather than filing a competing doc. Net additions, all in the new **§11**:
(1) the **five-epic spine** over the existing task plan; (2) **model-tiering by cost-of-being-wrong**;
(3) the **three-store model** (state / meaning / rules); (4) the **evaluation harness** as the one
net-new build; (5) **RACI-per-document** convention; and (6) the **Telegram reversal** — the deferred
custom cockpit of v0.2 §1/§8 is **reactivated as an active Round-2 build** (Claude Dispatch trialled
and rejected for voice-conducting, Rex 2026-07-01). This is the sanctioned "swappable-adapter" revisit
the v0.2 standard explicitly anticipated; the board stays the engine (Principle 4) and §6 control gates
are **unchanged**. The companion "Why" layer is filed separately as Hobbs-owned Canon
(`Canon/Strategy/Strategy-Influences-and-Authorities.md`). **Orchestrator = Holly** (Coordinator→Dispatcher),
corrected throughout from the proposal's "Holly or Hobbs" ambiguity; Hobbs is Consulted, not an ops seat.

**v0.2 changelog (the best-practice cross-check Rex commissioned):** The cockpit is
**re-based onto native Claude Code** (Claude mobile app + Remote Control/Dispatch + push +
Wispr Flow voice) instead of a custom Telegram build — voice lives in the app, not in a
chat bot. Unattended work moves to **Routines** (cloud, PC-off). Board-writes-on-completion
become **hook-enforced**, not instruction-only. A new **Autonomy & Safety model** (§6) turns
rails-before-freedom into concrete, infrastructure-enforced config. The first-cut autonomy
ceiling is **"execute reversible work"**. An **HTML command-centre** (§7) is added to this
round. The custom named-bot Telegram cockpit is **deferred**.

> **Reads with the set.** Roles = *who exists and is accountable*; Capability = *what they
> can do and what they operate*; Memory = *how they learn and how truth stays single*.
> **This document = *how work moves between them, how it runs while Rex is away, and how Rex
> sees and steers it without becoming the switchboard*.** (Set pointer in the other three
> Architecture docs to be updated from "three" to "four" in the next coordinated pass.)

---

## 0. The problem, in Rex's words

> *"I need to be captain of this fleet, not a doer."* · *"I can't keep running back to my PC
> to check whether something's been done."* · *"I need to be able to conduct — and do it from
> my phone."* · *"Sometimes I just need to dictate a bunch of thoughts and have them
> considered and assessed before coming back to me."* · *"Let the team get on with work in my
> absence and only output when complete."*

The operating model Rex is describing is **management by exception**: a few conversations,
the team gets on with it, he checks results and works the exceptions — conducted by **voice,
from his phone**, across **several projects at once** (orchestration, Quill, the paid
small-business track, the decks). The destination: agents that **don't stall on him**, work
**while he sleeps or drives**, and don't make him fight the team for PC resources. Three
failures are designed out: **(1)** Rex as the message bus; **(2)** context loss across
absences; **(3)** agents blocking on permission instead of getting on.

---

## 1. The architecture: four layers

| Layer | Answers | Built on |
|---|---|---|
| **A — System of record** (board + dashboard) | *What is the work, what state, whose hands?* | **Notion** (evolved Decision Board) + an **HTML command-centre** on top |
| **B — Cockpit** (how Rex sees & steers) | *How do I conduct, by voice, from my phone — and see only what needs me?* | **Native Claude Code**: mobile app + Remote Control / Dispatch + push notifications + **Wispr Flow** voice; Agent View |
| **C — Orchestration** (how work runs & moves) | *What runs while I'm away and moves between agents without me relaying?* | **Routines** (cloud, unattended) + **hooks** (board-write on completion) + sub-agents |
| **D — Autonomy & Safety** (the rails) | *How much may agents do unattended, and how is that bounded?* | Permission modes, pre-execution caps, control-gate hooks, sandbox — **infrastructure-enforced** |

**The trap avoided:** building "one board with chat windows" as a bespoke app. Native Claude
Code now supplies the cockpit and the unattended engine; we build only the **board**, the
**dashboard**, and the **safety config** — and we *configure* the rest. Less sprawl, more
maintainable, faster to value (Round-1 §3.4; the Hills "don't reinvent" instinct).

### Azure DevOps mapping (Rex's reference)
Work-item **states** → board `Status` (state machine, not a static label — the defect Rex
named). Moving **assignee** → `To`. Conversation **on the item** → the Notion page body.
**Roll-up** under Epics/Features → the hierarchy (§3.1). The **daily stand-up** → a generated
digest (now a cloud **Routine**, §5). The board was already three-quarters of this.

---

## 2. Channel-by-audience (ruling — binds the fleet)

Channels separate by **audience**, never mixed. Consistent with the WhatsApp AI Compliance
constraint (Canon, 2026-06-25).

- **Internal cockpit = native Claude Code** (the Claude mobile app / Remote Control / push).
  This is how the fleet talks to Rex. *Not* a consumer chat app in Round 1.
- **WhatsApp = external / customer-facing** (Ivy, Fern) + Rex's own mobile capture to Holly
  (`LOG:`/`DO:`). Governed by the WhatsApp constraint; kept clear of internal traffic.
- **Custom named-bot chat (Telegram) = deferred.** It buys per-agent named identities in an
  async text feed; native push + Agent View cover the need for now. Revisit in a later round
  if the "Holly/Cody messaged me by name" feel is missed. **The surface is a swappable
  adapter** (Round-1 §2) — the board engine is never welded to it.

---

## 3. Layer A — the board as PMO (evolve the Decision Board in place)

**Evolve, do not replace.** Keep `Court of Rex — Decision Board`
(`095e6b08-9db1-476e-8699-ce537ba9619c`); additive schema only; migrate live items by the
gold-rail (no blind replace — MEM-018).

### 3.1 Hierarchy — Epic → Feature → Task (three levels)
One database, two new properties: **`Level`** (`Epic`/`Feature`/`Task`, default Task) and
**`Parent`** (self-relation). Definitions tie to Canon: an **Epic** = a programme; a
**Feature** = a shippable chunk; a **Task** = one unit of work owned by one seat that runs to
one gate, **sized by its autonomy seams** (Capability §4). The Epic/Feature is the "subject";
each Task is a card with its own thread — Rex's "multiple chats on one board."

### 3.2 State model — unified lifecycle + build sub-states
Additive superset (existing build lanes kept, generic states added):
```
Backlog → Ready → In progress → (Blocked) → In review → Done
Build items continue: In review → Approved → Deploying → Verifying → Deployed (= Done)
Rejection: Rejected - revisit | Rejected - hold
```
Stand-up buckets: **Done** = Done/Deployed · **Doing** = Ready/In progress/In review/Approved/
Deploying/Verifying · **Blocked** = Blocked/Rejected-* · (Backlog excluded).

### 3.3 The per-item thread + completion writes
Each row's **page body is its thread** (`**[date time] <Agent>:** <update>`). Crucially,
**completion writes are hook-enforced** (§5): when an agent finishes, a `Stop`/`SubagentStop`
hook posts the result to the item and advances `Status` — so "agents keep the board true"
is infrastructure, not a polite instruction. The CLAUDE.md insert (Appendix A) is the
behavioural backstop, not the primary mechanism.

### 3.4 Fields + views
Keep: `Item`, `From Agent`, `To`, `Type`, `Priority`, `Status`, `Link`, `Rex Response`,
`What's needed`, `Created`. Add: `Level`, `Parent`, surface `Updated` (last-edited). Add an
`Epic`/programme tag for dashboard grouping. Views: **Kanban** (Tasks by Status), **Stand-up**
(by bucket, sorted Updated), **By Project** (by Parent), **Needs Rex** (To=Rex AND
Approval/Decision OR Blocked), **By Owner**. Reads for automations use the Notion **REST API**
(plan-independent; the MCP *query* tool is gated to Business+ — confirmed this session).

### 3.5 Who may write what (scope-of-target — Capability §5)
Operational (self-written): create items; advance `Status` of items where `To = self`; append
to threads of items it's involved in; hand off via `To`. **Not** without owner/Rex: close
another seat's item; **promote a build into a live agent's folder** (human — MEM-017); edit
another agent's identity/context/memory. State-change scope is an instruction-level gate
(acceptable for a non-destructive surface); the gates that **matter** are infra-enforced (§6).

---

## 4. Layer B — the cockpit (native-first)

**Decision: lean on native Claude Code; build nothing custom in Round 1.**

### 4.1 Voice conducting (the core want)
- **Claude mobile app + Remote Control / Dispatch.** Remote Control steers a *running*
  session from the phone; **Dispatch** fires a *new* task that spawns on the desktop —
  "text/voice your computer, come back to finished work." Outbound-HTTPS only, **no inbound
  ports**; optional Trusted-Devices + biometric step-up.
- **Voice = the Claude app's dictation + Wispr Flow** (Rex already uses Wispr Flow — MEM-007).
  There is no magic native voice bot; the proven path is a system-wide voice keyboard dictating
  *intent*, with the agent doing the work. Listen back via the app / device read-aloud.

### 4.2 Exceptions surface to Rex (management by exception)
- **Push notifications** when an agent finishes or needs a decision (native; free).
- **The "Needs Rex" board view** (`To = Rex` + Approval/Decision/Blocked) = the durable
  escalation queue.
- **Agent View** = one screen of every running agent: working / done / *waiting on you*.

### 4.3 Execution tiers (Rex's ruling)
- **Interactive (Holly, and Archy):** reply and act through the day; steered live via the app.
  Holly keeps her always-on hosted WhatsApp brain for personal capture.
- **Autonomous-batch (Cody, Hobbs, Marshall, future seats):** get on with work in Rex's
  absence and **output only when complete** — run as **Routines** (§5), not by queuing for a
  manual PC session.

### 4.4 Security cautions (from the review — design out)
Remote approval-fatigue (approving from a low-trust phone without reading) and the documented
risk that **repo config can override approval prompts** mean **control gates must be
infrastructure-enforced, never promptable** (§6). This is the Marshall `gmail.compose` gold
standard generalised.

---

## 5. Layer C — orchestration (Routines + hooks + sub-agents)

**Routines are the engine for "work while I'm away."** Cloud-run, **PC off**, autonomous (no
prompts), can use MCP connectors + skills + sub-agents, triggered by **schedule, API, or
GitHub event**. *Research preview* — pilot deliberately, don't bet everything on it.

- **First Routine = the fleet stand-up** (06:00 + 18:00), read-only, fleet-only, posts to
  Rex. Read-only makes it the safe proof that unattended cloud execution works end-to-end
  before we trust Routines with real work.
- **Real work** then runs as scoped Routines per agent (and **GitHub Actions + `claude -p` on
  cron** for the heavier/code paths) — each narrow, capped, single-job (§6).
- **Completion → board** via `Stop`/`SubagentStop` hooks (§3.3): deterministic, harness-run,
  low context cost.
- **Sub-agents** (orchestrator-worker, Capability §4a) are the path to "agents spin up
  sub-agents": a lead delegates to scoped workers that return summaries — Opus on judging,
  Sonnet on executing (Hills/Anthropic). **Not** for shared-context coding work (Anthropic's
  own caveat), and **never** peer-to-peer in chat — coordination is always through the board.
- **Considered-by-default:** Routines inherently batch — Rex dictates, the agent assesses,
  then returns. Even interactive Holly/Archy assess before replying. *Instant is the
  exception, not the norm* (Rex's steer).

**Toward Dispatcher (deferred):** Holly Coordinator→Dispatcher and any Make.com bus come
*after* the board is trusted and Routines are proven. Not built here.

**Routine authoring contract:** *how* a routine is written — trigger, single source of truth,
ownership/scope, fail-loud preconditions, and a fixed output contract — is specified in the
**Agent Routine Standard** (`Agent-Routine-Standard-v0_1.md`), the ratified Routines-layer spec
(Archy-owned). Every routine in this layer conforms to it; its R2 (single source of truth = the
Decision Board Command view) and R3 (one surface, one owner) are the guards that keep routines from
spawning divergent "waiting on Rex" lists.

---

## 6. Layer D — Autonomy & Safety (the rails, made concrete)

This is Principle 6 (rails before freedom) and Principle 7 (authority stays with Rex) turned
into enforceable config. The evidence is unambiguous: unattended agents have burned
**~4M tokens in under 5 minutes** via recursive sub-agent spawning, and multi-agent loops
have run for days on alerts-without-enforcement. **Alerts are not enforcement. Caps must be
hard, pre-execution, and outside the agent's own control.**

### 6.1 The graduated ladder — first-cut ceiling = "execute reversible work"
Per Rex's ruling, in the first cut an autonomous agent may, unattended:
- **research, draft, prepare, update the board, and do reversible/low-risk work** (e.g. write
  a doc, prep a build **in staging**).
It may **not**, unattended — these are **permanent control gates, infra-enforced**:
- **spend money, send anything external, promote a build into a live agent's folder, or edit
  another agent's identity/context/memory.**
Autonomy graduates **per agent, per skill**, only as monitored metrics hold (Capability §5) —
never as a blanket. Every agent has a **named human steward** (its senior seat; Rex final).

### 6.2 Enforcement (infrastructure, not instruction)
- **Permission model** (`settings.json`): `deny > ask > allow`, first match, **enforced by the
  harness not the model**. Control-gate classes go in `deny`; reversible tools in `allow`.
- **Recursive spawning denied at the settings/managed layer** (`Agent(...)` deny) — in-definition
  tool lists are known to fail; back the 5-deep cap with an **external iteration/cost cap**.
- **Pre-execution spend caps:** per-session token budget + per-agent ceiling, plus
  Anthropic **workspace-level spend + rate limits** as the backstop (Rex's hands — account level).
- **No `bypassPermissions` / `--dangerously-skip-permissions` outside an isolated cloud/container
  run** (Routines run autonomously by design — scope their connectors + permissions tightly).
- **Sandbox** (OS-level filesystem/network) for anything running Bash, so a script can't
  side-step file rules; **PreToolUse hooks (exit 2)** block money/send/delete/edit-another-agent
  *before* the permission prompt even evaluates.
- **HITL vs HOTL:** human-in-the-loop (blocking approval) for irreversible/high-cost actions;
  human-on-the-loop (monitor + sample) for reversible ones.

### 6.3 Why this is also the product
This is the typed-gate map (Capability §4) at fleet scale: the **capability gates** are the
roadmap (what graduates next), the **control gates** are the governance story (where a human
always stands). It is the responsible — and more sellable — correction to Hills's "hand it
over and walk away."

---

## 7. Command-centre (presentation)

- **Now:** Notion's own board views (work on phone + desktop) + **Agent View** (live sessions)
  + **ccusage** for spend.
- **This round (Rex ruled "build now"):** a **single-file HTML command-centre** on top of the
  board — reads the Notion data (REST → JSON), renders done/doing/blocked + Needs-Rex + per-Epic
  roll-up, mobile- and desktop-friendly, statically hostable. Matches the existing AIOS/Hobbs
  HTML-dashboard pattern (MEM-003/005). Potential to consolidate the existing dashboards onto it.

---

## 8. Build sequence & gates

| # | Build | Owner | Gate |
|---|---|---|---|
| **0** | **Ratified** | Rex | ✅ 2026-06-27 |
| **1** | **Board upgrade** (hierarchy, states, views, thread + completion-hook) | Cody | Archy review → Rex sign-off; gold-rail migration |
| **2** | **Autonomy & Safety guardrails** (permission model, caps, recursion-deny, sandbox, control-gate hooks; workspace caps = Rex) | Cody + Rex | Archy review of the gates → Rex sets account caps |
| **3** | **Stand-up as a Routine** (06:00/18:00, read-only, fleet-only) | Holly (built by Cody) | Archy review → Rex confirms; **first unattended pilot** |
| **4** | **HTML command-centre** | Cody | Archy review → Rex confirms |
| **5** | **Graduate autonomy** — reversible-work Routines per agent | Archy proposes → Rex ratifies | per-agent, on held metrics (§6.1) |
| — | Native cockpit setup (app, Remote Control, Wispr Flow, push) | **Rex** (his hands) | parallel; see Build Plan checklist |
| — | Per-seat CLAUDE.md board-discipline insert (Appendix A) | Archy → Rex | Rex ratifies; human promotion |
| — | *Custom Telegram named-bots · Dispatcher/Make bus* | — | **Deferred** — later rounds |

Each build: Phase-0 hard stop (Cody flags trade-offs + cost before code); Cody works inside
his scope gate; promotion into a live folder is Rex's hands.

---

## 9. Alignment — locked principles
- **P4:** cockpit is a swappable surface; board is the engine; agents express intent.
- **P5:** Holly's hosted pattern + Routines (cloud run copies) keep the split-brain clean.
- **P6:** autonomy granted in units, graduated on metrics, **enforced at the infra layer** (§6).
- **P7:** Rex is the exception handler; every control gate keeps authority with him.
- **P8:** board schema, channel rule, safety model and dashboard are **Datavation IP** — a
  client deployment fills them with its own channel and work.
- **Typed gates (Capability §4):** Task sizing by autonomy seams; capability gates = roadmap,
  control gates = governance, infra-enforced.

## 10. Open items / Rex's hands
1. **Native cockpit setup** (your hands): install/sign-in the Claude mobile app, pair Remote
   Control, confirm Wispr Flow on the phone, enable push. (Build Plan has the checklist.)
2. **Workspace spend + rate caps** at the Anthropic account level (the backstop in §6.2).
3. Confirm the per-agent autonomy ceiling as each agent graduates (default: reversible-work).
4. Sits alongside the still-PROPOSED Memory v0.3 gold-rail and the open shared People-layer card.

---

## Appendix A — Per-seat CLAUDE.md insert (behavioural backstop to the §3.3 hook)

> **Board discipline.** The Decision Board (Notion) is the fleet's single system of record.
> Start work → set your item `In progress`. Finish → advance `Status` and post a completion
> line to the thread. Blocked / need Rex → set `Blocked` (or `Decision needed`/`Approval
> Request`), `To = Rex`, and say why; the cockpit surfaces it — do **not** chase Rex directly.
> Advance only items where `To = you`; never close another seat's item, promote to live, or
> edit another agent's files. Coordinate agent-to-agent through the board, never by messaging.
> Default to **considered, not instant** — assess before you reply.

---

*RATIFIED by Austen King, 2026-06-27, v0.2. The fourth Agent Architecture standard.
Owner: Archy (Architectus), CTO — Court of Rex.*

---

## 11. v0.3 additions — ratified 2026-07-02 (the "How" merge)

Merged from the external *Strategic Architecture & Epic Timeline* proposal after Archy review
(`Agents/Archy/output/2026-07-02-Strategic-Architecture-Review-and-Merge-Plan.md`). These are
additions to — not replacements of — the v0.2 standard above; §6 control gates are unchanged.

### 11.1 The three problems, separated
The goal is **three builds of different difficulty**, not one — conflating them is why progress felt slow:
- **Interface** (reach the fleet by phone/voice) — *easy, solved plumbing* — days to ~2 weeks.
- **Orchestration** (agents coordinate, exceptions bubble up) — *medium, mostly built* — 6–12 weeks.
- **Autonomy** (sign-off-ready deliverables behind a human gate) — *hard, brittle* — months, never "done".
The binding truth: **agents for throughput, humans for taste and sign-off.** Autonomy = draft-ready-for-approval, never auto-publish; a human gate on anything client-facing, financial, or brand-voice is the design, not a limitation.

### 11.2 Model tiering — by cost of being wrong, not job title
- **Top tier** (reasoning/judgment): Hobbs, Holly, Archy. **Workhorse tier** (doing): most execution seats incl. Marshall's core. **Cody:** workhorse default, **escalates to top tier for hard architecture**. **Mechanical tier:** pure classification/routing/collation on the cheapest tier, escalating when judgment is actually required.
- Multi-model by default (now market-standard). Tier deliberately — token cost is the real variable; multi-agent runs burn heavily. Escalation paths, not fixed assignments.

### 11.3 The three stores — do not collapse them
- **Structured state → Notion** (rows/fields by exact match: status, owner, priority) — the control plane.
- **Semantic knowledge → a vector store** (text by *meaning*) — the Tabularium retrieval layer; how an agent "consults an advisor" without hand-tagging.
- **Relationships & rules → an ontology** (how things relate; rules like "architecture-touching changes log PROPOSED").
Three stores, three jobs. (Conceptual grounding: Tony Smith, in the companion "Why" doc.)

### 11.4 The evaluation harness — the one net-new build
The single *actionable* finding from the authorities (evaluation is the second-largest lever moving pilots→production):
- **Per deliverable type** (scorecard, proposal, post, client report): a real-case **eval set** (~20 items) + an **LLM-as-judge rubric** (accuracy, completeness, source quality, brand-voice fit).
- **The judge never publishes** — LLM self-eval is correlated error ("evaluator laundering"); the judge *screens*, the **human gate approves**. This is why sign-off is a permanent architectural feature.
- Wired to **autonomy graduation** (§6.1): nothing graduates to unattended drafting until it clears ~80% "usable with light edits" on its eval set. Commissioned as a build (board card, To Cody).

### 11.5 The epic spine (a view over the existing task plan, not a rewrite)
Five sequenced epics; **Accountable = Archy** for build epics, **Hobbs** for the productisation epic; **Consulted = Hobbs** where strategy meets build. Orchestrator = **Holly**.
1. **Reachability** *(Interface)* — VPS + Telegram + voice + allowlist + token cap. *Done: a phone voice-note yields a real action+reply, PC closed.* Days. Pillar: Agent Fleet.
2. **Control plane & exception surface** — Notion Agent Registry / Task Queue / Decisions / Run Log, single-writer; exceptions push to phone, reply writes back. *Done: an agent blocker reaches the phone and a one-word reply unblocks it.* Weeks 1–3.
3. **Orchestration & the sign-off gate** — native orchestration + the eval harness; final gate = human approval in Notion. *Done: each deliverable type hits ~80% on its eval set before drafting unsupervised.* Weeks 3–8.
4. **Scheduled autonomy, managed by exception** — proven workflows to scheduled runs; client-facing stays draft-only; add observability. *Done: a full week managed by exception, no unsupervised client-facing publish.* Weeks 8–12+.
5. **Productise the deployment** *(A: Hobbs, C: Archy)* — repeatable client deployment (AHS/ECC; personal-agent track). *Done: one external deployment on the same architecture, client brand on the door.* After Rex proof; months.

### 11.6 The interface (Telegram) — reversal recorded
Highest-pain, lowest-effort win, goes first. **Telegram bot → Claude Code on a small always-on VPS**; voice notes transcribed; questions/decisions return to the phone. **Claude Dispatch was trialled and rejected for this use case (Rex, 2026-07-01)** — Telegram is the path. It is a **swappable Layer-B adapter** (Principle 4): the board stays the single system of record. The hard parts are (a) the always-on host, (b) security/tool-gating (the §6 gates stay infra-enforced — no spend/send/promote/edit-another-agent unattended; a phone→desktop chain makes them *more* important), (c) exception-routing quality. Commissioned to Cody; **host + bot token + secrets = Rex's hands** (control gate).

### 11.7 RACI-per-document
Every Canon document carries a RACI header — **R**esponsible (does the work), **A**ccountable (single owner; only ever one), **C**onsulted (input before), **I**nformed (read/after). Applied *per document/decision*; sits **on top of** the roles architecture, never redefines a seat. A fleet-wide RACI *matrix* waits for a curator seat (Libby) to own it — **document-level only** until then. (Filing Standard carries the light convention note.)

*v0.3 additions ratified by Austen King, 2026-07-02. Owner: Archy (Architectus), CTO.*
