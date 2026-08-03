r"""
qa_verify.py — Tessa's mechanical QA check (skills/qa-verify).

Given a staged build folder, this script:
  1. Auto-detects the build's own self-test entry point.
  2. Runs it IN PLACE.
  3. Copies the build to an isolated scratch folder and runs the SAME entry point there
     ("clean-environment check") — so a test that only passes on the builder's own leftover
     state is caught, not trusted.
  4. Fingerprints the OS/interpreter this machine actually has.
  5. Writes a JSON evidence file and prints a summary. Exit 0 only if BOTH runs passed.

Deliberately narrow: this is the mechanical half of the qa-verify skill (SKILL.md). It does
NOT judge whether a Definition of Done is met semantically, and it does NOT drive a build's
real (non-test) entry point — those are the judgment steps SKILL.md hands to the agent running
this. This script never fixes anything and never writes outside the scratch folder it creates
and the evidence file it is told to write to.

No network access. No imports capable of reaching one — same discipline the finance-engine
build enforces on itself, checked by tests/selftest_qa_verify.py's own no_network_imports test.

Usage:
  python qa_verify.py --build-dir <path to Builds\<name>> --out <path for evidence JSON>
  python qa_verify.py --build-dir <path> --out <path> --scratch-root <path>
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Entry points tried in order; first match wins. Relative to the build root.
CANDIDATE_ENTRY_POINTS = [
    ("tests/run_selftest.py", ["python", "tests/run_selftest.py"]),
    ("tests/selftest.py", ["python", "tests/selftest.py"]),
    ("tests/run-tests.ps1", ["powershell", "-NoProfile", "-File", "tests/run-tests.ps1"]),
    ("tests/run_batch_selftest.py", ["python", "tests/run_batch_selftest.py"]),
]

# A pytest-discoverable tests/ folder is the fallback if none of the above exist.
PYTEST_FALLBACK = ("tests/", ["python", "-m", "pytest", "tests", "-q"])

# Never copied into the scratch clean-environment check — strips STATE, not vendored deps.
EXCLUDE_DIR_NAMES = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}


def _ignore_state_dirs(_dir, names):
    return [n for n in names if n in EXCLUDE_DIR_NAMES]


def detect_entry_point(build_dir: Path):
    """Return (relative_marker, command_list) for the first entry point found, or None."""
    for marker, cmd in CANDIDATE_ENTRY_POINTS:
        if (build_dir / marker).is_file():
            return marker, cmd
    tests_dir = build_dir / "tests"
    if tests_dir.is_dir() and any(tests_dir.glob("test_*.py")):
        return PYTEST_FALLBACK
    return None


def run_entry_point(build_dir: Path, cmd: list[str]) -> dict:
    """Run cmd with cwd=build_dir. Never raises — captures failure as a result, not an exception."""
    started = datetime.now(timezone.utc)
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(build_dir),
            capture_output=True,
            text=True,
            timeout=600,
        )
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        return {
            "command": cmd,
            "returncode": proc.returncode,
            "passed": proc.returncode == 0,
            "stdout_tail": proc.stdout[-4000:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-4000:] if proc.stderr else "",
            "elapsed_seconds": round(elapsed, 2),
            "error": None,
        }
    except FileNotFoundError as e:
        return {
            "command": cmd,
            "returncode": None,
            "passed": False,
            "stdout_tail": "",
            "stderr_tail": "",
            "elapsed_seconds": 0.0,
            "error": f"interpreter not found on this machine: {e}",
        }
    except subprocess.TimeoutExpired:
        return {
            "command": cmd,
            "returncode": None,
            "passed": False,
            "stdout_tail": "",
            "stderr_tail": "",
            "elapsed_seconds": 600.0,
            "error": "timed out after 600s",
        }


def make_clean_copy(build_dir: Path, scratch_root: Path, build_name: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = scratch_root / f"{ts}-{build_name}"
    shutil.copytree(build_dir, dest, ignore=_ignore_state_dirs)
    return dest


def env_fingerprint() -> dict:
    fp = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "powershell_available": shutil.which("powershell") is not None or shutil.which("pwsh") is not None,
    }
    ps_exe = shutil.which("powershell") or shutil.which("pwsh")
    if ps_exe:
        try:
            proc = subprocess.run(
                [ps_exe, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                capture_output=True, text=True, timeout=30,
            )
            fp["powershell_version"] = proc.stdout.strip() or None
        except Exception:
            fp["powershell_version"] = None
    else:
        fp["powershell_version"] = None
    return fp


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    p = argparse.ArgumentParser(description="Tessa qa-verify: self-test + clean-environment check.")
    p.add_argument("--build-dir", required=True, help="path to the build folder under Builds\\<name>")
    p.add_argument("--out", required=True, help="path to write the JSON evidence file")
    p.add_argument("--scratch-root", help="where to make the clean copy (default: alongside --out)")
    args = p.parse_args(argv)

    build_dir = Path(args.build_dir).resolve()
    out_path = Path(args.out).resolve()
    scratch_root = Path(args.scratch_root).resolve() if args.scratch_root else out_path.parent / "qa-scratch"
    scratch_root.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "build_dir": str(build_dir),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": env_fingerprint(),
        "entry_point": None,
        "in_place_run": None,
        "clean_copy_run": None,
        "clean_copy_path": None,
        "overall_pass": False,
        "notes": [],
    }

    if not build_dir.is_dir():
        result["notes"].append(f"FATAL: build_dir does not exist or is not a directory: {build_dir}")
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"[qa_verify] FATAL: build dir not found: {build_dir}", file=sys.stderr)
        return 2

    found = detect_entry_point(build_dir)
    if not found:
        result["notes"].append(
            "No self-test entry point found (checked run_selftest.py, selftest.py, "
            "run-tests.ps1, run_batch_selftest.py, pytest-discoverable tests/). "
            "This is a finding, not a silent pass: overall_pass stays False."
        )
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print("[qa_verify] FAIL: no self-test entry point found.", file=sys.stderr)
        return 1

    marker, cmd = found
    result["entry_point"] = marker

    result["in_place_run"] = run_entry_point(build_dir, cmd)

    build_name = build_dir.name
    try:
        clean_dir = make_clean_copy(build_dir, scratch_root, build_name)
        result["clean_copy_path"] = str(clean_dir)
        result["clean_copy_run"] = run_entry_point(clean_dir, cmd)
    except Exception as e:
        result["notes"].append(f"clean-copy check could not run: {e}")
        result["clean_copy_run"] = {"passed": False, "error": str(e)}

    result["overall_pass"] = bool(
        result["in_place_run"].get("passed") and result["clean_copy_run"].get("passed")
    )

    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    verdict = "PASS" if result["overall_pass"] else "FAIL"
    print(f"[qa_verify] {verdict} — entry point: {marker}")
    print(f"[qa_verify]   in-place:   {'PASS' if result['in_place_run'].get('passed') else 'FAIL'}")
    print(f"[qa_verify]   clean-copy: {'PASS' if result['clean_copy_run'].get('passed') else 'FAIL'}")
    print(f"[qa_verify]   ran on: {result['environment']['system']} {result['environment']['release']}, "
          f"Python {result['environment']['python_version']}")
    print(f"[qa_verify] evidence: {out_path}")

    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
