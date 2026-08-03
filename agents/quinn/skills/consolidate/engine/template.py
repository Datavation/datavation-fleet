"""--template mode: emit the engine as a data-stripped, shippable bundle
(§11, Principle 8). Engine code + figure-free rules skeleton + empty extracts
drop-zone + docs. Zero real figures ever leave.

No launcher scripts are emitted (deliberate — Quinn v1): the engine is a skill
an agent's routines drive, never a batch file a human double-clicks. The
superseded refresh.bat shape is the exact interface Rex ruled wrong.
"""

from __future__ import annotations

import os
import shutil

from .skeleton import write_rules_skeleton, HOW_TO_REFRESH

REQUIREMENTS = (
    "# Optional deps — the engine degrades loudly without them, never crashes.\n"
    "openpyxl    # xlsx report + Barclays workbook ingest\n"
    "pdfplumber  # Barclaycard / mortgage-letter PDF parsing\n"
)

_TEMPLATE_README = """# Personal & SMB Finance Consolidation — Engine (template)

A local, offline engine that consolidates statements from several accounts into
one honest view. **It has no network, no credentials, and cannot move money** —
it reads local files and writes local files, nothing else.

This is the deterministic layer behind an agent's `consolidate` skill: the
agent's routines run it and read its outputs. There is no launcher to
double-click, by design.

## Use it
1. Edit `rules/sources.csv` — point each row at your statement/extract files.
2. Edit `rules/accounts.csv` — name your accounts (numbers stay local, never
   shipped); add manual lines (savings, mortgage, assets) as opening_balance rows.
3. Put statements where `sources.csv` points (see `statements/`).
4. Run: `python -m engine --workdir <this folder>` (your agent's routines do this for you).
5. Read `Finance-Dashboard.html` / `Finance-Report.xlsx`. Answer anything in `open_items.csv`.

## Layers
- **Layer A** (this engine): deterministic, offline, free to re-run.
- **Layer B** (`layer-b/accountant-prompt.md`): an OPTIONAL supervised "accountant"
  pass that reads ONLY the redacted export in `_redacted/`. Never required.

Two dependencies (`openpyxl`, `pdfplumber`) are optional — without them you lose
the xlsx view / PDF parsing but the run still completes.
"""


def emit_template(dest: str, engine_pkg_dir: str) -> list:
    """Write the bundle to `dest`. Returns a list of created top-level entries."""
    os.makedirs(dest, exist_ok=True)
    created = []

    # 1. engine package (code is identical for template + real instance)
    eng_dest = os.path.join(dest, "engine")
    if os.path.exists(eng_dest):
        shutil.rmtree(eng_dest)
    shutil.copytree(
        engine_pkg_dir, eng_dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    created.append("engine/")

    # 2. figure-free rules skeleton (with generic examples)
    write_rules_skeleton(os.path.join(dest, "rules"), with_examples=True)
    created.append("rules/")

    # 3. statements drop-zone
    stmt_dir = os.path.join(dest, "statements")
    os.makedirs(stmt_dir, exist_ok=True)
    with open(os.path.join(stmt_dir, "README.txt"), "w", encoding="utf-8") as fh:
        fh.write("Drop your statement files here (or wherever rules/sources.csv points).\n"
                 "Nothing in this folder is ever sent anywhere.\n")
    created.append("statements/")

    # 4. Layer B prompt
    lb_src = os.path.join(os.path.dirname(engine_pkg_dir), "layer-b", "accountant-prompt.md")
    lb_dest_dir = os.path.join(dest, "layer-b")
    os.makedirs(lb_dest_dir, exist_ok=True)
    if os.path.exists(lb_src):
        shutil.copy2(lb_src, os.path.join(lb_dest_dir, "accountant-prompt.md"))
    created.append("layer-b/")

    # 5. docs (no launcher scripts — the agent drives the engine)
    _write(dest, "requirements.txt", REQUIREMENTS)
    _write(dest, "HOW-TO-REFRESH.txt", HOW_TO_REFRESH)
    _write(dest, "README.md", _TEMPLATE_README)
    created += ["requirements.txt", "HOW-TO-REFRESH.txt", "README.md"]
    return created


def _write(dest, name, content, executable=False):
    path = os.path.join(dest, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    if executable:
        try:
            os.chmod(path, 0o755)
        except OSError:
            pass
