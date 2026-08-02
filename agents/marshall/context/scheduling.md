# Context — Weekly Job Scheduling (Tonia's sheet → calendar)

> The **front half** of the TPG/Equans cycle. Tonia sends a weekly Excel job sheet; Marshall turns it into a routed, time-constrained set of calendar events, then drafts an ETA confirmation back to her. The **back half** (after the work is done) is the site-report workflow in `workflow.md`.
>
> Source of truth for *people/recipients* = `New-TPGSchedule.ps1` CONFIG + `New-TPGDraftEmail.ps1` CONFIG (code wins). Source of truth for *calendar mechanics* = `New-TPGSchedule.ps1`.

## The two halves must stay coherent
The events Marshall creates here are later **consumed** by the reporting workflow's ICS parser (`New-TPGReport.ps1`). So event titles **must** follow the reporting side's expected shape:
- `TPG - Undercuts - <first line of address>` for door-undercut jobs (the word `Undercuts` is what the reporting side's `\bundercuts?\b` regex keys on → DoorVentilation).
- `TPG - Maintenance - <first line of address>` for everything else → Maintenance.

Get the title wrong here and the report builder will misclassify the job weeks later.

## 1. People (confirmed from script CONFIG)
| Person | Role | Address |
|---|---|---|
| Tonia Weller | Equans/TPG scheduler — sends the weekly Excel sheet | Tonia.Weller@equans.com |
| Gary Wenlock | Cc on ETA summary | gary.wenlock@equans.com |
| Bradley Anderson | Cc on ETA summary | Bradley.Anderson@equans.com |
| Austen King | Rex Home Services operative | info@rexhomeservices.co.uk |

> The attached v1.0 brief listed Tonia as `sam.bollen@equans.com` and Gary/Bradley as TBC — **stale**. The working scripts carry the live addresses; those win. Sam Bollen has left.

## 2. The weekly job sheet
- Tonia emails a weekly Excel spreadsheet (`.xls` legacy or `.xlsx`), one row per job.
- Subject typically `Booked For Austin [dates]` (note: "Austin", her spelling) — **but subjects are unreliable** (one said "May" when the file/dates were June). Trust the filename and sheet.
- **Ingestion:** Marshall cannot fetch the attachment from Gmail (no MCP download tool; API 403s on `gmail.compose`). **Austen saves the sheet into `G:\My Drive\Clients\TP Group\Equans\`** (the established inbound folder); Marshall reads the newest `Booked For ... .xlsx` there via the `xlsx` skill / Drive MCP.
- Still read the covering email via Gmail `get_thread` and **check for `RE:` follow-up amendments** — Tonia sends extra instructions as replies.
- Columns: property address (full, incl. postcode), resident name, phone(s), job type / instruction notes, access notes (key-safe codes, VOID flags, time constraints), day assigned (usually spread across two days).
- **Legacy `.xls`** reads with the `xlrd` engine (`pd.read_excel(file, engine='xlrd')`) or the `xlsx` skill.

### Time-constraint keywords (honour before geography)
| Keyword | Meaning |
|---|---|
| `First appointment` | 08:30 start |
| `AM` | start before 12:30 |
| `Before X` | arrive before X |
| `After X` | do not arrive before X |
| `VOID` | property empty — flexible, schedule **last** in the day |
| `All day` | no constraint |

## 3. Calendar — scheduling rules
- **Calendar:** `info@rexhomeservices.co.uk` (resolve the id via `list_calendars`). **Never `primary`.**
- **Notifications:** always off — `sendUpdates: none`, reminders cleared. No reminders, no guest emails.
- **Mechanics:** the **Google Calendar MCP**, in-session (`list_events` / `create_event` / `update_event` / `delete_event`). Chosen over a PS script because this task is supervised weekly — it keeps the destructive delete human-confirmed and needs no new write-scope OAuth. `New-TPGSchedule.ps1` is **shelved** (in `scripts\`, not deployed) for any future unattended use.
- **MCP quirk:** `create_event` silently drops `location` — always follow each create with an `update_event` to set it. (Same quirk as the reporting workflow.)

### Slots & duration
- 2-hour slots from 08:30: **08:30, 10:30, 12:30, 14:30, 16:30** (last ends 18:30).
- Working hours 08:30–18:30 max.

### Diary constraints (Austen)
- **Thursday football 18:00** — **currently off-season as of 2026-07-08, expected back ~Sep 2026** (confirm with Austen before reapplying — don't assume the date). While off-season, Thursdays run the normal 08:30–18:30 slot grid same as any other day, no early cutoff. When back in season: no TPG job may finish after **17:30** on a Thursday. With 2-hour slots that caps the last Thursday start at 14:30 (ends 16:30); a 15:30 start (ends 17:30) is the absolute latest. Practically ~4 jobs on Thursdays.
- **Home base:** West Bergholt, near Colchester, Essex — first and last jobs route from/to here.

### Routing logic
- Honour all time constraints **first**, then optimise geography.
- Start from West Bergholt and work outward; cluster same village/road back-to-back.
- VOID properties go **last** in the day's sequence.

### Event format
| Field | Value |
|---|---|
| Title | `TPG - Undercuts - <addr line 1>` or `TPG - Maintenance - <addr line 1>` (see "two halves" above) |
| Location | full address incl. postcode (e.g. `14 Rectory Close, Raydon, Ipswich, IP7 5LS`) |
| Description | resident name, phone(s), job notes, access instructions |
| Start | per slot; first job 08:30 |
| Duration | 2 hours |

### Placeholders to clear first
Before creating events, delete any of these on the target dates — **but show Austen the matched list and get a yes first** (the only destructive step):
- `TPG - Provisional`
- `Blocked – Equans (TPG)` (match loosely as `^Blocked.*Equans`)
- `TPS - PROV`

## 4. ETA summary (draft to Tonia)
After events are created, re-read the calendar to confirm the final order, then produce a **plain-text** ETA summary.

**Format rules:** street name + village only — no postal town, no postcode, no resident names. One line per job, grouped under a day heading. **Subject:** `ETAs - <day> <date> & <day> <date>` (no "TPG" prefix). **Annotate any task that came from a follow-up `RE:`** as an addition in parentheses, so Tonia sees it's extra to the original sheet.

```
Thursday 21st May
14 Rectory Close, Raydon - ETA 08:30
31 Rectory Close, Raydon - ETA 10:30
19 Kersey Avenue, Great Cornard - ETA 10:30 (added from your follow-up - remove scaffold bolt)
...
```

**Signature:** Gmail does NOT auto-append — **always embed it in the body** after "Thanks, Austen". Canonical text in `MEMORY.md`.

**Distribution:** To **Tonia Weller**; Cc **Gary Wenlock, Bradley Anderson**. **Draft only — never send.** Gmail draft for Austen to review.

## 5. Tools & materials summary
After scheduling, produce a job-notes summary in two sections:
1. **Per address** — brief of what needs doing.
2. **Aggregated tools & materials** for the day(s), grouped by type.

Common materials: mould-wash solution; vent-blocking (foam, filler, cover plates); sealant/silicone cartridges; pointing mortar; interior filler; stepladder/access kit; cloths/scrapers.

## 6. Monthly provisional blocking
At the start of each month, block every **Thursday and Friday** of the coming month as `TPG - Provisional`, 08:00–17:00, notifications off — `create_event` per day via the Calendar MCP. Then draft (never send) a note to Tonia listing the blocked dates by week and asking her to advise ASAP if any are not needed, so Austen can release them.

## 7. Data-quality notes
- **"Sackvylle" is the correct spelling** for IP14 6RJ (confirmed 2026-06-10 via postcode lookup). Do NOT correct it to "Sackville" — that was a previous error now fixed.
- Spreadsheet spells "Keresy Avenue" — correct to **Kersey Avenue** (confirmed via postcode CO10 0DZ, Great Cornard).
- **Doubtful street/village names: verify against the postcode** (the structured, reliable anchor). Fix `O`/`0` errors (char after the space is always a digit), then look the postcode up (mapping connector if available, else `WebSearch`) and use the authoritative spelling, recording why. Inconclusive → flag both candidates, never guess. Full skill: `context/postcode_validation.md`.
- Resident name sometimes missing — note it in the description and **flag to Austen**, never invent.
- Work-schedule text overrides any geocoded address/notes when they conflict.
