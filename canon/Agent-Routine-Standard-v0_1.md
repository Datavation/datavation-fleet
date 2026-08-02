---
title: Agent Routine Standard
version: v0.1
status: ratified
date: 2026-07-11
owner: Archy (Architectus, CTO)
governs: how every seat converts a declared behaviour into a routine that reliably fires
sits-under: Agent-Orchestration-and-Work-Tracking.md (the concrete spec for its Routines layer, Layer C / §5)
labels: [architecture, orchestration, routines, decision-board, source-of-truth, fail-loud, output-contract, holly, archy, proactive-surfacing]
---

# Agent Routine Standard — v0.1

**Ratified by Rex 2026-07-11.** The concrete mechanism for the **Routines layer** of the
Orchestration & Work-Tracking Standard (Layer C, §5). This is not a free-standing standard — it
specifies *how a routine is authored* for a layer that already existed. Owned by Archy.

**Reconciles** Holly's `waiting_on_rex` (the rigid-contract *form*) with Archy's
`proactive_surfacing` (the judgment *content*) — two implementations wired 2026-07-09 from the Fleet
Behaviour & Build-Velocity Brief that had already diverged. This standard is the single shape they
collapse into.

---

## 1. Why this exists

A trait written in a CLAUDE.md — "be proactive", "keep the board honest" — is an **adjective**, and
an adjective never runs. The 4–8 July silent-queue failure (ten items sat waiting on Rex, unsurfaced)
was an adjective with no trigger. A routine is the fix: it turns the adjective into a **function that
fires on a trigger and returns a fixed shape**.

Left unstandardised, routines reproduce the fleet's root disease in a new place: on 2026-07-09 one
brief produced **two** "what's waiting on Rex" routines reading **two different Notion objects**. This
standard makes routines both *reliable* (they fire; they fail loud) and *single-truth* (they never
invent a private version of a fact the board already holds).

---

## 2. Definition

> A **routine** is a deterministic function an agent runs on a defined **trigger**, reading a named
> **source of truth**, producing a fixed **output contract**, and failing **loudly** when a
> precondition isn't met.

If you cannot state its trigger, its source of truth, and its exact output shape, it is not a routine
yet — it is still an adjective.

---

## 3. The four governing rules

**R1 — Behaviour lives in the steps, not in adjectives.**
Every step is one action a person could tick off. No step may contain a personality instruction.
Where a step needs judgment, that judgment is expressed as **named, auditable criteria** (§4), never
as a mood.

**R2 — Single source of truth.**
Every routine **names the one canonical object it reads and writes**. For anything Rex-facing, that
object is the **Decision Board Command view** (`Action Required = 🔴 Rex`) — the ratified surface the
cockpit already reads. A routine may **not** stand up a private list that competes with the board. If
the board cannot express what the routine needs, the fix is a board-schema change (architecture-class,
routed to Archy) — **not** a shadow list.

**R3 — One surface, one owner.**
A routine that renders a **consolidated, Rex-facing** result (a "waiting on you" headline, a daily
briefing) is a **single-instance** routine owned by one seat — it is **not** cloned to all thirteen.
Every other agent **feeds** its blocked items onto the board via the Output Record (Conclusion +
Action Required); the one surfacing routine reads the board and renders once. Cloning a surfacing
instance to N agents gives Rex the same list N times from N partial views — the noise the board exists
to remove.

**R4 — Fail loud, never silent.**
Preconditions gate the run; a failed precondition **stops and says so** ("Notion isn't responding, I
can't check"). It never returns an empty result that reads as "all clear". The Output Contract's
empty-case is an explicit, distinct line. Silence is always a bug, never a pass.

---

## 4. The Routine File Contract

Every routine is one markdown file with these sections, in order (blank template: Appendix A).

| Section | What it fixes | Mandatory |
|---|---|---|
| **Metadata** (agent · owner · version · updated · status) | provenance & lifecycle | yes |
| **Purpose** — one line it *does* + one line it deliberately does **NOT** do | stops sprawl into "be generally helpful" | yes |
| **Trigger** — type + exact fire condition | the layer whose absence = the routine never runs | yes |
| **Source of Truth** — the one canonical object read/written (R2) | prevents divergent private lists | yes |
| **Ownership & Scope** — single-instance or per-agent (R3) | prevents cloning a surface to 13 | yes |
| **Preconditions** — checks that must pass or the routine STOPS (R4) | silent-failure debt fixed at source | yes |
| **Steps** — one action each; mechanical or judgment | behaviour made concrete & auditable | yes |
| **Output Contract** — the exact shape, incl. the explicit empty-case | doubles as the test | yes |
| **Abort conditions** — named failure → exact fallback output | loud, predictable degradation | yes |
| **Change log** | versioning | yes |

**Two kinds of step** (the merge of the two source routines):

- **Mechanical step** — deterministic, verifiable, one action. *"Query the board for `Action Required
  = 🔴 Rex` and `Status` not terminal."*
- **Judgment step** — a decision bound to **explicit named criteria** so it stays auditable rather than
  becoming an adjective. *"Rank by cost-to-leave: (a) blocks other work, (b) time-decaying, (c) age of
  wait, (d) one-click vs real decision."*

A well-formed surfacing routine uses both: mechanical steps to *gather* truthfully, judgment steps to
*prioritise and move*. The judgment steps carry the behaviours that made `proactive_surfacing` useful:
- **rank by cost-to-leave** (not a static Priority field alone);
- **propose a close** — for at least one item, bring the specific decision so Rex approves in a word;
- **separate "needs Rex" from "I'm handling it"** — so management-by-exception works;
- **calibrate to his time** — headline-first, cap to what matters today, state the human action (not
  board jargon), route anything he needs while away from the PC to the phone via a `🔴 Rex` board card.

---

## 5. Testability — the output contract IS the test

A routine is "working" iff its output is one of the shapes declared in its Output Contract. Anything
else is a concrete, nameable defect, not a vague "the agent feels off". This is the done-line every
routine ships with.

---

## 6. Adoption

1. **Ratified** (Rex, 2026-07-11) — this is now the Routines-layer spec under the Orchestration
   Standard; Archy owns it.
2. **Reconcile the two existing routines** to the merged shape and the board as single source of
   truth. Archy's `proactive_surfacing` adopts the metadata/precondition/output-contract sections.
   Holly's `waiting_on_rex` keeps its form, drops the private-task-list assumption, folds in the
   judgment steps.
3. **Per-agent authoring is a peer-file change** — each seat's routine set is drafted **PROPOSED** and
   Rex ratifies before it is applied to that agent (never self-applied to a peer; control gate).
4. **Surfacing stays single-owner** (R3): one seat renders the consolidated "waiting on Rex"
   (recommended: Holly, EA/chief-of-staff lane, once she reads the board as truth); Archy's
   `proactive_surfacing` remains the CTO-desk instance for the architecture queue.

---

## Appendix A — Blank routine template (copy-ready)

```markdown
# Routine: [routine_name_in_snake_case]

**Agent:** [seat]   **Owner:** Austen King / Datavation Ltd
**Version:** 0.1   **Last updated:** [YYYY-MM-DD]   **Status:** [Draft / Active / Retired]

## Purpose
[One sentence: what it does.]
[One sentence: what it deliberately does NOT do.]

## Trigger
**Type:** [Session start / Scheduled / Trigger phrase / Event]
**Fires when:** [exact condition — a schedule, an event, or exact phrases.]

## Source of Truth
[The single canonical object this routine reads/writes. Rex-facing ⇒ Decision Board Command view
(`Action Required = 🔴 Rex`). No private competing list.]

## Ownership & Scope
[single-instance — this one seat renders for the fleet  |  per-agent — each seat runs its own.]
[If it renders a consolidated Rex-facing result, it MUST be single-instance.]

## Preconditions  (fail loud — if any fails, STOP and say so; never return an empty "all-clear")
1. [Tool/connection that must be live.]
2. [Data that must be reachable.]
3. [State that must be known, e.g. current date.]

## Steps  (one action each; mark each [mechanical] or [judgment])
1. [mechanical] **[Verb + object]** — [deterministic action against the Source of Truth.]
2. [judgment]  **[Verb + object]** — [decision bound to NAMED criteria: (a)… (b)… (c)…]
3. **Render** using the Output Contract.
4. **Stop.** [State explicitly what NOT to add.]

## Output Contract  (the exact shape — this is the test)
```
[Fixed header, fixed fields, fixed order.]
```
Empty case (explicit, distinct):
```
[The exact one-line output when there is nothing to report.]
```

## Abort conditions
- If [failure X] → [exact fallback output].
- If [failure Y] → [exact fallback output].

## Change log
| Date | Version | Change |
|---|---|---|
| [YYYY-MM-DD] | 0.1 | Created. |
```

---

## Change log
| Date | Version | Change |
|---|---|---|
| 2026-07-11 | 0.1 | Ratified by Rex. Merged Holly `waiting_on_rex` form + Archy `proactive_surfacing` content; added R2 (single source of truth) and R3 (one surface / one owner) as the architectural guards. Draft provenance: `Agents\Archy\output\proposals\2026-07-10-agent-routine-standard-v0_1-PROPOSED.md`. |

*Archy. The standard, held and enforced — so autonomy stays safe.*
