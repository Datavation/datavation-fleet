"""personal_store.py -- a seat's reference to the PERSONAL STORE (Option B, Rex/Archy 2026-08-03).

Personal-class context/memory lives in a SEPARATE private repo (${org.personal_store_repo}), never
in the shareable fleet repo. A seat resolves the store here and reads/writes its personal files
under agents/<seat>/ IN THE STORE -- never in agents/<seat>/MEMORY.md of the shareable repo. The
shareable repo carries only a HELD placeholder pointing here.

Config comes from the ENVIRONMENT (set at deploy by the human as a secret, never committed):
  PERSONAL_STORE_REPO    e.g. Datavation/datavation-fleet-personal
  PERSONAL_STORE_TOKEN   a fine-grained token scoped to ONLY that repo (contents: read+write)

FAIL-CLOSED by design: if the store is not configured, personal context is simply UNAVAILABLE and
the seat runs without it. It must NEVER fall back to reading or writing personal data in the
shareable repo -- that is the whole point of Option B. The token is never written to disk or logged.

stdlib only.
"""

import os
import subprocess
import tempfile


def is_configured():
    return bool(os.environ.get("PERSONAL_STORE_REPO") and os.environ.get("PERSONAL_STORE_TOKEN"))


def _authed_url(repo, token):
    return "https://x-access-token:%s@github.com/%s.git" % (token, repo)


def clone_store(dest=None):
    """Clone the personal store to a scratch dir; return its path, or None if not configured.
    Scrubs the token from the clone's remote so it is not left in .git/config."""
    repo = os.environ.get("PERSONAL_STORE_REPO")
    token = os.environ.get("PERSONAL_STORE_TOKEN")
    if not repo or not token:
        return None
    dest = dest or tempfile.mkdtemp(prefix="personal-store-")
    subprocess.run(["git", "clone", "--depth", "1", _authed_url(repo, token), dest],
                   check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", dest, "remote", "set-url", "origin",
                    "https://github.com/%s.git" % repo], capture_output=True, text=True)
    return dest


def seat_personal_dir(store_path, seat):
    """Path to a seat's personal tree inside a cloned store (agents/<seat>/)."""
    return os.path.join(store_path, "agents", seat)


def read_seat_personal(seat, dest=None):
    """Return {relpath: text} of a seat's personal files from the store, or {} if unavailable
    (fail-closed). The caller loads these as the seat's personal context/memory at boot."""
    store = clone_store(dest)
    if not store:
        return {}
    base = seat_personal_dir(store, seat)
    out = {}
    for root, _dirs, files in os.walk(base):
        for name in files:
            full = os.path.join(root, name)
            out[os.path.relpath(full, base)] = open(full, encoding="utf-8", errors="replace").read()
    return out
