r"""
selftest_qa_verify.py — Tessa's own self-test for the qa-verify skill (this build's DoD: "self-test
offline"). Run before this build is handed to Archy for gate-review, and again by Tessa herself
(or whoever verifies Tessa's own seat) before promotion.

Proves, against synthetic fixtures only (no real build touched, no network, nothing outside a
throwaway scratch dir this script creates and removes itself):

  1. A build with a genuinely passing self-test → qa_verify.py reports PASS, exit 0.
  2. A build with a genuinely failing self-test → qa_verify.py reports FAIL, exit 1.
  3. A build whose self-test only passes because of leftover cache-like state → the clean-copy
     re-run catches it and the OVERALL verdict is FAIL, even though the in-place run was PASS.
     This is the single most important behaviour of the whole skill.
  4. A build with no self-test at all → FAIL, explicit finding, never a silent/implicit PASS.
  5. A nonexistent build folder → exit code 2 (fatal), not a false PASS or a crash.
  6. qa_verify.py itself imports nothing capable of reaching a network (grep check, same
     discipline as the finance-engine build's no_network_imports test).

Usage: python selftest_qa_verify.py    (from anywhere; paths are resolved relative to this file)
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
QA_VERIFY = HERE.parent / "scripts" / "qa_verify.py"

FORBIDDEN_IMPORT_PATTERN = re.compile(
    r"\b(import\s+(requests|socket|urllib\d?|http\.client|smtplib|ftplib)\b"
    r"|from\s+(requests|socket|urllib\d?|http\.client|smtplib|ftplib)\b)"
)

results = []


def check(name: str, condition: bool, detail: str = "") -> None:
    results.append((name, bool(condition), detail))
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not condition else ""))


def run_qa_verify(build_dir: Path, scratch: Path, tag: str):
    out_json = scratch / f"{tag}-evidence.json"
    proc = subprocess.run(
        [sys.executable, str(QA_VERIFY),
         "--build-dir", str(build_dir),
         "--out", str(out_json),
         "--scratch-root", str(scratch / f"{tag}-qa-scratch")],
        capture_output=True, text=True, timeout=120,
    )
    evidence = None
    if out_json.is_file():
        evidence = json.loads(out_json.read_text(encoding="utf-8"))
    return proc.returncode, evidence, proc.stdout, proc.stderr


def main() -> int:
    print("Tessa qa-verify self-test\n" + "=" * 40)

    if not QA_VERIFY.is_file():
        print(f"FATAL: qa_verify.py not found at {QA_VERIFY}")
        return 2

    with tempfile.TemporaryDirectory(prefix="tessa-selftest-") as tmp:
        scratch = Path(tmp)

        # 1. Passing build -> PASS, exit 0
        rc, ev, out, err = run_qa_verify(FIXTURES / "passing_build", scratch, "passing")
        check("passing_build: exit code 0", rc == 0, f"got {rc}")
        check("passing_build: overall_pass true", bool(ev and ev.get("overall_pass") is True))
        check("passing_build: in-place run passed", bool(ev and ev["in_place_run"]["passed"]))
        check("passing_build: clean-copy run passed", bool(ev and ev["clean_copy_run"]["passed"]))

        # 2. Failing build -> FAIL, exit 1
        rc, ev, out, err = run_qa_verify(FIXTURES / "failing_build", scratch, "failing")
        check("failing_build: exit code 1", rc == 1, f"got {rc}")
        check("failing_build: overall_pass false", bool(ev and ev.get("overall_pass") is False))

        # 3. State-dependent build -> in-place PASS, clean-copy FAIL, overall FAIL
        # (this is the whole point of the clean-environment check — must never be skipped)
        rc, ev, out, err = run_qa_verify(FIXTURES / "statedependent_build", scratch, "statedep")
        check("statedependent_build: exit code 1 (overall FAIL)", rc == 1, f"got {rc}")
        check("statedependent_build: in-place run PASSED (had the stray cache)",
              bool(ev and ev["in_place_run"]["passed"] is True))
        check("statedependent_build: clean-copy run FAILED (cache correctly stripped)",
              bool(ev and ev["clean_copy_run"]["passed"] is False))
        check("statedependent_build: overall_pass false despite in-place PASS — the catch worked",
              bool(ev and ev.get("overall_pass") is False))

        # 4. No self-test at all -> FAIL, explicit finding, not a silent pass
        rc, ev, out, err = run_qa_verify(FIXTURES / "no_selftest_build", scratch, "nosuite")
        check("no_selftest_build: exit code 1", rc == 1, f"got {rc}")
        check("no_selftest_build: entry_point is null", bool(ev and ev.get("entry_point") is None))
        check("no_selftest_build: notes explain why", bool(ev and ev.get("notes")))

        # 5. Nonexistent build dir -> fatal, exit 2, never a false PASS
        rc, ev, out, err = run_qa_verify(FIXTURES / "does_not_exist", scratch, "missing")
        check("missing build dir: exit code 2", rc == 2, f"got {rc}")

    # 6. qa_verify.py itself has no network-capable imports
    source = QA_VERIFY.read_text(encoding="utf-8")
    match = FORBIDDEN_IMPORT_PATTERN.search(source)
    check("qa_verify.py: no network-capable imports", match is None,
          f"found forbidden import: {match.group(0) if match else ''}")

    print("=" * 40)
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
