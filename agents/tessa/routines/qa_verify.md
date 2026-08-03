# Routine: qa_verify

**Agent:** Tessa   **Owner:** Austen King / Datavation Ltd
**Version:** 0.1   **Last updated:** 2026-07-11   **Status:** Draft (staged, awaiting promotion)

## Purpose
Independently verify a staged build (`Builds\<name>\`) before it reaches Rex or is promoted to
a live agent folder, returning a structured PASS/FAIL verdict with evidence.
It deliberately does **NOT** fix defects, edit the build, judge architecture fit, or promote —
those stay Cody's hand, Archy's ruling, and Rex's hand respectively.

## Trigger
**Type:** Board card / direct request.
**Fires when:** a Decision Board card reaches `To = Tessa` (a build ready for gate-review), or
Tessa is directly asked to verify a named build folder under `Builds\`.

## Source of Truth
The build's own artefacts: its self-test suite (whatever it is, wherever it lives under
`tests\` or equivalent) and its `BUILD-HANDOFF.md` (or equivalent commission/spec) for the
stated Definition of Done. Tessa reads the Decision Board Command view for what is waiting on
her; she does not maintain a private queue.

## Ownership & Scope
Per-agent (single-instance for the fleet — there is one QA seat, not one per builder). Tessa
verifies builds from any agent that stages work in `Builds\`; at birth, Cody is the only source.

## Preconditions (fail loud — if any fails, STOP and say so; never return an empty "all-clear")
1. The build folder exists and is readable (`Builds\<name>\`).
2. A handoff/commission document exists stating a Definition of Done — if absent, the verdict
   says so and every DoD line reads "Cannot Verify: no DoD stated."
3. Tessa's own write path (`output\reviews\`, `output\logs\qa-scratch\`) is writable.

## Steps (one action each; mark each [mechanical] or [judgment])
1. [mechanical] **Locate and read** the build's `BUILD-HANDOFF.md` (or equivalent) for its
   stated Definition of Done and any declared target deployment environment.
2. [mechanical] **Run `skills\qa-verify\scripts\qa_verify.py --build-dir <path> --out
   output\logs\<date>-<name>-evidence.json`** — detects the build's self-test entry point, runs
   it in place, re-runs it from an isolated clean copy, fingerprints the actual OS/interpreter,
   exits 0 only if both runs passed.
3. [judgment] **Drive the real flow** — named criteria: (a) does the self-test actually exercise
   the build's stated real entry point, or only a unit/dry-run slice of it? (b) if only a slice,
   exercise the real entry point directly where practical and observe the output; (c) does the
   test suite's own logic ever assert success unconditionally (grep for the shape of the
   finance-engine `refresh.bat` defect)? Record what was actually exercised, not just the exit
   code.
4. [judgment] **Check the DoD line by line** — named criteria: for each stated DoD item, mark
   **Verified** (a specific test or direct check demonstrates it — cite which), **Not Verified**
   (claimed, no evidence — state what evidence is missing), or **Cannot Verify offline**
   (genuinely needs the live deployment environment/credentials Tessa does not hold — state
   what would need to run, and where).
5. **Render** using the Output Contract below; file to
   `output\reviews\<date>-<build-name>-qa-verdict.md` with the JSON evidence alongside it.
6. **Post one Board record** — `Conclusion` = PASS/FAIL headline, `Action Required` = 🟡 Cody
   (FAIL needing a fix) / ⚪ None (PASS, Archy owns the promotion decision from here) / 🔴 Rex
   (only if genuinely blocked), `Link` = the verdict file.
7. **Stop.** Do not edit the build. Do not promote. Do not soften a FAIL because the handoff
   reads well.

## Output Contract (the exact shape — this is the test)
```
# QA Verdict — <build-name>
Date: YYYY-MM-DD  Verified by: Tessa  Build: Builds\<name>\

## Verdict: PASS | FAIL

## Mechanical check (qa_verify.py)
- Entry point: <path or "none found">
- In-place run: PASS | FAIL (<returncode>, <elapsed>s)
- Clean-copy run: PASS | FAIL (<returncode>, <elapsed>s)
- Ran on: <OS> <release>, Python <version>[, PowerShell <version>]
- Evidence file: <path to JSON>

## Real-flow check
<what was actually exercised beyond the self-test suite, and what it showed>

## Definition of Done — line by line
| DoD item | Status | Evidence / what's missing |
|---|---|---|
| <item 1> | Verified / Not Verified / Cannot Verify offline | <cite the check, or the gap> |
...

## Notes
<anything a human should weigh before acting on this verdict>
```
Empty case (explicit, distinct):
```
No build specified / build folder not found — nothing to verify. STOP: cannot proceed.
```

## Abort conditions
- If the build folder does not exist or is unreadable → output the explicit empty-case line
  above, board record `Action Required = 🟡 Cody` ("build folder not found at <path>"), do not
  fabricate a verdict.
- If no self-test entry point exists anywhere in the build → verdict is **FAIL**, every DoD item
  defaults to "Not Verified: no test evidence available," never a silent skip or implicit PASS.
- If `qa_verify.py` itself errors (interpreter missing, timeout) → the JSON evidence records the
  error; verdict is **FAIL** with the error surfaced verbatim, not swallowed.

## Change log
| Date | Version | Change |
|---|---|---|
| 2026-07-11 | 0.1 | Created. Staged under Builds\tessa-seat-v1 by Cody per Rex's 2026-07-11 ruling (board card 39a06d59-4638-8187-a711-c450d664c526), conforming to Agent-Routine-Standard-v0_1. |
