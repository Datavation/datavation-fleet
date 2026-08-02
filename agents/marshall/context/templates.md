# Context — Report Templates & DOCX Logic

> Templates used by the scripts are the two `...- TEMPLATE.docx` files at the **TP Group root** (`G:\My Drive\Clients\TP Group\`):
> - `TPG Property Maintenance Site Report - TEMPLATE.docx`
> - `TPG Door Ventilation Site Report - TEMPLATE.docx`
>
> (The `Templates\` subfolder holds differently-named output-naming templates — not the ones the builder reads.)

## DOCX manipulation method
No Word COM for text edits: the `.docx` is unzipped, `word/document.xml` edited as raw XML (`System.Xml.XmlDocument`), then repacked. A `.docx.new` temp file marks an in-progress repack (safe to delete if a crash leaves one).
PDF export *does* use Word COM (`Export-TPGPdf.ps1`).

## Two report types
### Maintenance (`Insert-AllImages-Maintenance`)
- Date format: `ddd dd-MMM-yyyy` (e.g. `Tue 17-Mar-2026`).
- Word forces A4 (21 × 29.7 cm), 1.27 cm margins.
- PDF exported immediately.
- Template now contains **3 generic blank "Room - Task" tables** (changed 2026-06-01 from 8 named rooms) for manual use, plus the Auto-Inserted photo table.

### Door Ventilation (alias "Undercut", normalised to DoorVentilation)
- Date format: `dd-MMM-yy` (e.g. `17-Mar-26`).
- Page setup left as template.
- **PDF deliberately deferred** — exported later by `Export-TPGPdf.ps1` after manual photo sorting.
- Keeps its **named room tables** (Kitchen, etc.).
- Builds a "Doors undercut: X of Y" line by regex-scanning notes (`\d+ of/out of \d+`), defaulting to `X of Y`.

## Photo / image insertion — detection-based (important)
- **Preferred path (`Insert-IntoAutoInsertedTable`):** if a body table's header cell text == `"Auto-Inserted"`, all photos drop into *that* table (3 per row), every other table untouched. Column widths read from the table grid (fallback `3617/3224/3644`).
- **Legacy fallback:** if no Auto-Inserted table exists, the old logic runs — Maintenance deletes **all** tables and builds one big 3-col photo grid; DV inserts a photo table before the first room table.
- **Why detection-based:** Austen added the "Auto-Inserted" table to both templates so photos land in one obvious place and the room/Room-Task tables stay empty for manual dragging. The old delete-all-tables logic would destroy that structure — hence the guard.
- Photos sorted by filename; height fixed 6 cm (2160000 EMU), width scaled to aspect ratio. A spacer paragraph sits before the DV Auto-Inserted table so Word doesn't render touching tables.

## Template placeholders
Replaced in `word/document.xml`:
- `[JOB TYPE]` — Maintenance template only.
- `Address Line 1` / `2` / `3` / `4` — replaced with the job address.
- **Date** — a fixed **5-run XML pattern** with literal `DD/MM/2026` and rsid values `00F77F5B` / `00E31285` (SubtleReference style). **Will break silently / log a WARNING if the template's date runs are re-saved in Word.** Do not edit the date in the template by hand.
- Notes block inserted after the `Austen King` paragraph (`Job Notes:` / per line / DV `Doors undercut:` / `Visit Notes:`).
- Filenames use `YY-MM-DD`.

## Gotchas
- `PaperSize = 9` produces **A5** on this machine — Maintenance uses explicit `CentimetersToPoints` for A4 instead.
- Orphaned headless `WINWORD` after a crash → `Stop-Process -Name WINWORD -Force`.
- Word lock file `~$filename.docx` blocks re-runs with `-Force` — remove it first.
- PDF export fails if the PDF is open in Acrobat — close and re-run.
