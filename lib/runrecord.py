"""Run-record emitter and validator.

Built to Run-Record-Schema-v0_1 (Archy, 2026-07-23), delivered as dependency X1.

The rule it enforces: no run-record, no "done". A run that completes without a
valid record is a FAILED run whatever the platform's green tick says -- Anthropic's
own documentation states a green status does not mean the task succeeded.

stdlib only: this runs inside the cloud sandbox with no setup step.
"""

import json
import os
import time
from datetime import datetime, timezone

SCHEMA_VERSION = "0.1"

OUTCOMES = ("pass", "fail", "parked", "refused")
TRIGGERS = ("schedule", "api", "github", "manual", "oneoff")
VERIFY_RESULTS = ("pass", "fail", "not_run")

# A failure_reason must name a cause. These do not.
GENERIC_REASONS = {
    "", "error", "errored", "failed", "failure", "something went wrong",
    "unknown", "n/a", "na", "none", "-", "exception",
}


class RunRecordError(Exception):
    """Raised when a record is malformed. Loud by design -- a malformed record
    is itself a finding, not something to quietly patch."""


def _utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class RunRecord:
    """Build a record over the life of a run, then .write() it."""

    def __init__(self, run_id, seat, trigger, instruction, fired_by=None,
                 cap_consuming=False):
        if trigger not in TRIGGERS:
            raise RunRecordError("trigger must be one of %s, got %r" % (TRIGGERS, trigger))
        self.data = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "seat": seat,
            "trigger": trigger,
            "fired_by": fired_by,
            "instruction": (instruction or "")[:500],
            "started_at": _utc_now(),
            "ended_at": None,
            "elapsed_sec": None,
            "outcome": None,
            "failure_reason": None,
            "verification": {
                "result": "not_run",
                "rubric_id": None,
                "checks": [],
                "self_checked": False,
            },
            "cost": {
                "tokens_in": None,
                "tokens_out": None,
                "usd": None,
                "cap_consuming": bool(cap_consuming),
            },
            "artefacts": [],
            "notes": None,
        }
        self._t0 = time.time()

    # -- verification -------------------------------------------------------

    def add_check(self, name, passed, detail=None, tool_used=False):
        """Record one rubric check.

        tool_used=True means a TOOL established this (counted, ran, queried,
        diffed). Asserting a result is not checking it -- self_checked only ever
        becomes true through this flag.
        """
        self.data["verification"]["checks"].append(
            {"name": name, "passed": bool(passed), "detail": detail}
        )
        if tool_used:
            self.data["verification"]["self_checked"] = True

    def set_verification(self, result, rubric_id=None):
        if result not in VERIFY_RESULTS:
            raise RunRecordError("verification.result must be one of %s" % (VERIFY_RESULTS,))
        self.data["verification"]["result"] = result
        if rubric_id:
            self.data["verification"]["rubric_id"] = rubric_id

    def add_artefact(self, kind, path_or_url):
        self.data["artefacts"].append({"kind": kind, "path_or_url": path_or_url})

    def set_cost(self, tokens_in=None, tokens_out=None, usd=None):
        c = self.data["cost"]
        if tokens_in is not None:
            c["tokens_in"] = tokens_in
        if tokens_out is not None:
            c["tokens_out"] = tokens_out
        if usd is not None:
            c["usd"] = usd

    # -- closing ------------------------------------------------------------

    def close(self, outcome, failure_reason=None, notes=None):
        if outcome not in OUTCOMES:
            raise RunRecordError("outcome must be one of %s, got %r" % (OUTCOMES, outcome))
        self.data["outcome"] = outcome
        self.data["failure_reason"] = failure_reason
        self.data["notes"] = notes
        self.data["ended_at"] = _utc_now()
        self.data["elapsed_sec"] = round(time.time() - self._t0, 3)
        validate_runrecord(self.data)   # never write an invalid record
        return self.data

    def write(self, runs_dir="runs"):
        if self.data["outcome"] is None:
            raise RunRecordError("close() the record before writing it")
        os.makedirs(runs_dir, exist_ok=True)
        path = os.path.join(runs_dir, "%s.json" % self.data["run_id"])
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2, sort_keys=True)
            fh.write("\n")
        return path


# -- validation -------------------------------------------------------------

REQUIRED_TOP = (
    "schema_version", "run_id", "seat", "trigger", "instruction",
    "started_at", "ended_at", "elapsed_sec", "outcome", "verification",
    "cost", "artefacts",
)


def validate_runrecord(rec):
    """Reject per schema section 4. Raises RunRecordError with a named reason."""
    if not isinstance(rec, dict):
        raise RunRecordError("record is not an object")

    for field in REQUIRED_TOP:
        if field not in rec or rec[field] is None:
            raise RunRecordError("missing required field: %s" % field)

    if rec["trigger"] not in TRIGGERS:
        raise RunRecordError("invalid trigger: %r" % rec["trigger"])
    if rec["outcome"] not in OUTCOMES:
        raise RunRecordError("invalid outcome: %r" % rec["outcome"])

    ver = rec["verification"]
    for field in ("result", "checks", "self_checked"):
        if field not in ver:
            raise RunRecordError("verification.%s missing" % field)
    if ver["result"] not in VERIFY_RESULTS:
        raise RunRecordError("invalid verification.result: %r" % ver["result"])

    if "cap_consuming" not in rec["cost"]:
        raise RunRecordError("cost.cap_consuming missing -- set it from the adapter, never guess")

    # Rule: outcome != pass demands a NAMED cause.
    if rec["outcome"] != "pass":
        reason = (rec.get("failure_reason") or "").strip()
        if reason.lower() in GENERIC_REASONS:
            raise RunRecordError(
                "outcome=%s requires a named failure_reason, got %r -- "
                "a failure must be loud and diagnosable" % (rec["outcome"], rec.get("failure_reason"))
            )

    # Rule: a pass may not sit on an unverified or failed check. The silent pass
    # wearing a disguise.
    if rec["outcome"] == "pass" and ver["result"] in ("fail", "not_run"):
        raise RunRecordError(
            "outcome=pass with verification.result=%s -- this is the silent pass "
            "the record exists to prevent" % ver["result"]
        )

    # Rule: verification passed but nothing was actually checked with a tool.
    if ver["result"] == "pass" and not ver["self_checked"]:
        raise RunRecordError(
            "verification.result=pass with self_checked=false -- asserting a "
            "result is not checking it"
        )

    return True


def load_and_validate(path):
    with open(path, encoding="utf-8") as fh:
        rec = json.load(fh)
    validate_runrecord(rec)
    return rec
