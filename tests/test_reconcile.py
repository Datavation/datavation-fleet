#!/usr/bin/env python3
"""Tests for the memory-reconcile policy (lib/reconcile.py) and the git layer.

The policy is a pure function, so it is tested exhaustively against Archy's ruling.
Run: python tests/test_reconcile.py
"""

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from lib import reconcile as policy  # noqa: E402

PASSED, FAILED = [], []


def check(name, fn):
    try:
        fn(); PASSED.append(name); print("  PASS  %s" % name)
    except AssertionError as e:
        FAILED.append((name, str(e))); print("  FAIL  %s -- %s" % (name, e))
    except Exception as e:  # noqa: BLE001
        FAILED.append((name, "%s: %s" % (type(e).__name__, e)))
        print("  ERROR %s -- %s: %s" % (name, type(e).__name__, e))


# -- policy: the ruling, path by path -------------------------------------

def t_own_operational_memory_merges():
    for p in ("agents/cody/MEMORY.md", "agents/cody/memory/foo.md",
              "agents/cody/memory/sub/bar.md", "agents/cody/memory_log.md"):
        assert policy.classify_path(p, "cody") == policy.ALLOW, p


def t_own_identity_and_context_refused():
    assert policy.classify_path("agents/cody/CLAUDE.md", "cody") == policy.DENY_IDENTITY
    assert policy.classify_path("agents/cody/context/projects.md", "cody") == policy.DENY_CONTEXT


def t_canon_refused():
    assert policy.classify_path("canon/Architecture.md", "cody") == policy.DENY_CANON
    assert policy.classify_path("canon", "cody") == policy.DENY_CANON


def t_other_seat_refused_the_holly_gate():
    # Cody's branch touching Holly's memory -- the exact failure this gate prevents.
    assert policy.classify_path("agents/holly/MEMORY.md", "cody") == policy.DENY_CROSS_SEAT
    assert policy.classify_path("agents/holly/CLAUDE.md", "cody") == policy.DENY_CROSS_SEAT


def t_non_memory_paths_ignored():
    for p in ("runs/x.json", "reports/y.md", "lib/dispatch.py", "provision.py",
              "agents/cody/routines/r.md", "agents/cody/skills/s.md"):
        assert policy.classify_path(p, "cody") == policy.IGNORE, p


def t_seat_inferred_from_paths():
    seat, amb = policy.own_seat_of_changes(["agents/cody/MEMORY.md", "agents/cody/memory/a.md"])
    assert seat == "cody" and not amb


def t_multi_seat_branch_is_ambiguous_and_all_denied():
    changed = ["agents/cody/MEMORY.md", "agents/holly/MEMORY.md"]
    seat, amb = policy.own_seat_of_changes(changed)
    assert seat is None and amb is True
    part, own, ambiguous = policy.partition(changed)
    assert ambiguous and part[policy.ALLOW] == []
    assert len(part[policy.DENY_CROSS_SEAT]) == 2


def t_partition_mixed_branch():
    changed = ["agents/cody/MEMORY.md", "agents/cody/CLAUDE.md",
               "canon/X.md", "runs/r.json"]
    part, own, amb = policy.partition(changed)
    assert not amb and own == "cody"
    assert part[policy.ALLOW] == ["agents/cody/MEMORY.md"]
    assert part[policy.DENY_IDENTITY] == ["agents/cody/CLAUDE.md"]
    assert part[policy.DENY_CANON] == ["canon/X.md"]
    assert part[policy.IGNORE] == ["runs/r.json"]


# -- git layer: end-to-end in a throwaway repo ----------------------------

def _git(d, *a):
    r = subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True)
    assert r.returncode == 0, "git %s: %s" % (" ".join(a), r.stderr)
    return r.stdout


def _make_repo():
    d = tempfile.mkdtemp()
    _git(d, "init", "-b", "main")
    _git(d, "config", "user.email", "t@t"); _git(d, "config", "user.name", "t")
    os.makedirs(os.path.join(d, "agents", "cody", "memory"))
    with open(os.path.join(d, "agents", "cody", "MEMORY.md"), "w") as f:
        f.write("v1\n")
    _git(d, "add", "-A"); _git(d, "commit", "-m", "base")
    return d


def t_git_clean_memory_merge():
    """A claude/ branch that only edits own MEMORY.md merges to main cleanly."""
    import importlib
    d = _make_repo()
    _git(d, "checkout", "-b", "claude/x")
    with open(os.path.join(d, "agents", "cody", "MEMORY.md"), "w") as f:
        f.write("v1\nlearned something\n")
    _git(d, "add", "-A"); _git(d, "commit", "-m", "learn")
    # analyse via the module pointed at this repo
    sys.path.insert(0, d)
    import reconcile as recon  # noqa
    importlib.reload(recon)
    recon.ROOT = d
    part, seat, amb, statuses = recon.analyse("claude/x", main_ref="main")
    assert seat == "cody" and not amb
    assert statuses["agents/cody/MEMORY.md"] == "mergeable"
    recon.apply_merges("claude/x", statuses, seat)
    _git(d, "checkout", "main")
    got = open(os.path.join(d, "agents", "cody", "MEMORY.md")).read()
    assert "learned something" in got, got


def main():
    print("RECONCILE TESTS\n")
    for name, fn in sorted((k[2:].replace("_", " "), v) for k, v in globals().items()
                           if k.startswith("t_") and callable(v)):
        check(name, fn)
    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        for n, w in FAILED:
            print("  %s: %s" % (n, w))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
