# Context — Tools, Paths & Configuration

## Paths
- `$root` / `RootFolder` = `G:\My Drive\Clients\TP Group` (hardcoded in `New-TPGReport.ps1`; derived as parent of the script folder elsewhere).
- **Master scripts (edit here):** `C:\Users\Austen\OneDrive - Datavation Limited\Agent-Fleet\Agents\Marshall\scripts\`
- **Run scripts (execute here):** `G:\My Drive\Clients\TP Group\Marshall Scripts\`
- Legacy scripts: `G:\My Drive\Clients\TP Group\Claude Scripts\` (to be archived)
- Photo source: `G:\My Drive\Clients\TP Group\Timemark\`
- Templates (builder reads these): the two `...- TEMPLATE.docx` at the TP Group root.
- Output: `G:\My Drive\Clients\TP Group\Jobs\YYYY-MM-DD\<Address, Town>\`

## PowerShell / encoding rules
- Target **PowerShell 5.1+** (Windows PowerShell).
- **Scripts need a UTF-8 BOM.** The Write/Edit tools save `.ps1` without a BOM; PS 5.1 then reads them as Windows-1252 and corrupts non-ASCII chars (box-drawing `─ ═`, en/em-dashes, emoji), breaking the parser. After editing a script in the **master**, re-apply the BOM before deploying: `apply_bom.ps1` does this for `New-TPGReport.ps1` and `TPG-Daily-Workflow.ps1` and now targets `$PSScriptRoot`, so run it from whichever folder the scripts sit in. Extend its file list if you add BOM-needing scripts. (`New-TPGDraftEmail.ps1` and `Export-TPGPdf.ps1` ship without a BOM and run fine — leave them.)
- **Data files are the opposite — NO BOM.** `job_record.json`, `day_manifest.json`, `job_types.json`, and the OAuth cache are written via `UTF8Encoding($false)`. Do not add a BOM to these.

## Calendar (ICS)
- Secret iCal URL for `info@rexhomeservices.co.uk` is hardcoded in CONFIG in both `New-TPGReport.ps1` and `New-TPGDraftEmail.ps1`. No OAuth — it's a secret URL. One-time setup: paste the URL into `$CONFIG.IcsUrl`.

## Gmail (email drafts)
- `New-TPGDraftEmail.ps1` uses Gmail REST + OAuth, scope `gmail.compose`, token cached in `Marshall Scripts\.gmail-oauth.json` (run folder only — not in the master).
- Drafts only — no send capability via the MCP. Outlook MCP is read-only.
- ⚠ **SECURITY FLAG:** the OAuth **client ID and secret are committed in plaintext** in `New-TPGDraftEmail.ps1`. Flagged for Austen — consider moving to an untracked config / environment variable.

## job_types.json
- Auto-growing registry (`Register-JobTypes`), written **no-BOM** as `[{...}]`.
- Guarded against a prior single-entry serialisation bug (`@($registry)`).
- ⚠ **Known data-quality issue:** the registry stores the raw job-type word (often the whole `JobType | Address` blob when the second dash is missing), so entries can be **misclassified** (e.g. `"Door Undercuts | 12 Queens Close"` stored as `property_maintenance`). It does not reliably reflect true type — do not depend on it for classification; the `\bundercuts?\b` regex on the live event is authoritative.

## Weekly summary email format (`New-TPGDraftEmail.ps1`)
- **Body is HTML** (switched 2026-06-08). MIME part is `text/html; charset=UTF-8` with `Content-Transfer-Encoding: base64`.
- Structure: date heading (bolded `<strong>`) → report-type line → per-address line (indented `&nbsp;`) with door-count suffix where available. Each date block is a `<p>`.
- **Totals are conditional** — "Total doors undercut" line only emitted when count > 0; "Total maintenance reports" only when count > 0. No blank total lines.
- **Signature emojis** use HTML entities (`&#x1F4DE;`, `&#x1F4F1;`, `&#x1F310;`) — avoids UTF-8 garbling in plain-text MIME. Do not embed raw emoji in the script source.
- Enriched from the Google Calendar ICS feed (door counts from completion notes; event duration for maintenance hours).
- Subject logic: single day / "w/c" / same-month "&" / date range.
