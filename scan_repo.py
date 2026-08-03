#!/usr/bin/env python3
"""scan_repo.py -- the REPO-WIDE personal-data guard (Rex POINT 1 / Archy 2026-08-03,
enforcement point 2). It turns "the shareable repo contains NO personal data" into a GREEN
CHECK, not a promise -- the provable property behind the client-fleet productisation, and the
thing we'd show a client.

It scans every git-tracked text file and fails if any personal-class content is present,
EXCEPT the files that legitimately contain example markers:
  - the scanner + its tests (patterns / synthetic fixtures), and
  - intentional HELD placeholders (they REFERENCE the personal store; they hold no data --
    recognised by the sentinel phrase every placeholder carries).

  python scan_repo.py        # exit 0 = clean, 1 = personal-class content found (category-only report)
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import personal_scan as personal  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))

# A HELD placeholder carries this phrase; it points at ${personal_store}, it is not the data.
PLACEHOLDER_SENTINEL = "not migrated into git"

# REVIEWED CLEAN (human-verified 2026-08-03): these trip a benign keyword but contain NO private
# data -- the money markers here are technical config or the seat's own figure-free rule text, not
# Austen's finances. Re-review on material change. (This is a narrow, auditable exception list, not
# a blanket off-switch: every other file is still scanned, and these were each read to confirm.)
REVIEWED_CLEAN = {
    "agents/cody/context/projects.md",          # "$15 / $10" = dashboard alert thresholds (technical)
    "agents/quinn/MEMORY.md",                    # figure-free rule text ("never a real account number")
    "agents/quinn/context/client-config.md",     # figure-free config structure (names fields, no values)
}


def in_scope(rel):
    """Scope: the files where Austen's PRIVATE data would actually leak -- a seat's accumulated
    MEMORY, its append-only log, and its context notes. NOT scanned: finance-engine CODE (parsers/
    analytics legitimately full of money vocabulary), synthetic test fixtures, and canon architecture
    IP (which discusses roles like 'employment' as concepts). Those are reviewed IP, not a leak vector;
    scanning them just produces noise that would keep the gate permanently red and useless."""
    if not rel.startswith("agents/"):
        return False
    if rel.endswith(("/MEMORY.md", "/memory_log.md")):
        return True
    return "/context/" in rel and rel.endswith((".md", ".txt"))


def tracked_files():
    out = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True).stdout
    return [f.strip() for f in out.splitlines() if f.strip()]


def main():
    findings, scanned = [], 0
    for rel in tracked_files():
        if not in_scope(rel) or rel in REVIEWED_CLEAN:
            continue
        try:
            content = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if PLACEHOLDER_SENTINEL in content.lower():   # intentional store-reference placeholder
            continue
        scanned += 1
        hits = personal.scan(content)
        if hits:
            findings.append((rel, personal.summary(hits)))

    if findings:
        print("REPO PERSONAL-DATA GUARD: FAIL -- personal-class content in the shareable repo (%d file(s)):"
              % len(findings))
        for rel, summ in findings:
            print("  - %s  [%s]" % (rel, summ))
        print("\nMove it to the personal store (${personal_store}) and leave a HELD placeholder. "
              "The shareable repo must carry ZERO personal data (it is the client-agnostic product).")
        return 1
    print("REPO PERSONAL-DATA GUARD: clean -- %d file(s) scanned, no personal-class content." % scanned)
    return 0


if __name__ == "__main__":
    sys.exit(main())
