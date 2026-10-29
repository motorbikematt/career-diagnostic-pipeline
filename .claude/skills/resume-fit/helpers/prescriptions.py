"""Enforce the mandatory prescriptions rule (v1 Stage 3, preserved verbatim):

"Every Recoverable Gap identified in Stage 1 (items that are None/Partial on
resume but present in Work History) must have a corresponding Add prescription
below, citing the specific Work History section. No Recoverable Gap may be left
unaddressed."

This turns that rule into a code guarantee, not a prompt request: the finishing
loop cannot proceed while a recoverable gap has no covering Add prescription.

It also rejects AMBIGUOUS targets. Each prescription's `target` must name one
location. A target offering alternatives ("under the Summary or as a new early
entry") forces the drafting step to guess, and a wrong guess once put an old
role at the top of a resume.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

# Words that signal a target is offering a choice of locations.
_AMBIGUOUS = re.compile(r"\b(or|either|alternatively)\b", re.IGNORECASE)


#
# Summary and banner (TODO 32, decision D1, 2026-10-22).
#
# Every resume has a summary, so every run needs exactly one `summary`
# prescription (rebuild the seed resume's summary, or Add one if it has none).
# The banner line under the name uses the JD's title verbatim: an owner-approved
# exception to the no-fabrication rule, limited to the banner. The exception does
# not cover a credentialed title (one that implies a license or credential): such
# a banner needs a WHD `source` like any other claim, and without one it is not
# allowed. The term list is conservative and meant to be extended.
_CREDENTIALED = re.compile(
    r"\b(engineer|architect|nurse|rn|lpn|cpa|physician|doctor|surgeon|dentist|"
    r"pharmacist|veterinarian|attorney|lawyer|counsel|therapist|psychologist|"
    r"actuary|electrician)\b",
    re.IGNORECASE,
)


def _norm(text) -> str:
    return " ".join((text or "").split())


def credentialed_title(title: str) -> bool:
    return bool(_CREDENTIALED.search(title or ""))


def summary_issues(prescriptions: dict) -> list:
    n = sum(1 for p in prescriptions.get("prescriptions", []) if p.get("type") == "summary")
    if n == 0:
        return ["no summary prescription: every resume has a summary (rebuild or add one)"]
    if n > 1:
        return [f"{n} summary prescriptions: exactly one is allowed"]
    return []


def banner_issues(prescriptions: dict, requirements: dict | None = None) -> list:
    """Banner rules. Role-dependent checks run only when `requirements` is given."""
    banners = [p for p in prescriptions.get("prescriptions", []) if p.get("type") == "banner"]
    issues = []
    if len(banners) > 1:
        issues.append(f"{len(banners)} banner prescriptions: at most one is allowed")
    role = _norm(requirements.get("role")) if requirements else ""
    for b in banners:
        title = _norm(b.get("jd_title"))
        if not title:
            issues.append("banner prescription has no jd_title")
            continue
        if role and title != role:
            issues.append(f"banner jd_title {title!r} is not the JD role {role!r} verbatim")
        if credentialed_title(title) and not b.get("source"):
            issues.append(
                f"banner title {title!r} implies a license or credential: the banner "
                "exception does not cover it, so it needs a WHD source or no banner"
            )
    if requirements is not None and role and not banners and not credentialed_title(role):
        issues.append("no banner prescription: the JD title banner is required "
                      "(only a credentialed title is exempt)")
    return issues


def recoverable_gap_ids(gapmap: dict) -> list:
    return [r["id"] for r in gapmap.get("requirements", []) if r.get("recoverable")]


def ambiguous_targets(prescriptions: dict) -> list:
    return [
        p.get("target", "")
        for p in prescriptions.get("prescriptions", [])
        if _AMBIGUOUS.search(p.get("target") or "")
    ]


#
# Role budget (TODO 42, 2026-10-29). The density lint gives each Experience role a
# bullet budget by recency. An Add that grows a role past it must be paired with a
# Cut or Remove in the same role, or carry an approved `over_budget_reason`.
# Prescriptions never draft wording, so only bullet counts are checked here; the
# lint's word ceilings still apply to the draft. A role that is already over budget
# is not flagged unless an Add makes it grow.
#
_ROLE_SPLIT = re.compile(r"\s+[—–-]\s+")


def _role_key(text) -> str:
    return _norm(text).casefold()


def _find_role(name, roles: list):
    key = _role_key(name)
    if not key:
        return None
    for r in roles:
        if _role_key(r["entry"]) == key:
            return r
    hits = [r for r in roles if key in _role_key(r["entry"])]
    return hits[0] if len(hits) == 1 else None


def _count(p: dict) -> int:
    n = p.get("bullets")
    return int(n) if isinstance(n, (int, float)) and n > 0 else 1


def role_budget_issues(prescriptions: dict, resume_text: str | None) -> dict:
    """Net bullet growth per role against its budget. Needs the seed resume."""
    if resume_text is None:
        return {"issues": [], "notes": [], "roles": []}
    import density_lint

    roles = density_lint._parse(resume_text)["roles"]
    for rank, r in enumerate(roles):
        r["budget"] = density_lint._budget(rank)
    issues, notes = [], []
    delta, reasons = {}, {}
    for p in prescriptions.get("prescriptions", []):
        typ = p.get("type")
        if typ not in ("add", "cut", "remove"):
            continue
        if not p.get("role"):
            names = [r for r in roles
                     if _ROLE_SPLIT.split(r["entry"])[0].casefold() in _norm(p.get("target")).casefold()]
            if typ == "add" and names:
                notes.append(f"add {p.get('target')!r} names {names[0]['entry']!r} but has no "
                             "`role`, so its bullet budget is not checked")
            continue
        r = _find_role(p["role"], roles)
        if r is None:
            notes.append(f"{typ} role {p['role']!r} is not an Experience entry on the resume "
                         "(a new entry, or a misspelling): its bullet budget is not checked")
            continue
        sign = 1 if typ == "add" else -1
        delta[r["entry"]] = delta.get(r["entry"], 0) + sign * _count(p)
        if typ == "add" and p.get("over_budget_reason"):
            reasons[r["entry"]] = p["over_budget_reason"]
    rows = []
    for r in roles:
        d = delta.get(r["entry"], 0)
        projected = r["bullets"] + d
        rows.append({"entry": r["entry"], "bullets": r["bullets"], "net": d,
                     "projected": projected, "budget": r["budget"]})
        if d > 0 and projected > r["budget"] and r["entry"] not in reasons:
            issues.append(
                f"{r['entry']!r}: {r['bullets']} bullets now, {projected} after the "
                f"prescriptions, budget {r['budget']}. Pair each add with a cut or remove in "
                "this role, or give the add an approved `over_budget_reason`")
    return {"issues": issues, "notes": notes, "roles": rows}


def check_coverage(prescriptions: dict, gapmap: dict, requirements: dict | None = None,
                   resume_text: str | None = None) -> dict:
    needed = recoverable_gap_ids(gapmap)
    adds = [p for p in prescriptions.get("prescriptions", []) if p.get("type") == "add"]
    covered, uncovered = [], []
    for gid in needed:
        ok = any(gid in (p.get("closes") or []) and p.get("source") for p in adds)
        (covered if ok else uncovered).append(gid)
    ambiguous = ambiguous_targets(prescriptions)
    summary = summary_issues(prescriptions)
    banner = banner_issues(prescriptions, requirements)
    budget = role_budget_issues(prescriptions, resume_text)
    return {
        "needed": needed,
        "covered": covered,
        "uncovered": uncovered,
        "ambiguous_targets": ambiguous,
        "summary_issues": summary,
        "banner_issues": banner,
        "budget_issues": budget["issues"],
        "budget_notes": budget["notes"],
        "role_budgets": budget["roles"],
        "ok": (not uncovered and not ambiguous and not summary and not banner
               and not budget["issues"]),
    }


def check_files(prescriptions_path, gapmap_path, requirements_path=None,
                resume_path=None) -> dict:
    pres = yaml.safe_load(Path(prescriptions_path).read_text(encoding="utf-8"))
    gm = yaml.safe_load(Path(gapmap_path).read_text(encoding="utf-8"))
    req = None
    if requirements_path:
        req = yaml.safe_load(Path(requirements_path).read_text(encoding="utf-8"))
    resume = Path(resume_path).read_text(encoding="utf-8") if resume_path else None
    return check_coverage(pres, gm, req, resume)


if __name__ == "__main__":
    import argparse
    import json

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("prescriptions")
    ap.add_argument("gapmap")
    ap.add_argument("requirements", nargs="?")
    ap.add_argument("--resume", help="the seed resume markdown; also checks each role's "
                                     "bullet budget (Add paired with Cut)")
    args = ap.parse_args()
    result = check_files(args.prescriptions, args.gapmap, args.requirements, args.resume)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    for msg in result["budget_notes"]:
        print(f"ROLE BUDGET NOTE: {msg}")
    for msg in result["budget_issues"]:
        print(f"ROLE BUDGET: {msg}")
    for msg in result["summary_issues"] + result["banner_issues"]:
        print(f"SUMMARY/BANNER: {msg}")
    if result["uncovered"]:
        print(f"UNADDRESSED RECOVERABLE GAPS: {result['uncovered']}")
    if result["ambiguous_targets"]:
        print("AMBIGUOUS TARGETS (name exactly one location): "
              f"{result['ambiguous_targets']}")
    if not result["ok"]:
        sys.exit(1)
