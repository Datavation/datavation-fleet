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
from lib import reconcile as policy  # noqa: E402

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


def apply_merges(branch, statuses, own_seat):
    merged = [p for p, s in statuses.items() if s == "mergeable"]
    if not merged:
        return 0
    git("checkout", MAIN)
    for path in merged:
        content = _show(branch, path)
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        git("add", path)
    git("commit", "-m", "memory reconcile: %s own operational memory from %s" % (own_seat, branch))
    return len(merged)


def do_branch(branch, apply=False):
    part, own_seat, ambiguous, statuses = analyse(branch)
    report, has_findings = audit_report(branch, own_seat, ambiguous, part, statuses)
    print(report)
    if apply and not ambiguous:
        n = apply_merges(branch, statuses, own_seat)
        if n:
            print(">> merged %d memory path(s) to main." % n)
    elif apply and ambiguous:
        print(">> NOT applied: branch is ambiguous (spans seats) -- refused, escalated to audit.")
    if has_findings:
        os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
        safe = branch.replace("/", "_")
        out = os.path.join(ROOT, "reports", "MEMORY-AUDIT-%s.md" % safe)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report + "\n")
        print(">> findings written to reports/%s" % os.path.basename(out))
    return 1 if has_findings else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--branch")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    git("fetch", "origin", "--quiet", check=False)
    if args.list or (not args.branch and not args.all):
        for b in claude_branches():
            part, own_seat, ambiguous, statuses = analyse(b)
            print("%-40s seat=%-10s %s" % (b, own_seat or "?", policy.summarise(part)))
        return 0
    rc = 0
    for b in ([args.branch] if args.branch else claude_branches()):
        rc |= do_branch(b, apply=args.apply)
    return rc


if __name__ == "__main__":
    sys.exit(main())
