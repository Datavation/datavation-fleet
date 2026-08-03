"""personal_scan.py -- the personal-data GUARD for memory reconcile (Rex ruling 2026-08-03,
POINT 2). Defense-in-depth: before the trusted CI job promotes any memory to shared main, this
scans the content for personal-class markers and DIVERTS anything that looks personal to
quarantine + a loud flag -- it never reaches shared main by default.

Where this sits in the three-line defence:
  1. the agent's OWN write-time classification (operational vs architecture/personal) -- primary;
  2. THIS scanner at promotion time -- catches what slips past (1); FAIL-CLOSED;
  3. the periodic Memory Audit -- retrospective backstop.

Design stance: this is a HEURISTIC, and it is deliberately CONSERVATIVE -- it errs toward
flagging. A false positive costs one quarantined line a human re-clears; a false negative leaks
Austen's private data into a shareable repo. Those costs are not symmetric, so we bias to recall.
It is NOT the arbiter of truth; it is a tripwire that routes doubt to a human.

stdlib only -- runs in the CI job with no setup.
"""

import re

# Each category: (name, compiled patterns). Word-boundaried where a bare substring would over-match.
# Money -- ACTUAL personal financial DATA, not finance-domain vocabulary. Operational seats
# (Quinn, Marshall) legitimately mention banks/invoices/mortgages figure-free, so a bare bank
# name or "invoice" must NOT flag; a real figure, salary, or account identifier must.
_MONEY = [
    r"[£$€]\s?\d",                                                   # an actual currency figure
    r"\b\d+\s?k\b\s*(?:salary|pa|per annum|/?yr|a year|base|package)",  # "105k salary"
    r"\b(?:salary|payslip|take-?home|net worth|burn rate|disposable income)\b",
    r"\b(?:sort ?code|account number|iban|card number)\b",           # account identifiers
    r"\b(?:my|his|her|personal|household|family) finances\b",
    r"\bbank statement\b",
]
# Family / relationships / home life. Bare "family" dropped (technical "model family"); and
# "partner" (business partner), "separation" (routing/data separation), "children" (tree/docket
# children) dropped -- too many technical uses. Spouse/kin terms + possessive "family" cover the
# real signal.
_FAMILY = [
    r"\b(?:wife|husband|spouse|fianc)\b",
    r"\b(?:daughter|son|kids|newborn)\b",
    r"\b(?:married|divorce|widow)\b",
    r"\b(?:my|his|her) family\b", r"\bfamily member\b",
]
# Health / medical / mental state. "breakdown" dropped (cost/task breakdown is technical).
_HEALTH = [
    # "disease" dropped -- metaphorical use is common ("the root disease: duplicated truth").
    r"\b(?:diagnos|illness|medical|therapy|therapist|prescription|surgery|hospitali[sz]|mental health)\b",
    r"\b(?:anxiety|depression|burnout|insomnia)\b",
]
# Personal employment / job-hunt (distinct from fleet role changes).
_EMPLOYMENT = [
    r"\b(?:interview|rejection|recruiter|redundan|got the job|didn'?t get)\b",
    r"\brésumé\b", r"\bCV tailoring\b",   # bare "resume" dropped -- matches the --resume CLI flag
]
# First-person emotional / private-life notes.
_EMOTIONAL = [
    r"\bI (?:felt|feel|was|am) (?:worried|anxious|ashamed|afraid|scared|stressed|embarrassed|proud|hurt|angry|sad)\b",
    r"\b(?:self-doubt|imposter|my confidence|personally)\b",
]

_CATEGORIES = [
    ("money", _MONEY), ("family", _FAMILY), ("health", _HEALTH),
    ("employment", _EMPLOYMENT), ("emotional", _EMOTIONAL),
]
_COMPILED = [(name, [re.compile(p, re.IGNORECASE) for p in pats]) for name, pats in _CATEGORIES]


def scan(text):
    """Return a dict {category: [evidence snippets]} of personal-class hits. Empty = clean.

    Evidence is the matched fragment plus a little surrounding context, so a human reviewing the
    quarantine can judge fast WITHOUT the scanner having to reproduce the whole line elsewhere."""
    hits = {}
    for name, patterns in _COMPILED:
        for pat in patterns:
            for m in pat.finditer(text or ""):
                start, end = max(0, m.start() - 20), min(len(text), m.end() + 20)
                snippet = text[start:end].replace("\n", " ").strip()
                hits.setdefault(name, [])
                if snippet not in hits[name]:
                    hits[name].append(snippet)
    return hits


def is_personal(text):
    """True if the text trips any personal-class marker. Fail-closed: any hit -> personal."""
    return bool(scan(text))


def summary(hits):
    """One-line, category-only summary for a flag/log line. Reproduces NO sensitive content."""
    if not hits:
        return "clean"
    return "PERSONAL-CLASS: " + ", ".join("%s(%d)" % (c, len(v)) for c, v in sorted(hits.items()))
