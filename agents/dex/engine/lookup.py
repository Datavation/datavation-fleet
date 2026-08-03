"""Stage 4/6 — the dynamic-lookup matcher (the §6 'instinctive retrieval' core).

READ-ONLY COPY for Dex. Dex *reads* the alias-index to fire the retrieval reflex; he does
not own or evolve the engine — Libby (Curatrix) is single-writer to the full engine and to
the alias-index this reads. Keep this file in sync with Libby's canonical engine\lookup.py;
if the matcher changes, Libby re-stages, Rex re-promotes. Do not fork the logic here.

Given an utterance, return the knowledge nodes whose trigger aliases fire. This is the
deterministic layer of the reflex; the agent layer (Dex) adds synonym judgement on top.
Matching: lowercase substring on normalised text, word-boundary guarded for short aliases
so 'erd' cannot fire inside 'herd'.

CLI: python lookup.py "utterance text"
Lib: match(utterance) -> [(node_id, path, matched_aliases)]
"""

import json
import re
import sys
from pathlib import Path

# Live alias-index, resolved RELATIVE to this file's own location — never hard-coded.
# Promoted home is <fleet-root>\Agents\Dex\engine\lookup.py, so parents[3] == <fleet-root>:
#   parents[0]=engine  parents[1]=Dex  parents[2]=Agents  parents[3]=<fleet-root>
INDEX = Path(__file__).resolve().parents[3] / "Tabularium" / "Vault" / "Data" / "alias-index.json"


def _normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).replace("  ", " ")


def match(utterance: str, index_path: Path = INDEX):
    nodes = json.loads(index_path.read_text(encoding="utf-8"))
    text = " " + _normalise(utterance) + " "
    hits = []
    for n in nodes:
        fired = []
        for a in n["aliases"]:
            an = _normalise(a).strip()
            if not an:
                continue
            if len(an) <= 4 or " " not in an:
                # short/single-word alias: require word boundaries
                if re.search(r"(?<![a-z0-9])" + re.escape(an) + r"(?![a-z0-9])", text):
                    fired.append(a)
            elif an in text:
                fired.append(a)
        if fired:
            hits.append({"id": n["id"], "path": n["path"], "principle": n["principle"],
                         "matched": fired})
    hits.sort(key=lambda h: (-len(h["matched"]), not h["principle"]))
    return hits


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for h in match(" ".join(sys.argv[1:])):
        print(f"{h['id']:45s} {'PRINCIPLE' if h['principle'] else '        '}  <- {h['matched']}")
