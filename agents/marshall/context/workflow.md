# Context — Workflow & Scripts Catalogue

> Source of truth = the master scripts in `C:\Users\Austen\OneDrive - Datavation Limited\Agent-Fleet\Agents\Marshall\scripts\` (edited here), deployed to `G:\My Drive\Clients\TP Group\Marshall Scripts\` (run here). This file summarises them; if it disagrees with the code, the code wins — then update this file. `Claude Scripts\` is legacy.

## End-to-end daily workflow — `TPG-Daily-Workflow.ps1`
Interactive 4-step entry point. Run from `G:\My Drive\Clients\TP Group\Marshall Scripts\`. `$root` = parent of script folder = `G:\My Drive\Clients\TP Group`.

**Parameters:** `-Date` (default today), `-DVJobsJson`, `-MaintenanceJobsJson`, `-SkipDV`, `-SkipMaintenance`, `-FromStep 1-4`, `-DryRun`, `-ClientId TPG|Equans` (default TPG).

- **STEP 1 — Preview & confirm:** runs `New-TPGReport.ps1 -PreviewOnly` per active type, lists DV and Maintenance jobs, prompts `[Y]/[N]/[A]` (A = re-check). Skips empty types. Exits if zero jobs.
- **STEP 2 — Folders + records:** runs `-CreateFoldersOnly` per type, dedupes by folder path, assigns `job_type` (`door_ventilation` / `property_maintenance` / `''` if both). Writes a `job_record.json` per job folder (**never overwrites**; `job_id` = `REX-<date>-NNN`) and always overwrites `day_manifest.json`. Then runs `Sort-TPGPhotos.ps1 -Date`, then pauses for manual photo checking. `-DryRun` prints intended JSON and exits before sorting.
- **STEP 3 — Build DOCX:** builds DoorVentilation, then Maintenance (`-SkipPDF`), then pauses for Word review (manually drag DV photos into room tables).
- **STEP 4 — Export PDFs:** runs `Export-TPGPdf.ps1 -Date`.

`Launch-DailyWorkflow.bat` prompts for one or more space-separated dates and loops the workflow for each.

## Active scripts
| Script | Purpose |
|---|---|
| `TPG-Daily-Workflow.ps1` | Main 4-step interactive wrapper (entry point) |
| `New-TPGReport.ps1` | The builder: fetch jobs (ICS/JSON), create folders, fill template text, insert photos, footer, export PDF. Modes: `-CreateFoldersOnly`, `-PreviewOnly`, `-NoConfirm`, `-SkipPDF`, `-Force`, `-JobsJsonFile` |
| `Export-TPGPdf.ps1` | Recurses date folder for `*.docx` (excludes `~$*`), exports PDF via Word COM. Skips up-to-date PDFs unless `-Force`; `-FolderName` limits to one job |
| `Sort-TPGPhotos.ps1` | Moves Timemark photos into matching job folders (fuzzy address match) |
| `New-TPGDraftEmail.ps1` | Builds the weekly summary Gmail draft (OAuth, `gmail.compose`). `-Date` single day, `-Dates a,b` combines multiple days into one email (subject auto = day / `w/c` week / range), `-Note "..."` adds free-text (newlines → `<br>`) after the report list, before the sign-off — use for one-off remarks e.g. provisional booking dates |
| `New-TPGSchedule.ps1` | **SHELVED — not the active method.** Calendar-write script (Calendar API, OAuth `calendar.events`). The scheduling workflow uses the **Calendar MCP in-session** instead (supervised weekly; keeps deletes confirmed, no new write-scope OAuth). Kept in `scripts\` (not deployed) for possible future *unattended* use — would first need the plaintext-secret fix + a confirm-before-delete guard. See `routines/scheduling.md`. |
| `apply_bom.ps1` | Re-saves the two main scripts as UTF-8 **with** BOM |

**Active set** (in `scripts\` master + `Marshall Scripts\` run): the six scripts above plus `Launch-DailyWorkflow.bat`.

**Legacy / superseded (left in `Claude Scripts\`, do not use):** `Process-SiteReports.ps1`, `TPG_Build_Reports.ps1`, `TPG_Build_Maintenance_2026-02-27.ps1`, `New-WorkflowGuide.ps1`, `check_tools.ps1`, `check_files.ps1`, `convert_single.ps1`, and any `.bak` files.

## Job source — ICS / Google Calendar
- Secret iCal URL hardcoded in script CONFIG (also in the email script).
- **Event naming:** `Client - JobType - Address` preferred; loose fallback `Client - <addr|jobtype>`. Events with **no recognised client prefix are dropped**.
- **Door-undercut classification:** job-type word matching `\bundercuts?\b` → DoorVentilation; everything else under a valid client → Maintenance.
- **Address resolution:** cleaned SUMMARY, else `LOCATION` field, else `Address:` line in DESCRIPTION (fills town/postcode). Notes prefer text after the first blank line (completion notes); strip `Contact:` lines.
- **jobs.json fallback** (`-JobsJsonFile`): array of `{FolderName, Addr1, Addr2, [Addr3, Addr4, ClientName, Notes]}`. `FolderName` must match the existing folder exactly. JSON path **bypasses** the client-prefix filter — use it when ICS abbreviations don't match folder names.

## TPG invoice summary — in-session routine

Triggered by "invoice summary", "run invoice", or after completing the daily workflow + client email draft.

**Not a PS script** — runs in-session using Google Calendar MCP + Gmail MCP.

**Steps:**
1. Read `C:\Users\Austen\OneDrive\Documents\Claude\business-context.md` for process reminders (materials recharge, incomplete jobs checklist).
2. Call `list_events` on the primary calendar (info@rexhomeservices.co.uk) for the relevant work dates, `fullText: "TPG"`, `timeZone: Europe/London`. Find actual TPG work days — do **not** assume Thu/Fri.
3. Classify events: summary matches `\bundercuts?\b` → Undercuts; else → Maintenance. Ignore non-job events (Holly briefings etc.).
4. Extract: door count from description ("X of Y doors undercut"); maintenance summary from visit notes ("Visit Note" text, else job line). Hours = event end − start.
5. Format as a dense block (no blank lines anywhere — Monzo constraint):
   - `Undercuts | <Day> <D>-<Mon> |` then one address line per job: `<address> (<N> doors)`
   - `Maintenance | <Day> <D>-<Mon> |` then: `<address> — <summary> (<Xh>)`
   - Chronological day order; Undercuts before Maintenance within each day; empty sections omitted.
6. **Create a calendar event** (Calendar MCP, `info@rexhomeservices.co.uk`) at the closest upcoming half-hour on the current day — a 30-min block, popup at start (0 min), `AVAILABILITY_FREE`, title `TPG Invoice Summary — <Day> <D>`, description = the Monzo paste block + flags. **Not a Gmail draft** (corrected 2026-07-12). Full spec: `routines/pre_invoice_review.md` step 6 + [[feedback-pre-invoice-event]].
7. Report: dates, job counts, flags raised.

**Flags to surface:** missing door counts, failed/incomplete visits (do not invoice), deferred jobs needing reschedule.

**Format note:** "no blank lines" rule is Monzo-specific. Update when Austen moves to QuickBooks.

**CoWork task `tpg-invoice-email`** covers the same function but has a hard Thu/Fri date assumption — breaks non-Thu/Fri weeks. Marshall's version is date-agnostic. CoWork task can be retired once Marshall version is proven.

## Notion TPG Jobs sync — DEX-TPG-NOTION-001

Full run logic in `routines/notion_sync.md`.

**What it does:** scans G Drive TP Group folder for new date folders → creates a structured Notion record per job.
**Runs:** daily at 11:01 AM via CoWork scheduled task `dex-tpg-notion-001`. Also runnable in-session on demand.
**Tools:** Drive MCP (`search_files`, `download_file_content`, `read_file_content`) + Notion MCP (`notion-search`, `notion-create-pages`, `notion-update-page`).
**State:** `tpg_notion_sync_state.json` in CoWork TPG-Equans folder — tracks processed date folders.
**Notion DB:** https://www.notion.so/df6346822484475888cb06e6619f4e90
**Known issue:** Place (Maps View) field must be set via `notion-update-page` after page creation — do this for every new record.
**Analytical fields (added 2026-06-01):** `Doors Undercut`/`Doors Total` (number, DV only — `TPG-Daily-Workflow.ps1` now writes `doors_undercut`/`doors_total` into `job_record.json`), `Client` (select), `Hours` (number, deferred), plus formulas `Doors Outstanding` and `Status`. Views: By Date, By Address, By Job Type, Revisits Needed, Map. Mapping + rules in `routines/notion_sync.md`.
**Interactive:** Marshall can answer job-history queries (by address, date, type) using `notion-search` + `notion-fetch`.
**Future:** share a filtered read-only view with Equans/TPG once Place field is populated and a contract view is created.

## Photo handling — `Sort-TPGPhotos.ps1`
- Source: `Timemark\`. Filenames: `Timemark-YYYYMMDD-HHMM-<addr tokens split by ->.jpg`.
- Parses tokens from index 3; strips from the first country token (England/Scotland/Wales/Northern/Ireland) onward (drops postcode).
- **Match scoring:** short folder words (<5 chars, incl. house numbers) need **exact** match; words ≥5 chars tolerate Levenshtein ≤1 (handles geocoding typos, e.g. Sackvylle↔Sackville). All folder words must match or score = -1. Highest score wins.
- Ties / no match → left in `Timemark\` for manual handling. Identical filename already at destination → **skipped, not overwritten** (listed as "not moved").
- `-WhatIf` for dry-run.
