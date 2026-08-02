---
title: Agent Delivery and Governance Model
version: v0.1
status: ratified
date: 2026-07-22
owner: Archy (Architectus, CTO)
governs: the two axes of fleet work — what gets built, and what governs what gets built
sits-under: Agent-Orchestration-and-Work-Tracking.md (amends §3.1 and §3.4)
ratified-by: Rex (Austen), 2026-07-22, in session
ratified-note: Rex ratified explicitly and delegated execution in his absence
  ("Please accept all of this as my ratification and fire it off to Cody"). Archy
  executed the promotion; the ruling is Rex's, the file move is mechanical.
labels: [architecture, hierarchy, governance, docket, delivery, pillars, epics]
---

# Agent Delivery and Governance Model — v0.1

**RATIFIED by Rex, 22 July 2026.** Proposed by Archy the same day.
Authored at Rex's direct commission after the Epic backfill of the same day exposed the
defect this document exists to fix.

**Revised the same day, pre-ratification,** after Rex stress-tested the draft against a third
forum — a Business Strategy Board chaired by Hobbs, ruling on *what and why* rather than *how*.
The structure survived unchanged; the test produced three additions, all **rules rather than
tiers**: §3.3 forum scope and precedence · §4.3 direction-becomes-artifact · §3.2 "convenable"
in place of "not parked". Amended in place rather than versioned, because nothing here has
been ratified yet.

---

## 0. Why this exists

On 22 July the Decision Board carried 284 cards in one hierarchy. Four of the nine Epics
were meetings. Their agenda items sat at `Level = Feature` and their decisions at
`Level = Task`, structurally indistinguishable from delivery work.

Two consequences, both measured, neither noticed until the hierarchy was rendered:

1. **The delivery view under-reported committed work.** Five rulings — tenant-data isolation,
   the ops-lane split, Marshall's memory file, ECC/AHS postcode capture, multi-client
   invoicing — existed *only* as decisions inside dockets. No delivery card. Multi-client
   invoicing had been ruled *build now* and was absent from the Epic Rex calls "the money Epic".
2. **The governance view over-reported work.** A ruling at `Level = Task` counts as a task.
   "34 open tasks" included things that were not work at all.

There was no duplication between the two trees — zero cards, zero titles, zero near matches.
**The absence of overlap was the defect.** Two sealed forests, no bridge.

The root cause is a category error: **delivery and governance were modelled as one thing.**

---

## 1. The two axes

A fleet work item belongs to exactly one of two classes. They are not tiers of each other.

| | **Delivery** | **Governance** |
|---|---|---|
| What it is | Work | An event and a record |
| State | Progressive (backlog → done) | A date and a ruling |
| Question it answers | What are we building? | Who decided, when, and on what basis? |
| Root | A Pillar | A Forum |
| Store | Decision Board | Governance database |

**This is not an exemption from the hierarchy rule. It is a second hierarchy.** An exemption is
a hole in a rule and invites judgement calls; two axes with two invariants do not.

### 1.1 The two invariants

> **D1 — Delivery invariant.** Nothing exists without a parent except a Pillar.
> Everything rolls up to a Pillar.

> **G1 — Governance invariant.** Nothing exists without a parent except a Forum.
> Everything rolls up to a Forum.

Both are absolute. A card that satisfies neither is lost, and lost is the failure mode both
rules exist to prevent.

---

## 2. The delivery tree

```
Pillar  →  Epic  →  Feature  →  (User Story)  →  Task
```

**Ratified by Rex 2026-07-22.** User Story is **optional** between Feature and Task —
skipping it is allowed and normal. **Skipping Feature is not.** A Task always hangs off a
Feature or a User Story.

Legal edges, exhaustively:

| Parent | Child |
|---|---|
| Pillar | Epic |
| Epic | Feature |
| Feature | User Story |
| Feature | Task |
| User Story | Task |

Any other edge is a defect and must be reported by any view that renders the tree.

**Subtasks are not a tier.** Discussions and messages attach to a card; they are not a
`Level`. Nothing exists below Task. (Rex, 2026-07-22: *"maybe they could be described as
discussions or messages, but we don't really need the hierarchy."*)

### 2.1 What an Epic is

An Epic is a product, a service, or a coherent programme of work. Under a commercial pillar
an Epic is normally **a product**: Fleet as a Product, the phone-AI seat, a client-facing
operations dashboard. Under an enabling pillar it is a capability: the Fleet Engine, the
Operating Layer.

### 2.2 Where a product built for one pillar becomes another pillar's product

The build stays where it was built. **Productising it is a separate Epic under the pillar that
sells it, consuming the same codebase.** Work does not churn between pillars each time
something becomes sellable.

*Worked example.* The Rex Operations Dashboard is delivery work under Rex Home Services. A
packaged, multi-tenant version sold to clients is an Epic under Datavation Services. Two
Epics, one codebase, no migration. Same shape as the Console, which serves Pillar 1 as the
daily surface and Pillar 3 as the demo asset.

---

## 3. The governance tree

```
Forum  →  Docket  →  Agenda item  →  Decision
```

| Tier | What it is | Lifetime |
|---|---|---|
| **Forum** | A standing body with terms of reference and a standing agenda — Technical Review Board, Data Governance Board, Commercial Review | Permanent |
| **Docket** | One dated sitting of one Forum | One meeting |
| **Agenda item** | One topic within that sitting | One meeting |
| **Decision** | One ruling, with a date, an owner and a disposition | Until its disposition closes |

### 3.1 The Forum tier is the template source

A Forum carries the terms of reference and the standing agenda. **A docket is instantiated
from its Forum, not hand-built.** This is what makes the calendar loop possible: the meeting
invite is generated from the Forum, the docket arrives with its agenda already populated, and
the rulings are structured on the way out.

Without this tier every docket is authored by hand. That is why only four exist.

### 3.2 Every Forum has an owning seat, and that seat must be convenable

A Forum with no chair never sits. The owning seat is named in the Forum's terms of reference
and is accountable for convening it.

> **A Forum may not be created for a seat that cannot be convened.**

**"Convenable", not "unparked".** A seat may be perfectly live and still unable to chair. On
22 July Hobbs held four open cards and was not parked — but the dispatcher could reach only
Cody, Archy and Tessa, so he could not be woken at all. Two strategy items had been sitting
still for exactly that reason (`7a Accept the four horizons`, In progress; `Archy → Hobbs:
reconcile the estate audit`, Ready). A seat that exists but cannot be convened is as useless
for chairing as a parked one, and a Forum created for one is a Forum that never sits.

### 3.3 Forum scope and precedence

Each Forum's terms of reference name **the classes of question it may rule on**. Where two
Forums' scopes touch, precedence is explicit — never improvised in the moment.

| Forum | Rules on | May not rule on |
|---|---|---|
| **Business Strategy Board** | *What* and *why* — direction, sequencing, portfolio, which products exist | *How* anything is built |
| **Technical Review Board** | *How*, and whether a thing is feasible or safe | What the fleet should pursue instead |
| **Data Governance Board** | What data may be held, by whom, for how long, and under what control | Delivery priority |

The technical board may rule **"not feasible"** on a strategic direction. It may not rule
**"do something else instead"** — that is the strategy board's scope. A genuine conflict
between two Forums escalates to Rex and is recorded as a decision of the Forum that raised it.

**Why this is not optional.** Without a precedence order, two Forums produce two answers to
one question with no tiebreak — the duplicate-store defect this document exists to cure,
moved up a layer. It has already happened once: on 21 July Archy recommended Pillar 2 first on
a technical read; Rex ruled dog-food-first on a strategic one; card `6a` was then routed to
Hobbs specifically to obtain the counter-argument. That conflict was resolved by Rex ruling
personally, which is correct once and does not scale.

### 3.4 Altitude — what a Forum does not do

A Forum rules on direction and standards. **It does not re-prioritise individual delivery
cards.** A governance body moving card priorities is doing delivery management, and the sitting
has become a status meeting. If an agenda item can only be expressed as "move card X up", it
belongs to the seat that owns the work, not to a Forum.

---

## 4. The bridge — what a decision produces

**A decision is not work. It is an instruction that creates work, or changes a standard, or
stands as a record.** Containment is the wrong relationship between the trees; a link is the
right one.

Every decision carries exactly one **disposition**:

| Disposition | Links to | Closed when |
|---|---|---|
| **Directs work** | A delivery card (Feature, User Story or Task) | The linked card is terminal |
| **Amends the estate** | A Canon artifact — a standard, a control, a policy | The artifact is created or amended |
| **Record only** | Nothing | On ruling — e.g. "accept the risk", "park it" |

A decision whose disposition is *Directs work* or *Amends the estate* and which carries **no
link is an open defect**: ruled and never commissioned. This is the exact failure the 22 July
audit found five times, and it is invisible today because nothing checks for it.

### 4.1 Dual-nature outcomes

One decision may produce both a standard and its rollout. These are two links, not one:

> **The artifact is the document. The rollout is delivery work.**

*Worked example.* "Roll the permissions baseline into every seat's `settings.json`" — the
baseline standard is an artifact under *Amends the estate*; rolling it onto eleven seats is a
delivery Task under the Seats Epic. Both must exist, and the decision closes only when both do.

### 4.2 A direction that governs future work must become an artifact

Strategy rulings are the hard case. *"Pillar 2 first, then Pillar 3, with Pillar 1 frozen to
subtraction"* directs no work, may produce no obvious document, and calling it *record only*
wildly undersells it — it governs everything that follows.

A fourth disposition, *Sets direction*, was drafted and **rejected**: a standing direction never
closes, so a docket full of directions would never close, which breaks §5 on contact.

The resolution is a rule inside the existing three dispositions:

> **A direction that governs future work must become an artifact. A direction not worth
> writing down is not a direction — it is an opinion.**

So a sequencing ruling is written as a standing artifact in Canon and closes on being written.
Anything not worth writing down is *Record only*, and carries no standing force.

This is deliberately load-bearing. It forces a governance forum to produce durable artifacts
rather than minutes that evaporate — and the failure it prevents is live: `6a Agree the
sequencing` has sat *In review* since 21 July and exists in no durable form anywhere. Under
this rule it would have become a Canon document on the day it was ruled.

### 4.3 Decisions must be structured, not prose

For a ruling to be actionable without a human re-reading it, a decision carries its
disposition and its link **as fields, not as sentences**. A minute describes; an instruction
executes. Free-text rulings cannot drive an unattended build and must not be relied on to.

---

## 5. Docket state is derived, never set

**Ratified by Rex 2026-07-22.** A docket has no hand-set status. Its state is computed:

- **Open** — one or more decisions unruled
- **Ruled** — every decision has an answer, but at least one disposition is still open
- **Closed** — every decision is ruled *and* every disposition has closed: linked delivery
  cards terminal, linked artifacts written, record-only rulings taken. A decision may also be
  explicitly **cancelled**, which closes it.

Only **Closed** dockets drop out of the working lists.

**Why derived, in Rex's words:** *"the only way the card would be derived as closed is by the
separate tasks being closed off. Those tasks have actions. Those actions need to be agreed and
closed, or we can cancel things, but it needs to be at that level to maintain some form of
integrity."*

The property this buys: **"ruled but never built" cannot hide.** On 22 July the Estate Audit
docket displayed as *done* while all 27 of its board cards sat open — because "done" meant
"every decision answered", conflating a ruling with its delivery. Under this model that docket
reads *Ruled*, and stays there until the work lands.

---

## 6. Two stores, and why that is not a breach

Governance is stored in its own Notion database. Delivery stays on the Decision Board. A
relation links a decision to the delivery card or artifact it produces.

This does not breach **one store, many views** (Orchestration v0.3, ratified 2026-07-21).
That principle forbids **two stores of the same object**. It does not forbid one store per
object class — and the same reasoning already carried the ops-lane split, ratified 21 July.

**The load-bearing reason is volume.** Forums recur. One weekly Technical Review Board is
~52 dockets a year at roughly 8 agenda items and 14 decisions each: **~1,100 cards a year**.
The entire Decision Board today is 284 cards. Held in one store, governance out-grows delivery
within about three months and the delivery view becomes mostly minutes.

---

## 7. What any view of either tree must report

A view that renders the hierarchy is a **compliance surface**, not a picture. It must show:

1. Every illegal edge, live work first
2. Every card with no parent that is not a Pillar or a Forum
3. Every decision with an open disposition and no link — *ruled, never commissioned*
4. Every docket in **Ruled** state, with what is holding it open

A view that shows the tree without showing its violations lets the tree rot quietly. That is
how 46 illegal edges and 20 orphans accumulated unnoticed.

---

## 8. State of the estate at proposal (22 July 2026, measured)

| | Count |
|---|---|
| Cards on the board | 284 |
| Filed in the delivery spine | 184 |
| Live cards on an illegal edge | **46** (94 including finished work) |
| — of which `Epic → Task` | 34 |
| — of which `Epic → User Story` | 12 |
| Parentless cards that are really messages | 20 |
| Docket Epics with no parent | 4 |
| User Stories with no children | 12 of 12 |
| Decisions ruled with no delivery card behind them | ≥5 confirmed by probe |

**Products named by Rex versus products on the board:** phone-AI 0 cards, white-label 0,
franchise 0, deployment kit 0, digital twin 1 (a decision inside a docket, not work), client
operations dashboard 5 (all filed under Rex Home Services, not as a product). The Datavation
Services pillar is not thin because the work is early — it is thin because **products were
never made first-class**.

---

## 9. Migration — what ratification commits to

Ordered. Each step is reversible; none is started before ratification.

1. **Create the governance database** — Forum, Docket, Agenda item, Decision; the disposition
   field; the relation to the Decision Board; forum scope and precedence per §3.3.
2. **Stand up the first Forum** — Technical Review Board, chaired by Archy, with terms of
   reference and a standing agenda. It is the only one convenable today (§11).
3. **Migrate the four existing dockets** (76 cards) into it. They stop being Epics.
4. **Backfill the missing dispositions** — every open decision gets a disposition and, where
   it directs work or amends the estate, a link. Gaps surface as defects, which is the point.
5. **Propose the missing Features** — roughly 12–15, to house the 46 orphaned Tasks and
   stories. Rex approves the list; Archy backfills. Same pattern as the Epics.
6. **Archive the 20 message cards.** Rex's hand — deletion is never Archy's.
7. **Only then** hand the hierarchy view to Cody, with the rules of §2 and §7 as a validator.
8. **Then** the status collapse (14 → 6), still sequenced last as ruled on 22 July.

Steps 1 and 6 need Rex. Steps 2–5 and 8 are Archy's, once ratified.

---

## 10. What this amends

- **Agent-Orchestration-and-Work-Tracking §3.1** — the hierarchy gains a Pillar tier above
  Epic, loses any tier below Task, and makes User Story explicitly optional.
- **Agent-Orchestration-and-Work-Tracking §3.4** — dockets cease to be Epics and leave the
  delivery hierarchy entirely.
- **Agent-Routine-Standard-v0_1 R2** — "read the Decision Board Command view" becomes "read
  the delivery store or the governance store as the item's class requires". R2's intent —
  one source of truth per thing — is strengthened, not weakened.

Nothing else in Canon is touched by this proposal.

---

## 11. The three Forums, and what gates each

| Forum | Chair | Convenable today? | Gate |
|---|---|---|---|
| **Technical Review Board** | Archy | **Yes** | none — can stand up on ratification |
| **Business Strategy Board** | Hobbs | **No** | dispatcher cannot wake Hobbs — blocked on `3a`, the watched wake |
| **Data Governance Board** | Dex | **No** | seat parked (Rex, 21 July) — §3.2 forbids creation until unparked |

**Two of the three Forums are gated behind the same piece of engine work.** Widening the
dispatcher roster is not just an autonomy feature; it is the precondition for governance
existing at all beyond the technical board.

Launch with the Technical Review Board alone. The other two are defined and dormant — created
the moment their chair becomes convenable, not before.

---

## 12. Open questions this version does not settle

1. **Does a Forum need to appear on any Rex-facing surface**, or is it purely a template
   source that only ever surfaces as dockets?
2. **Retention.** At ~1,100 governance cards a year, when does a closed docket leave the
   working store — and does it archive or summarise?
3. **Does an Agenda item need its own tier at all**, or is it presentation over a group of
   decisions? Kept as a tier here because it carries the discussion; worth revisiting after
   one real forum has run.
4. **Where standing artifacts live.** §4.2 sends directions to Canon. Canon currently holds
   *how we work* standards; a sequencing ruling is *what we are doing*. Same shelf, or a new
   one? Not settled here.

---

*Archy · 22 July 2026 · PROPOSED, not ratified. Held per Agent Architecture — Memory v0.2:
architecture-class change, logged and awaiting Rex's ruling. Not self-applied.*
