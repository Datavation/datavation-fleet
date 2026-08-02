# Context — TP Group (Client & Business)

## Who TP Group is
- **TPG / TP Group / Total Protection** — all names refer to the same organisation. Primary client of the field workflow.
- Work delivered: property maintenance and door ventilation/undercut jobs across multiple addresses, scheduled via Google Calendar.

## Business model & client chain (important)
- **Datavation Ltd** = the brain. Marshall is a Datavation-owned agent.
- **Rex Home Services** (Austen) = the field business that does the work and owns the output. **Rex subcontracts for TP Group.**
- **TP Group** = the contractor Rex subcontracts *for*. Cc'd on reporting.
- **Equans** = the **ultimate client**. The reporting is addressed *to* Equans.
- Chain: Rex → (subcontracts for) → TP Group → (ultimate client) → Equans.
- The same workflow could be re-pointed at another client — keep it generic where possible.

## Key people / contacts
- **Austen King** — sole operator of Datavation and Rex. No team, no handoff considerations.
- **Tonia Weller** (`Tonia.Weller@equans.com`) — scheduler; sends the weekly Excel job sheet (front-half workflow). Also Cc on the weekly report summary.
- **Sam Bollen** — former TPG contact, has left.
- **Ellie Francis** (`ellie@thetpgroup.co.uk`) — TPG billing contact; primary To: on client-facing invoice emails. Greeting: "Hi Ellie,".
- **Will Smith** (`WillS@thetpgroup.co.uk`) — TPG contact; Cc on invoice emails.
- **Jack Darby** (`JackD@thetpgroup.co.uk`) — TPG contact; Cc on invoice emails.
- **Eastern County Clearances (ECC)** — Dan Keen, partner business.
- **Accredited Home Services (AHS)** — Ian Jack, partner business.

## Email recipients (weekly ETA / scheduling draft)
- The **ETA summary** (front half — after scheduling) goes **To:** Tonia Weller; **Cc:** Gary Wenlock (`gary.wenlock@equans.com`), Bradley Anderson (`Bradley.Anderson@equans.com`). Different from the report summary below. Draft only.
- **Gary Wenlock (Equans) — comms preference (2026-06-19):** prefers a **phone call** over text/email. Don't default to drafting Gary an email; he won't mind not getting one. He also sometimes sends **ad-hoc snagging lists directly** (with the address order he wants), bypassing Tonia's weekly sheet — when that happens, load the jobs to calendar in *his* stated order, classify as Maintenance unless told otherwise, and **no ETA email** is needed (the ETA email is Tonia's, for the scheduling flow).

## Email recipients (weekly summary draft) — CONFIRMED correct
- **To:** Equans contacts — becky.sewell@equans.com, gary.wenlock@equans.com (the ultimate client)
- **Cc:** TP Group — Tonia Weller, Bradley Anderson, Will Smith / Jack Darby @thetpgroup.co.uk (the contractor Rex subcontracts for)
- Body greeting: "Dear Becky".
- This To/Cc split is **intended** (Equans = client, TPG = contractor). Not an error. Still: drafts only, Austen sends.

## Clients supported by the scripts
- `-ClientId TPG` (default) and `-ClientId Equans` are both recognised. Client prefix on calendar events is matched fuzzily (TPG within 1 edit, Equans within 2).

## Paths (live data lives in the Drive, not here)
- `$root` = `G:\My Drive\Clients\TP Group\`
- Run scripts: `G:\My Drive\Clients\TP Group\Marshall Scripts\` (legacy `Claude Scripts\` to be archived)
- Photo source: `G:\My Drive\Clients\TP Group\Timemark\`
- Templates (used by scripts): the two `...- TEMPLATE.docx` files at the TP Group root.
- Per-job output: `G:\My Drive\Clients\TP Group\Jobs\YYYY-MM-DD\<Address, Town>\` (dated folders moved under `Jobs\` 2026-06-22; scripts still write the old root — see MEMORY.md Output flag).
