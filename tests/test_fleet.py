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


def t_coordinate_review_reads_across_claude_branches():
    """The cloud reality: the report is committed to the SENDER's claude/ branch, and the
    reviewer clones main -- so review must read across branches, not just the local dir."""
    import importlib
    d = tempfile.mkdtemp()
    _git(d, "init", "-b", "main"); _git(d, "config", "user.email", "t@t"); _git(d, "config", "user.name", "t")
    os.makedirs(os.path.join(d, "reports"))
    open(os.path.join(d, "reports", ".gitkeep"), "w").write("")
    _git(d, "add", "-A"); _git(d, "commit", "-m", "base")
    # Holly files a report on HER branch (not main), addressed to marshall
    _git(d, "checkout", "-b", "claude/holly1")
    open(os.path.join(d, "reports", "report-r1.md"), "w").write("# Report from holly -> marshall\n\n- task: do X\n")
    _git(d, "add", "-A"); _git(d, "commit", "-m", "holly files")
    # Marshall is on main (no report in his checkout) -- must find it across branches.
    _git(d, "checkout", "main")
    # simulate an 'origin' so origin/claude/holly1 exists (review scans origin/claude/*)
    bare = tempfile.mkdtemp()
    _git(d, "clone", "--bare", "-q", d, bare) if False else None
    _git(d, "remote", "add", "origin", d)          # self-remote: origin/* mirrors local branches
    _git(d, "fetch", "origin", "--quiet")
    sys.path.insert(0, d); import coordinate as c2; importlib.reload(c2); c2.ROOT = d; c2.REPORTS = os.path.join(d, "reports")
    open_reports = c2.gather_open_reports("marshall")
    ids = [rid for rid, frm, _ in open_reports]
    assert "r1" in ids, "review did not find Holly's report on her claude/ branch: %s" % ids


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


def t_personal_scan_separates_operational_from_personal():
    """The guard must PASS legitimate operational memory (Quinn mentions Monzo/mortgage figure-free,
    Cody says 'Claude 5 family') and FLAG actual personal data (figures, family, health, emotional)."""
    from lib import personal_scan as ps
    clean = ["MEM-001: RHS source is Monzo CSV export, not the live QB connector.",
             "mortgage letters carry no balance; anchor from a statement date.",
             "Default to the latest Claude 5 family of models."]
    personal = ["Austen's wife Joanne; ~£35k loss; salary was 105k.",
                "burnout risk is documented and current.",
                "his sort code and account number are on file."]
    for t in clean:
        assert not ps.is_personal(t), "false positive on operational memory: %r -> %s" % (t, ps.summary(ps.scan(t)))
    for t in personal:
        assert ps.is_personal(t), "MISSED personal content: %r" % t


def t_personal_memory_quarantined_not_promoted():
    """End-to-end: a seat writes PERSONAL content to its own memory on its claude/ branch. reconcile
    must NOT promote it to main -- it is quarantined and reported. This is the guard that stops
    Austen's private data reaching the shareable repo even if the seat mis-classifies it."""
    import importlib
    d = tempfile.mkdtemp()
    _git(d, "init", "-b", "main"); _git(d, "config", "user.email", "t@t"); _git(d, "config", "user.name", "t")
    os.makedirs(os.path.join(d, "agents", "hobbs", "memory"))
    open(os.path.join(d, "agents", "hobbs", "MEMORY.md"), "w").write("# Hobbs memory\n\n- (baseline)\n")
    _git(d, "add", "-A"); _git(d, "commit", "-m", "base")
    _git(d, "checkout", "-b", "claude/hobbs1")
    # personal content the seat should never have self-written, but did:
    open(os.path.join(d, "agents", "hobbs", "MEMORY.md"), "a").write(
        "- his wife Joanne and the ~£35k loss weigh on the salary decision\n")
    _git(d, "add", "-A"); _git(d, "commit", "-m", "leak")
    sys.path.insert(0, d); import reconcile as r2; importlib.reload(r2); r2.ROOT = d
    part, seat, amb, statuses = r2.analyse("claude/hobbs1", main_ref="main")
    promotable, quarantined = r2.screen_personal("claude/hobbs1", statuses)
    assert not promotable, "personal memory was marked promotable: %s" % promotable
    assert any("agents/hobbs/MEMORY.md" in p for p, _ in quarantined), "personal path not quarantined"
    # and apply_merges must refuse to write it to main
    r2.apply_merges("claude/hobbs1", promotable, seat)
    _git(d, "checkout", "main")
    on_main = open(os.path.join(d, "agents", "hobbs", "MEMORY.md")).read()
    assert "Joanne" not in on_main and "35k" not in on_main, "PERSONAL DATA LEAKED TO MAIN: %r" % on_main


def t_zero_connector_seat_denies_all_mcp_tools():
    """The flagged blast radius: a zero-connector seat/routine must be unable to call ANY
    connector tool. provision generates `mcp__*` into its settings.json deny; a seat WITH
    connectors must NOT get that blanket deny (it would break its declared connectors)."""
    cfg = provision.resolve_inputs(provision.load_yaml(os.path.join(ROOT, "fleet.yaml")))
    by = {s["name"]: s for s in cfg["seats"]}
    cody_deny = provision.seat_settings(cfg, "cody")["permissions"]["deny"]
    assert not (by["cody"].get("connectors") or []), "test assumes cody is the zero-connector seat"
    assert "mcp__*" in cody_deny, "zero-connector seat 'cody' does not deny all connector tools"
    holly_deny = provision.seat_settings(cfg, "holly")["permissions"]["deny"]
    assert by["holly"].get("connectors"), "test assumes holly declares connectors"
    assert "mcp__*" not in holly_deny, "connector-bearing seat 'holly' wrongly blanket-denies mcp__*"


def t_forbidden_connector_rejected_by_gate():
    """No build seat OR utility routine may declare a money/live-comms connector, whatever its
    write_scope. This is the code lever we DO control (there is no API to stop the console
    attaching one, so declaring is refused and the runbook forces removal + verify)."""
    import copy
    for holder_key in ("seats", "utility_routines"):
        cfg = copy.deepcopy(provision.resolve_inputs(
            provision.load_yaml(os.path.join(ROOT, "fleet.yaml"))))
        cfg.setdefault(holder_key, [])
        if not cfg[holder_key]:
            cfg[holder_key].append({"name": "x", "connectors": []})
        cfg[holder_key][0].setdefault("connectors", []).append(
            {"id": "stripe", "write_scope": "read"})
        try:
            provision.check_connector_gate(cfg)
        except provision.ProvisionError as e:
            assert "FORBIDDEN" in str(e), str(e)
            continue
        raise AssertionError("a forbidden (stripe) connector was allowed in %s" % holder_key)


def t_utility_routine_heartbeat_is_zero_connector():
    """The exact routine Rex flagged: cody-heartbeat must be declared with NO connectors, so
    'zero connectors' is a code fact carried into the runbook, not a manual thing to remember."""
    cfg = provision.resolve_inputs(provision.load_yaml(os.path.join(ROOT, "fleet.yaml")))
    hb = next((u for u in cfg.get("utility_routines") or [] if u["name"] == "cody-heartbeat"), None)
    assert hb is not None, "cody-heartbeat is not declared as a utility routine"
    assert not (hb.get("connectors") or []), "cody-heartbeat must declare zero connectors"
    steps = provision.manual_steps(cfg)
    assert "cody-heartbeat" in steps and "REMOVE ALL" in steps, "runbook missing heartbeat REMOVE-ALL step"


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
