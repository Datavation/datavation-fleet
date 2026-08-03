# Quinn — Memory Log (append-only)

Black-box recorder per Agent-Architecture-Memory v0.2: every change Quinn makes to
`memory.md` is appended here as `DONE`; every architecture-touching change (a standard,
another agent, shared IP, her own routine contracts) is appended as `PROPOSED` and held —
never self-applied. Never edited, never overwritten, never loaded as authority.

Entry format:
```
## [Timestamp] Quinn — [DONE | PROPOSED] — [Brief label]
Entry: MEM-0NN (or "new")
Class: OPERATIONAL | ARCHITECTURE
Change: …
Previous: …
Circumstance: …
Reason: …
```

---

## 2026-07-14 Quinn — DONE — First config + consolidation memory
Entry: MEM-001, MEM-002, MEM-003
Class: OPERATIONAL
Change: Recorded RHS=Monzo (not QB), mortgage letters carry no balance (manual lines), and net-flow≠true-balance anchoring facts.
Previous: memory empty at birth.
Circumstance: First workdir config + first consolidation run for client-0 (Rex), 2026-07-14.
Reason: Durable "how I work" facts, needed to avoid re-deriving next session and to prevent double-count / mis-stated balances.

## 2026-07-14 Quinn — DONE — Built Finance-Insights.html analysis view
Entry: MEM-005
Class: OPERATIONAL
Change: Added skills/finance-review/insights.py (new tool in own tree) generating Finance-Insights.html from the engine's transactions.csv — trend chart, entity filter, mortgage paydown, regular-outgoings/DD detection, overlap flags. Reconciles exactly to engine totals.
Previous: only the engine's basic Finance-Dashboard.html existed.
Circumstance: Rex asked for monthly trend, collapsible sections, mortgage panel, business filter, and standing-order/DD identification, 2026-07-14.
Reason: Client-0 analysis need; built client-side so the shared engine stays untouched. Upstream fold-in and routine integration are architecture-class — see next PROPOSED note if/when raised.

## 2026-07-14 Quinn — PROPOSED — Card balance statement-authoritative
Entry: MEM-004
Class: ARCHITECTURE
Change: Propose extending analytics.py authoritative-balance override from mortgage to credit_card, using the latest statement's printed new balance.
Previous: card balance = sum of parsed transactions (excludes interest/fees; unreliable, can show wrong sign).
Circumstance: First consolidation showed Barclaycard with the wrong sign vs the statement's real owed balance.
Reason: Numbers-honesty — the card line must reflect the real liability. Touches the shared consolidate skill → held for Archy/Rex, not self-applied.
