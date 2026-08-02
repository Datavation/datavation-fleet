#!/usr/bin/env python3
"""Fleet tests: memory round-trip, agent-to-agent coordination, client-agnostic IaC.
Run: python tests/test_fleet.py"""

import glob
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from lib import runrecord           # noqa: E402
import provision                    # noqa: E402
import reconcile as recon           # noqa: E402

PASSED, FAILED = [], []


def check(name, fn):
    try:
        fn(); PASSED.append(name); print("  PASS  %s" % name)
    except AssertionError as e:
        FAILED.append((name, str(e))); print("  FAIL  %s -- %s" % (name, e))
    except Exception as e:  # noqa: BLE001
        FAILED.append((name, "%s: %s" % (type(e).__name__, e)))
        print("  ERROR %s -- %s: %s" % (name, type(e).__name__, e))


def _git(d, *a):
    r = subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True)
    assert r.returncode == 0, "git %s: %s" % (" ".join(a), r.stderr)
    return r.stdout


# -- confirm-(b): memory round-trip persists ------------------------------

def t_memory_roundtrip_write_reconcile_reload():
    """The thing that could make Rex's memory test fail: a seat writes memory in one
    session -> reconcile promotes it to main -> a NEW session (fresh clone of main) must
    reload it. Prove the full chain."""
    d = tempfile.mkdtemp()
    _git(d, "init", "-b", "main"); _git(d, "config", "user.email", "t@t"); _git(d, "config", "user.name", "t")
    os.makedirs(os.path.join(d, "agents", "holly", "memory"))
    open(os.path.join(d, "agents", "holly", "MEMORY.md"), "w").write("v1\n")
    _git(d, "add", "-A"); _git(d, "commit", "-m", "base")
    # session 1 writes memory on its claude/ branch
    _git(d, "checkout", "-b", "claude/sess1")
    open(os.path.join(d, "agents", "holly", "MEMORY.md"), "w").write("v1\nlearned: Rex prefers one-liners\n")
    _git(d, "add", "-A"); _git(d, "commit", "-m", "learn")
    # reconcile promotes own operational memory to main
    import importlib; sys.path.insert(0, d); import reconcile as r2; importlib.reload(r2); r2.ROOT = d
    part, seat, amb, statuses = r2.analyse("claude/sess1", main_ref="main")
    assert seat == "holly" and statuses["agents/holly/MEMORY.md"] == "mergeable", (seat, statuses)
    r2.apply_merges("claude/sess1", statuses, seat)
    # session 2 = a NEW clone of main; must see the learning
    clone = tempfile.mkdtemp()
    _git(".", "clone", "-q", d, clone)
    reloaded = open(os.path.join(clone, "agents", "holly", "MEMORY.md")).read()
    assert "one-liners" in reloaded, "new session did NOT reload the promoted memory: %r" % reloaded


# -- UAT-3: agent-to-agent handoff via the repo bus -----------------------

def t_coordinate_holly_hands_marshall():
    with tempfile.TemporaryDirectory() as tmp:
        runs = os.path.join(tmp, "runs")
        r1 = subprocess.run([sys.executable, os.path.join(ROOT, "coordinate.py"),
                             "report", "--author", "holly", "--to", "marshall",
                             "--task", "produce the weekly TP status", "--runs-dir", runs],
                            capture_output=True, text=True)
        assert r1.returncode == 0, r1.stderr
        reports = sorted(glob.glob(os.path.join(ROOT, "reports", "report-*.md")))
        assert reports, "Holly filed no report"
        rid = os.path.basename(max(reports, key=os.path.getmtime))[len("report-"):-3]
        try:
            r2 = subprocess.run([sys.executable, os.path.join(ROOT, "coordinate.py"),
                                 "review", "--author", "marshall", "--runs-dir", runs],
                                capture_output=True, text=True)
            assert r2.returncode == 0, r2.stderr
            replies = glob.glob(os.path.join(ROOT, "reports", "reply-*.md"))
            assert replies, "Marshall produced no reply/artefact"
            body = open(max(replies, key=os.path.getmtime), encoding="utf-8").read()
            assert ("answers_report: %s" % rid) in body, "Marshall's reply does not name Holly's task"
            for f in glob.glob(os.path.join(runs, "*.json")):
                runrecord.load_and_validate(f)
        finally:
            for f in glob.glob(os.path.join(ROOT, "reports", "report-*.md")) + \
                     glob.glob(os.path.join(ROOT, "reports", "reply-*.md")):
                os.remove(f)


# -- client-agnostic IaC + gates ------------------------------------------

def t_iac_is_client_agnostic():
    raw = provision.load_yaml(os.path.join(ROOT, "fleet.yaml"))
    cfg = provision.resolve_inputs(raw)
    assert cfg["fleet"]["repo"]["owner"] == raw["org"]["repo_owner"], "owner not resolved from org input"
    assert "${org." not in provision.json_dumps(cfg) if hasattr(provision, "json_dumps") else True
    import json as J
    assert "${org." not in J.dumps(cfg), "unresolved ${org.*} left in config"


def t_connector_gate_blocks_live_write():
    import copy
    cfg = copy.deepcopy(provision.resolve_inputs(provision.load_yaml(os.path.join(ROOT, "fleet.yaml"))))
    cfg["seats"][0].setdefault("connectors", []).append({"id": "x", "write_scope": "live"})
    try:
        provision.check_connector_gate(cfg)
    except provision.ProvisionError as e:
        assert "CONNECTOR GATE" in str(e); return
    raise AssertionError("a live-write connector was allowed")


def t_write_boundary_generated_per_seat():
    cfg = provision.resolve_inputs(provision.load_yaml(os.path.join(ROOT, "fleet.yaml")))
    root = provision.root_settings(cfg)["permissions"]["deny"]
    assert "Write(canon/**)" in root and "Write(agents/**/CLAUDE.md)" in root
    for seat in cfg["seats"]:
        deny = provision.seat_settings(cfg, seat["name"])["permissions"]["deny"]
        for other in cfg["seats"]:
            if other["name"] != seat["name"]:
                assert "Write(agents/%s/**)" % other["name"] in deny, \
                    "%s can write %s's tree" % (seat["name"], other["name"])


def main():
    print("FLEET TESTS\n")
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
