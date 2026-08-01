#!/usr/bin/env python3
"""provision.py -- stand up a Court-of-Rex fleet from fleet.yaml.

CLIENT-AGNOSTIC: nothing here is hardcoded to Datavation. Everything org-specific is
read from the `org` block in fleet.yaml and substituted for `${org.*}` references. The
same code with a different `org` block stands up a client's fleet -- that reusability
is the strategic deliverable, not this one fleet.

  python provision.py plan      # read config, resolve inputs, print what it would do
  python provision.py apply     # generate the repo layer (idempotent)

What it generates (idempotent -- re-running changes nothing already correct):
  fleet.lock.json                 machine artefact, committed (what code reads)
  .claude/settings.json           the defense-in-depth WRITE-BOUNDARY (Archy 2026-08-01)
  agents/<seat>/.claude/settings.json   per-seat cross-seat deny (belt to the braces)
  MANUAL-STEPS.md                 the console runbook (routines have no management API)

The account layer (routines, triggers, tokens, connector OAuth) has no API -- it is a
generated, numbered console runbook, per the amended T8 bar. No undocumented hand steps.

Parallel build: this only ever writes inside the repo. It never touches OneDrive or any
agent's live location -- those stay authoritative and untouched until the final gated cutover.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yaml  # noqa: E402  (local tooling; cloud code reads fleet.lock.json)

ROOT = os.path.dirname(os.path.abspath(__file__))

# Connector write scopes permitted during the PARALLEL BUILD. A connector that can write
# a LIVE production surface is never auto-granted -- it is a separate gated decision.
ALLOWED_WRITE_SCOPES = {"none", "read", "sandbox"}


class ProvisionError(Exception):
    pass


# --------------------------------------------------------------------------
# config + input resolution (the client-agnostic core)
# --------------------------------------------------------------------------

def load_yaml(path=None):
    with open(path or os.path.join(ROOT, "fleet.yaml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def resolve_inputs(cfg):
    """Substitute every ${org.<key>} reference with the value from the org block.
    This is what makes the config client-agnostic: org values are inputs, not literals."""
    org = cfg.get("org") or {}

    def sub(value):
        if isinstance(value, str):
            def repl(m):
                key = m.group(1)
                if key not in org:
                    raise ProvisionError("fleet.yaml references ${org.%s} but org.%s is not set" % (key, key))
                return str(org[key])
            return re.sub(r"\$\{org\.([a-zA-Z0-9_.]+)\}", repl, value)
        if isinstance(value, dict):
            return {k: sub(v) for k, v in value.items()}
        if isinstance(value, list):
            return [sub(v) for v in value]
        return value

    return sub(cfg)


def check_connector_gate(cfg):
    bad = []
    for seat in cfg["seats"]:
        for conn in seat.get("connectors") or []:
            if conn.get("write_scope") not in ALLOWED_WRITE_SCOPES:
                bad.append("seat %s connector %s write_scope=%r (allowed: %s)"
                           % (seat["name"], conn.get("id"), conn.get("write_scope"),
                              ", ".join(sorted(ALLOWED_WRITE_SCOPES))))
    if bad:
        raise ProvisionError(
            "CONNECTOR GATE: a seat asks for a live-write connector -- refusing.\n  "
            + "\n  ".join(bad)
            + "\nA live-write connector is a separate gated decision, never auto-granted in the build.")


# --------------------------------------------------------------------------
# the write-boundary (defense-in-depth, Archy 2026-08-01)
# --------------------------------------------------------------------------

def _deny(paths):
    out = []
    for p in paths:
        out.append("Write(%s)" % p)
        out.append("Edit(%s)" % p)
    return out


def root_settings(cfg):
    """Fleet-wide, committed write-boundary: the human-final paths NO seat may write in
    session -- shared canon, and every seat's IDENTITY and CONTEXT. Memory is deliberately
    NOT denied here (a seat writes its own memory); the cross-seat memory boundary is the
    per-seat file below + the reconcile allowlist.

    Mechanism note / FINDING to verify: routines run without permission PROMPTS mid-run;
    whether the cloud runtime still enforces permissions.deny during an autonomous run is
    to be verified before final certification. If it is ignored, reconcile.py remains the
    load-bearing gate (it is, and it is tested)."""
    deny = _deny(["canon/**", "agents/**/CLAUDE.md", "agents/**/context/**"])
    return {
        "permissions": {"deny": deny},
        "hooks": {
            "SessionStart": [
                {"hooks": [{"type": "command",
                            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/seat_boundary.py\" || true"}]}
            ]
        },
    }


def seat_settings(cfg, seat_name):
    """Per-seat cross-seat deny: this seat may not write ANY other seat's tree. Written to
    agents/<seat>/.claude/settings.json, and activated per session by the SessionStart hook
    (which copies the right one to .claude/settings.local.json based on $SEAT)."""
    others = [s["name"] for s in cfg["seats"] if s["name"] != seat_name]
    deny = _deny(["agents/%s/**" % o for o in others])
    return {"permissions": {"deny": deny}}


SEAT_BOUNDARY_HOOK = """#!/usr/bin/env python3
# SessionStart: activate this seat's cross-seat write-boundary. Reads $SEAT and copies
# agents/<seat>/.claude/settings.json to the session's .claude/settings.local.json so the
# runtime's permission layer denies writes to every OTHER seat's tree. Defense-in-depth on
# top of reconcile.py. If the runtime ignores in-session deny, reconcile remains the gate.
import json, os, shutil, sys
root = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
seat = os.environ.get("SEAT")
if not seat:
    sys.exit(0)  # interactive session names its seat later; nothing to enforce yet
src = os.path.join(root, "agents", seat, ".claude", "settings.json")
if os.path.isfile(src):
    dst = os.path.join(root, ".claude", "settings.local.json")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    print("[seat-boundary] activated write-boundary for seat", seat)
"""


# --------------------------------------------------------------------------
# generation
# --------------------------------------------------------------------------

def write_if_different(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            if fh.read() == content:
                return "unchanged"
        action = "updated"
    else:
        action = "created"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return action


def manual_steps(cfg):
    org = cfg["org"]
    out = ["# MANUAL-STEPS.md -- console runbook (GENERATED, do not hand-edit)", "",
           "Routines, triggers, tokens and connector OAuth have no management API; they are",
           "created in the web console. Generated from fleet.yaml for org **%s**." % org["name"], "",
           "For each seat, in claude.ai/code/routines > New routine > Cloud:", ""]
    n = 0
    for seat in cfg["seats"]:
        conns = seat.get("connectors") or []
        conn_txt = ", ".join("%s (%s)" % (c["id"], c["write_scope"]) for c in conns) or \
                   "REMOVE ALL (least privilege -- this seat needs none)"
        n += 1
        out += ["## %d. Routine `%s`" % (n, seat["name"]),
                "    Name:        %s" % seat["name"],
                "    Model:       %s" % seat.get("model", "default"),
                "    Prompt:      paste agents/%s/CLAUDE.md" % seat["name"],
                "    Repository:  %s/%s (default branch)" % (org["repo_owner"], org["repo_name"]),
                "    Environment: %s" % cfg["fleet"]["environment"]["name"],
                "    Connectors:  %s" % conn_txt,
                "    Permissions: leave 'Allow unrestricted branch pushes' OFF.",
                "    Triggers:    %s (event-driven wake)" % ", ".join(t["type"] for t in seat.get("triggers") or []),
                ""]
    out += ["Then: `python verify.py`.", ""]
    return "\n".join(out)


def do_apply(cfg):
    check_connector_gate(cfg)
    actions = []

    # root write-boundary + hook
    actions.append((".claude/settings.json",
                    write_if_different(os.path.join(ROOT, ".claude", "settings.json"),
                                       json.dumps(root_settings(cfg), indent=2) + "\n")))
    actions.append((".claude/hooks/seat_boundary.py",
                    write_if_different(os.path.join(ROOT, ".claude", "hooks", "seat_boundary.py"),
                                       SEAT_BOUNDARY_HOOK)))
    # per-seat cross-seat deny
    for seat in cfg["seats"]:
        rel = os.path.join("agents", seat["name"], ".claude", "settings.json")
        actions.append((rel, write_if_different(os.path.join(ROOT, rel),
                        json.dumps(seat_settings(cfg, seat["name"]), indent=2) + "\n")))

    # lock + runbook
    actions.append(("fleet.lock.json",
                    write_if_different(os.path.join(ROOT, "fleet.lock.json"),
                                       json.dumps(cfg, indent=2, sort_keys=True) + "\n")))
    actions.append(("MANUAL-STEPS.md",
                    write_if_different(os.path.join(ROOT, "MANUAL-STEPS.md"), manual_steps(cfg))))

    for rel, act in actions:
        print("  %-9s %s" % (act, rel))
    changed = sum(1 for _, a in actions if a != "unchanged")
    print("  -> %d changed, %d unchanged" % (changed, len(actions) - changed))
    return actions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["plan", "apply"])
    args = ap.parse_args()
    raw = load_yaml()
    cfg = resolve_inputs(raw)
    print("FLEET '%s' (org: %s, repo: %s/%s)"
          % (cfg["fleet"]["repo"]["name"], cfg["org"]["name"],
             cfg["org"]["repo_owner"], cfg["org"]["repo_name"]))
    print("  seats: %s" % ", ".join(s["name"] for s in cfg["seats"]))
    try:
        check_connector_gate(cfg)
        if args.action == "apply":
            print("APPLY (repo layer)")
            do_apply(cfg)
        else:
            print("PLAN ok -- inputs resolve, connector gate clean.")
    except ProvisionError as exc:
        print("\nPROVISION FAILED: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
