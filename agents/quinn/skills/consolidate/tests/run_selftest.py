"""Dependency-light self-test. Run:  python tests/run_selftest.py

Uses plain asserts (no pytest needed) and prints a PASS/FAIL summary. Verifies
the guardrails that matter for the gate: no-network, redaction, determinism, the
PDF tie-out flag, transfer netting, custodial exclusion, the QuickBooks-extract
adapter, the manual-line net-worth roll-up (asset class), --template, and that
no launcher script is emitted (the superseded refresh.bat shape).

Synthetic, figure-free fixtures only — never real financial data.
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from engine.main import main                                    # noqa: E402
from engine.model import money, parse_date                      # noqa: E402
from engine.redact import mask_text, redacted_rows              # noqa: E402
from engine.adapters.barclaycard_pdf import parse_barclaycard_text  # noqa: E402
from engine.adapters.mortgage_pdf import parse_mortgage_text    # noqa: E402
from engine.adapters.quickbooks_csv import QuickBooksCsvAdapter  # noqa: E402
from engine.pipeline.tieout import tieout                       # noqa: E402
from engine.pipeline.dedup import dedup                         # noqa: E402
from engine.config import SourceRow                             # noqa: E402
from engine.model import Txn                                    # noqa: E402
from tests import fixtures                                      # noqa: E402


_results = []


def check(name, fn):
    try:
        fn()
        _results.append((name, True, ""))
        print(f"  PASS  {name}")
    except AssertionError as e:
        _results.append((name, False, str(e)))
        print(f"  FAIL  {name}: {e}")
    except Exception as e:  # unexpected
        _results.append((name, False, f"ERROR {type(e).__name__}: {e}"))
        print(f"  ERROR {name}: {type(e).__name__}: {e}")


# ---------------------------------------------------------------- guardrails
FORBIDDEN = ["requests", "urllib", "http.client", "httplib", "socket", "smtplib",
             "ftplib", "telnetlib", "asyncio", "aiohttp", "websocket", "paramiko"]


def test_no_network_imports():
    hits = []
    eng_dir = os.path.join(ROOT, "engine")
    for dp, _, files in os.walk(eng_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            with open(os.path.join(dp, f), encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    s = line.strip()
                    if s.startswith("#"):
                        continue
                    for mod in FORBIDDEN:
                        if f"import {mod}" in s or f"from {mod}" in s:
                            hits.append(f"{f}:{i} {s}")
    assert not hits, f"forbidden network imports found: {hits}"


# ---------------------------------------------------------------- pure units
def test_money():
    assert str(money("1,234.56")) == "1234.56"
    assert str(money("(50.00)")) == "-50.00"
    assert str(money("£9.9")) == "9.90"
    assert str(money("100")) == "100.00"


def test_dates():
    assert parse_date("02/05/2025") == "2025-05-02"
    assert parse_date("15 May 2025", fmts=["%d %b %Y"]) == "2025-05-15"
    assert parse_date("2025-05-02") == "2025-05-02"


def test_redaction():
    assert mask_text("TRANSFER 12345678 sort 22-22-00") == "TRANSFER ###### sort **-**-**"
    t = Txn(date="2025-05-01", amount=money("-10.00"), description="CARD 4000123412341234",
            raw_description="x", account_id="a", world="Personal", source_file="f", adapter="x")
    row = redacted_rows([t])[0]
    assert "4000123412341234" not in row["description"]
    assert "raw_description" not in row  # raw dropped entirely


def test_barclaycard_parse_and_tieout_good():
    txns, ct, notes = parse_barclaycard_text(
        fixtures.BARCLAYCARD_TEXT_GOOD, "barclaycard", "Personal", fixtures.BARCLAYCARD_FILE)
    assert len(txns) == 3, f"expected 3 txns, got {len(txns)}"
    # one credit (positive), two charges (negative)
    assert sum(1 for t in txns if t.amount > 0) == 1
    assert str(ct.total_spend) == "74.99"
    assert str(ct.total_payments) == "100.00"
    items = tieout(txns, [ct])
    assert items == [], f"good statement should not flag: {items}"


def test_barclaycard_tieout_bad_flags():
    txns, ct, notes = parse_barclaycard_text(
        fixtures.BARCLAYCARD_TEXT_BAD, "barclaycard", "Personal", fixtures.BARCLAYCARD_FILE)
    items = tieout(txns, [ct])
    kinds = {i["type"] for i in items}
    assert "tieout_spend" in kinds, f"bad statement must flag tieout_spend, got {kinds}"


def test_mortgage_parse():
    ct, notes = parse_mortgage_text(fixtures.MORTGAGE_TEXT, "mortgage", "m.pdf")
    assert ct.extras.get("balance") == "150000.00", ct.extras
    assert ct.extras.get("payments_made") == 12, ct.extras
    assert notes == [], f"consistent letter should not warn: {notes}"


def test_mortgage_tieout_warns():
    bad = fixtures.MORTGAGE_TEXT.replace("Total amount paid 9600.00",
                                         "Total amount paid 9999.00")
    ct, notes = parse_mortgage_text(bad, "mortgage", "m.pdf")
    assert notes, "inconsistent mortgage letter should warn"


def _qb_source_row(path):
    return SourceRow(world="RexHomeServices", account_id="rhs_quickbooks",
                     adapter="quickbooks_csv", path=path, kind="file")


def test_quickbooks_adapter_parse():
    adapter = QuickBooksCsvAdapter()
    with tempfile.TemporaryDirectory() as wd:
        qb = os.path.join(wd, "qb_rhs.csv")
        with open(qb, "w", encoding="utf-8") as fh:
            fh.write(fixtures.QB_CSV)
        mz = os.path.join(wd, "monzo.csv")
        with open(mz, "w", encoding="utf-8") as fh:
            fh.write(fixtures.MONZO_CSV)
        # detection: claims the QB export, does NOT grab a Monzo export
        assert adapter.detect(qb), "QB adapter must detect a QB transaction export"
        assert not adapter.detect(mz), "QB adapter must not claim a Monzo export"
        res = adapter.ingest(qb, _qb_source_row(qb), rules=None)
        # 4 data rows in; title rows, header, and the no-date TOTAL footer skipped
        assert len(res.transactions) == 4, [t.description for t in res.transactions]
        amounts = sorted(str(t.amount) for t in res.transactions)
        assert amounts == ["-85.25", "120.00", "120.00", "350.00"], amounts
        assert all(t.ext_id == "" for t in res.transactions), \
            "QB Num must not be used as ext_id (split lines share it)"
        assert all(t.date.startswith("2025-05-") for t in res.transactions)


def test_quickbooks_split_lines_survive_dedup():
    adapter = QuickBooksCsvAdapter()
    with tempfile.TemporaryDirectory() as wd:
        qb = os.path.join(wd, "qb_rhs.csv")
        with open(qb, "w", encoding="utf-8") as fh:
            fh.write(fixtures.QB_CSV)
        res = adapter.ingest(qb, _qb_source_row(qb), rules=None)
        txns = [Txn.from_raw(r) for r in res.transactions]
        deduped, n_dups = dedup(txns)
        # the two identical split lines are genuine repeats — both must survive.
        # (Re-run idempotency is separately proven by test_determinism: each run
        # re-reads the file once and reproduces the same occurrence ordinals.)
        assert n_dups == 0, f"split lines wrongly collapsed ({n_dups} dropped)"
        assert len(deduped) == 4, len(deduped)


# ---------------------------------------------------------------- end to end
def _run_engine(workdir):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main(["--workdir", workdir, "--run-date", "2025-06-01"])
    return rc, buf.getvalue()


def test_end_to_end():
    with tempfile.TemporaryDirectory() as wd:
        facts = fixtures.build_workdir(wd)
        rc, out = _run_engine(wd)
        assert rc == 0, f"engine exit {rc}\n{out}"
        for f in ["transactions.csv", "open_items.csv", "Finance-Dashboard.html"]:
            assert os.path.exists(os.path.join(wd, f)), f"missing output {f}"
        assert os.path.exists(os.path.join(wd, "_redacted", "transactions_redacted.csv"))
        # xlsx OR the csv fallback
        assert (os.path.exists(os.path.join(wd, "Finance-Report.xlsx"))
                or os.path.isdir(os.path.join(wd, "report_csv")))
        # transfer netting
        if facts["has_xlsx"]:
            assert "internal transfers   : 1" in out, out
        # uncategorised counted (MYSTERY VENDOR)
        assert "uncategorised        :" in out
        # redacted export must not contain a raw fake account number
        with open(os.path.join(wd, "_redacted", "transactions_redacted.csv"), encoding="utf-8") as fh:
            red = fh.read()
        assert "22220000" not in red, "account number leaked into redacted export"


def test_determinism():
    with tempfile.TemporaryDirectory() as wd:
        fixtures.build_workdir(wd)
        _run_engine(wd)
        with open(os.path.join(wd, "transactions.csv"), "rb") as fh:
            first = fh.read()
        _run_engine(wd)
        with open(os.path.join(wd, "transactions.csv"), "rb") as fh:
            second = fh.read()
        assert first == second, "transactions.csv not byte-identical on re-run"


def _dashboard_data(wd):
    import json, re
    html = open(os.path.join(wd, "Finance-Dashboard.html"), encoding="utf-8").read()
    m = re.search(r'type="application/json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1).replace("<\\/", "</"))


def test_custodial_excluded():
    with tempfile.TemporaryDirectory() as wd:
        facts = fixtures.build_workdir(wd)
        _run_engine(wd)
        con = _dashboard_data(wd)["consolidated"]
        # the 50000 custodial bond must be in custodial_total, not net_position/net_worth
        assert float(con["custodial_total"]) >= 50000.0, con["custodial_total"]
        assert float(con["net_position"]) < 50000.0, "custodial leaked into net position"
        expected_worth = float(con["liquid_total"]) + float(con["asset_total"]) \
            + float(con["liability_total"])
        assert abs(float(con["net_worth"]) - expected_worth) < 0.01, \
            "net_worth must be liquid + assets + liabilities only (no custodial)"


def test_manual_lines_net_worth_rollup():
    """The §10.2 manual/config lines: an illiquid asset (the house) and a manual
    savings line, declared in accounts.csv with an opening_balance and no
    transactions, must land in the right buckets of the roll-up."""
    with tempfile.TemporaryDirectory() as wd:
        facts = fixtures.build_workdir(wd)
        _run_engine(wd)
        con = _dashboard_data(wd)["consolidated"]
        # the house: in asset_total and net_worth, never in liquid or net_position
        assert con["asset_total"] == facts["asset_total"], con["asset_total"]
        assert float(con["liquid_total"]) < float(facts["asset_total"]), \
            "illiquid asset leaked into liquid total"
        assert abs(float(con["net_worth"]) - float(con["net_position"])
                   - float(facts["asset_total"])) < 0.01, \
            "net_worth must equal net_position + illiquid assets"
        # the manual savings line: non-custodial savings counts as liquid
        assert float(con["liquid_total"]) >= float(facts["manual_savings"]), \
            "manual savings line missing from liquid total"
        # both manual lines appear as account rows with the right class
        by_id = {a["account_id"]: a for a in con["accounts"]}
        assert by_id["house"]["class"] == "asset", by_id["house"]
        assert by_id["ns_savings"]["class"] == "liquid", by_id["ns_savings"]


def test_init_creates_rules_skeleton():
    with tempfile.TemporaryDirectory() as wd:
        dest = os.path.join(wd, "fresh")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--init", dest])
        assert rc == 0, buf.getvalue()
        rules = os.path.join(dest, "rules")
        assert os.path.isdir(rules), "--init did not create rules/"
        for f in ["sources.csv", "accounts.csv", "categories.csv", "recurring.csv"]:
            assert os.path.exists(os.path.join(rules, f)), f"--init did not seed {f}"
        assert os.path.exists(os.path.join(dest, "HOW-TO-REFRESH.txt"))
        # a run against the freshly-seeded rules must not hit "rules folder not found"
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2):
            rc2 = main(["--workdir", dest, "--inventory-only"])
        assert rc2 == 0, buf2.getvalue()


def test_run_without_rules_fails_loud_not_silent():
    with tempfile.TemporaryDirectory() as wd:
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc = main(["--workdir", wd])
        assert rc != 0, "run against a workdir with no rules/ must not report success"
        assert "rules folder not found" in buf.getvalue()


def test_template_emits_clean_bundle():
    with tempfile.TemporaryDirectory() as dest:
        out_dir = os.path.join(dest, "bundle")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--template", out_dir])
        assert rc == 0
        assert os.path.isdir(os.path.join(out_dir, "engine"))
        assert os.path.exists(os.path.join(out_dir, "rules", "sources.csv"))
        assert os.path.exists(os.path.join(out_dir, "layer-b", "accountant-prompt.md"))
        # no machine-owned ledger or real data in a fresh template
        assert not os.path.exists(os.path.join(out_dir, "transactions.csv"))
        # NO launcher scripts — the superseded refresh.bat shape must not return
        for launcher in ("refresh.bat", "refresh.command", "install-routine.bat"):
            assert not os.path.exists(os.path.join(out_dir, launcher)), \
                f"template must not emit {launcher} (batch-file interface superseded)"
        assert not os.path.exists(os.path.join(out_dir, "engine", "runners.py")), \
            "runners.py (launcher bodies) must not ship in the engine"


def run():
    print("Finance Engine — self-test")
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            check(name[5:], fn)
    passed = sum(1 for _, ok, _ in _results if ok)
    total = len(_results)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(run())
