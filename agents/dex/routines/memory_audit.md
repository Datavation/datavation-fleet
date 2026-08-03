# Routine — Memory Audit (Dex)
*Per Agent Architecture — Memory v0.2 §5. Weekly. Read-only. Human-gated. Never self-resolves.*

**Trigger:** "memory audit", or on the weekly schedule.

**What it is:** the retrospective governance the live-write memory model depends on. It reviews the change log and sweeps the canonical store. It is **read-only** with respect to `memory.md` and `memory_log.md` — it surfaces findings; Austen decides. It is NOT data reconciliation (that word belongs to Marshall's Calendar↔Notion sync alone), and it is NOT a review of the Knowledge Map or wiki (that is Libby's library-reconcile — my vault is read-only to me).

---

## Part A — Review the log (`memory_log.md` since the last run)

For each **DONE** entry (operational self-writes):
- Was it sound? Recommend one of: **confirm** (stands), **amend** (needs revision), **roll back** (revert to the `Previous:` state the log captured).

For each **PROPOSED** entry (architecture-touching, not self-applied):
- Surface it for Austen to **ratify** (then write to `memory.md`), **revise**, or **reject**.
- High-stakes proposals: note that Court counsel applies before the ruling — architecture decisions go to Archy (CTO) for counsel; Austen makes the final call.

## Part B — Sweep the store (`memory.md`)

For each existing entry, check three things:
1. **Staleness** — is it still true? Has the tool, document, path, node, alias, or workflow it refers to changed since it was written?
2. **Contradiction** — does it conflict with another entry? The more recent one is not automatically right; surface both.
3. **Orphaning** — does it refer to a skill, tool, document, path, Knowledge Map node, or agent that no longer exists?

## Part C — Fleet signal

If the same change appears in more than one agent's `memory_log.md` in the same cycle, flag it as a candidate for **elevation to the Tabularium** (itself an architecture-class proposal).

---

## Output

A findings list to Austen — each flagged item with its reason and the recommended action. Write the findings to `output/logs/` dated.

**Do not edit `memory.md` or `memory_log.md` during the audit.** Any write that follows a ruling (a ratified proposal, a rollback, an amendment, a retirement) is a deliberate act taken **after** the audit, each appended to `memory_log.md` as its own entry.

## My own note

My owned working knowledge is narrow: my **retrieval quirks** (an alias that over- or under-fires in practice, a synonym the matcher misses that I bridge by eye), my **voice register** calibration, and **intake candidates** I've spotted where the vault is thin. Most of what I learn that touches *another seat, a standard, or shared IP* — including anything about the Knowledge Map, the taxonomy, or the wiki — is architecture-class and reaches `memory.md` only as a ratified proposal, or goes to Libby as an intake proposal. When in doubt, I propose. Erring toward proposing is safe; erring toward self-writing is the failure mode the architecture exists to prevent.
