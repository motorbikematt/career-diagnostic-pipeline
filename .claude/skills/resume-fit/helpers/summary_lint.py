"""Summary lint: the mechanical summary rules (deterministic, value-blind).

Rules come from `docs/research/resume-fit-guidance.md` section 7 (S5, S8, S9) and
decision D1 (2026-10-22): every resume has a summary, built as who / what / how /
proof, two to four lines, no first person, no objective statement. This helper
checks only what a script can: it never judges wording and never rewrites.

Two inputs:
  summary_lint.py <resume.md>
      Finds the Summary section (a heading named "Summary" or "Professional
      Summary") and lints its text.
  summary_lint.py --options <summary_options.yaml> [--whd <whd.md>]
      Lints every option's text (and `final_text` if present), checks that each
      option's claims all carry a WHD anchor, that `chosen` names a real option, and,
      with --whd, that every cited anchor exists in the WHD.

VIOLATIONS (exit 1)
  missing-summary   no Summary section, or it is empty
  first-person      "I", "I'm", "my", "me" and the like
  objective         objective-statement wording ("seeking", "looking for", ...)
  unsupported-claim an option claim with no anchor, or an anchor not in the WHD
  bad-choice        `chosen` does not match an option id

WARNINGS (reported, never fail)
  long              over MAX_WORDS words: about four lines at 11 pt. Approximate; the
                    real line count depends on margins and font, so check the docx.
  no-number         no digit anywhere: the "proof" element usually carries a measure
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

MAX_WORDS = 75

_HEADING = re.compile(r"^#{1,3}\s*(?:professional\s+)?summary\s*$", re.IGNORECASE)
_ANY_HEADING = re.compile(r"^#{1,6}\s")
_FIRST_PERSON_I = re.compile(r"\bI(?:'m|'ve|'ll|'d|’m|’ve|’ll|’d)?\b")
_FIRST_PERSON_OTHER = re.compile(r"\b(?:my|me|mine|myself)\b", re.IGNORECASE)
_OBJECTIVE = re.compile(
    r"\b(?:seeking|seeks|looking\s+(?:for|to)|objective|eager\s+to|to\s+obtain|"
    r"aspiring|aspires?)\b",
    re.IGNORECASE,
)


def extract_summary(markdown: str) -> str:
    """The body of the Summary section, or "" when there is none."""
    lines = markdown.splitlines()
    for i, line in enumerate(lines):
        if _HEADING.match(line.strip()):
            body = []
            for nxt in lines[i + 1:]:
                if _ANY_HEADING.match(nxt):
                    break
                body.append(nxt)
            return "\n".join(body).strip()
    return ""


def lint_text(text: str) -> dict:
    violations, warnings = [], []
    text = (text or "").strip()
    if not text:
        violations.append({"rule": "missing-summary", "detail": "no summary text"})
        return {"violations": violations, "warnings": warnings, "words": 0}
    words = len(text.split())
    for m in _FIRST_PERSON_I.finditer(text):
        violations.append({"rule": "first-person", "detail": m.group(0)})
    for m in _FIRST_PERSON_OTHER.finditer(text):
        violations.append({"rule": "first-person", "detail": m.group(0)})
    for m in _OBJECTIVE.finditer(text):
        violations.append({"rule": "objective", "detail": m.group(0)})
    if words > MAX_WORDS:
        warnings.append({"rule": "long", "detail": f"{words} words (limit ~{MAX_WORDS})"})
    if not re.search(r"\d", text):
        warnings.append({"rule": "no-number", "detail": "no measure or count in the summary"})
    return {"violations": violations, "warnings": warnings, "words": words}


def lint_resume(markdown: str) -> dict:
    return lint_text(extract_summary(markdown))


def check_options(data: dict, whd_text: str | None = None) -> dict:
    """Lint a summary_options.yaml document."""
    import whd_anchors

    violations, warnings, per_option = [], [], {}
    anchors = set(whd_anchors.list_anchors(whd_text)) if whd_text else None
    ids = []
    for opt in data.get("options", []):
        oid = opt.get("id", "?")
        ids.append(oid)
        res = lint_text(opt.get("text", ""))
        per_option[oid] = res
        violations += [{**v, "option": oid} for v in res["violations"]]
        warnings += [{**w, "option": oid} for w in res["warnings"]]
        for claim in opt.get("claims", []):
            anchor = claim.get("anchor")
            if not anchor:
                violations.append({"rule": "unsupported-claim", "option": oid,
                                   "detail": f"no anchor: {claim.get('claim')!r}"})
            elif anchors is not None and anchor not in anchors:
                violations.append({"rule": "unsupported-claim", "option": oid,
                                   "detail": f"anchor not in WHD: {anchor}"})
    chosen = data.get("chosen")
    if chosen is not None and chosen not in ids:
        violations.append({"rule": "bad-choice", "detail": f"chosen {chosen!r} is not an option id"})
    if data.get("final_text"):
        res = lint_text(data["final_text"])
        per_option["final_text"] = res
        violations += [{**v, "option": "final_text"} for v in res["violations"]]
        warnings += [{**w, "option": "final_text"} for w in res["warnings"]]
    return {"violations": violations, "warnings": warnings, "options": per_option}


if __name__ == "__main__":
    import argparse
    import json
    import sys

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("resume", nargs="?", help="resume markdown")
    ap.add_argument("--options", help="summary_options.yaml to check")
    ap.add_argument("--whd", help="WHD markdown, to verify cited anchors exist")
    args = ap.parse_args()
    if args.options:
        whd = Path(args.whd).read_text(encoding="utf-8") if args.whd else None
        data = yaml.safe_load(Path(args.options).read_text(encoding="utf-8"))
        result = check_options(data, whd)
    elif args.resume:
        result = lint_resume(Path(args.resume).read_text(encoding="utf-8"))
    else:
        ap.error("give a resume or --options")
    result["clean"] = not result["violations"]
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["clean"] else 1)
