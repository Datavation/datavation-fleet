"""Config loader. Reads fleet.lock.json -- the committed machine artefact that
provision.py generates from fleet.yaml.

Why a lock file: the cloud sandbox has no PyYAML unless we install it, and a
setup step we don't need is a setup step that can fail at 3am. fleet.yaml is the
human source; fleet.lock.json is what code reads. verify.py fails loud if the
two have drifted, so the indirection cannot hide a change.

stdlib only.
"""

import json
import os

LOCK_FILE = "fleet.lock.json"

UNSET = "UNSET"


class ConfigError(Exception):
    pass


def repo_root(start=None):
    """Walk up until we find the lock file. Works from any depth, and from the
    cloud clone where the checkout path is not ours to choose."""
    here = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    while True:
        if os.path.exists(os.path.join(here, LOCK_FILE)):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            raise ConfigError("could not find %s above %s" % (LOCK_FILE, start or here))
        here = parent


def load(path=None):
    path = path or os.path.join(repo_root(), LOCK_FILE)
    if not os.path.exists(path):
        raise ConfigError("%s missing -- run provision.py plan first" % path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def seat(cfg, name):
    for s in cfg["seats"]:
        if s["name"] == name:
            return s
    raise ConfigError(
        "no seat named %r in fleet.lock.json (declared: %s)"
        % (name, ", ".join(s["name"] for s in cfg["seats"]))
    )


def is_set(value):
    return value is not None and value != UNSET


def require_set(value, what):
    """Refuse to proceed on an unresolved decision rather than guessing one."""
    if not is_set(value):
        raise ConfigError(
            "%s is UNSET in fleet.yaml -- this is an open decision, not a default. "
            "Resolve it and re-run provision.py." % what
        )
    return value
