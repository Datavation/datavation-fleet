# Agent Architecture — Capability (v0.3 — RATIFIED) — Roles → Skills → Tools

**Document owner (principal):** Archy — CTO seat, Court of Rex. The architecture standards are a technical standard of how the harness is built; they belong to the CTO as principal owner. Stored in the Tabularium (knowledge store), curated for health by Libby (Curatrix) once she exists, and held intellectually coherent across the whole information estate by Cyrus (CIO). Holly does **not** own these standards — Holly is the kernel and provisioner who *builds* agents; she does not *govern* the standards by which they are built.
**Operator:** Austen King — Datavation Ltd / Rex Home Services
**Status:** RATIFIED, dated 2026-06-09; ratified as one of the three Agent Architecture documents 2026-06-10. Supersedes the v0.2 PROPOSED FRAMEWORK and the v0.1 SKELETON. Formerly titled *Capability Architecture v0.3*. The framework was tested against the real Marshall workflow (architecture doc + TPG/Equans SOP) on 2026-06-09; it survived, gained one upgrade, and surfaced two genuine gaps, all now folded in below. This is the second foundation of the harness, settled the way the Court (Agent Architecture — Roles) is settled.

> **Part of the Agent Architecture set — read all three together:**
> - **Agent Architecture — Roles** (`Agent-Architecture-Roles-v0_3.md`) — the Court of Rex: who exists, who is accountable, the locked principles.
> - **Agent Architecture — Capability** *(this document)* — roles → skills → tools: what each seat can do and what it operates.
> - **Agent Architecture — Memory** (`Agent-Architecture-Memory-v0_2.md`) — how agents learn and how truth stays single: the memory primitive, the live-write model, the memory log, the Memory Audit.
>
> Read the set as one: Roles says *who exists and is accountable*; this document says *what they can do and what they operate*; Memory says *how they learn and how truth stays single*. The whole assembly — model plus personalisation, context, action, memory and delegation — is, in the industry's term, a **harness** (see Appendix A for the lineage of that term and the standards this document adopts).

> Why this document exists: in v0.3 we tried to hang a tool (the knowledge store) off a role (Cyrus/CIO) inside the org chart. That was a category error — three officers each had a legitimate ownership claim (CTO technically, CDO for governance, CIO intellectually), which is the tell-tale sign of shared infrastructure, not a reporting line. Tools are not seats. They belong here.

-----

## 0. What this document is, and what the Marshall test proved

The skeleton captured five good ideas but left the central word — *skill* — carrying two meanings at once: a concrete workflow an agent runs, and a permission an agent is granted. v0.2 resolved that by **adopting Anthropic's published primitives rather than inventing our own.** This matters more than it looks: the reason the Skill primitive exists in the wider ecosystem is the exact problem this whole fleet is built to cure — without shared, packaged capability you get prompt sprawl and inconsistent behaviour across agents. Our instinct and the industry standard turned out to be the same instinct. So the job is not to invent a way of working; it is to adopt the standard and decide which capabilities exist and which seat holds each one.

v0.3 ratifies that framework after testing it against the real Marshall workflow — the live architecture document plus the TPG/Equans SOP. The test was deliberately run against the messy real thing, not a tidy invented example, because a framework that only survives a clean case is worth little. Three things came out of it, all folded into the sections below:

- **The sizing rule and the two gate types held, and were independently confirmed.** Marshall's back-half workflow had *already* organised itself into skill-sized chunks separated by human gates, with no one having designed it that way. The rule described a shape that was already there rather than imposing one (see §4).
- **One upgrade: infrastructure-enforced control gates.** Marshall's Gmail uses the `gmail.compose` scope, which technically *cannot send*. The control gate is not a policy that asks nicely — it is physically unbreakable at the tooling layer. This is now named as the gold standard for control gates (§4).
- **Two gaps the framework did not yet cover: pipeline ownership across seats, and the Memory Audit as a canonical skill.** Marshall's work is already multi-seat (Dex/CDO owns the Notion sync, `dex-tpg-notion-001`), which raised the question of who owns a *pipeline* that spans seats (§4a). And Marshall already runs a hand-built `marshall-weekly-reconcile` task whose whole job is to stop documentation drifting from code — which is an antibody to the fleet's root disease, built in one corner without being named as the general cure. The generalised, memory-validity form of that check must become a canonical skill — the **Memory Audit** (§4b).

Everything below is the second foundation of the harness — the layer beneath the Court where capability and safety actually live.

-----

## 1. The four primitives, named correctly

A role does not use a tool directly. Between them sits a skill, and a skill is a folder of packaged know-how that knows how and when to drive a tool. Four primitives, kept strictly distinct — most of this project's earlier confusion was four different things all being called "skill" because they all live as folders next to each other.

**Role** — identity and accountability. A seat in the Court of Rex (Holly, Cody, Cyrus…). A role is *who* an agent is and *what it is answerable for*. Roles are defined in the Court document, not here.

**Skill** — a folder of packaged know-how: a `SKILL.md` file plus any scripts and reference files it needs. It carries domain expertise — the workflow, the context, the best practice — that turns a general agent into a specialist at one kind of task. Its header description is the trigger that tells an agent *when* the skill applies and when it does not. A skill *prepares* an agent to do the work; it does not by itself reach out and act.

**Tool** — the external thing a skill operates: software, a store, an API, a connector. Make.com, Railway, Python, Notion, Sage, Google Calendar. A tool *executes and returns a result*. The line between skill and tool is the cleanest test we have: if it runs and hands back an outcome, it is a tool; if it is instructions that know how to make the tool do the right thing at the right moment, it is a skill.

**Connector (MCP)** — the specific class of tool that plugs an agent into an external system (Gmail, Notion, QuickBooks). A connector gives *connection* portability — the same agent intent can be pointed at a different system — but it does **not** give *schema* portability. That second gap is closed by the canonical data model and the adapter pattern (later layers), not by the connector. This is Principle 4's caveat, restated precisely.

A fifth word worth pinning so it never causes confusion again: a **Plugin** is not a primitive at all. It is a *bundle* — a way to install several related skills and connectors in one action (the Design plugin installs design-critique, ux-copy, user-research and the rest together). Plugins are a packaging-and-distribution convenience, nothing more.

```
ROLE              →   SKILL                    →   TOOL
(identity,            (packaged know-how:           (the external thing
 accountability;      SKILL.md + scripts +          the skill drives;
 a Court seat)        reference files; knows        executes and returns)
                      how + WHEN to drive a tool)

Marshall (role)   →   "build daily reports"    →   Google Calendar, Word/PDF gen, the file store
                  →   "plan jobs from schedule"→   Gmail, the drive
                  →   "draft the invoice"      →   Sage (target) / Monzo (today)
```

### The other three folders an agent carries

A skill is only one of the four files that make up a complete agent. When Holly scaffolds a new agent (Marshall, Cody), she creates more than skills — and conflating those other folders with skills was part of the earlier fog. The full shape, following the four-file system already in the v0.3 appendix:

- **Context** — who the agent is, its remit, its split-brain configuration. This is Principle 4 made concrete: identity expressed as capability, not implementation.
- **Memory** — what the agent has learned, owned and written by the agent itself and reloaded each session, with every change recorded in an append-only log. This is *how* an agent learns safely under Principle 6: operational learning is self-written and audited retrospectively, while the one dangerous class — changes to a standard or to another agent — is proposed, never self-applied (the precise thing Cody did wrong). Specified in full in Agent Architecture — Memory.
- **Skills** — the folders of know-how this document is about.
- **Pipelines (the "Agents" file in the Hills naming)** — ordered runs that chain skills together in sequence, with human gates between them (see §4).

This document owns the Skills and Pipelines layers. Context and Memory belong to the agent-template/build methodology layer and are noted here only so the boundary is clear.

-----

## 2. Rule One — shared definition, singular ownership

This is the rule that makes the whole layer travel across deployments, and it is Principle 8 (template-and-fill) applied one level down, to capabilities instead of seats.

A skill has **one canonical definition**, written once. Every agent that holds that skill behaves identically, because they are all reading the same file. This is the consistency guarantee — the cure for divergent behaviour — and it is the entire reason the primitive exists.

But a skill is **mounted onto exactly one role per deployment.** Whoever holds it owns it, and ownership carries the permission to perform it. Ownership is singular and local to the deployment; definition is shared and universal.

The worked illustration is the knowledge-store curator. The skill "update and manage the library" is defined once. On a small deployment (Iain Jack/AHS, say) there is no Libby, so that skill is mounted on **Cyrus (CIO)** — he tends the store himself. On a larger deployment the load justifies a dedicated curator, so the *same* skill is mounted on **Libby (Curatrix)** instead, and Cyrus's responsibility changes from *doing it* to *managing her*. The skill did not change. Where it is mounted changed.

So: **definition is shared and consistent; ownership is singular and local.** A library of canonical skill definitions is Datavation IP; which seat carries each one is a per-deployment configuration decision.

### The extension for the dangerous case — permission is two-dimensional

"Ownership equals permission" is right for the common case but quietly assumes a skill is all-or-nothing: you either hold "manage the library" or you don't. The Cody-rewrote-Holly incident did not happen because Cody lacked a skill — he had ample building skill. It happened because he pointed a skill he legitimately held at the *wrong target* (editing Holly when he should only touch what he is briefed to touch). So permission needs a second dimension beyond *which* skills a role holds: *what each skill is allowed to act upon* — its scope of targets. This is flagged here as a required part of the guardrail model (§5) and is not yet fully specified. It is the single most important thing still to design.

-----

## 3. Rule Two — agent birth is a remounting, not a creation

The skeleton framed the agent-birth rule as a skill being *created* when a new sub-agent is born. That is not quite right, and the correction sharpens it.

The capability already existed — as a skill mounted on a senior seat. Birth is a **remounting**: the skill moves *down* from the senior seat onto a new, dedicated seat that now owns it, its identity, its accountability, and its own context and memory. The senior seat's own skill simultaneously **flips from execution to delegation** — Cyrus stops holding "curate the store" and starts holding "manage the agent who curates the store."

**The rule, restated:** an agent is born when a skill (or a cluster of related skills) mounted on a senior role grows heavy enough to deserve its own identity, accountability, and context — and when that happens, the skill is *remounted* onto the new agent and the parent's skill becomes a delegation skill. This is the precise mechanism behind the standing discipline that no agent gets built until a real problem demands it. The trigger to build Libby (Curatrix) is exactly this: when the curation load (contradiction-and-orphan health-checks, the Karpathy pattern) outgrows Cyrus carrying it as a side-skill.

What "heavy enough to graduate" means in measurable terms is left for §5 to define properly. The shape of the rule, though, is settled: birth = remounting + parent flips to delegation.

-----

## 4. Rule Three — sizing a skill by its autonomy seams

This is the rule the whole document hangs on, because it answers the one question that otherwise has no principled answer: *how big is a skill?* It was derived from Marshall's real daily-reporting workflow, which turned out to be not one skill but four, run at different times with a human standing between each.

**The sizing rule:** a skill is the largest chunk of work that runs to completion **without needing a human decision in the middle.** The moment a human has to look, approve, or correct before the next step can proceed, that is a skill boundary. Size a skill by its autonomy seams — not by file count, not by cleverness, not by how much it *could* technically do in one run.

This rule does two jobs with one idea. It tells you where to draw skill boundaries, *and* it keeps the system safe, because every boundary is a seam where a human can stand. A monolithic "do all my admin" skill would be both badly sized and unsafe — there would be nowhere to stand inside it. Good sizing and good safety are the same act.

### The two kinds of gate — the part that makes the map sell

The seams between skills are human gates, and they come in two kinds with **opposite lifecycles.** Labelling every gate as one or the other is mandatory, because they behave differently over time and they mean different things commercially.

A **capability gate** is *provisional.* A human stands here only because the tooling cannot yet do this step reliably. It carries an implied trigger for its own removal: when the capability arrives, the gate dissolves and two skills may merge into one. Example from Marshall: you currently hand-sort the job photos into order because no vision tool sorts them reliably — the day a good vision-sort skill exists, that gate is gone.

A **control gate** is *permanent.* A human stands here by design, regardless of how capable the tooling becomes. It is Principles 6 and 7 made physical — authority staying with Rex on the things that matter most. Example from Marshall: the invoice is reviewed before anything financial leaves, and that never changes, even after the Monzo-to-Sage migration lets the data flow straight through. The data automating does not retire the gate; the gate was never about capability.

Same seam in the workflow; one is waiting to be automated away, the other must never be.

**Why this is Datavation IP, not just tidiness.** When you map any client's workflow (Joanne, Iain Jack, anyone), you walk their process and tag every gate as capability or control. The capability gates become the **roadmap** — the visible backlog of what gets automated next as tooling matures, which is a maturity path the client is buying into. The control gates become the **governance story** — "here is where a human will always stand, by design, no matter how good this gets," which is the reassurance an SMB owner needs before letting agents near their business. The same map sells the ambition and the safety at once.

### Worked sizing — Marshall's daily reporting, fully typed

Four skills, run at different times, separated by typed gates:

1. **Plan the jobs from the Equans schedule.** An Equans email lands with an attachment a day or two ahead; it is saved to the drive; Marshall reads it and plots the jobs across the working days.
   *→ capability gate: you check the plotted jobs today; automatable later.*
2. **Build the daily property reports.** At the end of each working day, Marshall reads the photos, reads back the Google Calendar events with your notes, creates dated subdirectories, and drafts the property reports as Word documents.
   *→ capability gate: you sort photos into order and edit the docs; dissolves when reliable vision-sort exists.*
3. **Assemble and draft the completion email.** The reviewed reports are attached to a draft completion email back to Equans confirming the work is done.
   *→ lighter capability gate.*
4. **Draft the invoice and the TPG report.** From the same reports Marshall drafts the invoice — job summary, times worked, doors cut, other job detail — which is filed to the invoicing system (Monzo today, Sage in migration), and a report email goes to the TP group.
   *→ control gate: permanent. Nothing financial leaves without review, ever — even when Sage allows straight-through data flow.*

The seams are typed; the roadmap (gates 1–3) and the governance line (gate 4) both fall straight out of the typing.

### The gold standard — control gates enforced in infrastructure, not instructions

The Marshall test surfaced the strongest form a control gate can take, and it is now the standard to aim for. Marshall's email capability uses the Gmail `gmail.compose` OAuth scope, which can draft but **technically cannot send.** The human gate on "nothing financial or client-facing leaves without Austen" is therefore not a rule the agent is asked to honour — it is a thing the agent *physically cannot do* even if instructed to. The control gate lives in the tooling, not in the prompt.

This is the gold standard: **the best control gate is one the agent cannot cross even if it tried, because the capability to cross it was never granted at the infrastructure layer.** A control gate written only as an instruction ("always let a human review") is a weaker gate — it depends on the agent's compliance, which is exactly what failed in the Cody-rewrote-Holly incident. Where a control gate guards something that truly matters (money, sending, editing another agent), prefer to enforce it by *withholding the capability* — a missing scope, a read-only connector, a draft-only permission — over enforcing it by instruction. Instruction-level control gates are acceptable where infrastructure enforcement is impractical, but they are the fallback, not the target.

### §4a. Pipeline ownership across seats

The Marshall test showed that a real workflow is often **not single-seat.** Marshall builds the reports, but the Notion data sync is owned by Dex (CDO) and runs as `dex-tpg-notion-001` — because syncing job data into the system of record is genuinely a data-governance concern, not a reporting one. This is Rule Two (remounting) already happening in the wild: a data skill is mounted on the seat that should own it, not on the agent that happens to sit nearest the workflow.

That raises a question the sizing rule alone does not answer: when a pipeline spans several seats, *who owns the pipeline itself* — the ordered definition that says these skills run in this sequence with these gates between them? The rule:

**A pipeline is owned by the seat accountable for its outcome, even when the individual skills in it are owned by different seats.** The owning seat does not have to *perform* every step; it is answerable for the pipeline running correctly end to end, and it holds the delegation relationship to the other seats whose skills the pipeline calls. For the Marshall daily cycle, the outcome is a correct client deliverable, so the pipeline is owned by Marshall's seat; Marshall calls Dex's sync skill as a step, but Marshall is answerable for the cycle. Pipeline ownership follows *accountability for the outcome*, skill ownership follows *the nature of the capability*. They are allowed to differ, and naming both prevents the confusion of assuming the agent running the workflow owns every part of it.

### §4b. The Memory Audit is a canonical skill, not a Marshall quirk

Marshall already runs `marshall-weekly-reconcile` — a scheduled task whose entire job is to check whether the documentation still matches the live scripts and flag drift, documentation-only, never editing code. Look at what that is: it is a direct antibody to the fleet's **root disease** — duplication and divergence of truth with no single authoritative source. It was built by hand, in one corner, to solve a local problem, without being recognised as the general cure.

It must be promoted. **The Memory Audit — a scheduled check that an agent's description still matches its reality, surfacing drift for human review without self-editing — is a canonical skill that belongs in the shared library and should be mounted on every agent.** (Marshall's `marshall-weekly-reconcile` is the hand-built local instance that revealed the need; the canonical, fleet-wide form is named the Memory Audit to keep it distinct from data-sync reconciliation. See **Agent Architecture — Memory** for its full specification.) It is the operational mechanism by which the architecture documents stay *living* rather than rotting, which is exactly how Archy's ownership of the standards (see header) is actually enforced: not by Archy promising the docs are current, but by a Memory Audit that proves it on a schedule. The full specification of this skill — what it checks, how it reports, the human-review gate on any correction — lives in **Agent Architecture — Memory** (`Agent-Architecture-Memory-v0_2.md`), the third foundation, now complete.

-----

## 5. Still to design — the guardrail model (carried forward, sharpened)

If capabilities are explicit skills mounted on roles, autonomy becomes **grantable in units** rather than as a vague blanket. You do not give Cody "autonomy"; you give him a Make skill and a Railway skill and you withhold an "edit-another-agent" skill. The skills layer is where Principle 6 is enforced in practice — the rails are a list of which skills a role does and does not hold.

To build out next, in priority order:

1. **The two-dimensional permission model (§2 extension)** — the single most important open piece. Not just *which* skills a role holds, but *what targets each skill may act upon.* This is the precise gap the Cody incident exposed, and "withhold the architecture-editing skill" only fully works once scope-of-target is modelled.
2. **Granting, withholding, revoking** — the lifecycle of a skill on a role, and how that lifecycle is recorded.
3. **Autonomy level per skill** — how each skill records whether it runs unattended, runs-then-reports, or requires human-in-the-loop (the Principle 7 flag), and how the two gate types from §4 are encoded in the skill or pipeline definition.
4. **"Heavy enough to graduate" (§3)** — real, measurable criteria for when a skill remounts into its own agent.

-----

## 6. Tool ownership — multi-dimensional, as the org chart could not express

A single reporting line cannot express tool ownership, because ownership genuinely has several dimensions. A tool is shared infrastructure sitting *beneath* the roles, used via skills, owned and governed by different officers in different respects:

- **CTO (Archy)** owns tools *technically* — selection, integration, deprecation, the build.
- **CDO (Dex)** governs *what data* may live in a tool and under what rules — data governance, quality and compliance (the tool-facing slice of the CDO's full remit: enterprise data strategy + the DAMA-DMBOK data value chain, defined in Roles).
- **CIO (Cyrus)** owns the *information estate* the tools collectively form — the intellectual and structural view.
- **Any agent** may *use* a shared tool (read/write), subject to the skills it has been granted and the targets those skills may act on (§2 extension).

This is richer and truer than "X reports to Y," and it is why the knowledge store could never sit cleanly on the org chart.

-----

## 7. The tool register (seeded; to be populated)

A running catalogue of tools, what they are, who owns and governs them, and which skills drive them.

| Tool | Type | Used by (role / skill) | Tech owner | Governance | Notes |
|------|------|------------------------|------------|------------|-------|
| Knowledge store (Obsidian / Notion / Fabric) — "Tabularium" | Store | All agents (read/write) | CTO | CDO | Formerly mis-placed on the org chart. Curator = Libby (Curatrix), a future remounting per §3. |
| Make.com | Automation | Cody / Make skill | CTO | — | vs Railway — a live choice to document. |
| Railway | Hosting/deploy | Cody / Railway skill; Holly WhatsApp deployment | CTO | — | Trial expiry ~early July; GDPR US-West→EU-West migration outstanding. |
| Python | Runtime | Cody / Python skill; Marshall (PowerShell today) | CTO | — | |
| Google Calendar | Connector (MCP) | Marshall / "build daily reports" skill | CTO | — | Source of job notes read back into the reports. |
| Gmail / email | Connector | Marshall / "plan jobs" + "completion email" skills | CTO | — | Equans inbound; completion + TPG outbound. **`gmail.compose` scope only — cannot send. Infrastructure-enforced control gate (§4 gold standard).** |
| Word/PDF generation | Document tool | Marshall / "build daily reports" skill | CTO | — | The property report artefacts. |
| Monzo (today) → Sage (target) | Invoicing | Marshall / "draft invoice" skill | CTO | CDO | Migration in progress; straight-through data flow possible post-migration, but the control gate (§4) remains. |
| Notion (TPG Jobs DB) | Connector (MCP) | **Dex (CDO)** / "job-data sync" skill (`dex-tpg-notion-001`) | CTO | CDO | System of record for jobs. Owned by the CDO, not Marshall — confirms §4a: skill ownership follows the nature of the capability (data governance), not the workflow it sits in. |
| *(Collibra vs Purview, etc.)* | Governance | *(future)* | CTO | CDO | Future tool decisions that must not clutter the Court. |

-----

## 8. Where the knowledge-store discipline lives

The Karpathy `raw`/`wiki` discipline (a `raw` folder the agent never edits, a `wiki` folder the human never touches) is the operating rule for the Tabularium tool, and the periodic contradiction-and-orphan health-check is the **birth trigger** for Libby (Curatrix) per §3. Both are recorded here, against the tool, not on the Court. Full build-out of the monitoring sits with the build methodology layer.

-----

## 9. Status of the build-out

**Done and ratified in v0.3:**
1. §§1–4 — the four primitives and the three rules — ratified.
2. Framework tested against the real Marshall workflow (architecture doc + TPG/Equans SOP). It held; the sizing rule and gate types were independently confirmed by a workflow that had already self-organised along them.
3. One upgrade folded in: infrastructure-enforced control gates (§4 gold standard).
4. Two gaps closed: pipeline ownership across seats (§4a) and the Memory Audit as a canonical skill (§4b).
5. Ownership of the standards assigned: Archy (CTO), curated by Libby, coherence held by Cyrus (header).

**Still open — carried to the guardrail build and the next foundation (§5):**
1. The two-dimensional permission model (§5.1) — scope-of-target. Highest-priority open piece; the precise gap the Cody incident exposed.
2. Autonomy levels and gate-encoding (§5.3) — how capability vs control gates, including the infrastructure-enforced kind, are written into a skill or pipeline file.
3. "Heavy enough to graduate" (§5.4) — measurable remounting criteria.
4. Write the first real library entry: the **Memory Audit skill** (§4b), specified in **Agent Architecture — Memory** — the bridge into the third foundation, now complete.

**The third foundation document — Agent Architecture — Memory (now complete).** Two independent tests pointed at the same missing piece: the Hills harness comparison flagged that Memory is the engine that makes the whole system compound and we held only the principle, not the routine; and the Marshall test showed a validity check already running by hand as the antibody to the root disease. That document tells Cody *how an agent learns and how truth stays single* — the exact safeguard against the failure where Cody rewrote Holly. It is the prerequisite for the Cody-rebuilds-Holly work, and the third and final foundation needed before that rebuild. The scaling layers (canonical data model, adapter pattern, comms portability) are real and sequenced but are **not** prerequisites for rebuilding the kernel.

-----

*v0.3 ratifies the framework after testing it against the real Marshall workflow. It is the second foundation after the Court: the layer where capability and safety physically live. It now carries the authority the Court already holds. The third foundation, Agent Architecture — Memory, is complete — the engine that makes every layer above compound, and the safeguard that keeps truth single.*

-----

## Appendix A — Lineage and adopted standards

These standards are not invented here; they are adopted from named external work, recorded so the provenance is never lost and so the harness remains legible to others as a recognised pattern.

- **Andrej Karpathy** — context engineering; the `raw`/`wiki` second-brain pattern and the periodic contradiction/orphan/missing-page health check (the basis of the Tabularium discipline and Libby's birth trigger). GitHub gist, April 2026.
- **Mitchell Hashimoto** — coined "harness" / harness engineering (2026): the model plus tools, memory, guardrails and specialists. The word this whole architecture now uses for itself.
- **Boris Cherny** — runs Claude Code at Anthropic; his `CLAUDE.md` is the closest thing to a community best-practice base template, on which agent personalisation/context files sit.
- **Greg Isenberg** — popularised the four-file framing (Context / Memory / Skills / Agents) that the agent template follows.
- **Charlie Hills / MarTech AI** — the practitioner who assembled the above into a teachable method; the three articles (first agent, second brain, harness) against which this architecture was benchmarked. See `Hills-Harness-Comparison.md`.
- **Anthropic** — the Skill primitive (`SKILL.md` = name + when-to-use description + bundled scripts/reference files), Plugins as bundles, MCP connectors, and Routines (cloud-scheduled skills). The primitives this document adopts wholesale.

The harness lineage in one line: prompt engineering (≈2022–24) → context engineering (Karpathy, ≈2024–25) → harness engineering (Hashimoto, 2026). Datavation builds, deploys and tunes personal AI **harnesses** to that standard, with one addition the standard does not yet have: **typed gates** (capability vs control), the distinction that lets a real small business know exactly where a human will always stand.

---

## Addendum — Fleet Permissions Baseline (ratified 2026-07-02)

Every seat shipped `permissions.allow = []`, so *every* action fired a prompt — rails were honoured but **freedom within the rails was never switched on at the infra layer**. This baseline grants the safe, reversible, routine capabilities to every seat up front, so prompts fire only where they matter. It is the practical expression of "freedom within the rails" for the **capability** gate; it changes **no control gate**.

**Granted fleet-wide (the baseline allowlist):**
1. **Read-only tools** — `Read`, `Glob`, `Grep` across the fleet root (Canon, a peer's files, shared artifacts). Reading is safe by definition.
2. **The Notion board MCP** — read the Decision Board; write the seat's **own** cards / Output Records.
3. **Self-writes only** — each seat writes within **its own** `Agents\<seat>\` tree (memory, output).
4. **Shared work directory** — read/write `Agent-Fleet\Shared\` (collaborative deliverables; see Filing Standard Shared-Artifact addendum).

**Stays OFF the allowlist (control gates — infra-enforced, never promptable-away):** writing into **another agent's** folder/identity/memory/context; **money, send** (email/WhatsApp/publish); **promote-to-live**; anything irreversible or outward-facing.

**Coordination ruling (ratified):** agents coordinate through the **board (async)** — read a peer's work to answer a question; write a card to ask a peer to do/decide. **Not** via live session-to-session chat (`send_message` / `search_session_transcripts`), which stays supervised-only.

**Rollout & gate:** Cody rolls the allowlist into every seat's `settings.json`; **Rex promotes** (peer-file edit = human hand); verify per seat. A seat may **not** self-grant this — the baseline is a deliberate Rex-authorised change (an attempted self-apply this session was correctly blocked by the auto-mode classifier — the gate working). *Provenance: `Agents/Archy/output/proposals/2026-07-02-Permissions-Baseline-Standard-PROPOSAL.md`.*
