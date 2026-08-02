---
id: Agent-Library-Filing-Standard-v0_1
title: Agent Library — Filing Standard
domain: architecture
trust_class: canon
owner_seat: Architectus (Archy)
version: v0.5
status: ratified
date: 2026-07-09
provenance: Austen King + Claude, scoping sessions 11-12 June 2026
labels: [tabularium, library, filing, metadata, catalogue, libby, template]
---

# Agent Library — Filing Standard v0.1

**Status:** Ratified by Austen King, 12 June 2026. Canon document. Owned by Archy (Architectus); operated by Libby (Curatrix) on her birth; curated manually by Austen until then.

This document practises its own convention: the front matter above is the master metadata record for this file.

---

## 1. The Tabularium

The Tabularium is the **library institution** of a deployment — the records hall, in the Roman sense — under the stewardship of Libby (Curatrix). It contains three wings. Every document in the building carries exactly **one trust class**, and the classes never blur:

- **Canon** — the fleet's **authoritative library**: what the fleet treats as binding and refers to as truth. Two sub-classes (see §9 for who writes them): **standards** (architecture, the method, the advisory standard — Datavation IP, deliberately small, changed only by *ratification* — Archy proposes, Rex ratifies) and **curated content** (this deployment's authoritative reference — advisor profiles, registers — fleet-curated under Archy/Libby oversight, audited in the library reconcile, **not** per-edit ratified). Agents read Canon; **humans do not hand-edit it** — they ratify standards and request curation.
- **Vault** — **internal-origin** working knowledge. Career and corporate documents, engagement harvests, project outputs, intake (digests, road captures), and knowledge promoted from agent memories. Written continuously by the fleet, curated, never "ratified."
- **Reference** — **external-origin** material with provenance, **read-only**. Influences (the Board Advisors' sources), articles, sector regulations, third-party engagement documents. Reference is *mined, never edited*: extractions are rewritten in our own words as new artefacts — Vault, or Canon curated content where they become fleet doctrine (e.g. advisor profiles) — with citation preserved.

> **Reference vs Vault** differ by **origin**: Reference is someone else's work (mined, cited); Vault is our own output. Both are fleet-managed; the line is provenance and must not blur.

**The Tabularium is not agent memory.** Memory is seat-local and per-agent, governed by the Memory Architecture. The bridge runs one way and deliberately: reusable knowledge is *promoted* from seat memory into the Vault by curation, never poured in raw.

## 2. Organising spine: domain, never agent

Canon (and the library generally) is filed **by functional domain, not by agent**. Rationale: agents are born by remounting — a skill moves down a line to a new seat. Filing by agent breaks on every birth; filing by domain survives all births, because births happen *within* a line. The functions are stable; the agents occupying them are not.

Domains follow the court's lines: `architecture`, `engineering`, `data`, `strategy`, `brand`, `commercial`, `operations`, `customer`, `risk`, `finance`. A domain **earns its shelf when its first document arrives** — no empty scaffolding.

## 3. Directory skeleton (template layer)

```
tabularium/
  _catalogue.md            <- generated view; never hand-edited
  canon/
    architecture/
    engineering/
    brand/
    ...                    <- one folder per court line, on first document
  vault/
    career/
    engagements/<name>/
    projects/<name>/
    intake/
    agent-knowledge/
  reference/
    influences/<thinker>/
    standards/<scheme>/
    engagements/<name>/
```

This skeleton, the naming convention, and the metadata schema are **template layer — Datavation IP**, identical in every deployment. The *contents* are **instance layer** and belong to the deployment (per the tenancy & detachability requirement, logged 12 June). A white-label client receives the empty building and fills it; Rex's institutional knowledge stays Rex's.

## 4. File naming *(v0.2 — version-less live filenames)*

`Function-Descriptor.md` — PascalCase words joined by hyphens, **no version number in the live filename**. The **function prefix groups related documents**; the descriptor names the specific document. The friendly name of an agent never appears in a filename — a seat is identified by its function (e.g. `Agent-Strategy-`), not by 'Hobbs'.

**The version and date live INSIDE the document** (front matter and header), never in the live filename. This is deliberate: embedding the version in the filename meant every bump broke every cross-reference that named the file — a fleet-wide cascade, including into peer agents' context files that the architect may not edit. Version-less live names end that cascade. *(Lesson banked 2026-06-25, Roles v0.3→v0.4 bump.)*

**On supersession (the only place a version enters a filename):** when a document is bumped, the superseded copy is moved to `_version-history/` and **only then** gains a version + retire-date suffix — e.g. `Agent-Architecture-Roles-v0_3-retired-2026-06-25.md`. The version number thus lives in a filename **only in history**, for provenance. The live folder shows one current file per document, version-less.

**Cross-references** (in any document, context file, or register) use the **version-less** name — `Agent-Architecture-Roles` — so a bump never breaks a reference again.

Examples (live): `Agent-Architecture-Roles.md`, `Agent-Architecture-Capability.md`, `Agent-Library-Filing-Standard.md`. Status (ratified/draft) lives in the document header, never in the filename.

**Migration:** existing versioned canon files migrate to version-less names progressively. **Roles migrated 2026-06-25.** The remaining canon files (Capability, Memory, Filing Standard, Seat-Definition, Roster-and-Name-Bank) migrate in one coordinated pass, run together with the peer-agent context-reference updates so the rename and the reference-fix happen as a single change.

## 5. Metadata: front matter is master

Every library document opens with a front-matter block carrying: `id`, `title`, `domain`, `trust_class`, `owner_seat`, `version`, `status`, `date`, `provenance`, `labels`. The metadata **lives in the document** — one master. The catalogue (`_catalogue.md`) is a **generated view** built from front matter. It is never hand-edited; a hand-edited index is a second master waiting to drift.

## 6. Libby's three duties (Curatrix)

1. **Catalogue** — regenerate `_catalogue.md` from front matter; maintain the labels vocabulary.
2. **Enforce filing** — agents *submit* documents to the correct wing with correct front matter; Libby audits placement and metadata.
3. **Reconcile** — run the canonical reconcile skill on the library itself, periodically: catalogue vs front matter vs files on disk. Flag orphans, missing metadata, and trust-class violations (e.g., an unratified draft squatting in Canon).

Until Libby is born, Austen performs these duties manually and minimally; the convention is followed from today regardless.

## 7. The four-way split for any agent (including outliers)

Where does an agent's "stuff" go? Always the same answer, ghostwriter included:

- **Standards** it must follow → `canon/<domain>/`
- **Finished outputs** worth keeping → `vault/projects/` or `vault/engagements/`
- **Drafts and work-in-progress** → the workspace, **never** the library. The Tabularium holds records, not scribbles.
- **Memory** → seat-local, per the Memory Architecture.

Findability follows: any agent or human can predict where a thing lives without asking.

## 8. Open items

- Physical platform for the library (one-master rule; current OneDrive/Google Drive/Obsidian split violates it): scoped **Archy ruling** on agent-access facts, then Cody migration. This standard is platform-agnostic by design.
- Catalogue generation tooling: manual until Libby; a Cody task at her birth.
- Labels vocabulary: seeded by first filings; Libby curates.

---

## 9. Rule of the Road — write ownership & the Drop Zone *(v0.3, ratified 2026-06-25)*

The library has **two axes**: *trust class* (Canon / Vault / Reference — what kind of truth) and *write ownership* (who may write). §1 fixed the first; this section fixes the second — because the structure must be **managed by the fleet, not hand-edited by the human**.

### The Drop Zone (human-owned)
`Oz Files\` is the **Drop Zone** — Austen's personal WIP area ("Oz" is Rex). He drops raw material here (PDFs, transcripts, articles, emails, notes) and refers an agent to it — *"review this, fold it into the marketing advisor."* The fleet then curates what's needed into the Tabularium. The Drop Zone is **not** part of the library; nothing in it is authoritative until the fleet works it up. Austen writes here freely.

Structure: **`Oz Files\For-Fleet\`** is the queue Austen drops into for the fleet to pick up; the fleet moves a source into **`Oz Files\For-Fleet\Processed\`** once it has been worked up, so Austen can see it was actioned.

**The Tabularium holds markdown only — never the original binary.** A PDF, transcript, or doc is worked up into a markdown summary/profile *inside* the Tabularium that **cites the original** (filename + that it lives in `Oz Files\For-Fleet\Processed\`), giving a lineage trail. The binary itself never enters the library.

### The Tabularium is fleet-managed
**Humans do not hand-edit the Tabularium.** They **ratify** Canon standards and **request** curation; they do not author or edit library files directly. The library is managed by three seats:
- **Libby (Curatrix)** — filing, cataloguing, reconciliation *(Austen/Archy perform her duties until she is born)*.
- **Holly (Praetor)** — coordination of what gets promoted and when.
- **Archy (Architectus)** — architecture oversight and the **ratification gate** for standards.

Other agents **read** Canon and follow it; they curate their **own** memory and their **assigned** advisor profiles within these rules.

### Binaries never enter the Tabularium
The original source (PDF, transcript) stays in `Oz Files\For-Fleet\` (then `Processed\`). The fleet produces a **markdown** summary in `reference/influences/<person>/` that cites the original for lineage. Austen does **not** place binaries in the Tabularium, nor create or edit the distilled summaries, advisor profiles, or any Canon standard — that is fleet work.

### Who writes where
| Location | Who writes | How |
|---|---|---|
| `Oz Files\For-Fleet\` (Drop Zone) | **Human** | Freely — raw drops (incl. binaries), "review this" |
| `reference/` (markdown summaries only) | Fleet (Libby / assigned agent) | Mined from the source; **markdown only**, cites the original in Oz Files (lineage) |
| `canon/` standards | Fleet via **ratification** | Archy proposes → **Rex ratifies** |
| `canon/advisory/` profiles & registers | Fleet (Libby / assigned agent), Archy oversight | Curated; **audited**, not per-edit ratified |
| `vault/` outputs & records | Fleet | Written continuously |
| agent memory | **the owning agent only** | Live self-write (Memory Architecture) |

The discipline in one line: **the human drops and ratifies; the fleet curates and files; nobody hand-edits another's managed space.**

---

## Addendum — Shared-Artifact Rule (ratified 2026-07-02)

Two different things were being mixed inside `Agents\<seat>\output\`: an agent's **private working output** and **shared valuable artifacts** others use or build on. The rule that separates them:

- **Private-to-the-agent → stays in `Agents\<seat>\`.** Drafts, working notes, the seat's own memory/output, commission files it authored. Single-writer; nobody else writes these.
- **Shared / collaborative artifact → graduates to `Agent-Fleet\Shared\`.** Anything meant to be **used, edited, or built on by another agent or by Rex** — presentations, spreadsheets, client reports, dashboards.

**Test:** *"Will another agent or Rex need to open, edit, or build on this?"* Yes → `Shared\`. No → the agent's own tree.

`Agent-Fleet\Shared\` is the live collaborative work surface and **the one place multiple agents are permitted to write** (Capability Permissions-Baseline item 4) — which is why cross-agent write access is granted there and nowhere inside another agent's folder. It is distinct from the Tabularium (ratified/curated library material); a finished artifact that becomes durable reference still graduates onward into the appropriate Tabularium wing. *Provenance: `Agents/Archy/output/proposals/2026-07-02-Shared-Artifact-Filing-Rule-PROPOSAL.md`.*

---

## Addendum — Standard Output-Tree Subfolders (ratified 2026-07-06)

Every agent's private working output uses the **same subfolder set** under `Agents\<seat>\output\` — created on first use, not scaffolded empty, and never left loose in the `output\` root:

- **`commissions\`** — a brief this agent is handing to another agent to build (non-architecture-class; recipient reads/builds from it in place).
- **`proposals\`** — an architecture-touching proposal awaiting ratification (a standard, another agent's identity/context, shared IP) — held here per the Memory Architecture's PROPOSED discipline until Rex rules. Also the right home for **cross-agent briefs raised for Archy's and/or Cody's review** — a brief for review is a proposal, not a finished commission.
- **`reviews\`** — this agent's own finished review/analysis output.
- **`snapshots\`** — point-in-time exports (HTML/board captures) kept for reference.
- **`logs\`** — routine/session logs.
- Drafts and true scratch WIP that aren't yet ready to be *any* of the above stay in the agent's own workspace (e.g. a `design\` working folder) — never the library, per §7.

**Rationale:** this was previously followed inconsistently — Archy's own tree carried the full set (codified operationally, `output/README.md`, 2026-07-05) while other seats used ad hoc top-level folders (e.g. a bare `proposals\` sibling to `context\`/`routines\`, not under `output\`). One set, applied fleet-wide, means any agent or Rex can predict where a thing lives without asking — the same findability goal as §7, extended from the library into each seat's own tree. *Provenance: Archy memory MEM-045; ratified by Rex 2026-07-06, extending the 2026-07-05 single-seat codification to the whole fleet.*

---

## Addendum — Brief → Design Spec → Build Spec pipeline & brief lifecycle (ratified 2026-07-09)

Establishes the standing path a **brief** travels from Rex's hand to a build, and how a brief is retired once actioned — so Rex always knows, at a glance, that a handover has been picked up and what it produced.

**The pipeline — three artifacts, three owners:**

1. **Brief** — *Rex authors.* The *what* and *why*, plus the constraints the build must not break. Lives in `Oz Files\Briefs\` (Drop Zone; human territory, per §9).
2. **Technical Design Specification** — *Archy authors.* The *how* at design level: architecture, components, interfaces, decisions locked, acceptance criteria. Lives in **`Oz Files\Design\`**. This is Archy's deliverable from reading a brief. It is **not** a "consolidated brief" — a brief is Rex's artifact, a design spec is Archy's.
3. **Build Specification** — *Cody authors.* The *build*: file layout, libraries, exact paths/commands, schema. Cody writes it **from the TDS**, builds in `Builds\`, **Rex promotes**.

> `Brief (Rex) → Technical Design Spec (Archy · Oz Files\Design\) → Build Spec (Cody · Builds\) → build → Rex promotes.`

**Brief lifecycle — the processed stamp (so a handover is visibly picked up):**
When Archy has read a brief and written its Design Spec, the brief is:
- **stamped at the very top** with a one-line processed header — *read by whom, date, and which Design Spec resulted*;
- **moved to `Oz Files\Briefs\_processed\`**, renamed with `_PROCESSED-<YYYY-MM-DD>` appended.

A brief sitting in `Briefs\` means *awaiting Archy*; the same brief, stamped, in `_processed\` means *actioned — design spec written, over to Cody*. Rex never has to ask whether a handover landed. This mirrors §9's Drop-Zone "moved to `Processed\` once worked up" discipline, applied to the brief artifact specifically.

*Provenance: Rex directive + Archy execution, 2026-07-09 — first run was the Voice Agent Engine consolidation. Extends §9 (Drop Zone) and the 2026-07-06 output-tree addendum.*
