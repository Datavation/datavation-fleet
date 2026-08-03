#!/usr/bin/env python3
"""reconcile.py -- the git layer for path-scoped memory write-back (see
lib/reconcile.py for the ruled policy). Merges a seat's OWN operational memory from
its claude/ branch to main, refuses everything else loudly, and never clobbers a
concurrent main edit.

  python reconcile.py --list                     # show claude/ branches + what each would do
  python reconcile.py --branch <name>            # dry-run one branch (default: dry-run)
  python reconcile.py --branch <name> --apply    # actually merge the allowed memory paths
  python reconcile.py --all --apply              # every claude/ branch

Exit non-zero if any branch has a refused path or a conflict -- those are findings,
surfaced to reports/MEMORY-AUDIT-*.md, never silently swallowed.
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import reconcile as policy        # noqa: E402
from lib import personal_scan as personal  # noqa: E402  (personal-data guard, Rex 2026-08-03)

ROOT = os.path.dirname(os.path.abspath(__file__))
MAIN = "main"


def git(*args, check=True):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def claude_branches(remote="origin"):
    out = git("branch", "-r", "--format=%(refname:short)")
    pref = "%s/claude/" % remote
    return [b.strip() for b in out.splitlines() if b.strip().startswith(pref)]


def _show(ref, path):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (ref, path)],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None  # None = path absent at that ref


def analyse(branch, main_ref=MAIN):
    """Return (partition, own_seat, ambiguous, per-allow-path status) for a branch."""
    base = git("merge-base", main_ref, branch).strip()
    changed = [p for p in git("diff", "--name-only", base, branch).splitlines() if p.strip()]
    part, own_seat, ambiguous = policy.partition(changed)

    # Three-way status for each allow path: mergeable / already-current / conflict.
    statuses = {}
    for path in part[policy.ALLOW]:
        base_v, main_v, br_v = _show(base, path), _show(main_ref, path), _show(branch, path)
        if main_v == br_v:
            statuses[path] = "already-current"
        elif main_v == base_v:
            statuses[path] = "mergeable"          # main untouched since base -> safe to take branch
        else:
            statuses[path] = "conflict"           # both moved -> surface, never clobber
    return part, own_seat, ambiguous, statuses


def audit_report(branch, own_seat, ambiguous, part, statuses):
    lines = ["# MEMORY AUDIT -- reconcile of %s" % branch, "",
             "- own seat: %s%s" % (own_seat or "UNKNOWN",
                                   "  (AMBIGUOUS -- branch spans multiple seats)" if ambiguous else ""),
             "- summary: %s" % policy.summarise(part), ""]
    refused = [(v, p) for v in policy.DENY_VERDICTS for p in part[v]]
    conflicts = [p for p, s in statuses.items() if s == "conflict"]
    if refused:
        lines.append("## REFUSED (fail loud -- architecture-class stays human-final)")
        for v, p in refused:
            lines.append("- [%s] %s" % (v, p))
        lines.append("")
    if conflicts:
        lines.append("## CONFLICT (own MEMORY.md moved on both sides -- human/Tessa merge, never clobbered)")
        for p in conflicts:
            lines.append("- %s" % p)
        lines.append("")
    merged = [p for p, s in statuses.items() if s == "mergeable"]
    if merged:
        lines.append("## MERGED to main (own operational memory)")
        for p in merged:
            lines.append("- %s" % p)
        lines.append("")
    return "\n".join(lines), bool(refused or conflicts)


def screen_personal(branch, statuses):
    """Split the mergeable memory paths into (promotable, quarantined) using the personal-data
    guard. A path whose content trips any personal-class marker is QUARANTINED -- never promoted
    to shared main -- and returned with a category-only summary (no sensitive content). This is
    defense-in-depth on top of the seat's own write-time classification (Rex ruling 2026-08-03)."""
    promotable, quarantined = [], []
    for path, status in statuses.items():
        if status != "mergeable":
            continue
        hits = personal.scan(_show(branch, path) or "")
        if hits:
            quarantined.append((path, personal.summary(hits)))
        else:
            promotable.append(path)
    return promotable, quarantined


def apply_merges(branch, promotable, own_seat, target=None):
    """Promote ONLY the screened-clean paths onto `target` (a branch created/reset from main).
    `promotable` comes from screen_personal -- quarantined paths never reach here, so personal-class
    memory cannot land on shared main.

    target defaults to main (local/tests: commit straight to main). The CI job passes a reconcile
    branch instead, so the promotion lands on a branch and reaches main only via an auto-merged PR
    (Archy ruling 2026-08-03, condition-b design B -- no branch-protection bypass, full audit trail)."""
    target = target or MAIN
    if not promotable:
        return 0
    # Switch to target; create it from main only the FIRST time (so promotions from multiple seats
    # ACCUMULATE on one reconcile branch instead of each `-B` reset wiping the last).
    exists = subprocess.run(["git", "-C", ROOT, "rev-parse", "--verify", target],
                            capture_output=True, text=True).returncode == 0
    if exists:
        git("checkout", target)
    else:
        git("checkout", "-b", target, MAIN)
    for path in promotable:
        content = _show(branch, path)
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        git("add", path)
    git("commit", "-m", "memory reconcile: %s own operational memory from %s" % (own_seat, branch))
    return len(promotable)


def do_branch(branch, apply=False, target=None):
    part, own_seat, ambiguous, statuses = analyse(branch)
    report, has_findings = audit_report(branch, own_seat, ambiguous, part, statuses)

    # Personal-data guard: screen mergeable memory BEFORE any promotion (both dry-run and apply).
    promotable, quarantined = screen_personal(branch, statuses)
    if quarantined:
        qlines = ["## QUARANTINED -- personal-class, NOT promoted to shared main (personal-data guard)",
                  "*Rex ruling 2026-08-03: personal data never lands on shared main; it stays in the "
                  "personal store. Category-only below -- no sensitive content is reproduced.*", ""]
        for path, summ in quarantined:
            qlines.append("- %s  [%s]" % (path, summ))
        report = report + "\n" + "\n".join(qlines) + "\n"

    print(report)
    if apply and not ambiguous:
        n = apply_merges(branch, promotable, own_seat, target=target)
        if n:
            print(">> merged %d clean memory path(s) onto %s." % (n, target or MAIN))
        if quarantined:
            print(">> QUARANTINED %d personal-class path(s) -- NOT promoted:" % len(quarantined))
            for path, summ in quarantined:
                print("   - %s  [%s]" % (path, summ))
    elif apply and ambiguous:
        print(">> NOT applied: branch is ambiguous (spans seats) -- refused, escalated to audit.")

    findings = has_findings or bool(quarantined)
    if findings:
        os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
        safe = branch.replace("/", "_")
        out = os.path.join(ROOT, "reports", "MEMORY-AUDIT-%s.md" % safe)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report + "\n")
        print(">> findings written to reports/%s" % os.path.basename(out))
    return 1 if findings else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--branch")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--target-branch", default=None,
                    help="commit promotions onto this branch (created from main) instead of main "
                         "itself. The CI job passes a reconcile branch so main is reached only via an "
                         "auto-merged PR. Omit for local/direct-to-main use.")
    args = ap.parse_args()

    git("fetch", "origin", "--quiet", check=False)
    if args.list or (not args.branch and not args.all):
        for b in claude_branches():
            part, own_seat, ambiguous, statuses = analyse(b)
            print("%-40s seat=%-10s %s" % (b, own_seat or "?", policy.summarise(part)))
        return 0
    rc = 0
    for b in ([args.branch] if args.branch else claude_branches()):
        rc |= do_branch(b, apply=args.apply, target=args.target_branch)
    return rc


if __name__ == "__main__":
    sys.exit(main())
