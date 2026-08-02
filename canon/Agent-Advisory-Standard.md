---
id: Agent-Advisory-Standard
title: Agent Advisory — Standard (Board Advisors)
domain: architecture
trust_class: canon
owner_seat: Architectus (Archy)
version: v0.1
status: ratified
date: 2026-06-25
provenance: Austen King + Archy, advisory-layer design session 25 June 2026
labels: [advisory, board-advisors, influences, governance, reference, vault, template-and-fill]
---

# Agent Advisory — Standard (Board Advisors) v0.1

**Status:** Ratified by Austen King, 25 June 2026. Canon document. Owned by Archy (Architectus).
*(Live filename is version-less per Filing Standard §4; this is v0.1, dated 2026-06-25.)*

This standard defines the **advisory layer**: how the Court's officers draw on the
thinking of real, named experts without that thinking being re-explained every session.

---

## 1. Two things that must never be confused

- **Board Members** — the Court of Rex officers (Holly, Hobbs, Archy, …). They **execute**
  and hold operational accountability. Defined in `Agent-Architecture-Roles`.
- **Board Advisors** — real, named people (Daniel Priestley, Alex Hormozi, Jeremy
  Connell-Waite, Charlie Hills, …) whose published thinking has influenced Austen. They
  **inform**; they hold no accountability and execute nothing. Defined here.

A Board Advisor gives a seat an opinion, an approach, and a way of behaving — so Austen
does not have to keep saying "think about this the way Priestley would." Advisors are
consulted *by* officers (notably Hobbs for strategy and Victor for governance); they do
not replace those seats.

---

## 2. The ruling that keeps it clean (Austen, 2026-06-25)

The risk with advisors is the same one that bites everywhere: the same thing living in
several places at different levels of authority. The ruling:

1. **One advisor = one profile = one location.** Each advisor is a single profile file
   in `canon/advisory/`. There is exactly one object per advisor. An agent that wants
   "the Priestley advisor" looks in exactly one place.
2. **Type lives in the file header, never in the filename or the directory.** An advisor's
   class is a front-matter field — `advisor_class: [influence]`, `[governance]`, or both.
   It is **not** encoded as a filename suffix and **not** split into separate folders.
   This is deliberate: an advisor can be *both* influence and governance, and splitting by
   type would force one advisor into two homes — the exact mess we are avoiding.
3. **Degree of authority is carried by `advisor_class` + the assignment, not by location.**
   A governance-class rule is authoritative; an influence-class view is soft counsel. Both
   sit in the same folder; what differs is the field, not the address.

> The agent's single lookup point is `canon/advisory/`. The raw source material in
> `reference/influences/` is **provenance only** — the agent loads the *profile*, never the
> raw sources.

---

## 3. The three layers

| Layer | Trust class | Location | What it is |
|---|---|---|---|
| **The standard** *(this doc)* | Canon | `canon/architecture/Agent-Advisory-Standard.md` | The system: schema, classes, the link mechanism, the portability rule. Datavation IP. |
| **The sources** | Reference | `reference/influences/<person>/` | Raw external material with provenance — the books, talks, articles. Read-only; mined, never edited. |
| **The profiles** | Canon *(curated content)* | `canon/advisory/<person>.md` | The distilled, usable advisor an agent loads: how they think, how to apply it, citing the sources. Instance-local; fleet-curated, not per-edit ratified. |

Three locations, three distinct jobs — but an **agent only ever reads the profiles wing**.
Sources back the profile; the standard governs the system.

---

## 4. The two advisor classes

- **`influence`** — soft guidance. Shapes approach, opinion, framing, personality. The seat
  is *informed* by it and may exercise judgement. (e.g. Priestley's "income follows assets";
  Hormozi on offers.)
- **`governance`** — a rule the seat must **check and respect**. (e.g. the WhatsApp AI policy
  constraints on any WhatsApp-connected agent.) Where a governance advisor encodes a **hard**
  rule, the rule is also expressed as a Canon constraint and the profile cross-links to it —
  the profile explains the thinking; the Canon constraint enforces it. Soft governance (a
  best-practice lean) may live in the profile alone.

An advisor may carry **both** classes (`advisor_class: [influence, governance]`).

---

## 5. The link mechanism (Austen's one-line rule)

An agent's `CLAUDE.md` does **not** carry advisory content. It carries a **single pointer
line** instructing it, on load, to consult its advisory assignment. The assignment — which
advisors this seat draws on — lives outside the identity file, in the instance assignment
register (`canon/advisory/_advisor-assignments.md`). Each assignment resolves to a profile.

```
CLAUDE.md (one line):  On load, consult your Board Advisors — see
                       Tabularium\Canon\Advisory\_advisor-assignments.md for this seat.
```

This keeps identity files lean and lets advisors be reassigned without touching a seat's
identity. **Adding the pointer line to a peer agent's CLAUDE.md is a peer-context edit** —
only that agent or Rex may make it (the architect proposes; he does not edit peers). Archy's
own CLAUDE.md carries the reference implementation.

---

## 6. Portability — Principle 8 applied to influence

The advisor *slot* is template (Datavation IP, identical in every deployment); the *actual
advisors* are instance-local. Rex/Datavation fill the marketing slot with Hormozi and
Priestley; an AHS/Iain-Jack deployment fills the same slots with **his** heating-engineering
authorities. The standard and the empty structure ship with every deployment; the named
advisors and their profiles belong to the deployment. This is Principle 8 (template-and-fill)
applied to influence and personality, exactly as it already applies to data and knowledge.

The assignment register and the profiles are therefore **instance content within Canon** —
fleet-curated, not per-edit ratified (Filing Standard §9) — distinct from the **template
standards** (this doc), which are Datavation IP and ship to every deployment. Only the
standard is template; the profiles are this deployment's.

---

## 7. Profile schema

Every `canon/advisory/<person>.md` opens with front matter:

```yaml
id: advisor-<person>
title: <Person> — Board Advisor Profile
advisor_class: [influence]            # influence | governance | both
domains: [strategy, marketing]        # which court lines this advisor serves
serves_seats: [Hobbs, Mason, Oscar]   # friendly names of assigned seats
sources: reference/influences/<person>/   # provenance backing this profile
status: active
date: <YYYY-MM-DD>
```

Body: **How they think** (the principles, in our words) · **How to apply it here** (the
seat-facing instruction — what to actually do differently) · **Cautions** (where the
advisor's frame over-reaches or sells something) · **Citations** (back to the sources wing).

---

## 8. How an advisor comes to exist (promotion flow)

1. Austen drops source material into the **Drop Zone** (Oz Files) or names it (a book, talk, article) — see Filing Standard §9.
2. The raw material is filed to `reference/influences/<person>/` with provenance.
3. It is **distilled** — mined and rewritten in our words — into a `canon/advisory/<person>.md`
   profile (never a raw paste; Reference is mined, not copied — Filing Standard §1).
4. The advisor is **assigned** to one or more seats in `_advisor-assignments.md`.
5. The seat consults it on load via its one-line pointer.

Austen can say "look at this article, fold it into the marketing advisor," and the relevant
agent updates its advisor profile — operational curation, not an architecture change.

---

## 9. What advisors do NOT do

- They do not execute, decide, or hold accountability — they inform officers who do.
- They do not replace Hobbs (strategy) or Victor (governance) — those seats *consult* them.
- A soft `influence` advisor never overrides a Canon constraint or a ratified standard.
- An advisor profile is not memory: it is shared, assigned reference, not the seat's own
  live self-written memory.

---

*Canon. Ratified by Austen King, 25 June 2026. Owned by Archy (Architectus).*
*Companion instance artefacts: `canon/advisory/` (profiles + `_advisor-assignments.md`).*
*Next review: at next Memory Audit, or when the first partner-fleet deployment fills the advisor slots.*
