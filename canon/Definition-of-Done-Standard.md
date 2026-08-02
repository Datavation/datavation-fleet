---
title: Definition of Done Standard
version: v0.1
status: ratified
date: 2026-07-18
owner: Archy (Architectus, CTO)
governs: what "done" means for any fleet work item — a checkable rubric, not a claim
sits-under: Agent-Orchestration-and-Work-Tracking.md; consumed by Agent-Routine-Standard-v0_1 verification routines
labels: [architecture, definition-of-done, rubric, verification, eval-rubric, honest-completion]
---

# Definition of Done Standard — v0.1

**Ratified by Rex 2026-07-18.** Authored by Cody under Build-Spec-Cody-Verification-Loop-v0_1
(Rex, 2026-07-18); promoted to Canon by Rex the same day.

**Scope of this version (deliberate):** only the rubric-format section (§1) and one worked
example (§2) are filled — the minimum the Cody Verification Loop needs to fire. The full
standard (per-work-type criteria libraries, board wiring, the DoD-empty transition block,
Tessa-as-oracle) is a dedicated session with Austen and remains Archy's later build.

---

## 1. The rubric format — "done" as a checkable object

Every work item carries, **before build starts**, a Definition of Done written as a list of
**binary, inspection-verifiable criteria**. Not prose intent — checkable facts. Each criterion
must be answerable PASS/FAIL by **opening a file, running a command, or reading a log**.

The required form (each line one criterion, one check):

- `File exists at <path>` ✓/✗
- `Running <command> exits 0 and prints <expected>` ✓/✗
- `<function> returns <value> for input <x>` ✓/✗
- `Routine file has explicit trigger, action, and output-contract sections` ✓/✗

Rules of the form:

1. **Binary.** Each criterion resolves to exactly PASS or FAIL. No "mostly", no percentages,
   no "improved".
2. **Inspection-verifiable.** The check names its evidence source — a path to open, a command
   to run, a log to read. A criterion whose truth can only be asserted from memory or
   intention is malformed.
3. **Rewrite until checkable.** If a criterion cannot be phrased as an inspectable check, the
   item is **not done-able as scoped** — the criterion (or the scope) must be rewritten until
   it can. "Make the dashboard better" is not done-able; "dashboard renders the Blocked
   column from live board data — verified by loading <url> and reading the column header +
   ≥1 row" is.
4. **The rubric precedes the build.** Writing it after the fact invites criteria shaped to
   what was built rather than what was commissioned.
5. **Verification is against actual state.** A verifier (human, or the building agent's own
   session-end routine) marks PASS only from a check **performed that run** — opening the
   file, running the command, reading the log. Evidence is recorded beside each verdict.
   Unverifiable never rounds up to PASS.

This is the eval-rubric discipline (HyperAgent pattern): the rubric makes "done" an object an
agent can be **measured against**, rather than a claim it can assert.

## 2. Worked example

**Work item:** *session-end verification routine for Cody* (the first item verified under
this standard — recursion intended).

| # | Criterion | Check performed |
|---|---|---|
| 1 | `File exists at Agents\Cody\routines\cody-session-end-verify.md` | `Test-Path` the exact path → True/False |
| 2 | Routine file has explicit trigger, action (steps), and output-contract sections | Open the file; confirm the `## Trigger`, `## Steps`, `## Output Contract` headings are present and non-empty |
| 3 | The routine's steps require checking each criterion against actual file/command/log state and recording the evidence inspected | Open the file; confirm the step text forbids PASS from memory/intention and requires evidence beside each verdict |
| 4 | The routine is invocable in an attended session with no headless-scheduler dependency | Run it once, live, against a real work item; confirm a completion report in the declared output-contract shape was produced and filed |

Each row is binary, names its evidence, and can be executed by any verifier — the building
agent, a future QA oracle, or Austen — with identical results. That interchangeability is the
point: "done" stops depending on who is asked.

## 3. Not yet in this version

Criteria libraries per work type · Decision Board wiring (DoD-empty transition block) ·
separate-oracle verification (Tessa) · the scheduled escalation ladder. Named here so this
version is honest about being the format core, not the whole standard.

## Change log
| Date | Version | Change |
|---|---|---|
| 2026-07-18 | 0.1 | Authored (rubric format + one worked example) under Build-Spec-Cody-Verification-Loop-v0_1. Staged in Builds\ — the spec's premise that this file already existed scaffolded in Canon was false on disk, and Cody's control gate (correctly) cannot write Canon. Promotion to Canon\Architecture\ is Rex's hand. |
| 2026-07-18 | 0.1 | Promoted to `Tabularium\Canon\Architecture\` by Rex. |
