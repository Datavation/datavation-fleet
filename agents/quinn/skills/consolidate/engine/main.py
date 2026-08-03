"""CLI entry point (Layer A orchestration).

  python -m engine --workdir DIR         run the full pipeline
  python -m engine --workdir DIR --inventory-only    just report what's found
  python -m engine --init DIR            seed a fresh workdir with a rules skeleton
  python -m engine --template DIR        emit the data-stripped shippable bundle

The engine reads local files and writes ONLY inside WORKDIR. It imports nothing
that can reach a network, a bank, or an email server.
"""

from __future__ import annotations

import argparse
import os
import sys

from .config import load_rules
from .skeleton import write_rules_skeleton, HOW_TO_REFRESH
from .pipeline.inventory import build_inventory, format_inventory
from .pipeline.ingest import ingest_all
from .pipeline.normalise import normalise
from .pipeline.dedup import dedup
from .pipeline.categorise import categorise
from .pipeline.reconcile import reconcile
from .pipeline.tieout import tieout
from .pipeline.render import write_transactions, append_open_items
from .redact import write_redacted
from .report_xlsx import write_report
from .dashboard import write_dashboard
from .analytics import compute

_NOTE_FLAGS = ("NO ADAPTER", "tie-out", "not in accounts.csv", "not installed")


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


def cmd_run(args) -> int:
    workdir = os.path.abspath(args.workdir)
    rules_dir = os.path.abspath(args.rules) if args.rules else os.path.join(workdir, "rules")
    base_dir = os.path.abspath(args.sources_base) if args.sources_base else workdir
    run_date = args.run_date or _today()

    if not os.path.isdir(rules_dir):
        print(f"ERROR: rules folder not found: {rules_dir}\n"
              f"Seed one with:  python -m engine --init \"{workdir}\"", file=sys.stderr)
        return 2
    os.makedirs(workdir, exist_ok=True)

    rules = load_rules(rules_dir)

    # 1. inventory
    inventory = build_inventory(rules, base_dir)
    print(format_inventory(inventory))
    print()
    if args.inventory_only:
        return 0

    # 2-6. ingest -> normalise -> dedup -> categorise -> reconcile -> tieout
    bundle = ingest_all(inventory, rules)
    txns = normalise(bundle.raw_txns, rules)
    txns, n_dups = dedup(txns)
    n_uncat = categorise(txns, rules)
    n_transfers, transfer_items = reconcile(txns, args.window_days, rules)
    tieout_items = tieout(txns, bundle.control_totals)

    # mortgage balances (liability side) from the letter control totals
    mortgage_balances = {}
    for ct in bundle.control_totals:
        bal = ct.extras.get("balance") if ct.extras else None
        if bal is not None:
            mortgage_balances[ct.account_id] = bal

    # important ingest notes -> persistent open_items (deduped by id downstream)
    note_items = [
        {"type": "ingest_note", "account_id": "", "detail": n}
        for n in bundle.notes if any(f in n for f in _NOTE_FLAGS)
    ]

    # 7. write ledger + open_items
    txn_path = write_transactions(txns, workdir)
    oi_path, n_new_items, all_items = append_open_items(
        transfer_items + tieout_items + note_items, workdir, run_date)

    # 8. views: redacted export, xlsx, dashboard
    views = compute(txns, rules, mortgage_balances=mortgage_balances, open_items=all_items)
    red_path = write_redacted(txns, workdir)
    xlsx_path, xlsx_note = write_report(views, txns, workdir)
    dash_path = write_dashboard(views, workdir)

    # 9. console summary (§4.8)
    print("=" * 60)
    print("RUN SUMMARY")
    print(f"  transactions written : {len(txns)}  (dropped {n_dups} duplicate rows)")
    print(f"  uncategorised        : {n_uncat}")
    print(f"  internal transfers   : {n_transfers} pair(s) netted out of burn")
    print(f"  open items (total)   : {len(all_items)}  ({n_new_items} new this run)")
    for n in bundle.notes:
        print(f"  note: {n}")
    if xlsx_note:
        print(f"  note: {xlsx_note}")
    print("  outputs:")
    for p in (txn_path, oi_path, red_path, xlsx_path, dash_path):
        print(f"    - {p}")
    needs_judgment = n_uncat + len(tieout_items) + len(transfer_items)
    if needs_judgment:
        print(f"\n  Run the accountant pass (Layer B) to resolve {needs_judgment} item(s).")
    print("=" * 60)
    print("DONE.")
    return 0


def cmd_init(dest) -> int:
    dest = os.path.abspath(dest)
    os.makedirs(dest, exist_ok=True)
    write_rules_skeleton(os.path.join(dest, "rules"), with_examples=True)
    with open(os.path.join(dest, "HOW-TO-REFRESH.txt"), "w", encoding="utf-8") as fh:
        fh.write(HOW_TO_REFRESH)
    print(f"Seeded workdir at {dest} (edit rules/*.csv, then run without --init).")
    return 0


def cmd_template(dest) -> int:
    from .template import emit_template
    engine_pkg_dir = os.path.dirname(os.path.abspath(__file__))
    created = emit_template(os.path.abspath(dest), engine_pkg_dir)
    print(f"Template bundle written to {os.path.abspath(dest)}:")
    for c in created:
        print(f"  - {c}")
    print("Data-stripped: zero real figures. This is the shippable fleet asset.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="engine", description="Finance Consolidation Engine (Layer A)")
    p.add_argument("--workdir", help="working folder (rules/, outputs). Default: current dir")
    p.add_argument("--rules", help="rules folder (default: WORKDIR/rules)")
    p.add_argument("--sources-base", help="base dir for relative source paths (default: WORKDIR)")
    p.add_argument("--window-days", type=int, default=3, help="internal-transfer match window (default 3)")
    p.add_argument("--run-date", help="date stamped on new open_items (default: today)")
    p.add_argument("--inventory-only", action="store_true", help="only report what's found")
    p.add_argument("--init", metavar="DIR", help="seed a fresh workdir with a rules skeleton")
    p.add_argument("--template", metavar="DIR", help="emit the data-stripped shippable bundle")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.template:
        return cmd_template(args.template)
    if args.init:
        return cmd_init(args.init)
    if not args.workdir:
        args.workdir = os.getcwd()
    return cmd_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
