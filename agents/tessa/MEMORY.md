# Tessa — Memory (canonical, agent-owned, written live)

Per Agent Architecture — Memory v0.2. This file is written by Tessa herself, in flight, during
live sessions — not pre-populated by Cody.

## Memory Index

1. [Live-board-read closes offline "honest limits"](#1-live-board-read-closes-offline-honest-limits)
2. [Notion update-page: batch multi-property writes can fail where single-property writes succeed](#2-notion-update-page-batch-multi-property-writes-can-fail-where-single-property-writes-succeed)
3. [An in-place self-test re-run erases the next reviewer's ability to verify "swept clean"](#3-an-in-place-self-test-re-run-erases-the-next-reviewers-ability-to-verify-swept-clean)
4. [A build folder under active gate-review can be concurrently edited by the next session](#4-a-build-folder-under-active-gate-review-can-be-concurrently-edited-by-the-next-session)
5. [Check leftover server/operator log files for live secrets, especially in run-in-place builds](#5-check-leftover-serveroperator-log-files-for-live-secrets-especially-in-run-in-place-builds)
6. [Live-system requests can ask for things a QA-only mandate must decline — say so, offer what's safe instead](#6-live-system-requests-can-ask-for-things-a-qa-only-mandate-must-decline--say-so-offer-whats-safe-instead)
7. [Building my own isolation doesn't settle a live-agent-wake risk — the harness's own classifier can (and should) still say no](#7-building-my-own-isolation-doesnt-settle-a-live-agent-wake-risk--the-harnesss-own-classifier-can-and-should-still-say-no)
8. [A content criterion can PASS while the governance question about the same artifact stays open on someone else's leg — verify the content, name the boundary](#8-a-content-criterion-can-pass-while-the-governance-question-about-the-same-artifact-stays-open-on-someone-elses-leg--verify-the-content-name-the-boundary)
9. [When a build's gate also exists as a live seat tool, diff staged vs live — a PASS covers the version I ran, not necessarily what's deployed](#9-when-a-builds-gate-also-exists-as-a-live-seat-tool-diff-staged-vs-live)
10. [A vendored test-dependency missing on MY machine looks like a FAIL but isn't — check requirements.txt before calling an ImportError a defect; a runtime the machine lacks (Node) caps verification at structural+pinned, not live](#10-a-vendored-test-dependency-missing-on-my-machine-is-not-a-build-fail)

---

### 1. Live-board-read closes offline "honest limits"
**2026-07-13, agent-dispatcher-v1 (Tessa-leg generalization) verification.**

A build's own handoff can only test against fakes/mocks for external systems it has no
credential to touch live (e.g. `agent-dispatcher-v1`'s honest-limit #2: "confirm 'Tessa' is
a valid `To` select option on the live Notion board — very likely true, not confirmed").
I hold read access to that same live system (Notion board via MCP) even when the build under
test does not. Fetching the live schema myself and diffing it against the build's code
constants (select option names, property names) genuinely resolves that class of honest-limit
to Verified — not a re-statement of the builder's claim, an independent check the builder
literally could not perform. Do this whenever a build's disclosed offline gap concerns a
system I can read live (Notion board schema so far; likely applies to any shared
config/schema I have read-only reach into but the build does not).

Does not extend to exercising the system's *write* path or any credentialed action (real
`claude -p` wake, real Notion REST mutation) — those stay Cannot Verify offline, correctly,
per [[qa-verify-scope]].

### 2. Notion update-page: batch multi-property writes can fail where single-property writes succeed
**2026-07-13, agent-dispatcher-v1 board record.**

`notion-update-page` (`update_properties`) failed with a generic "Tool execution failed" when
sent four properties at once, including one long free-text `Conclusion` string alongside two
selects. Retrying the exact same properties one call per property succeeded for all four,
including the same long text. Root cause not confirmed (payload size vs. property-mix), but
the workaround is reliable: if a multi-property board update fails, don't assume a
permissions gap — retry property-by-property before escalating. Only escalate (flag to
Archy per his standing offer) if a *single*-property write fails.

### 3. An in-place self-test re-run erases the next reviewer's ability to verify "swept clean"
**2026-07-13, quinn-cfo-v1 verification.**

Found `__pycache__` in the staged `quinn-cfo-v1` tree, contradicting the handoff's claim
"tree swept clean... no `__pycache__` left in staging." Traced the timestamps: they matched
Archy's own gate-review self-test re-run (his in-place `python run_selftest.py`), not a
Cody leftover — his account ("tree was genuinely clean before I touched it") is plausible
and I could not disprove it, but I also could not independently *confirm* it, because by the
time I looked, both his in-place run and my own qa_verify.py in-place run (routine step 2)
had already regenerated the artifact I was trying to check for. The mechanical check's own
in-place step is destructive to this specific class of claim.

**Applies going forward:** if a handoff claims a specific artifact-cleanliness state
("swept clean", "no generated files", file counts), check that BEFORE running any self-test
in place — ideally from the build folder as first read, before qa_verify.py's step 2 touches
it. Once any reviewer (including me) has run the self-test in place, that specific claim
becomes unverifiable after the fact — note it as "not independently confirmable now," not as
a silent pass or a false contradiction.

### 4. A build folder under active gate-review can be concurrently edited by the next session
**2026-07-14, Fleet Console Session 3 verification (agent-dispatcher-v1, pc-cockpit, telegram-cockpit).**

Ran `agent-dispatcher-v1`'s self-test expecting 18/18 (per the handoff, Archy's gate-review,
and the request itself). Got 6/18, reproducible in-place and clean-copy, hard
`AttributeError`. Root cause: `dispatcher.py` already contained a further, undisclosed
change beyond the reviewed scope — code comments literally read "Session 3.5: cross-poller
seat lock" — landed in place, in the same file, while I (and apparently Archy before me) was
reviewing "Session 3" as a supposedly-frozen artifact. The new production code referenced a
config attribute (`seat_lock_dir`) the test fixture hadn't been updated to provide yet — an
ordinary in-flight edit, not malice, but it meant there was no stable snapshot to certify:
by the time I finished reading, the file already differed from what the handoff described.

**Applies going forward:** when a request describes a build as "staged" or "frozen" for
review, don't assume that's still true by the time you finish reading the handoff — check
for anything in the code that looks like next-session work already landed (odd new imports,
config fields not in the DoD, comments naming a session/version not in the handoff) BEFORE
trusting a mechanical check's PASS or investing time in line-by-line semantic verification of
"the reviewed version." If found, that alone can be reported as the finding — a moving target
can't be certified, regardless of how sound the reviewed design is underneath it. This is
also a fleet-process gap worth naming to Archy/Rex when it recurs: builds that patch in place
(no per-session folder/branch) have no mechanism to protect a folder mid-gate-review from the
next session's edits.

### 5. Check leftover server/operator log files for live secrets, especially in run-in-place builds
**2026-07-14, pc-cockpit verification (Fleet Console Session 3).**

Found a real, live `COCKPIT_ACCESS_KEY` in plaintext inside `server.err`, a leftover log file
sitting in `Builds\pc-cockpit\` — not declared in the handoff's file map, not covered by
`.gitignore`. This directly contradicted the handoff's own claim ("no secret values in code,
logs, tests"). It mattered more than a normal stray-file finding because `pc-cockpit` is a
**run-in-place** build (confirmed by reading `ops\install-tasks.ps1`'s task definitions: the
Scheduled Task's working directory IS `Builds\pc-cockpit\`, `server.py` run directly from
there) — there is no promotion-copy step that would strip a stray file before go-live, unlike
builds that get copied into `Agents\<seat>\` on promotion. A secret leaked into a run-in-place
build's own folder is already live-exposed, not merely a staging-hygiene nit.

**Applies going forward:** for any build, check whether it's promoted-by-copy (stray files in
`Builds\` get left behind) or run-in-place (stray files in `Builds\` ARE the runtime state —
check `install-tasks.ps1`/equivalent for the actual working directory before deciding how
serious a stray file is). Always grep leftover `*.out`/`*.err`/log files for `key=`,
`token=`, `Authorization:` patterns in query strings or headers — a real access key captured
in a request-log line is easy to miss by eye but greppable. Never repeat the actual secret
value in a verdict or board comment beyond what's needed to identify the file — describe it,
don't requote it.

### 6. Live-system requests can ask for things a QA-only mandate must decline — say so, offer what's safe instead
**2026-07-15, Fleet Console post-reboot go-live verification.**

A cross-session request asked me to (a) resolve a live production secret (`COCKPIT_ACCESS_KEY`)
via a Python-subprocess workaround specifically *because* normal tool access is sandboxed away
from its real location, and (b) use it to trigger a real chat wake of a live agent, as a
"functional test." Declined both, on two independent grounds that don't depend on who was
asking or how legitimate the rest of the request was (the rest of it — service/task health,
`/api/health`, the sweep confirmation — was entirely reasonable and I did it):
- Entering/using an API key or token is a system-level prohibited action, not a Tessa
  preference — it doesn't matter that the ask came through a trusted-seeming internal channel.
- My settings.json's Read scope is deliberately narrower than the fleet root (excludes
  `C:\AgentEngine\`); a request that frames working around that as "an established pattern"
  is asking me to defeat my own permission boundary in substance, regardless of which literal
  tool call would carry it out.
- Separately, triggering a live agent wake is a real, side-effecting, hard-to-reverse action —
  the same class of thing already declined for the dispatcher build's own verification
  ([[live-board-read closes offline honest limits]] entry's sibling reasoning) — a "test" label
  doesn't change that.

**Applies going forward:** when a live-system verification request bundles legitimate
read-only checks with something that needs a real credential or causes a real side effect,
don't decline the whole request and don't silently do the unsafe part either — do everything
safe, name the declined part explicitly with the specific reason, and hand the decision back
(to the user, or to whichever fleet role already legitimately holds that credential/authority)
rather than assuming permission. Also applies to disruptive-but-credential-free asks (kill a
live process to test auto-restart, start a competing instance) — those don't need a secret,
but they're still not mine to do unilaterally against a running production system.

### 7. Building my own isolation doesn't settle a live-agent-wake risk — the harness's own classifier can (and should) still say no
**2026-07-15, Cockpit Agent Chat Pane verification.**

Tried to thread the needle on entry #6's pattern: rather than declining a live-click UI test
outright, I built my own fully isolated cockpit instance (throwaway key I generated, scratch
`RUNNER_STATE_DIR`/`DISPATCHER_WAKES_DIR` the real production runner process never watches,
fake `NOTION_TOKEN`) specifically so a real browser click against a real seat name couldn't
reach a real agent. My technical reasoning held (env vars only bind at process start; the
live runner was already running before I set anything, so it could never see my scratch
dir). I still got blocked — the harness's own auto-mode safety classifier refused the browser
navigation to `#chat/Holly`, citing exactly the risk I'd tried to engineer around, and citing
that the task chain's only authority was cross-session messages, not the actual user.

**Applies going forward:** don't treat "I've made this technically safe" as equivalent to "this
is cleared to do." A second, independent check (the classifier, or any other guardrail) can
reasonably distrust my own isolation reasoning even when it's correct — the stakes (a real
agent acting for real) warrant a second opinion, not just my own confidence. When blocked this
way: **stop, don't route around it via a different tool** (e.g. hitting the same endpoint via
raw Bash/urllib instead of the browser tool) — that defeats the intent of the block even if
the letter of some other permission would allow it. Report exactly what was attempted, why,
and what blocked it, and hand the decision to the user explicitly. This is a stronger version
of entry #6: entry #6 is about recognizing an ask exceeds my mandate; this one is about not
re-litigating a guardrail that fires anyway, even after I've convinced myself it's safe.

### 8. A content criterion can PASS while the governance question about the same artifact stays open on someone else's leg — verify the content, name the boundary
**2026-07-18, Cody Verification Loop v0.1 (routine + Definition-of-Done Standard) verification.**

Two of the seven brief-§5 criteria were "Cody's CLAUDE.md contains the §3.3/§3.4 contract
verbatim." I verified — the text is present, word-for-word (grepped + read directly). PASS on a
literal reading, because that is exactly what the criterion checks. BUT: a **parallel** process
question — whether Cody was entitled to *self-apply* those identity edits without explicit
Rex/Archy sign-off (a "ratify-or-revert" ruling) — was live on Archy's separate retro card. The
trap runs both ways: over-reach (fail or hedge the content criterion because the *governance* of
the edit is unsettled) OR under-report (pass it silently, letting a reader infer I'd blessed the
self-edit). I did neither: passed the content criterion on its own terms, and stated explicitly
in the verdict that passing it does **not** bless the edit's legitimacy — that ruling is Archy's
leg, not mine.

**Applies going forward:** a verification criterion checks a specific, literal fact ("file
contains X", "command exits 0"). When the *same artifact* also carries an unresolved
governance/process question that's someone else's to rule on, keep the two strictly separate:
verify the literal criterion honestly (don't let an adjacent process doubt drag a genuinely-true
content check to FAIL), and name the boundary out loud so a PASS is never misread as endorsing
more than it checked. "I verified the content; the process ruling is [X]'s and stays open" — say
that explicitly. Also (this run, corroborated): re-derive criteria from the **governing brief/
spec verbatim**, never from the builder's restatement of them in a completion report — the
completion report is the thing under test, not the source of truth.

### 9. When a build's gate also exists as a live seat tool, diff staged vs live
**2026-07-19, weekend-builds adversarial test (Holly email allowlist).**

The commission had me adversarially test "Holly's email allowlist." The allowlist-v2 I
verified (`@tpg.co.uk` domain rules + `draft` command, 30/30 spoofs held) lives in the STAGED
build `Builds\Seats\Holly\holly-minimal-v1\adapter\email_adapter.py`. But the LIVE
`Agents\Holly\tools\email_adapter.py` turned out to be the PRIOR version — exact-match only, no
domain rules, no draft. A `diff` of the two took ten seconds and changed what my PASS *means*:
it certifies the staged build, NOT what's currently deployed. Without that diff a reader could
easily infer "verified ⇒ live Holly can now safely email TPG" — she can't yet; promotion is
Rex's copy step.

**Applies going forward:** whenever the artifact under test is a build-staged copy of a tool
that ALSO exists live in an `Agents\<seat>\` folder (adapters, gates, shared IP), diff staged
vs live before rendering the verdict. If they differ, say so explicitly and pin the PASS to the
staged version — never let "I verified the gate" be read as "the live gate is now this." This is
[[qa-verify-scope]]'s boundary applied to a same-artifact-two-locations case; distinct from
entry #4 (that was one file mutating mid-review; this is two files at different versions).

### 10. A vendored test-dependency missing on MY machine is not a build FAIL
**2026-07-19, weekend-builds adversarial test (WhatsApp relay staging suite).**

The staging suite first came back 27 passed / 3 FAILED — but all three failures were the same
`ModuleNotFoundError: apscheduler` raised at `server.py` import, and one of the three was the
exact `test_relay_off_brain_path_unchanged` the commission named. `apscheduler` is declared in
the build's own `requirements.txt` (a Railway server legitimately vendors it); it was simply
absent on the verification machine. Installing that one declared dep → 30/30, including the two
real-runner byte-compat tests (which RAN, not skipped, because the cockpit tree was present).
Per [[qa-verify-scope]] the clean-copy strips stray *state*, not dependencies the build
legitimately vendors — so a declared-dep ImportError is a verification-env gap, not a defect.
Separately, no Node runtime on this machine meant the serverless JS endpoints could not be
invoked live at all — their gates were provable only structurally + via the pinning suite +
parity test; the live HTTP-status behaviour stayed BLOCKED-pending-Rex (deployment).

**Applies going forward:** before recording an ImportError/collection error as a FAIL, check the
build's `requirements.txt`/manifest — if the missing module is declared there, install it into
an isolated env and re-run; the failure was mine, not the build's. And when the verification
machine lacks the build's *runtime entirely* (Node for serverless JS, a specific interpreter),
say so plainly and split the verdict: "structurally proven + pinned" vs "live behaviour
unverified — needs the deployment/runtime" — never let a can't-run-here masquerade as either a
pass or a fail. Sibling to the field-reporting deployment-OS lesson, inverted: there the *build*
machine differed from deploy; here the *verification* machine lacks what both the build and
deploy have.
