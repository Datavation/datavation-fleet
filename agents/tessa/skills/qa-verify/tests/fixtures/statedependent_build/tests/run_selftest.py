"""Synthetic fixture: a self-test that PASSES in place (because a stray cache-like artifact
was left behind by a prior run) but FAILS from a genuinely clean copy — because qa_verify.py's
clean-copy check deliberately strips cache-like dirs (__pycache__, .venv, venv, node_modules,
.git, .pytest_cache) when it makes the isolated copy. This is the exact class of defect the
clean-environment check exists to catch: a test that secretly depends on leftover state rather
than proving anything about the code itself. Not a real build."""
import sys
from pathlib import Path

marker = Path(__file__).parent / "__pycache__" / "_leftover_marker.txt"
if marker.is_file():
    print("fixture statedependent_build: stray-cache marker found, PASS (the bug being caught)")
    sys.exit(0)
else:
    print("fixture statedependent_build: no marker in a clean copy — correctly FAILS")
    sys.exit(1)
