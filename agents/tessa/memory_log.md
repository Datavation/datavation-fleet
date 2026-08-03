# Tessa — Memory Log (append-only, never edited, never overwritten)

Per Agent Architecture — Memory v0.2. Every write Tessa makes to `memory.md` is recorded here
as a `DONE` entry (operational, self-written); every architecture-touching change she may not
self-apply is recorded as a `PROPOSED` entry and held for Archy/Rex to rule on. Never loaded as
authority at session start — `memory.md` is the authority; this is the audit trail.

Starts empty at birth. The first entry is written by Tessa, not Cody — this build only creates
the (empty) file, per the same discipline as `memory.md`.

---

**2026-07-13T18:45Z — DONE (operational).** Added memory.md entry #1: live-board-read closes
offline "honest limits" a build's own self-test cannot reach. Learned during
agent-dispatcher-v1 verification (board card 39c06d59-4638-81e0-a4fe-c0d4123373d6) —
independently confirmed the live Notion board's `To`/`Action Type`/`Dispatch State`/
`Review State` select options match the build's code constants, resolving the handoff's
own honest-limit #2 to Verified rather than relaying it as an unconfirmed claim.

**2026-07-13T18:45Z — DONE (operational).** Added memory.md entry #2: `notion-update-page`
batch multi-property writes can fail (generic error) where the same properties sent
individually succeed. Learned posting the board record for agent-dispatcher-v1 — initial
4-property `update_properties` call failed; four sequential single-property calls all
succeeded. No architecture-class change implied — routine-level tooling note only.

**2026-07-13T19:10Z — DONE (operational).** Added memory.md entry #3: an in-place self-test
re-run (mine or a prior reviewer's) regenerates `__pycache__`/similar artifacts, which erases
the next reviewer's ability to verify a handoff's "swept clean" claim after the fact. Learned
during quinn-cfo-v1 verification — found `__pycache__` present, timestamps matched Archy's own
gate-review self-test run rather than a Cody leftover, but I could not independently confirm
his "clean before I touched it" account since my own routine's in-place step had by then also
touched the tree. Process note for future qa-verify passes: check artifact-cleanliness claims
before running any self-test in place.

**2026-07-14T18:35Z — DONE (operational).** Added memory.md entries #4 and #5 from the Fleet
Console Session 3 verification (agent-dispatcher-v1, pc-cockpit, telegram-cockpit; board card
39d06d59-4638-8196-96a7-e7e82fd4c7f2, verdict FAIL). #4: a build folder under active
gate-review can be concurrently edited by the next session — found "Session 3.5" code already
landed mid-review, breaking the dispatcher's own self-test (6/18 vs. expected 18/18),
reproducible in-place and clean-copy. #5: found a real live `COCKPIT_ACCESS_KEY` in plaintext
in `Builds\pc-cockpit\server.err`, which matters more than an ordinary stray-file finding
because pc-cockpit is a run-in-place build (confirmed via `install-tasks.ps1`) with no
promotion-copy step to strip it. Both reported to the board with Action Required = 🔴 Rex.

**2026-07-15T10:20Z — DONE (operational).** Added memory.md entry #6: live-system requests can
bundle legitimate read-only checks with asks that need a real credential or cause a real side
effect — decline only the unsafe part, explicitly, and hand it back rather than doing it or
refusing everything. Learned during the Fleet Console post-reboot go-live verification (board
card 39d06d59-4638-816b-a255-d1e4adeafccd) — declined resolving `COCKPIT_ACCESS_KEY` via a
sandbox-workaround and triggering a live agent wake for a "functional chat test," while
completing service health, `/api/health`, and the sweep confirmation (all PASS). Re-ran all
three suites fresh against current state: dispatcher 21/21, pc-cockpit 71/71, telegram-cockpit
66/66 — all clean, confirming the 2026-07-14 FAIL had been properly remediated via a separate,
honestly-reviewed Session 3.5 build.

**2026-07-15T13:15Z — DONE (operational).** Added memory.md entry #7: building my own
isolated test instance doesn't settle a live-agent-wake risk on its own — the harness's own
safety classifier blocked a browser navigation to a real seat's chat pane even inside my
isolated, unwatched setup, given the task chain's only authority was cross-session messages.
Learned during the Cockpit Agent Chat Pane verification (board card
39e06d59-4638-81fc-aea8-fd9ae65078d2, verdict PARTIAL — code+mechanical checks pass, 79/79 and
77/77 in-place+clean-copy with proper sibling layout; live click-through gate not completed,
handed back to the user rather than routed around).

**2026-07-15T13:40Z — no new memory.md entry (log note only).** The Cockpit Agent Chat Pane
verdict was upgraded PARTIAL → PASS after the user (Rex) drove the blocked live click-through
himself and supplied a screenshot — the route-to-Rex option the verdict recommended. Assessed
the screenshot honestly (confirmed core feature end-to-end; flagged that intra-session --resume
memory continuity is still not positively shown — Holly's memory-check reply is consistent with
a reset, inconclusive either way). Board card set To=Archy, Status=Done, ⚪ None. No new
generalizable lesson beyond memory.md entries #6/#7 (which already cover declining/handing-back
live-side-effect asks) — the loop-closure here is just applying them, so no new entry, only
this trace.

**2026-07-18T17:50Z — DONE (operational).** Added memory.md entry #8: a content-verification
criterion can PASS on its literal terms while a governance/process question about the same
artifact stays open on another agent's leg — verify the content honestly, name the boundary so
the PASS isn't misread as endorsing more. Learned during the Cody Verification Loop v0.1
independent verification (board card 3a106d59-4638-81ae-87e9-d668368aba34, verdict PASS 7/7).
Criteria 3/4 checked that Cody's CLAUDE.md CONTAINS the §3.3/§3.4 contract verbatim (it does);
the separate ratify-or-revert question on whether he could self-apply those identity edits is
Archy's retro card, explicitly kept out of my content leg. Also recorded: re-derive criteria
from the governing brief verbatim, not from the builder's completion-report restatement (the
report is under test, not the source of truth). Card closed To=Archy, Status=Done, ⚪ None.

**2026-07-19T14:35Z — DONE (operational).** Added memory.md entries #9 and #10 from the
weekend-builds independent adversarial test (Archy commission 2026-07-19; board card
3a206d59-4638-81a4-a183-e9148e40d83e, To=Archy, Action Type=Review, verdict PASS offline —
no gate broke). #9: when a build's gate also exists as a live seat tool, diff staged vs live
before the verdict — the Holly email allowlist-v2 (`@tpg.co.uk` rules + draft) I verified is
STAGED in holly-minimal-v1, but the LIVE `Agents\Holly\tools\email_adapter.py` is the prior
exact-match version, so my PASS covers the staged build, not what's deployed. #10: a vendored
test-dep missing on MY machine (`apscheduler`, declared in the build's requirements.txt) is a
verification-env gap, not a build FAIL — install the declared dep and re-run before calling an
ImportError a defect; and a runtime the machine lacks entirely (no Node → serverless JS not
live-invokable) caps the verdict at structural+pinned, with live behaviour BLOCKED-pending-Rex.
Session evidence: Console gates 7/7 (+clean), board-data parity 8/8, email core 23/23 (+clean),
holly-minimal 59/59 (+clean), relay_core 10/10 (+clean), WhatsApp staging 30/30, voice tools
25/25, and my own independent 30/30 spoof battery (CRLF/LF injection, homoglyph IDN, double-@,
trailing-dot, wildcard entry — none leaked). Also confirmed the WhatsApp voice-note silent-drop
gap (server.py:1036) and the hosted-console sole-gate risk (Vercel Deployment Protection must
cover production before NOTION_TOKEN) — both in the ranked findings on the card.
