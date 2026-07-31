"""reconcile.py -- path-scoped memory write-back, cloud claude/ branch -> main.

Ruled by Archy 2026-07-31 (RULING-Archy-Memory-Reconcile-ControlGate). The problem:
a cloud session edits its own memory mid-run, but the claude/-branch push restriction
(kept) means those edits land on a claude/ branch, never main; the operating layer is
READ from main -> memory silently forks and goes stale. This reconcile closes that gap
WITHOUT weakening the control gate, because the boundary is enforced here in code (an
infrastructure allowlist, Capability section 4 gold standard), not by instruction.

THE POLICY (per the ruling) -- a seat may only ever write its OWN operational memory:

  AUTO-MERGE to main (a seat's own operational memory, the v0.2 self-learning engine):
    agents/<own>/MEMORY.md
    agents/<own>/memory/**            (operational memory files)
    agents/<own>/memory_log.md        (append-only black box)

  REFUSED, FAIL LOUD (architecture-class stays human-final):
    canon/**                          -- shared standards
    agents/<other>/**                 -- the Cody-rewrote-Holly gate
    agents/<own>/CLAUDE.md            -- identity
    agents/<own>/context/**           -- context

  CONFLICT (own MEMORY.md changed on BOTH main and the branch, divergently):
    surface to the Memory Audit -- NEVER fast-forward-clobber.

  PROPOSED (architecture-touching) log lines ride to main IN THE LOG so the audit sees
  them, but the reconcile NEVER applies a proposal to MEMORY.md -- it waits for
  ratification. (We merge whatever MEMORY.md already is; we never synthesise edits.)

The policy layer below is a pure function so it can be tested exhaustively. The git
layer is separate. Mine to decide (per the ruling): the merge does a path-scoped
three-way check (merge-base vs main vs branch) rather than a blind fast-forward, so a
concurrent main edit is detected as a conflict instead of being clobbered.
"""

import posixpath

# Verdicts
ALLOW = "allow"
DENY_CANON = "deny-canon"
DENY_CROSS_SEAT = "deny-cross-seat"
DENY_IDENTITY = "deny-identity"
DENY_CONTEXT = "deny-context"
IGNORE = "ignore"   # not a memory path -- out of this reconcile's scope entirely

DENY_VERDICTS = {DENY_CANON, DENY_CROSS_SEAT, DENY_IDENTITY, DENY_CONTEXT}


def classify_path(path, own_seat):
    """Pure policy: what does the reconcile do with this changed path, given the
    branch's own seat? Returns one of the verdict constants above.

    `path` is repo-relative, forward-slashed. `own_seat` is the seat that owns the
    branch (inferred by own_seat_of_changes)."""
    p = path.replace("\\", "/").strip("/")

    # Shared canon is never machine-merged.
    if p == "canon" or p.startswith("canon/"):
        return DENY_CANON

    parts = p.split("/")
    if parts[0] != "agents" or len(parts) < 2:
        return IGNORE  # runs/, reports/, lib/, provision.py ... not memory reconcile's business

    seat = parts[1]
    rest = parts[2:] if len(parts) > 2 else []

    # Another seat's tree -- the gate this whole architecture exists to hold.
    if own_seat is not None and seat != own_seat:
        return DENY_CROSS_SEAT

    # Within the (own) seat: only operational memory is auto-mergeable.
    if not rest:
        return IGNORE
    leaf = "/".join(rest)
    if leaf == "MEMORY.md":
        return ALLOW
    if leaf == "memory_log.md":
        return ALLOW
    if rest[0] == "memory":            # agents/<own>/memory/**
        return ALLOW
    if leaf == "CLAUDE.md":
        return DENY_IDENTITY
    if rest[0] == "context":           # agents/<own>/context/**
        return DENY_CONTEXT
    # Anything else under the seat (routines/, skills/, code) -- not memory; leave to
    # the normal PR/promotion flow, not this reconcile.
    return IGNORE


def own_seat_of_changes(changed_paths):
    """Infer the seat that owns a branch from the agent subtrees it touched.

    Returns (seat, ambiguous). If more than one seat's tree is touched, the branch is
    ambiguous -- treated as a cross-seat breach, not guessed. canon/ and non-agent
    paths don't vote."""
    seats = set()
    for path in changed_paths:
        p = path.replace("\\", "/").strip("/").split("/")
        if len(p) >= 2 and p[0] == "agents":
            seats.add(p[1])
    if len(seats) == 1:
        return seats.pop(), False
    if len(seats) == 0:
        return None, False
    return None, True   # multiple seats touched -> ambiguous / cross-seat


def partition(changed_paths):
    """Classify every changed path. Returns a dict verdict -> [paths], plus the
    inferred own_seat and whether the branch is cross-seat-ambiguous."""
    own_seat, ambiguous = own_seat_of_changes(changed_paths)
    result = {ALLOW: [], DENY_CANON: [], DENY_CROSS_SEAT: [],
              DENY_IDENTITY: [], DENY_CONTEXT: [], IGNORE: []}
    if ambiguous:
        # Every agent path is a cross-seat write when the branch spans seats.
        for path in changed_paths:
            v = classify_path(path, own_seat=None)
            if v == IGNORE:
                result[IGNORE].append(path)
            else:
                # force non-canon agent paths to cross-seat
                result[DENY_CANON if v == DENY_CANON else DENY_CROSS_SEAT].append(path)
        return result, own_seat, ambiguous
    for path in changed_paths:
        result[classify_path(path, own_seat)].append(path)
    return result, own_seat, ambiguous


def summarise(part):
    """One-line human summary of a partition (for the audit / ledger)."""
    allowed = len(part[ALLOW])
    denied = sum(len(part[v]) for v in DENY_VERDICTS)
    return "%d memory path(s) mergeable, %d refused (canon/cross-seat/identity/context), %d ignored" % (
        allowed, denied, len(part[IGNORE]))
