"""Bullet lint: duty openers, missing measures, vague qualifiers (advisory).

Basis (docs/research/resume-fit-guidance.md section 2 and 9): a bullet should say
what was accomplished and how it was measured, the Google X-Y-Z pattern [S78, S80],
and the recruiter makeover in [W2] led each role with scope and wrote bullets as
result plus method. This helper finds the bullets that state only an activity.

Input is resume markdown, the same input as `density_lint.py`, whose parser it
reuses. It never suggests a number: a missing measure becomes a question for the
candidate (contracts/finishing.md, Measure round), never an edit.

FLAGS (advisory: always exits 0)
  duty-opener      after any bold "Label:" lead-in the bullet opens "responsible
                   for", "worked on", "helped with" and the like
  no-measure       no number and no outcome wording: an activity-only bullet
  vague-qualifier  an adverb such as "significantly" or "dramatically" with no
                   number in the bullet

INFORMATION (counted, never flagged)
  qualitative_only a bullet with no number that does state a result in words
                   ("resulting in", "earning", "reaching", ...)

NOT LINTED: the method (Z in X-Y-Z). Only about a quarter of real bullets carry
"by", "via", "using" or "through", and good bullets usually put the method in the
action verb, so a word rule would flag most of them. The method is asked for in the
evidence interview instead.

A digit is a weak proxy for a measure ("Led 3 meetings" passes), and the outcome
wording list is deliberately loose to keep false flags down. The lint finds absence
only. Skills, education and speaking/IP lists are skipped, as in the density lint.

REVIEW FILE (`--review <work>/measure_review.yaml`): the candidate's answers, so a
later round does not ask again. Each flag prints a `key`; map it to a decision:
    "<key>": no-measure     no number or named result exists (silences no-measure
                            and vague-qualifier for that bullet)
    "<key>": keep           keep the bullet as written (silences every flag)
or `{decision: ..., note: ...}`. A key matches any bullet whose normalized text
starts with it (at least KEY_MIN_CHARS characters). Keys that match no bullet are
reported as `stale_review_keys`: harmless, usually a bullet that gained a measure.
VALUE-BLIND beyond that: it never rewrites the resume.
"""
from __future__ import annotations

import re
from pathlib import Path

import density_lint
import verbatim

KEY_CHARS = 60
KEY_MIN_CHARS = 20
PRIORITY_RANKS = 2          # the newest roles carry the most weight [S33, S39]
DECISIONS = ("no-measure", "keep")

# Bold lead-in label: "**Discovery and Validation:** Ran ..." or "**Label** Ran ...".
_LABEL = re.compile(r"^\s*\*\*[^*]+\*\*\s*:?\s*")
_DUTY = re.compile(
    r"^(?:was\s+|were\s+)?(?:responsible\s+for|in\s+charge\s+of|helped(?:\s+with|\s+to)?|"
    r"assisted(?:\s+with|\s+in)?|worked\s+(?:on|with)|involved\s+in|participated\s+in|"
    r"tasked\s+with|duties\s+included|contributed\s+to)\b",
    re.IGNORECASE,
)
# Loose on purpose (see the module note). Extend rather than tighten.
_OUTCOME = re.compile(
    r"\b(resulting\s+in|resulted\s+in|earning|earned|reaching|reached|cut|reduc\w+|"
    r"sav(?:ed|ing)|grew|grow\w*|increas\w+|doubl\w+|tripl\w+|rais\w+|lift\w+|won|"
    r"secur\w+|signed|adopt\w+|retention|revenue|first|highest|record|only|enabl\w+|"
    r"unlock\w+|so\s+that|which)\b",
    re.IGNORECASE,
)
_VAGUE = re.compile(
    r"\b(significantly|greatly|substantially|dramatically|vastly|tremendously|"
    r"hugely|massively)\b",
    re.IGNORECASE,
)


def bullet_key(text: str) -> str:
    """The short stable key a review file uses for a bullet."""
    return verbatim.normalize(text)[:KEY_CHARS]


def opener(raw_text: str) -> str:
    """The bullet's own first words, after a bold lead-in label."""
    return density_lint._visible(_LABEL.sub("", raw_text, count=1))


def classify(raw_text: str) -> dict:
    """Rules that fire for one bullet, plus whether it has a measure in words."""
    visible = density_lint._visible(raw_text)
    has_number = bool(density_lint.numbers(visible))
    has_outcome = bool(_OUTCOME.search(visible))
    rules = []
    if _DUTY.match(opener(raw_text)):
        rules.append("duty-opener")
    if not has_number and not has_outcome:
        rules.append("no-measure")
    if not has_number and _VAGUE.search(visible):
        rules.append("vague-qualifier")
    return {"rules": rules, "has_number": has_number,
            "qualitative_only": (not has_number) and has_outcome}


def load_review(path) -> dict:
    """{normalized key: decision}. Fails loudly on an unknown decision."""
    import yaml

    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    out = {}
    for key, val in data.items():
        decision = val.get("decision") if isinstance(val, dict) else val
        if decision not in DECISIONS:
            raise ValueError(f"measure_review: {key!r} has decision {decision!r}; "
                             f"use one of {', '.join(DECISIONS)}")
        out[verbatim.normalize(str(key))] = decision
    return out


def _decision_for(text: str, review: dict):
    norm = verbatim.normalize(text)
    for key, decision in review.items():
        if len(key) >= KEY_MIN_CHARS and norm.startswith(key):
            return key, decision
    return None, None


def check(md_text: str, review: dict | None = None) -> dict:
    parsed = density_lint._parse(md_text)
    rank_of = {r["entry"]: i for i, r in enumerate(parsed["roles"])}
    review = review or {}
    flags, used = [], set()
    counts = {"bullets": 0, "with_number": 0, "qualitative_only": 0, "activity_only": 0,
              "acknowledged": 0, "priority_activity_only": 0}
    per_role = {r["entry"]: {"entry": r["entry"], "rank": i, "bullets": 0, "activity_only": 0}
                for i, r in enumerate(parsed["roles"])}

    for b in parsed["bullets"]:
        if density_lint._LIST_SECTIONS.search(b["section"]):
            continue
        counts["bullets"] += 1
        c = classify(b["text"])
        counts["with_number"] += c["has_number"]
        counts["qualitative_only"] += c["qualitative_only"]
        rank = rank_of.get(b["role"])
        if b["role"] in per_role:
            per_role[b["role"]]["bullets"] += 1
        key, decision = _decision_for(b["text"], review)
        if key is not None:
            used.add(key)
        activity_only = "no-measure" in c["rules"]
        for rule in c["rules"]:
            silenced = decision == "keep" or (
                decision == "no-measure" and rule in ("no-measure", "vague-qualifier"))
            if silenced:
                continue
            flags.append({
                "rule": rule, "line": b["line"], "role": b["role"], "rank": rank,
                "priority": rank is not None and rank < PRIORITY_RANKS,
                "key": bullet_key(b["text"]),
                "detail": {"duty-opener": "opens with a duty phrase: lead with what was done",
                           "no-measure": "no number and no stated result: ask the candidate for "
                                         "a measure or a named result",
                           "vague-qualifier": "a vague qualifier with no number beside it"}[rule],
            })
        if activity_only:
            if decision in ("keep", "no-measure"):
                counts["acknowledged"] += 1
            else:
                counts["activity_only"] += 1
                if b["role"] in per_role:
                    per_role[b["role"]]["activity_only"] += 1
                if rank is not None and rank < PRIORITY_RANKS:
                    counts["priority_activity_only"] += 1
    stale = sorted(k for k in review if k not in used)
    return {"clean": not flags, "flags": flags, "stats": {**counts, "roles": list(per_role.values())},
            "stale_review_keys": stale}


def check_file(path, review_path=None) -> dict:
    review = load_review(review_path) if review_path else None
    return check(Path(path).read_text(encoding="utf-8"), review)


if __name__ == "__main__":
    import argparse
    import json

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("resume", help="resume markdown")
    ap.add_argument("--review", help="measure_review.yaml: the candidate's answers")
    args = ap.parse_args()
    result = check_file(args.resume, args.review)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["flags"]:
        print(f"BULLET LINT: {len(result['flags'])} advisory flag(s), "
              f"{result['stats']['priority_activity_only']} activity-only in the newest roles")
