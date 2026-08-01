#!/usr/bin/env python3
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
