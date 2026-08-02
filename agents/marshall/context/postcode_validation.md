# Context — UK Postcode & Address Validation

> A cross-cutting skill used wherever Marshall reads addresses from an external source (Tonia's sheet, Timemark filenames, geocoded data). Tonia's sheet routinely misspells street/village names; the **postcode is the reliable anchor** because it is structured, checkable, and rarely wrong. Use it to confirm or correct a doubtful spelling before it lands in a calendar event or a report folder name.

## Why this exists
- Sheet typos already caught: **Keresy → Kersey** (Avenue, Great Cornard, CO10 0DZ). The postcode unambiguously identified the correct street/town.
- **"Sackvylle" is the correct spelling** for Sackvylle Street, Debenham (IP14 6RJ) — confirmed 2026-06-10 via postcode lookup. A previous entry incorrectly listed this as a typo to fix; do not change it.
- Standing rule reminder: **never invent** an address. Validation *confirms* against an authority (postcode lookup / mapping); it does not guess. If lookup is inconclusive, flag to Austen — don't pick a spelling.

## UK postcode format
Structure: **outward code** (before the space) + **inward code** (after the space).
- **Outward** = area (1–2 letters) + district (1–2 digits, occasionally a trailing letter for dense London districts). 2–4 chars, always starts with a letter.
- **Inward** = sector (1 digit) + unit (2 letters). Always exactly 3 chars, always starts with a digit.
- There is **always a single space** before the inward code.

Six valid patterns (A = letter, 9 = digit):
| Pattern | Example |
|---|---|
| `A9 9AA` | `W1 1AA` |
| `A99 9AA` | `M60 1NW` |
| `A9A 9AA` | `W1A 0AX` |
| `AA9 9AA` | `CO7 6QY` |
| `AA99 9AA` | `CO10 0DZ` |
| `AA9A 9AA` | `EC1A 1BB` |

Total length 5–7 alphanumerics (excluding the space).

### Letter constraints (use these to spot OCR/typo errors)
- **First position:** never `Q`, `V`, `X`.
- **Second position:** never `I`, `J`, `Z`.
- **Final two letters (unit):** never `C`, `I`, `K`, `M`, `O`, `V` (chosen to not resemble digits/each other in handwriting).

### The O-vs-0 trap (high value, common)
A postcode's **digit positions** (district number(s) and the sector digit) must be **numerals**, and its **letter positions** must be letters. The most common corruption is letter `O` typed where digit `0` belongs (and vice-versa).
- In `CO10 0DZ`: positions are `C`(letter) `O`(letter) `1`(digit) `0`(digit) [space] `0`(**digit, the sector — must be zero, not O**) `D`(letter) `Z`(letter).
- Rule of thumb: the character immediately **after the space is always a digit** — if it reads as `O`, correct it to `0`. Likewise the district number(s) before the space are digits.

## Cross-check procedure (when a name looks doubtful or two sources disagree)
1. **Take the postcode as the anchor.** Validate its shape against the patterns above; fix any obvious O/0 (or I/1, S/5) confusions first.
2. **Look the postcode up** to get the authoritative street + locality + post town:
   - **Mapping connector** if one is wired in (none currently in this project — check `list_connectors` before assuming).
   - Otherwise **`WebSearch`** the postcode (e.g. `"CO10 0DZ" street Great Cornard`) — streetcheck.co.uk, checkmypostcode.uk, postcode lookups return the street/town. **`WebFetch`** a result page if you need to confirm.
3. **Compare** the looked-up street/town to the sheet spelling. If they match a known street and differ only in spelling, **use the authoritative spelling** and record *why* in the event description / folder note (e.g. `confirmed via postcode CO10 0DZ`).
4. **If inconclusive** (postcode maps to a different street, or covers several), **flag to Austen with both candidates** — do not choose silently.
5. **Work-schedule text still wins** over geocoded data on genuine conflicts (standing rule) — but a *spelling* correction confirmed by the postcode is a correction, not a conflict.

## When an address is incomplete (no street/town/postcode at all)
Sometimes a job comes in as just a house number + partial name — e.g. Gary's ad-hoc snag emails often give "8 Vicary" or "37 Kersey" with nothing else. **Before flagging this as unresolved and asking Austen, search Marshall's own history for a match** — these are usually repeat properties:
1. **Notion REX Addresses DB first** (`data_source_id: 31555f77-ee9c-48ed-8d3d-df77fd240c64`) — this is the deduplicated master property list (one row per address, not per job), so it's the fastest match. Query `Address`/`Town`/`Postcode` for the partial street name via `notion-query-data-sources` (SQL, e.g. `WHERE "Address" LIKE '%Vicary%'`). If found, this is also the record to link the new job's `Address` relation to (see `routines/scheduling.md` step 7a). Fall back to the REX Jobs DB (`52ace12c-464d-46c5-8f58-20ab49ecea98`) only if the Addresses DB has no match.
2. **Previous Equans booking sheets** in `G:\My Drive\Clients\TP Group\Equans\` — grep past `Booked For ... .xlsx` files for the street name; Rex has done multiple passes over these properties before.
3. **Previous job folders** under `G:\My Drive\Clients\TP Group\Jobs\YYYY-MM-DD\<Address, Town>\` — folder names carry the full address.
4. If a confident match is found (same house number + street name, no ambiguity), **use it** and note the source (e.g. "address from REX-2026-05-14-003, confirmed same street/number"). If two properties could plausibly match, or nothing turns up, **flag both candidates / the gap to Austen** — don't guess a postcode.
This costs one query round-trip and should always be tried before creating an "address needed" placeholder — Austen has often already attended these properties.

## Known corrections (apply on sight)
| Sheet spelling | Correct | Confirmed by |
|---|---|---|
| Keresy Avenue, Great Cornard | **Kersey Avenue** | CO10 0DZ |
| ~~Sackvylle Street~~ | **Sackvylle Street is correct** — do not change | IP14 6RJ (confirmed 2026-06-10) |

## References
- UK postcode format: https://ideal-postcodes.co.uk/guides/uk-postcode-format
- Letter-position rules: https://www.postcodearea.co.uk/facts/formats/ ; https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom
- Full government spec (ILR Appendix C): https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/611951/Appendix_C_ILR_2017_to_2018_v1_Published_28April17.pdf
- Format guide: https://legalclarity.org/united-kingdom-postcode-system-structure-and-format/
