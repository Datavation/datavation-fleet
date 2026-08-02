# Agent Architecture — Memory (v0.2 — RATIFIED)

**Document owner (principal):** Archy — CTO seat, Court of Rex. Memory discipline is a technical standard for how the harness is built and maintained; it belongs to the CTO as principal owner. Stored in the Tabularium, curated by Libby (Curatrix) once she exists, coherence held by Cyrus (CIO).
**Operator:** Austen King — Datavation Ltd / Rex Home Services
**Status:** RATIFIED. v0.1 dated 2026-06-09; **v0.2 dated 2026-06-10 — substantive model change, see below.** The third and final foundation before rebuilding the kernel. Formerly titled *Agent Memory Architecture v0.1*.

> **Part of the Agent Architecture set — read all three together:**
> - **Agent Architecture — Roles** (`Agent-Architecture-Roles-v0_3.md`) — the Court of Rex: who exists, who is accountable, the locked principles.
> - **Agent Architecture — Capability** (`Agent-Architecture-Capability-v0_3.md`) — roles → skills → tools: what each seat can do and what it operates.
> - **Agent Architecture — Memory** *(this document)* — how agents learn and how truth stays single: the memory primitive, the live-write model, the memory log, the Memory Audit.
>
> Read the set as one: Roles says who exists and is accountable; Capability says what they can do and what they operate; this document says how they learn and how truth stays single.

> **What changed in v0.2, and why.** v0.1 gated memory *before* the fact: the agent wrote rough flags to `NOTES.md`, and a human (or Court seat) promoted them into a canonical `MEMORY.md` during a consolidation session. The agent never wrote to its own canonical memory. Testing that against the actual intent — agents that run routines unattended, when Austen is not present to approve — showed the gate was in the wrong place. An agent that cannot update its own memory mid-run cannot operate alone, and a pre-emptive human gate on every memory breaks the very self-learning engine (Hills / Claude Code best practice) the fleet is built to use. **v0.2 inverts the flow.** The agent owns and writes its own `MEMORY.md` live, in flight — the engine stays intact. Governance becomes *retrospective*: every write is recorded in an append-only `memory_log.md`, and the Memory Audit consumes that log so changes can be confirmed, amended, or rolled back after the fact. The antibody against the Cody-rewrote-Holly failure did not weaken — it moved from "ask first" to "show your work, and the one dangerous class still asks first." That single exception is the architecture-touching class (§3), which is still prospective: an agent may not self-write a change to a standard or to another agent's identity; it logs that as a *proposal* and keeps using its existing memory unchanged until a human rules.

> Why this document exists: two independent tests pointed at the same missing piece. The Hills harness comparison flagged that Memory is the engine that makes the whole system compound and improve — the fleet held the principle but not the operating routine. The Marshall test showed the need for a standing validity check on what an agent has been told to remember — the routine this document specifies as the **Memory Audit**, the antibody to the fleet's root disease. This document specifies the learning model, the change log, and the audit properly, and hands Cody the safeguard he needs before rebuilding Holly.

-----

## NAMING & MODEL HISTORY

**v0.2 model change — 2026-06-10.** The memory flow was inverted (see header rationale). Concrete naming consequences:
- The agent now writes its own `MEMORY.md` live. The pre-emptive consolidation gate is retired for operational memory.
- The old `NOTES.md` (rough capture buffer feeding human promotion) is replaced by **`memory_log.md`** — an append-only, timestamped record of changes the agent has *already made* to `MEMORY.md`, plus *proposals* it is not permitted to self-apply. The word "notes" is retired here: this is a log, not a notepad, and the Memory Audit routine consumes it.
- The **Memory Audit** routine is unchanged in name and purpose but now also reads `memory_log.md` to perform retrospective review, not only sweeps `MEMORY.md`.

**v0.1 naming history (renames executed 2026-06-10).** The three foundations were given a shared **`Agent Architecture — …`** name prefix so they group together in any sorted view and leave a clean namespace for future architecture documents. Filenames carry independent version numbers — the three revise at different rates. For the record:

1. `Working-Architecture-v0_3.md` → `Agent-Architecture-Roles-v0_3.md`; title heading now *Agent Architecture — Roles*. (Was *Working Architecture v0.3*.)

2. `Capability-Architecture-v0_3.md` → `Agent-Architecture-Capability-v0_3.md`; title heading now *Agent Architecture — Capability*. (Was *Capability Architecture v0.3*.)

3. This document: `Memory-Reconciliation-v0_1.md` → `Agent-Memory-Architecture-v0_1.md` → `Agent-Architecture-Memory` (now at v0.2); title heading now *Agent Architecture — Memory*.

4. The memory-validity check formerly called the "reconciliation skill" inside the Capability document (§4b, and the Libby birth trigger in §3/§8) is named the **Memory Audit**.

5. **Marshall's `marshall-weekly-reconcile` was deliberately NOT renamed.** That routine is genuine data reconciliation — it syncs Google Calendar and Notion and writes to both. Freeing the word *reconciliation* for Marshall's routine is the entire point of naming the memory check the Memory Audit.

-----

## 0. The root disease, restated

The fleet has one disease with many symptoms: duplication and divergence of intelligence and truth with no single authoritative source. Holly's WhatsApp Railway deployment drifts from her local version because it builds from a hardcoded constant rather than live context files — two versions of Holly exist, neither aware the other is wrong. Cody rewrote Holly into an unwanted version because he was given latitude without rails and there was nothing authoritative to check his work against. Marshall's scripts could drift from their documentation without anyone noticing.

Memory, the memory log, and the Memory Audit are the cure, not symptom management. Memory is the mechanism by which an agent accumulates correct knowledge over time. The memory log is the append-only record of every change the agent makes to that memory, so nothing changes invisibly. The Memory Audit is the mechanism by which both the standing memory and the log are checked — for staleness, contradiction, and orphaning, and for whether each logged change should stand — on a schedule. Together they enforce a single authoritative source that is also fully accountable: one place where truth lives, one log that records how it got there, one routine that keeps it honest.

-----

## 1. What a memory is

A memory is a **cause-action pair**: here is what happened, here is what the agent does differently as a result. One primitive, not three. The label on it — correction, preference, decision record — is descriptive colour, not architectural structure. All three are the same primitive:

- A *correction* says: this went wrong; don't do it again.
- A *preference* says: this worked better; do it this way.
- A *decision record* says: we chose this path for this reason; stay on it.

Same primitive, different label. The model has one write discipline, not three.

**What a memory is not:** it is not a re-statement of what is already in the context file. Context (`CLAUDE.md`) is stable identity — who the agent is, what it is responsible for, how it is configured. Memory adds something the agent did not know before. Writing a memory that duplicates the context is the root disease appearing in miniature: duplicated truth, two places, diverging over time. The test: if removing the memory entry would leave the agent's behaviour unchanged, it is not a memory — it belongs in `CLAUDE.md`, or nowhere.

**Quiet workflows generate nothing.** A workflow that runs cleanly without error, correction, or new information produces no memory candidates. That is correct behaviour, not a gap. The memory model produces signal only when there is something worth remembering.

-----

## 2. The physical structure — two files per agent, three tiers across the fleet

### The two per-agent files

**`MEMORY.md` — the canonical memory, agent-owned and live.**

The authoritative memory for this agent. Loaded at every session start, and **written by the agent itself, in flight, during a live session** — this is the self-learning engine, kept intact. When the agent learns something during a run (an error surfaced, Austen amended a draft, a preference was expressed, new information changed a decision), it updates `MEMORY.md` then and there. It does not wait for a human and does not stop the run to ask. Formatted as cause-action pairs, each entry self-contained, dated, and attributed. An index at the top lists every entry by brief label; before writing a new entry the agent checks the index, so the same learning updates an existing entry rather than landing twice. Format:

```
## Memory Index
- [Date] MEM-001: [Brief label]
- [Date] MEM-002: [Brief label]
...

---

## MEM-001 — [Brief label]
Date: YYYY-MM-DD
Cause: [what happened]
Action: [what the agent now does differently]
Scope: LOCAL | ELEVATED
Class: OPERATIONAL | ARCHITECTURE
```

`MEMORY.md` is the single authoritative source for what this agent has learned. It is owned by the agent and kept current by the agent. The one thing the agent may **not** self-write is the architecture-touching class — see §3; those are logged as proposals and do not enter `MEMORY.md` until a human rules.

**`memory_log.md` — the append-only change record.**

Pre-existing, always present in the agent's memory folder, never needs creating. **Append-only — never edited, never overwritten.** It is the black-box recorder: every time the agent writes to `MEMORY.md`, it appends an entry here saying what changed, when, the circumstance, and why. This is what makes a live-write memory *accountable* rather than opaque — the change happened without a prior gate, but it cannot happen invisibly, and it can always be rolled back because the log captured the before-state and the reason. Format:

```
## [Timestamp] [Agent] — [DONE | PROPOSED] — [Brief label]
Entry: MEM-0NN (or "new")
Class: OPERATIONAL | ARCHITECTURE
Change: [what was written to MEMORY.md, or what is being proposed]
Previous: [the prior state, for rollback — or "none / new entry"]
Circumstance: [what was happening when this arose]
Reason: [why the agent made / proposes this change]
```

Two entry types live in the log:

- **DONE** — an operational memory the agent has *already written* to `MEMORY.md`. Governance is retrospective: the Memory Audit surfaces it for confirm / amend / roll back after the fact.
- **PROPOSED** — an architecture-touching change the agent is **not permitted to self-apply** (see §3). The agent logs it as a proposal, does **not** write it to `MEMORY.md`, and continues operating on its existing memory unchanged until a human rules. Governance here stays prospective — proposed, then ratified, then written.

`memory_log.md` is never loaded as authoritative knowledge at session start — `MEMORY.md` is the authority; the log is the audit trail. The log's job is to make every change to memory traceable and reversible, and to hold proposals safely until they are ruled on.

### The third tier — elevation to the Tabularium

When a memory is general enough to apply across the whole fleet — not an agent-specific quirk but a fleet-wide learning — it is elevated from the agent's `MEMORY.md` into the Tabularium (the shared knowledge store). Elevation is a deliberate act, confirmed by the human, written into the shared library as Datavation IP. The marker `Scope: ELEVATED` in the originating entry flags that it has been promoted. Because elevation changes shared fleet IP rather than one agent's local memory, it is treated as architecture-class: proposed in the log, ratified, then written — never self-applied.

**The fleet-level signal:** when the same change appears in more than one agent's `memory_log.md` in the same Memory Audit cycle, that is the indicator — not a local quirk, a systemic issue. It belongs in the fleet library, not in any one agent's memory. This is the mechanism by which individual agent learning becomes organisational learning across the fleet.

-----

## 3. The authorship model — two classes, one dividing line

The whole model rests on a single distinction: **what an agent may write to its own memory in flight, and what it may only propose.**

**Operational memory — the agent writes it, live, and the log records it.** The everyday class: a tool quirk, a phrasing preference, how Austen wants a task done, a contact's preference, a workflow adjustment, a correction to its own prior behaviour. The agent writes these to `MEMORY.md` in the moment, with no prior gate, and appends a `DONE` entry to `memory_log.md`. This is the self-learning engine and it is deliberately ungated — an agent running a routine unattended must be able to learn without stopping to ask. Governance is **retrospective**: the Memory Audit surfaces these for confirm / amend / roll back after the fact. The cost is real and accepted — a wrong operational memory can run for a while before it is caught — but operational memories are survivable when wrong and reversible from the log, so the cost is worth the autonomy.

**Architecture-touching memory — the agent proposes it, and a human rules before it is written.** The narrow dangerous class: anything that would change an architecture standard or principle, change another agent's identity, behaviour, or context, or elevate a learning into the shared Tabularium. The agent may **not** self-write these. It appends a `PROPOSED` entry to `memory_log.md`, does not touch `MEMORY.md`, and **keeps operating on its existing memory unchanged until a human rules.** Governance here stays **prospective** — proposed, then ratified, then written. This is the one place the pre-emptive gate survives, and it survives exactly where the Cody-rewrote-Holly failure lives.

**How an agent tells the two apart.** The test is *what the change can break.* If the worst case is this agent behaving slightly wrong until the next audit — operational, write it. If the worst case touches a standard, another agent, or shared fleet IP — architecture, propose it. When genuinely unsure, the agent treats it as architecture and proposes: erring toward proposing is safe; erring toward self-writing is the failure mode. The `Class:` field on every memory and every log entry records which call was made.

**The safeguard against the Cody-rewrote-Holly failure, restated for this model.** Cody had the engineering skill and was given latitude without rails. He rewrote Holly because there was no authoritative version of Holly to check against and no gate on changes that affect another agent. Two rules close this, and both fall on the architecture side of the line:

1. A memory about another agent may only be written by that agent itself or by Rex — never self-written by a peer agent. A peer may only *propose*.
2. Any change touching another agent's behaviour or identity, or any architecture standard, is architecture-class by definition: proposed, Court-routed for counsel, human-final. Never self-written, however capable the agent.

No agent, however capable, accumulates the right to redefine another. Cody builds containers. He does not fill another agent's memory.

**Court counsel on architecture proposals.** When a `PROPOSED` entry is ruled on, high-stakes ones are circulated to the relevant Court seat for counsel before the human's final call — CTO (Archy) for technical and architecture decisions, CIO (Cyrus) for information-estate matters, CDO (Dex) for data governance, CRO (Victor) for risk and compliance. The Court advises; the human decides. This is how Archy's ownership of the architecture standards is enforced in practice rather than as a promise.

**Graduated autonomy applies to the line itself.** As the Memory Audit builds a confidence case that an agent's operational self-writes are consistently sound, the line can be held steady or, deliberately and by human decision, adjusted. It does not move the other way by drift. The human stays in the loop longest on the architecture class — that is where it matters most, and where Principles 6 and 7 apply with the most force.

-----

## 4. The write routine — three stages

### Stage 1 — Write or propose (event-driven, during the workflow)

The trigger is a decision point: something notable occurs. An error surfaces. Austen amends a draft. New information is provided. A preference is expressed. The agent classifies it (§3):

- **Operational** → the agent updates `MEMORY.md` immediately (new entry, or an in-place update of an existing indexed entry) and appends a `DONE` entry to `memory_log.md` capturing the change, the previous state, the circumstance, and the reason.
- **Architecture-touching** → the agent appends a `PROPOSED` entry to `memory_log.md`, leaves `MEMORY.md` untouched, and carries on with its existing memory.

Lightweight in the moment. The log entry is what makes the live write safe; it is never skipped.

Quiet workflows generate nothing. A run that completes cleanly with no error, correction, or new information writes no memory and logs nothing. Correct behaviour, not a gap.

### Stage 2 — Audit (scheduled — the Memory Audit, §5)

On a schedule appropriate to the workflow cadence (weekly for active agents; monthly for lower-frequency ones), the **Memory Audit** runs. It is the retrospective governance the live-write model depends on, and it is specified in full in §5. In summary, it:

1. Reads `memory_log.md` since the last audit and reviews every `DONE` entry — should this self-written operational memory stand, be amended, or be rolled back (using the `Previous:` state the log captured)?
2. Surfaces every `PROPOSED` entry for the human to rule on — ratify (then write to `MEMORY.md`), revise, or reject. Court counsel is sought on high-stakes proposals first.
3. Sweeps the standing `MEMORY.md` for staleness, contradiction, and orphaning (the original Memory Audit checks).
4. Scans for the same change appearing across multiple agents' logs — if present, flags it as a candidate for elevation to the Tabularium (itself an architecture-class proposal).

The Memory Audit is read-only with respect to `MEMORY.md` and `memory_log.md`: it surfaces findings and the human (or, for counsel, the Court) decides. Ratified proposals are written to `MEMORY.md` as a deliberate act after the ruling, with a corresponding `DONE` entry appended to the log.

### Stage 3 — Reload (before next session)

At the start of the next session the agent reloads `MEMORY.md`. Its own in-flight operational writes are already there; any proposals ratified during the audit are now there too; anything rolled back is gone, with the log preserving why. The agent begins from the corrected baseline. No re-explanation, no re-derivation. This is how the system compounds: each cycle leaves the next session starting from sounder memory than the last.

-----

## 5. The Memory Audit — specified

The Memory Audit is **distinct from the write routine of §4**. The agent writes operational memory live; the Memory Audit is the retrospective check that makes that live-write safe, plus the standing-validity check on memory already held. It does two jobs: it reviews the change log (`memory_log.md`) since the last run, and it sweeps the canonical store (`MEMORY.md`) for decay.

**What it is not:** it is not a data synchronisation routine. Marshall already runs a routine he calls reconciliation (`marshall-weekly-reconcile`) that keeps Google Calendar and Notion consistent — it writes to both stores to bring them into agreement. That is a workflow integrity check belonging to the workflow layer. The Memory Audit is named deliberately to avoid overloading the word *reconciliation*: the two are different operations. Reconciliation syncs data between stores and writes; the Memory Audit checks memory for validity and only reports. Do not conflate them.

**Part A — review the log.** The Memory Audit reads every `memory_log.md` entry since the last run:
- **`DONE` entries** (operational self-writes): was each one sound? Confirm it stands, flag it for amendment, or roll it back using the `Previous:` state the log captured. This is the retrospective governance the live-write model depends on.
- **`PROPOSED` entries** (architecture-touching): surface each for the human to rule on — ratify (then it is written to `MEMORY.md`), revise, or reject. High-stakes proposals go to the relevant Court seat for counsel first.

**Part B — sweep the store.** On the same run, the Memory Audit sweeps `MEMORY.md` and asks three questions of each existing entry:

1. **Staleness** — is this memory still true? Has the tool, workflow, or context it refers to changed since the entry was written? A memory written when a script behaved one way may now be wrong because the script has changed.

2. **Contradiction** — does this memory conflict with any other entry in `MEMORY.md`? Two entries written at different times may now say opposite things. The more recent entry is not automatically correct — both are surfaced for human adjudication.

3. **Orphaning** — does this memory refer to a skill, tool, context, or agent that no longer exists? If so, the memory is inert at best and actively misleading at worst.

**How it reports:** documentation-only. The Memory Audit produces a findings list — flagged entries with the reason for the flag — and presents them for human review. It does not itself edit `MEMORY.md` or `memory_log.md`. That gate is non-negotiable, and where possible it is enforced at the infrastructure layer (read-only access during Memory Audit runs) rather than by instruction alone — per the gold standard from Agent Architecture — Capability §4. Writes that follow a ruling (a ratified proposal, a rollback) are deliberate acts taken after the audit, each appended to the log.

**Human decisions on findings:** for each flagged item the human decides:
- *Confirm* — the memory (or the logged self-write) stands; it is valid.
- *Amend* — the entry is revised; the revision is written to `MEMORY.md` and a `DONE` entry recording the amendment is appended to the log.
- *Roll back* — a `DONE` self-write is reverted to its `Previous:` state from the log; the reversal is itself logged.
- *Ratify / revise / reject* — for a `PROPOSED` entry: ratify (write to `MEMORY.md`, log it), revise then ratify, or reject (the proposal is closed in the log with a reason; `MEMORY.md` was never touched).
- *Retire* — an existing entry is removed from `MEMORY.md` and archived (not deleted; archived, so it can be recovered if the retirement was wrong).

**How it enforces Archy's ownership in practice:** Archy owns the architecture standards. That ownership is enforced on a schedule, not by promise. Every architecture-class change reaches `MEMORY.md` only as a ratified proposal, and when the Memory Audit surfaces an operational memory that contradicts an architecture principle, that is Archy's flag and it is reclassified and routed accordingly: Court counsel, human final call.

**Connection to the Karpathy health-check and Libby's birth trigger:** the Memory Audit operationalises the contradiction/orphan/missing-page health-check from the Karpathy second-brain pattern. When the volume of findings consistently exceeds what Cyrus can manage as a side-skill, that is the birth trigger for Libby (Curatrix) — the same trigger already specified in Agent Architecture — Capability §3 and §8.

-----

## 6. How memory and the Memory Audit together cure the root disease

**Memory** ensures that what an agent learns is written down and reloaded — not held in human memory (which degrades between sessions) and not re-derived fresh each session (which produces drift). The single authoritative source for what an agent has learned is its `MEMORY.md`. The agent keeps it current itself; the log keeps every change to it accountable.

**The Memory Audit** ensures that `MEMORY.md` remains accurate over time. A memory written correctly last month may be wrong today, and a memory the agent self-wrote yesterday may have been wrong on arrival. Without a scheduled check, divergence is silent — the agent behaves as if something is true that is no longer true, and no one notices until a symptom appears. The Memory Audit reviews the log and sweeps the store, surfacing divergence before it produces a symptom.

**Together:** `MEMORY.md` holds what the agent currently knows, written by the agent and live. `memory_log.md` records every change to it, so nothing changes invisibly and anything can be rolled back. The Memory Audit keeps `MEMORY.md` honest — confirming sound self-writes, reverting bad ones, and ruling on the architecture-class proposals the agent was not allowed to self-apply. The Tabularium holds what applies fleet-wide. Nothing important lives only in a conversation. Nothing important changes without a trace. This is the single authoritative source, made accountable.

**The Holly WhatsApp drift, diagnosed and fixed under this model:** Holly's Railway deployment drifts from her local version because it holds a frozen snapshot of Holly from deployment day, with no `MEMORY.md` reload at session start. Every learning made locally since that deployment date is invisible to the Railway version. The fix is not a one-time sync — it is establishing the memory discipline on the Railway deployment: the same `MEMORY.md` source, the same reload at session start, the same Memory Audit schedule. Then there is one Holly, not two. This is Principle 5 (split-brain, local master — run copy is a deployment artefact) applied to memory: the local `MEMORY.md` is the brain; the Railway deployment reads from it, never diverges from it.

-----

## 7. The handoff to the rebuild

This document is the safeguard Cody needs before rebuilding Holly. What it gives him, specifically:

1. **The file structure:** every agent has `MEMORY.md` (canonical, indexed, agent-owned, loaded at session start, written live) and `memory_log.md` (append-only change record, never loaded as authority), in a memory folder containing both. Holly's rebuild gets both files from the start, not as an afterthought.

2. **The write routine:** during a live Holly session, when Holly learns something operational she updates her own `MEMORY.md` and appends a `DONE` entry to `memory_log.md`. When something architecture-touching arises — anything affecting a standard, another agent, or shared IP — she appends a `PROPOSED` entry and does not self-apply it. She keeps running on her existing memory until Austen rules.

3. **The Memory Audit:** Holly runs the Memory Audit on a weekly schedule. It reviews her log (confirming or rolling back her operational self-writes, surfacing her proposals for ruling) and sweeps her `MEMORY.md` for staleness, contradiction, and orphaning. Findings go to Austen. Holly never resolves findings herself; the audit is read-only at the infrastructure layer where possible.

4. **The boundary that prevents the original failure:** Cody builds Holly's structure — the folders, the files, the scaffold — and her `MEMORY.md` starts empty but for its index header. Holly fills her own operational memory thereafter; that is hers to do. What no one self-writes is the architecture class: any change to Holly's identity or context is architecture-touching — proposed, Court-routed (Archy for architecture decisions), human-final. Cody builds the container. He does not fill another agent's memory, and he never writes to another agent's `MEMORY.md` except by explicit instruction from Rex, never wholesale. This is the exact gate whose absence let Cody rewrite Holly.

5. **The Railway discipline:** Holly's Railway deployment must be rebuilt with the same memory discipline as local — same `MEMORY.md` source, same reload at session start, same live-write-plus-log behaviour, same Memory Audit schedule, live context files rather than hardcoded constants. One Holly, learning in one place, audited in one place.

-----

## 8. Status of the build-out

**Settled in v0.1 (and carried forward):**
1. The memory primitive — cause-action pair; one primitive regardless of label.
2. The Tabularium third tier — fleet-level elevation of memories general enough to be shared IP.
3. The Memory Audit's standing-validity checks — staleness, contradiction, orphaning; documentation-only; human-gated; read-only at infrastructure layer where possible.
4. The root-disease framing — a single authoritative source per agent, kept honest over time.

**Changed / settled in v0.2 (2026-06-10):**
1. **The flow inverted to live-write.** `MEMORY.md` is agent-owned and written in flight — the self-learning engine kept intact for unattended operation. The pre-emptive consolidation gate is retired for operational memory.
2. **`NOTES.md` replaced by `memory_log.md`** — append-only, timestamped record of every change made (`DONE`) and every architecture-touching change proposed (`PROPOSED`). The black-box recorder that makes live-write accountable and reversible.
3. **The two-class authorship model (§3)** — operational memory is self-written and audited retrospectively; architecture-touching memory is proposed and ratified prospectively. The dividing line is *what the change can break*.
4. **The architecture-class exception** — an agent may not self-write a change to a standard, to another agent, or to shared IP; it logs a proposal and keeps using existing memory unchanged until a human rules. This is where the Cody-rewrote-Holly gate survives.
5. **The Memory Audit became log-aware (§5)** — Part A reviews the log (confirm/roll-back self-writes, rule on proposals); Part B sweeps the store. Still read-only, still human-final.
6. **The rebuild handoff (§7)** rewritten so Holly is built on this model from birth.

**Carried to the build layer:**
1. The exact tooling and trigger for the Memory Audit — how it is invoked, its output format in practice, whether a scheduled Claude Code routine or a manually triggered session.
2. Infrastructure-level enforcement of the read-only audit gate, and of the architecture-class write-block — currently instruction-level; design target is infrastructure-level per Agent Architecture — Capability §4 gold standard. (How an agent is *physically* prevented from self-writing an architecture-class change, not merely instructed not to, is the highest-value open item — it is the §2-extension scope-of-target problem from the Capability document, applied to memory.)
3. Tabularium integration — how elevated memories are written, versioned, and indexed in the shared library.
4. The Railway `MEMORY.md` live-reload — the technical implementation; a Cody brief once the rebuild begins.
5. Memory Audit cadence configuration — how cadence is recorded in each agent's context file so it does not drift between deployments.
6. `memory_log.md` retention and rotation — how far back the log is kept, and whether audited-and-confirmed entries are archived to keep the live log lean.

-----

*Three foundations stand: Agent Architecture — Roles (the Court of Rex), Agent Architecture — Capability (roles → skills → tools), and Agent Architecture — Memory (how agents learn and how truth stays single). The kernel can now be rebuilt safely. Rebuild Cody first so Cody can correctly rebuild Holly. Do not start the scaling layers — canonical data model, adapter pattern, comms portability — until the kernel is sound. The document is the safeguard. The safeguard exists. Build.*
