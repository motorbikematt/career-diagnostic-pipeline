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


def check_coverage(prescriptions: dict, gapmap: dict, requirements: dict | None = None) -> dict:
    needed = recoverable_gap_ids(gapmap)
    adds = [p for p in prescriptions.get("prescriptions", []) if p.get("type") == "add"]
    covered, uncovered = [], []
    for gid in needed:
        ok = any(gid in (p.get("closes") or []) and p.get("source") for p in adds)
        (covered if ok else uncovered).append(gid)
    ambiguous = ambiguous_targets(prescriptions)
    summary = summary_issues(prescriptions)
    banner = banner_issues(prescriptions, requirements)
    return {
        "needed": needed,
        "covered": covered,
        "uncovered": uncovered,
        "ambiguous_targets": ambiguous,
        "summary_issues": summary,
        "banner_issues": banner,
        "ok": not uncovered and not ambiguous and not summary and not banner,
    }


def check_files(prescriptions_path, gapmap_path, requirements_path=None) -> dict:
    pres = yaml.safe_load(Path(prescriptions_path).read_text(encoding="utf-8"))
    gm = yaml.safe_load(Path(gapmap_path).read_text(encoding="utf-8"))
    req = None
    if requirements_path:
        req = yaml.safe_load(Path(requirements_path).read_text(encoding="utf-8"))
    return check_coverage(pres, gm, req)


if __name__ == "__main__":
    import json
    import sys

    result = check_files(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(json.dumps(result, indent=2))
    for msg in result["summary_issues"] + result["banner_issues"]:
        print(f"SUMMARY/BANNER: {msg}")
    if result["uncovered"]:
        print(f"UNADDRESSED RECOVERABLE GAPS: {result['uncovered']}")
    if result["ambiguous_targets"]:
        print("AMBIGUOUS TARGETS (name exactly one location): "
              f"{result['ambiguous_targets']}")
    if not result["ok"]:
        sys.exit(1)
