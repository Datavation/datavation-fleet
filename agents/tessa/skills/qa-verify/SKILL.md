---
name: qa-verify
description: >
  Verify a staged build (a folder under Builds\<name>\) before it reaches Rex or is promoted
  to a live agent folder. Use when a build's own handoff/commission claims it is tested and
  ready, and that claim needs independent confirmation rather than a re-read of the same
  handoff. Runs the build's own self-test suite, re-runs it from a clean isolated copy (never
  trusting the builder's in-place state or claimed deployment environment), fingerprints the
  OS/interpreter it actually ran under, and returns a structured PASS/FAIL verdict with
  evidence. Does not fix, does not edit the build, does not promote — verification only.
---

# QA Verify

## What this is, and is not

**Is:** an independent check that a build's *own* tests actually run, actually pass, and keep
passing when run somewhere other than the exact spot and state the builder left it in.

**Is not:** a re-statement of the build's handoff. A handoff that says "38/38 tests pass" is a
**claim to verify**, not a fact to relay. This skill exists because a claim and a fact look
identical in a summary and only running the thing tells them apart — see the finance-engine
`refresh.bat`-lies-about-success class of defect and the field-reporting-v1 deployment-OS gap
(built/tested on Fable 5 macOS PowerShell 7.6.3, deployed to Windows PowerShell 5.1 — a real
parse-compatibility gap only a clean deployment-OS run could catch).

## Procedure

1. **Locate the build.** Given `--build-dir Builds\<name>\`, read its `BUILD-HANDOFF.md` (or
   equivalent) for the stated Definition of Done and any declared target deployment
   environment (OS, interpreter version).

2. **Run the mechanical check** — `scripts\qa_verify.py`:
   - Auto-detects the build's own self-test entry point (`tests\run_selftest.py`,
     `tests\selftest.py`, `tests\run-tests.ps1`, or a pytest-discoverable `tests\` folder —
     first match wins, in that priority order).
   - Runs it **in place** — records exit code, stdout/stderr, elapsed time.
   - Copies the build into an **isolated scratch folder** under Tessa's own
     `output\logs\qa-scratch\<timestamp>-<name>\` (excluding `.git`, `__pycache__`, `.venv`,
     `venv`, `node_modules` — a fresh copy, not a fresh install; the point is to strip stray
     *state*, not dependencies the build legitimately vendors) and **re-runs the same entry
     point there**. A test that only passes in the builder's original folder is not proven —
     it may be reading leftover output, a cached venv, or a prior run's artefact.
   - Fingerprints the actual environment it ran under: OS, OS release, Python/PowerShell
     version available on **this** machine — the machine running the verification, which per
     the field-reporting lesson may not be the machine the build was built on.
   - Writes a JSON evidence file + prints a summary. Exit code 0 only if both runs (in-place
     and clean-copy) passed.
   - **No network calls, no writes outside the scratch folder it creates and the evidence file
     it writes** — greppable in the script itself, same discipline as the finance-engine's
     `no_network_imports` self-test.

3. **Drive the actual flow (judgment step, not scripted).** A green self-test is necessary,
   never sufficient. Read what the self-test actually exercises — if it is a `--dry-run` or
   unit-level check that never touches the build's real entry point (the "prints DONE
   unconditionally" class of defect the finance-engine review caught), say so explicitly in the
   verdict rather than letting a passing unit suite stand in for the whole build. Where
   practical, exercise the build's stated real command/entry point directly (not just its
   tests) and observe the output, per the `/verify` discipline: observe behaviour, don't just
   read a report of it.

4. **Check the DoD line by line (judgment step).** Take the build's own stated Definition of
   Done (from its handoff/commission) and mark each item one of:
   - **Verified** — the self-test or a direct check actually demonstrates it.
   - **Not Verified** — claimed in the handoff, no evidence found; state what evidence would
     be needed.
   - **Cannot Verify offline** — genuinely requires the live deployment environment/credentials
     Tessa does not and should not hold (e.g. a real Windows box, a live API key). Say so — this
     is a legitimate outcome, not a failure to hide.
   Never collapse this into a single "meets spec" line — that is exactly the kind of blanket
   claim this skill exists to replace.

5. **Render the verdict** (Output Contract, `routines\qa_verify.md`) and file it to
   `output\reviews\<date>-<build-name>-qa-verdict.md`, plus the raw JSON evidence alongside it.

6. **Stop.** Do not edit anything under `Builds\` or any other agent's folder. Do not promote.
   Do not soften a FAIL because the handoff reads well.

## When this skill does NOT apply

- The target is not a staged build (e.g. a live agent's ongoing work, a Tabularium document) —
  Tessa verifies builds heading to Rex/promotion, not general code review.
- No self-test exists at all in the build. This is itself a finding, not a silent skip — the
  verdict says "no self-test found" and marks every DoD item Not Verified / Cannot Verify, it
  does not invent a PASS.
