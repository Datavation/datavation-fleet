# context/patterns.md — Cody Reference

Reusable automation and integration patterns. Add entries as they are established and proven.

---

## Pattern format

Each entry:
- **Problem it solves**
- **Where it has been used**
- **Code or Make.com module sequence**
- **Known gotchas and edge cases**

---

## Additive Notion schema migration on a live board (gold-rail safe)

- **Problem it solves:** evolving a live Notion database (new properties, more select
  options, a hierarchy) without orphaning existing row values — MEM-018 additive-only.
- **Where used:** Decision Board → PMO upgrade, Build 1 (2026-06-28).
- **Sequence:**
  1. `notion-fetch` the database → capture full schema (property names, every select
     option's exact name + colour + option ID).
  2. **Back up rows first.** If `query_data_sources`/`query_database_view` are plan-gated
     (Business+AI only), fall back to `notion-search` (several varied queries, dedupe) to
     enumerate, then `notion-fetch` each page for its property values. Save to
     `output\backups\`. Note it's a workaround and recommend a native CSV export too.
  3. Add new properties with `update-data-source` `ADD COLUMN` — pure addition, cannot
     touch existing row data. Self-relation: `ADD COLUMN "Parent" RELATION('<same-ds-id>',
     DUAL 'Sub-items' 'sub_items')` creates the two-way companion automatically.
     Last-edited-time: `ADD COLUMN "Updated" LAST_EDITED_TIME`.
  4. Extend select options with `ALTER COLUMN "X" SET SELECT(...)` — there is no "ADD
     OPTION", so **list ALL existing options (exact names + colours) + the new ones**.
     Matching by name preserves the original option IDs, so existing row values survive.
     Isolate this in its own call so a syntax error can't roll back the ADD COLUMNs.
  5. Verify: re-fetch the schema (all options present, original IDs intact) and re-fetch a
     few real rows spanning the riskiest option values to confirm none were orphaned.
- **Gotchas:**
  - `ALTER COLUMN SET` *replaces* the option list — omitting an existing option deletes it.
  - The brief's option list may be stale; trust the live schema (found an unlisted
    `Parked - Revisit` option in active use).
  - Notion selects have no schema-level default; "default Task" must be set by the writer.
  - Relation values in `create-pages`/`update-page` are a JSON-array-of-page-URLs string:
    `"[\"https://app.notion.com/p/<id>\"]"`.
  - View DSL handles nested booleans — `FILTER (A AND (B OR C)) OR D` compiled correctly —
    and `GROUP BY` on a relation property works.
  - Plan-gating: MCP *query* tools need Business+AI; schema/page/search/fetch do not. Read
    rows via raw REST `POST /v1/data_sources/{id}/query` + integration token on lower plans.
    **On Business+AI (now active) the MCP `query-data-sources` + `update-data-source ADD COLUMN`
    work directly — no REST fallback needed** (used live 2026-06-30 for the Output Record fields).
  - **Verify count by *diffing*, not assuming.** Post-change `COUNT(*)` came back 37→38; the +1 was
    a card another actor created mid-run, not corruption. ADD COLUMN cannot mutate existing rows, so
    a count change = concurrent write — list rows and identify the new id before flagging a problem.
  - **The auto-mode classifier gates a live shared-board schema write** even when an upstream
    approval exists, if it can't see that approval in the transcript. Expect to surface the approval
    and get an explicit go rather than retrying — and that's the correct rails behaviour.

## Autonomous-agent guardrail layer (infra-enforced, reusable)

- **Problem it solves:** let an agent run unattended doing only *reversible* work while control
  gates (spend, external send, promote-to-live, edit-another-agent, recursive spawn) are
  *impossible*, not merely discouraged. Alerts ≠ enforcement.
- **Where used:** `Builds\fleet-guardrails-v1\` (Build 2). Mounted per-agent by a human.
- **Shape:**
  - **Declarative `deny` is the primary gate** — first-match, non-overridable, no script, holds
    on every platform (incl. native Windows, which has no sandbox). Allow-only base: anything not
    in `allow` is denied, so spend/send tools are denied just by being absent.
  - Deny `Agent` at the settings layer → no recursive sub-agent spawn (the ~4M-token-in-5-min
    blowup becomes structurally impossible). In-definition tool lists are unreliable — use settings.
  - Deny `Edit/Write(**/.claude/**)` → an agent can't disarm its own guardrails (self-disarm hole).
  - Deny destructive shell in BOTH `Bash(...)` and `PowerShell(...)` — on Windows the destructive
    shell is PowerShell.
  - `permissions.disableBypassPermissionsMode:"disable"` + `disableAutoMode:"disable"`;
    un-overridable only via managed settings (`HKLM\SOFTWARE\Policies\ClaudeCode`, maybe plan-gated).
  - **Hooks = defense-in-depth, not the sole gate.** `PreToolUse` exit-2 catches spend/send MCP
    tools by name *substring* (declarative deny can't, because server ids are per-connection hashes).
    `PostToolUse` iteration-cap = proxy for the absent native token cap. `Stop` hook = §3.3
    board-write (append thread + advance Status via Notion REST). Target the cloud Routine (Linux).
- **Gotchas:**
  - **No native token/cost cap** — the real ceiling is the Anthropic *account-level* spend/rate
    limits (a human/owner action), backed by the iteration-cap hook + `Agent`-deny.
  - **No OS sandbox on native Windows** (macOS/Linux/WSL2 only) → run unattended work in the cloud
    Routine or WSL2; never an unsandboxed autonomous Bash agent on native Windows.
  - **Write hooks dependency-light** — `jq` is absent in the local Git Bash, so a jq-dependent hook
    silently no-ops (fails open). Parse with grep/tr. Unit-test gate logic with sample stdin JSON.
  - End-to-end gate refusal can only be verified once *mounted* — ship a V1–V8 verification
    checklist for the human promoter; "instruction-only gate is a finding, not a pass."

## Phone→fleet cockpit: Telegram long-poll over the board, gated Claude Code dispatch

- **Problem it solves:** conduct the fleet by voice/text from the phone, PC closed, with control
  gates that make a one-tap phone approval safe — without inbound ports or a bespoke app.
- **Where used:** `Builds\telegram-interface-v1\` (Epic 1 · Reachability), 2026-07-02.
- **Shape:**
  - **Long-poll, not webhook.** Telegram `getUpdates` is **outbound HTTPS only** → no inbound ports to
    expose/secure. A `worker` process (not a web server); Procfile `worker: python bot.py`.
  - **Allowlist-of-one is a CODE control gate** on the numeric `from.id` (never username — spoofable).
    Every other sender dropped + logged. Pure function → unit-tested offline (no network/secrets).
  - **The board is the engine (Principle 4).** The cockpit's Claude conducts *through the Notion board*,
    not a local fleet FS — the Railway host has no OneDrive mount by design. Exception surface **reuses**
    `Action Required = 🔴 Rex`; never invent a parallel channel.
  - **Reply-correlation for writeback:** remember `{sent_message_id → board_page_id}` in a volume file;
    Rex's *reply* to a pushed exception maps back and writes the decision. A plain message = fresh dispatch.
  - **Headless Claude = `claude -p --output-format json` on `ANTHROPIC_API_KEY`** (Max sub OAuth can't run
    unattended). Run it in a workdir whose `.claude/settings.json` is the `fleet-guardrails-v1` config →
    reversible-work-only; deny spend/send/promote/edit-another-agent/recursive-spawn; no bypassPermissions.
  - **The bot's own Telegram send is plumbing to the single owner**, NOT a Claude-invocable send tool — so
    the §6 external-send gate (on Claude's tools) stays intact.
  - **Cost cap made real:** `--max-turns` + iteration-cap hook bound one dispatch; a durable daily-cost
    tally refuses new work past `DAILY_COST_CAP_USD`; the true ceiling is the Anthropic *workspace* cap (Rex).
- **Gotchas:**
  - Railway needs **both** Python (bot) and Node + `@anthropic-ai/claude-code` (CLI) — `nixpacks.toml`
    installs both. **Validate `claude -p` actually runs in the container first (V0)** before assuming the
    host works; if not, report logs before reaching for a dedicated VPS.
  - Long-poll client read-timeout must **exceed** the server long-poll window (else spurious timeouts).
  - `python` may be absent from Git Bash PATH on this box — run Python via PowerShell (`python …`).
  - Chunk sends at ~4000 chars (Telegram caps at 4096).

## Read-only HTML dashboard over a data source (token-out-of-page)

- **Problem it solves:** a glanceable single-file dashboard over live data (e.g. the Decision Board)
  without ever exposing the API token to the browser.
- **Where used:** `Builds\fleet-dashboard-v1\` (Build 4) over the Notion board.
- **Shape — two pieces:**
  1. **Sync step** (server-side/local, holds the token): reads the source via REST and writes a flat
     `*.json`. Token in env only; fail loud if missing; nothing secret in the output.
  2. **Single-file `index.html`** (HTML + embedded CSS/JS, no build): `fetch()`es the JSON and renders.
     The page never holds the token — host the JSON, not the secret.
- **Why decoupled:** the page is static + cacheable; the token stays out of the client; the sync can run
  on any scheduler (local task or cloud Routine); hosting is trivial (GitHub Pages free).
- **Render logic reuse:** same bucketing as the stand-up (terminal-status exclusion, blank-row +
  digest-item skip, Needs-you wins ties) so board, digest, and dashboard agree.
- **Gotchas:**
  - Browsers **block `fetch()` from `file://`** — the page MUST be served (`python -m http.server`),
    not double-clicked. Add a graceful on-error message telling the user to serve/host it.
  - Verify by serving the folder and checking the feed + computed buckets (Python/Node), not only by
    eyeballing — the Claude_Preview screenshot tool can time out (renderer hiccup ≠ broken page).
  - Resolve Notion relations (Parent) by matching the related page-id to each row's id to build the
    Epic→Feature→Task tree; REST returns relations as `[{id}]`.

## Completion record: agent authors, hook enforces (the honest split)

- **Problem it solves:** guaranteeing a standardized "what I concluded + what's needed" record gets
  written when an agent finishes work — without pretending a deterministic hook can write a *good*
  conclusion. A Stop hook can't synthesise judgement; it CAN guarantee presence.
- **Where used:** `Builds\fleet-output-record-v1\` (Output Record, build 1 of N), 2026-06-30.
- **Shape — two tiers, one record:**
  - **Authorship = the agent** (its judgement): writes `Conclusion` + `Action Required` + `Status`
    advance via Notion MCP (interactive) or a REST helper (cloud/scripted). Behaviour, not a hook.
  - **Enforcement = `Stop`/`SubagentStop` hook** (deterministic): verifies the record exists; if
    missing, **flags** it (append a `⚠` callout + set a marker) and stamps `Updated`. It never
    authors the content.
- **Keep the decision logic in a pure, sourced function** (`record_present <conclusion> <status>`,
  no I/O) so it unit-tests anywhere with no token/network/jq. present = conclusion non-empty AND
  status advanced past the working states (Open/Backlog/Ready/Approved/In progress); Blocked-with-
  conclusion counts. 11/11 case test ran green before staging.
- **Non-blocking is the rule, not a default.** A hygiene miss is flagged, never `exit 2`. Reserve
  block-stop for control-gate violations — a blocking Stop hook on a missing record trapped a live
  session (Archy ruling 2026-06-30).
- **"Which item did this run own?"** env var (`GUARDRAIL_BOARD_ITEM_ID`) for cloud Routines; a
  run-state file written at pickup / cleared on completion for attended local seats.
- **Default-select-when-blank:** Notion has no schema default, so the hook stamps `⚪ None` only if
  the field is empty — never overriding an explicit value.
- **Gotchas:**
  - The hook needs `jq` (parses Notion JSON) → runs on the cloud Routine; **no-ops on native
    Windows where jq is absent** (C3/V8). Author-via-MCP works on every seat regardless.
  - The hook's full path can only be proven end-to-end where it actually executes (cloud) — ship the
    pure-logic unit test (runs now) + a stubbed-curl offline test + a live scratch-row procedure.
  - Dogfood it: have the build's own board card carry the first real record — proves the loop and
    surfaces tone/shape for review.

## Two-skin A/B decision toggle on the shared design system

- **Problem it solves:** the estate's skin contract (`--skin-*` variables over shared
  tokens) makes colourway a one-file decision — but Rex picks by eyeball, not by hex
  list. This stages N candidate skins in one build and lets the decider flip them live
  on the real page, so the pick happens on rendered evidence and costs one click.
- **Where it has been used:** `Builds/austenking-site-v1/` (2026-07-05) — skin-a
  (Ink & Ember) vs skin-b (Indigo & Violet) for austenking.com.
- **Code:** one `<link id="skin-link" href="assets/css/skin-a.css">` after tokens.css;
  fixed pill (`.skin-toggle`, buttons with `data-skin`) + ~15-line inline script that
  swaps the link href and persists the choice to localStorage. All candidate skins are
  full `--skin-*` overrides, so components/base need zero awareness.
- **Known gotchas and edge cases:** (1) mark everything REVIEW ONLY in comments and
  ship a de-review checklist (rename winner → skin.css, delete loser, strip toggle
  markup + CSS + script) — a review affordance must never reach production. (2) Keep
  candidate palettes distinct across the ESTATE, not just within the page — e.g.
  magenta was skipped for austenking because skin-rex already owns that register.
  (3) localStorage persistence means a reviewer who toggled B sees B after reload —
  fine for review, another reason the toggle must be stripped at deploy.

## Config-driven vault reconnaissance (Libby Stage 0 — manifest, never a copy)

- **Problem it solves:** triaging a huge messy personal/corporate archive (thousands of
  files, GBs, heavy duplication) into keep/triage/discard WITHOUT copying, moving, or
  deleting anything, and without silently dropping a single file — every record carries
  a flag and a reason.
- **Where used:** Dex knowledge engineering Gate 0 (2026-07-05),
  `Builds\dex-knowledge-engineering\engine\recon.py`.
- **Sequence:**
  1. Split engine from fill: `anchors.json` (per-person vocabulary: categories, terms,
     weights, vault root) vs `rules.json` (portable: skip classes, junk signals, diagram
     signals, thresholds, dedup bounds). New client = new anchors file only.
  2. Metadata walk first (os.walk + stat) — path/ext/size/mtime; ~10s for 2,341 files,
     zero content reads.
  3. Score relevance on the *relative path* (folders + filename, keyword hits × category
     weight, capped stacking). Content classification deferred to the next stage — keeps
     Stage 0 cheap, deterministic, auditable.
  4. Classify with explicit precedence: skip > junk > diagram/image > score thresholds.
     Every "discard by class" rule gets a relevance escape hatch to triage.
  5. Dedup only size-collision groups: full MD5 ≤8MB, first-1MB above, hard cap, and
     cloud-placeholder detection (`st_file_attributes & (OFFLINE|RECALL_*)`) so a synced
     drive is never mass-downloaded. Canonical = shortest path; duplicates flagged, not
     deleted.
  6. Emit four artefacts: `manifest.jsonl` (every file), `discard-log.md` (every discard
     + reason, grouped), `skipped-log.md` (unprocessable classes for later human review),
     `recon-summary.md` (counts, clusters, method notes + honest caveats) — the gate packet.
- **Gotchas:** topic guesses skew to folder vocabulary (a `CAREER\` tree guesses "career"
  for everything — say so in the packet); over-keep is the safe direction at Stage 0;
  spot-check the DISCARD pile in self-review, not just keeps — that's where the
  Balance-Scorecard PNG bug was caught.

---

## Two-layer local finance/data engine (deterministic core + optional redacted LLM)

- **Problem it solves:** consolidate sensitive data (money) from many source formats into
  one honest view that is cheap+deterministic to re-run, private, and shippable as a
  data-stripped fleet asset — without a "re-run the agent every time" design that fails all
  three. The Libby ingest→normalise→dedup→categorise→view shape applied to money.
- **Where used:** Finance Consolidation Engine, `Builds\finance-engine\` (2026-07-06).
- **The split (non-negotiable):**
  - **Layer A** — deterministic Python, no LLM: ingest→normalise→dedup→categorise(rulebook
    CSV)→reconcile→render. Free, offline, byte-identical re-run. The thing the human runs.
  - **Layer B** — optional saved Claude prompt for JUDGMENT only (seed rulebook, spot
    anomalies, write the letter). Reads ONLY a redacted export. Never in the critical path;
    engine completes with it switched off.
- **Guardrails as capability, not instruction (the gold-standard):**
  - No-send/no-credential enforced by ABSENCE — the package imports nothing network-capable,
    and a unit test greps the source tree for `requests/urllib/socket/smtplib/http.client/…`
    and fails the build if any appears. A guarantee you can test beats a promise in a doc.
  - One `--workdir` is the sole writable root; sources opened read-only. The boundary is
    structural, not a rule to remember.
  - Redaction pass (mask sort codes + 6+ digit runs, drop the raw description column) runs
    before anything model-facing; the redacted CSV is the only Layer-B input.
- **Determinism recipe:** money as `Decimal` quantised to 2dp (never float); composite
  idempotency key `sha1(date+amount+desc+account)`; output sorted by (date, id). Re-dropping
  an overlapping statement can't double-count and the file is byte-identical → testable with
  a run-twice-compare-bytes assertion.
- **Fragile-parser discipline (PDF tie-out):** never trust a blind parse. Capture the
  statement's OWN stated control totals, reconcile parsed-vs-stated in code, and FLAG a
  mismatch to a question log rather than silently accept it. Split extraction (pdfplumber)
  from the pure parse function so the tie-out is unit-testable on captured TEXT — no binary
  fixtures, and it works even when you (correctly) have no access to the real files.
- **Dependency posture:** stdlib core; heavy deps (openpyxl, pdfplumber) OPTIONAL and degrade
  LOUDLY (xlsx→CSV views; PDF→flagged, never silently skipped). Keeps a fresh-machine install
  trivial and the failure mode honest.
- **Machine-owned vs human-owned files:** one file is never both. `transactions.csv` is
  regenerated every run (never hand-edit); `sources/accounts/categories/recurring.csv` are
  hand-edited; `open_items.csv` is append-only by the engine with a stable id per question so
  re-runs never duplicate and never clobber the human's `answer` column.
- **Data-stripped `--template`:** same engine, figure-free skeleton — the shippable asset.
  Verify with a test that the template contains no ledger and no real figures.
- **Gotchas:**
  - openpyxl `read_only=True` holds the Windows file handle open — read all rows into memory
    then `wb.close()`, or temp-dir cleanup fails with WinError 32.
  - Keep local-only secrets (account-number→world map, custodial value) OUT of the build
    entirely — they're hand-entered rows in the local CSV, never in repo/template/redacted/
    board/memory.

## Board-as-message-bus: addressed dispatch envelopes + venue-split runner (phone→named agent)

- **Problem it solves:** a hosted channel (Telegram bot on Railway) must route a human's
  one-line reply to a NAMED agent whose identity (CLAUDE.md/context/memory) lives only on
  the PC — without mounting identities into the cloud, opening ports, or ever falling back
  to bare Claude Code. Also: an unattended builder needs a push channel to the owner's
  phone without holding any token.
- **Where used:** `Datavation/telegram-cockpit` PR #1 (`routing.py` + `runner/local_runner.py`),
  2026-07-07; the §0 build-ops DONE push of the same build.
- **Shape:**
  - **The board is the queue.** The hosted side writes an *addressed envelope* as a card
    comment — `[DISPATCH → <Agent>] from: rex · task: <page_id>` + payload — and re-addresses
    the card (`To=<agent>`, `Action Required=🟡 Agent`) so the queue is human-visible. The
    PC-side runner polls 🟡 cards, parses envelopes, wakes the agent with `claude -p`
    cwd=`Agents\<Name>` (its own gates apply). Runner off ⇒ envelope waits on the card —
    delivery degrades to "picked up on next wake", never drops.
  - **Envelope format is a shared contract** — generator (`routing.dispatch_envelope`) and
    parser (`runner.parse_envelope`) round-trip in one unit test, so producer/consumer can't drift.
  - **Identity gate in the runner:** unknown name (registry) or missing `CLAUDE.md` ⇒ wake
    refused + flagged on the card. Impersonation is impossible, not discouraged.
  - **At-most-once:** mark the envelope comment id processed BEFORE dispatching (Holly
    double-reply lesson); runner completion writes a `[WAKE COMPLETE · agent · ≈$cost]` comment.
  - **Outbound-push-without-secrets:** any agent that can write the board can page the owner —
    flip a card to `🔴 Rex` with the message in `What's needed`; the live cockpit's exception
    sweep delivers to the phone in ≤ its poll interval. Zero tokens outside the cockpit.
- **Gotchas:**
  - Notion comments: write = `POST /v1/comments` (parent.page_id), read =
    `GET /v1/comments?block_id=`; the integration must have the **insert-comments capability**
    enabled — make it an explicit promotion step.
  - Any "push on state X" poller landing on a live board needs **first-run baseline seeding**
    (mark existing state-X rows pushed, send nothing) or promotion floods the phone with history.
  - Reply correlation must remember **every chunk's** message_id of a chunked send — the human
    replies to whichever chunk is on screen.
  - Runner-written comments must not themselves parse as envelopes (distinct prefixes).
  - httpx exception strings embed the request URL → redact at the exception boundary in any
    client whose URL carries a secret (`/bot<token>/`), not just in happy-path logs.

## Engine repath: relative-upward to fleet-root (staged build → live agent home)

- **Problem it solves:** an engine built in `Builds\<build>\` hard-references build-time paths
  (e.g. `tabularium-staging\`); once promoted to `Agents\<Agent>\engine\` those paths break.
  Fix the resolution ONCE so the file works from its live home without a hard-coded absolute.
- **Where it has been used:** Dex/Libby completeness (2026-07-07) — Libby `engine\lookup.py`
  (INDEX → live `Tabularium\Vault\Data\alias-index.json`) and `build_map.py` (scan Canon+wiki /
  emit map+index); Dex read-only `engine\lookup.py` (same live index).
- **Code:** resolve relative to the file's own location, counting parents up to the fleet root:
  ```python
  # promoted home: <fleet-root>\Agents\<Agent>\engine\<file>.py
  #   parents[0]=engine  parents[1]=<Agent>  parents[2]=Agents  parents[3]=<fleet-root>
  TARGET = Path(__file__).resolve().parents[3] / "Tabularium" / "Vault" / "Data" / "alias-index.json"
  ```
  Mirrors the CLAUDE.md `..\..\Tabularium\` rule (up to fleet-root, then across) — invariant
  under a move/rename of the whole fleet because `<root>\Agents\<agent>` + `<root>\Tabularium`
  is structural.
- **Known gotchas:**
  - `parents[N]` index is tied to the PROMOTED depth, not the staging depth. Staged at
    `Builds\<build>\<agent>\engine\`, `parents[3]` resolves to `Builds\` — so the file will NOT
    run correctly from staging. Verify by simulating the promoted `__file__` (or overriding the
    module path var to the live absolute) — don't just run it in place and trust a green.
  - Prove idempotency where the engine both reads and regenerates a live artefact: re-run against
    live and diff output vs the current live file (build_map reproduced the live alias-index
    byte-for-byte — strongest possible signal the repath is correct).
  - Keep write scope inside the agent's permitted tree: build_map reads Canon (read is fleet-wide)
    but writes ONLY Vault\Data (Libby's single-writer wiki tree), never Canon.

## Gold-rail persona migration: mechanical derivation, not hand-carry

- **Problem it solves:** re-seating a live agent's persona/memory onto a new chassis without
  identity drift. Hand-copying prose invites silent re-authoring; "carried intact" becomes
  an unverifiable claim.
- **Where used:** Holly re-base, `Builds\voice-agent-engine-v1\migration\rebase_holly.py` (2026-07-09).
- **Shape:** a migration SCRIPT (idempotent, live source opened read-only) does the carry:
  byte-copy what can be byte-copied (hash both sides into the report); anything that must
  change shape is DERIVED by code from the live source (regex-extract the prompt, apply the
  ruled transformation), then a unified diff old→new goes in the report. Every diff is a
  numbered KNOWN DIFF with its ruling. Re-run any time → report regenerates from live truth.
- **Acceptance twin:** selftest re-hashes carried files against the live source at test time,
  so drift after the migration also fails loudly.
- **Gotchas:** triple-quoted Python prompts with line-continuation backslashes — regex capture
  must apply `"\\n" → ""` or the carried text silently gains stray backslashes; per-entry
  checklists (### sections) catch a truncated copy that hashes would only report as "different".

## Staged-build acceptance vs mock service (prove logic credential-free)

- **Problem it solves:** control gates keep credentials out of staging, but the build must
  still PROVE its integration logic before promotion (retry, catch-up, idempotency).
- **Where used:** `Builds\voice-agent-engine-v1\tests\selftest.py` (2026-07-09) — mock Notion
  (stdlib ThreadingHTTPServer) honouring the real API shape (query-by-key + create), plus a
  dead-port phase for outage behaviour; also the swap-brain-for-mock seam (`ENGINE_LLM=mock`).
- **Shape:** the worker takes its base URL from env (`NOTION_BASE_URL`) so tests point it at
  the mock; outage = dead port; replay = delete state file and assert the store count is
  unchanged. The real-credential first run is then a WATCH item at promotion, not a leap.
- **Gotcha:** put the isolation seam at the protocol boundary (base URL / one env flag), not
  inside business logic — otherwise the tested path isn't the shipped path.

## Measuring streaming latency honestly (SSE/token streams)

- **Problem it solves:** proving first-chunk latency of a streaming endpoint. Two harness
  artifacts routinely fake the numbers.
- **Where used:** voice adapter latency fix, `Builds\voice-agent-engine-v1\tests\selftest_phase2.py` (2026-07-10).
- **Gotchas that produced false readings:**
  - httpx's ASGI TestClient BUFFERS the whole response body — `client.stream()` over it shows
    every chunk arriving together. Streaming is only measurable end-to-end: subprocess the real
    server, hit it over a real socket.
  - Bare `httpx.get/post/stream` calls each construct a fresh client — ~0.5s on Windows
    (SSL cert-store load) — which lands on "time to first byte". Use one persistent
    `httpx.Client`; real callers (ElevenLabs etc.) hold warm connections.
  - Send a warm-up request first: ASGI/threadpool cold-start is not per-turn latency on a
    long-running server.
- **Streaming-endpoint design twin:** prime the generator's FIRST piece eagerly before
  constructing the StreamingResponse — write-ahead guarantees and startup errors then keep
  their non-streamed timing (clean 500 before headers), instead of silently deferring past a 200.

---

## Canonical ops modules with byte-parity-tested deployed copies

- **Problem it solves:** two+ separate builds (e.g. the agent-dispatcher and the telegram
  runner) need the SAME small infrastructure module (lockfile, heartbeat, alerts) but
  cannot import across build folders without fragile sys.path coupling - and plain
  copy-paste is the root disease (vendored drift) the parity suite exists to catch.
- **Where used:** Fleet Console Session 2 (2026-07-14): `single_instance.py`,
  `poller_alerts.py`, `heartbeat.py` - canonical in `Builds\pc-cockpit\ops\`, byte-identical
  copies beside each poller, guarded by `test\test_ops_parity.py`.
- **Sequence:** (1) write the module stdlib-only with NO package-relative imports so the
  same file works as a package member (`from ops import x`) and as a standalone copy
  (`import x`); (2) Copy-Item to each consumer build; (3) a parametrized pytest asserts
  `canonical.read_bytes() == deployed.read_bytes()` for every (module, build) pair -
  drift fails loudly with "re-copy, never fork".
- **Gotchas:** the canonical home needs an `__init__.py` if the host build imports it as a
  package; edits ALWAYS land canonical-first then re-copy (editing a copy passes locally
  and fails the parity test - which is the point).

## Windows PowerShell 5.1 scripts written by tooling must be pure ASCII

- **Problem it solves:** .ps1 files written UTF-8 WITHOUT BOM are read as ANSI/CP1252 by
  Windows PowerShell 5.1 - an em-dash (U+2014) mangles to a sequence containing a CP1252
  smart-quote, which PowerShell treats as a QUOTE DELIMITER: strings terminate early and
  the script fails to parse with baffling errors ("unexpected token", "missing
  terminator") pointing at innocent lines.
- **Where used:** `Builds\pc-cockpit\ops\install-tasks.ps1` (2026-07-14) - first version
  had em-dashes/section-signs and produced 6 phantom parse errors; ASCII rewrite parses
  clean.
- **Rule:** any .ps1 destined for PS 5.1 is pure ASCII (state it in the file header), and
  validate before shipping:
  `[System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw $f), [ref]$err)`
  plus a `[^\x00-\x7F]` regex sweep.
- **Gotchas:** PS 7 tolerates no-BOM UTF-8 fine, so the bug hides if you test in pwsh;
  emoji in strings hit the same class of failure via the cp1252 console encoder
  (UnicodeEncodeError on print) - `$OutputEncoding`/`sys.stdout.reconfigure` for output,
  ASCII for source.

## Visual testing is part of every build's DoD (runbook)

- **Problem it solves:** unit tests prove logic, not the screen — a build passed 57/57
  while its banner/stream states had never been SEEN until they were driven explicitly.
- **Where used:** Fleet Console Sessions 2-3.5 (banner green->red->green, live stream
  pane, attention-first board), fleet-state-view generator (4-tab render) - 2026-07-14/15.
- **The routine:** `Agents\Cody\output\VISUAL-TESTING-RUNBOOK.md` - Part A = what I do
  in-session (safe launch, drive the STATES, DOM assertions, headless-Edge evidence to
  docs\, console clean, declare in handoff); Part B = Rex's 5-minute eyeball.
- **Gotchas:** pages holding an open SSE stream never finish loading - headless Edge
  won't screenshot them (record DOM transcripts instead); stale http.server processes
  squat ports 8791-8797 and block dev servers; always prefer a dry-run mode over a
  live-writing instance. Fleet-DoD adoption is PROPOSED to Archy (standards are his).

## Read-only control gate: (method, path-shape) allowlist, not a verb string-grep

- **Problem it solves:** a plan-stage self-test that forbids the literal string
  `client.post(` as a proxy for "no write call anywhere" breaks once real code exists,
  because some REST APIs expose read-only operations through POST (Notion's
  `POST /v1/databases/{id}/query` is the *only* way to list a database's rows — the
  HTTP verb says nothing about whether the endpoint writes). A string-grep gate can't
  tell a read-only POST from a write-shaped one, and loosening it to "POST is fine" is
  worse — it stops catching a real write call.
- **Where used:** Notion Data Export Pipeline Phase 1, `Builds\Apps\notion-data-export\v1\export.py`
  (2026-07-16) — control gate is a Rex/Archy-mandated permanent no-write requirement.
- **The pattern:** define an explicit allowlist of `(method, compiled path-regex)` pairs
  — one entry per operation actually needed, not per verb. Route every outbound call
  through a single `_request()` chokepoint that checks the call against the allowlist
  and raises before a request is ever sent if it doesn't match exactly. Test the gate
  itself offline (stub transport): assert both an off-allowlist path AND a same-path
  wrong-verb call (e.g. PATCH to a GET-only path) are refused — path-only allowlists
  silently pass a wrong-verb call to an otherwise-allowed path.
- **Gotchas:** if the plan-stage self-test already asserts a cruder proxy (string-grep
  on `client.post(`), don't silently keep it once real code lands — it will fail-closed
  on legitimate reads or fail-open on verb confusion. Replace it and say so explicitly
  in the handoff so the change in enforcement mechanism isn't mistaken for a loosened
  control gate.

## Dual-mode page action: served -> API, file:// -> download (never lose the offline path)

Established on the Fleet Dashboard Vercel build (2026-07-18). A generated HTML page that
must work both hosted and as a local file gets ONE action handler that branches on
`location.protocol`: http(s) -> `fetch()` a same-origin serverless endpoint; `file:` ->
the original download-JSON fallback. The API failure path alerts LOUDLY and then falls
back to the download, so a dead endpoint degrades to the offline workflow instead of a
silent no-op. Pair it with a deploy-repo `vercel.json` rewrite map when generated pages
use folder names (`/Canon-Views/`) that differ from the served layout (`/canon/`), and a
local preview server that emulates those rewrites + stubs the API so the whole loop is
verifiable before any deploy. Secrets stay in platform env vars; a token-leak sweep in the
sync script fails the build if a credential-shaped string reaches a deployable file.

## One component, many self-contained pages: share at BUILD time, never at runtime

Established merging the Docket's and the Kanban's decision UI (2026-07-22). Two
generated HTML pages needed the *same* interactive component, but each had to remain a
single self-contained file — no `<script src>`, no CDN, no fetch — because that is what
lets them open from OneDrive on an iPad. The two constraints look opposed and are not.

- **The pattern:** put the component in a Python module beside the generators
  (`Shared\Boards\_dialog.py`) exporting the CSS and JS as plain raw strings plus the
  marker constants (`MARK_CSS`, `MARK_JS`). Each page template carries those markers;
  a `splice(template)` helper substitutes them at build time and **raises if a marker
  is missing**, so an un-spliced page fails loudly instead of rendering as merely empty.
  The text is copy-inlined into both outputs — one source of truth in the build layer,
  full self-containment in the artefact.
- **Keep the component dumb.** It renders and reports: `render(d, features) -> html`,
  `wire(root, d, features, hooks)`. It holds no state, touches no `localStorage`, writes
  no files, and does not decide what "send" means. Each page passes hooks and keeps its
  own semantics — one batches many answers behind an Update button, the other sends one
  card immediately. Those genuinely differ; forcing them together is how a shared
  component becomes a pile of per-caller branches.
- **Normalize at the boundary.** Callers adapt their own data (`toDecision(card)` /
  `decisionFor(item, action)`) into ONE shape before rendering, and declare differences
  as explicit feature flags (`screenshots`, `immediateSend`, `siblings`, `lockable`,
  `noteBox`, `showRuling`) rather than letting the module sniff which caller it is.
- **Prefix every shared selector** (`dq-`) so it cannot collide with either page's own
  styles, then delete the CSS the module now owns from both pages. Orphaned rules are
  how the "shared" version quietly stops being the one in effect.
- **Why it is worth doing:** the duplication is never only cosmetic. These two copies
  had already drifted on the map deciding which QUEUE a decision lands in — the same
  verdict routed two different ways depending on which page you happened to open. Before
  shipping, run every real input through old-copy-A vs old-copy-B vs the unified version
  and print the table. Four rows moved; each was a bug, but only the table proved which.

