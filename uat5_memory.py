#!/usr/bin/env python3
"""uat5_memory.py -- end-to-end self-verify of the memory round-trip UAT-5 puts in Rex's
hands. It runs the REAL reconcile.py CLI (the exact command the memory-reconcile GitHub
Action runs), not a reimplementation, against throwaway local repos -- so a PASS here means
the actual mechanism works, not that a model of it works (Tessa's "run the real thing").

The flow it proves, identical to the phone steps:
  1. A seat (holly) writes a NEW fact to agents/holly/MEMORY.md on its claude/* branch, pushes.
  2. The reconcile actor runs `python reconcile.py --all --apply` and pushes main
     (promoting only the seat's OWN operational memory -- path-scoped policy).
  3. A NEW session = a fresh clone of main; it must reload the fact.

  python uat5_memory.py      # prints PASS / FAIL, exit 0 / 1.  stdlib only, no network.
"""

import os
import shutil
import subprocess
import sys
import tempfile

FLEET = os.path.dirname(os.path.abspath(__file__))
FACT = "learned: Rex takes his flat white with an extra shot -- UAT5-MARKER-7f3a"


def git(d, *a, check=True):
    r = subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("git %s failed in %s: %s" % (" ".join(a), d, r.stderr.strip()))
    return r.stdout


def _seed_repo_files(work):
    """Put the fleet's real reconcile.py + lib/ into the repo so the CLI runs against it
    exactly as it does in the cloud (reconcile.py resolves ROOT to its own location)."""
    shutil.copy(os.path.join(FLEET, "reconcile.py"), os.path.join(work, "reconcile.py"))
    shutil.copytree(os.path.join(FLEET, "lib"), os.path.join(work, "lib"))
    os.makedirs(os.path.join(work, "agents", "holly"), exist_ok=True)
    with open(os.path.join(work, "agents", "holly", "MEMORY.md"), "w", newline="\n") as fh:
        fh.write("# Holly memory\n\n- (baseline, pre-UAT5)\n")


def main():
    tmp = tempfile.mkdtemp(prefix="uat5-")
    try:
        bare = os.path.join(tmp, "origin.git")
        git(tmp, "init", "--bare", "-q", bare)

        # --- main baseline -------------------------------------------------
        work = os.path.join(tmp, "seed")
        git(tmp, "clone", "-q", bare, work)
        git(work, "config", "user.email", "t@t"); git(work, "config", "user.name", "seed")
        git(work, "checkout", "-q", "-b", "main")
        _seed_repo_files(work)
        git(work, "add", "-A"); git(work, "commit", "-q", "-m", "baseline main")
        git(work, "push", "-q", "origin", "main")
        # Model GitHub's default_branch: main -- so a plain clone (a new session) checks out main.
        git(bare, "symbolic-ref", "HEAD", "refs/heads/main")

        # --- 1. Holly session writes a fact on its claude/ branch ----------
        holly = os.path.join(tmp, "holly")
        git(tmp, "clone", "-q", bare, holly)
        git(holly, "config", "user.email", "holly@t"); git(holly, "config", "user.name", "holly")
        git(holly, "checkout", "-q", "main")
        git(holly, "checkout", "-q", "-b", "claude/holly-s1")
        mem = os.path.join(holly, "agents", "holly", "MEMORY.md")
        with open(mem, "a", newline="\n") as fh:
            fh.write("- %s\n" % FACT)
        git(holly, "add", "-A"); git(holly, "commit", "-q", "-m", "holly learns a fact")
        git(holly, "push", "-q", "origin", "claude/holly-s1")

        # --- 2. Reconcile actor runs the REAL CLI + pushes main -----------
        recon = os.path.join(tmp, "recon")
        git(tmp, "clone", "-q", bare, recon)
        git(recon, "config", "user.email", "reconcile@t"); git(recon, "config", "user.name", "reconcile")
        git(recon, "checkout", "-q", "main")
        git(recon, "fetch", "-q", "origin", "+refs/heads/claude/*:refs/remotes/origin/claude/*")
        cli = subprocess.run([sys.executable, "reconcile.py", "--all", "--apply"],
                             cwd=recon, capture_output=True, text=True)
        print(cli.stdout.strip())
        if cli.returncode != 0:
            print(cli.stderr.strip())
        git(recon, "push", "-q", "origin", "main")

        # --- 3. A NEW session = fresh clone of main; must reload the fact --
        s2 = os.path.join(tmp, "session2")
        git(tmp, "clone", "-q", bare, s2)
        reloaded = open(os.path.join(s2, "agents", "holly", "MEMORY.md"), encoding="utf-8").read()

        ok = FACT in reloaded
        print("\n%s -- session 2 (fresh clone of main) %s the fact Holly wrote in session 1."
              % ("PASS" if ok else "FAIL", "RELOADED" if ok else "did NOT reload"))
        if not ok:
            print("   MEMORY.md on main was:\n%s" % reloaded)
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
