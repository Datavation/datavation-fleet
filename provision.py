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

# Connector *classes* NO build seat may hold, whatever its write_scope: money movement and
# live outbound comms on Rex's real accounts. The console attaches all org connectors by
# default (there is NO management API to prevent it -- same platform gate as T8), so this is
# the code lever we DO control: fleet.yaml may never DECLARE one of these, and the console
# runbook forces their removal + a verify step. (2026-08-02: added after a heartbeat routine
# was found holding Stripe + Gmail on Rex's live account -- exactly this blast radius.)
FORBIDDEN_BUILD_CONNECTOR_IDS = {
    "stripe", "paypal", "square", "quickbooks", "docusign",  # money / contracts
    "gmail", "ms365", "outlook",                             # live outbound email
}


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
    # Seats AND utility routines are both gated -- a scheduled ops routine can hold connectors
    # too (that is how the flagged heartbeat happened), so it gets the same scrutiny.
    holders = [("seat", s) for s in cfg["seats"]] + \
              [("utility-routine", u) for u in cfg.get("utility_routines") or []]
    for kind, holder in holders:
        for conn in holder.get("connectors") or []:
            cid = (conn.get("id") or "").lower()
            if conn.get("write_scope") not in ALLOWED_WRITE_SCOPES:
                bad.append("%s %s connector %s write_scope=%r (allowed: %s)"
                           % (kind, holder["name"], conn.get("id"), conn.get("write_scope"),
                              ", ".join(sorted(ALLOWED_WRITE_SCOPES))))
            if cid in FORBIDDEN_BUILD_CONNECTOR_IDS:
                bad.append("%s %s declares FORBIDDEN connector %r (money/live-comms class -- "
                           "may never hold it)" % (kind, holder["name"], conn.get("id")))
    if bad:
        raise ProvisionError(
            "CONNECTOR GATE: a seat asks for a live-write or forbidden connector -- refusing.\n  "
            + "\n  ".join(bad)
            + "\nA live-write / money / live-comms connector is a separate gated decision, "
              "never auto-granted in the build.")


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


def connector_deny(seat):
    """The in-session connector boundary (defense-in-depth, code layer).

    A seat that declares NO connectors must call NO connector tool: deny `mcp__*` outright.
    That is a certain, reproducible rule and it is exactly the flagged case -- the Cody
    builder and the cody-heartbeat routine need only the repo + git, so any Gmail/Stripe tool
    call is denied at the permission layer regardless of what the console attached.

    A seat WITH connectors cannot be allow-listed here from code: the cloud connector tool
    namespaces are not known at provision time, so we do NOT ship a fabricated glob that might
    silently fail to match. For those seats the load-bearing control stays the console-minimal
    set (MANUAL-STEPS + verify), and the provision-time FORBIDDEN gate prevents ever declaring
    a money/live-comms connector. Same open finding as the write-boundary: whether the cloud
    runtime honours permissions.deny in an autonomous run is still to be certified; until then
    NOT-attaching in the console is the primary gate and this is defense-in-depth."""
    if not (seat.get("connectors") or []):
        return ["mcp__*"]
    return []


def seat_settings(cfg, seat_name):
    """Per-seat write + connector boundary. Written to agents/<seat>/.claude/settings.json,
    activated per session by the SessionStart hook (copies it to .claude/settings.local.json
    based on $SEAT). Denies: (1) writing ANY other seat's tree, (2) all connector tools for a
    zero-connector seat."""
    seat = next(s for s in cfg["seats"] if s["name"] == seat_name)
    others = [s["name"] for s in cfg["seats"] if s["name"] != seat_name]
    deny = _deny(["agents/%s/**" % o for o in others]) + connector_deny(seat)
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


def _connector_lines(conns):
    """The runbook's connector instruction. The console pre-attaches ALL org connectors by
    default, so every routine's step is REMOVE-ALL-first, then add back ONLY the minimal set,
    then a mandatory VERIFY (re-open the routine and confirm the list equals exactly this set).
    Trust-nothing: the verify line is what caught this being wrong the first time."""
    allowed = ", ".join("%s (%s)" % (c["id"], c["write_scope"]) for c in conns)
    if not conns:
        set_txt = "{ } (NONE)"
        add_txt = "REMOVE ALL. This routine needs no connector -- add nothing back."
    else:
        set_txt = "{ %s }" % allowed
        add_txt = "REMOVE ALL, then add back ONLY: %s" % allowed
    forbidden = ", ".join(sorted(FORBIDDEN_BUILD_CONNECTOR_IDS))
    return [
        "    Connectors:  %s" % add_txt,
        "    VERIFY (evidence, per Archy ruling 2026-08-02 -- no routine closed on assertion):",
        "                 re-open the SAVED routine and confirm BOTH, capturing a screenshot:",
        "                   (a) PRESENT -- the connector list equals exactly %s; and" % set_txt,
        "                   (b) ABSENT  -- NONE of the forbidden money/live-comms set is attached:",
        "                        %s." % forbidden,
        "                 The console attaches all org connectors by default, so proving (b) ABSENT",
        "                 matters as much as (a) PRESENT. A routine is DONE only with that evidence.",
    ]


def manual_steps(cfg):
    org = cfg["org"]
    out = ["# MANUAL-STEPS.md -- console runbook (GENERATED, do not hand-edit)", "",
           "Routines, triggers, tokens and connector OAuth have no management API; they are",
           "created in the web console. Generated from fleet.yaml for org **%s**." % org["name"], "",
           "> LEAST PRIVILEGE IS NOT OPTIONAL. The New-routine form pre-attaches every org",
           "> connector. For each routine below you MUST remove all, add back only the listed set,",
           "> and VERIFY the saved routine matches. A routine silently holding Stripe/Gmail on the",
           "> real org account is the exact blast-radius failure this runbook exists to prevent.", "",
           "In claude.ai/code/routines > New routine > Cloud:", ""]
    n = 0

    def emit(name, model, prompt_ref, conns, triggers, purpose=None):
        nonlocal n, out
        n += 1
        out.append("## %d. Routine `%s`%s" % (n, name, ("  -- %s" % purpose) if purpose else ""))
        out += ["    Name:        %s" % name,
                "    Model:       %s" % model,
                "    Prompt:      %s" % prompt_ref,
                "    Repository:  %s/%s (default branch)" % (org["repo_owner"], org["repo_name"]),
                "    Environment: %s" % cfg["fleet"]["environment"]["name"]]
        out += _connector_lines(conns)
        out += ["    Permissions: leave 'Allow unrestricted branch pushes' OFF.",
                "    Triggers:    %s (event-driven wake)" % ", ".join(t["type"] for t in triggers or []),
                ""]

    for seat in cfg["seats"]:
        emit(seat["name"], seat.get("model", "default"),
             "paste agents/%s/CLAUDE.md" % seat["name"],
             seat.get("connectors") or [], seat.get("triggers"))

    for ur in cfg.get("utility_routines") or []:
        emit(ur["name"], next((s.get("model", "default") for s in cfg["seats"]
                               if s["name"] == ur.get("owner_seat")), "default"),
             "ops routine owned by seat '%s' -- %s" % (ur.get("owner_seat"), ur.get("purpose", "")),
             ur.get("connectors") or [], ur.get("triggers"), purpose=ur.get("purpose"))

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
