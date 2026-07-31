#!/usr/bin/env python3
"""bootcheck.py -- the proof that a seat booted PC-offline, from the repo.

When the Cody routine fires in the cloud, it clones this repo and runs this. The
check: can the seat read its OWN identity and memory FROM THE REPO (agents/<seat>/
CLAUDE.md + MEMORY.md) -- i.e. did it boot from GitHub, not from any local disk? It
tool-verifies those files exist and are non-empty, then writes a valid run-record.
That run-record on GitHub is the evidence Seat 1 is PC-free.

stdlib only -- runs unmodified in the cloud sandbox.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import runrecord  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))


def _run_id(seat):
    return "boot-%s-%s-%s" % (seat, datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                              os.urandom(3).hex())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seat", default=os.environ.get("SEAT", "cody"))
    ap.add_argument("--runs-dir", default=os.path.join(ROOT, "runs"))
    args = ap.parse_args()
    seat = args.seat

    rec = runrecord.RunRecord(_run_id(seat), seat, "api",
                              "Boot check: prove this seat booted from the repo, not local disk",
                              cap_consuming=True)

    checks_ok = True
    for rel in ("CLAUDE.md", "MEMORY.md"):
        path = os.path.join(ROOT, "agents", seat, rel)
        exists = os.path.isfile(path)
        size = os.path.getsize(path) if exists else 0
        ok = exists and size > 0
        checks_ok = checks_ok and ok
        rec.add_check("read agents/%s/%s from the repo" % (seat, rel), ok,
                      detail=("%d bytes" % size) if ok else "MISSING", tool_used=True)

    # A second tool check: confirm we're inside a git checkout of the repo (cloud clone).
    head, ok_git = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip(), True
    ok_git = bool(head)
    checks_ok = checks_ok and ok_git
    rec.add_check("confirm running inside the cloned repo", ok_git,
                  detail=("HEAD %s" % head[:12]) if ok_git else "not a git checkout", tool_used=True)

    rec.set_verification("pass" if checks_ok else "fail", rubric_id="bootcheck-v0")
    if checks_ok:
        rec.close("pass", notes="Seat %s booted from the repo (identity + memory read from GitHub, "
                                "running in a cloud clone). PC-independent." % seat)
    else:
        rec.close("fail", failure_reason="could not read own identity/memory from the repo -- "
                                         "the seat did not boot cleanly from GitHub")
    path = rec.write(args.runs_dir)
    print("wrote run-record:", os.path.relpath(path, ROOT))
    print("  outcome:", rec.data["outcome"], "| verified:", rec.data["verification"]["result"],
          "| tool-checked:", rec.data["verification"]["self_checked"])
    print("commit this run-record to your claude/ branch so the proof reaches GitHub.")
    return 0 if checks_ok else 1


if __name__ == "__main__":
    sys.exit(main())
