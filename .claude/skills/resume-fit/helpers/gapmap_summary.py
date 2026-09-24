"""Build a screening-safe summary of the gapmap.

The screening subagent must be WHD-blind. The full gapmap carries WHD-derived
fields (whd_evidence, recoverable, and seeker_archetype, which the fit step reads
from the resume AND the WHD); those are STRIPPED so the screening input reflects
only what the resume alone supports. This is the dispatch-construction layer of
screening-blindness enforcement (plan section 9, layer 1).

The seeker archetype reaches screening only as `seeker_archetype_resume`, which
the fit step derives from the resume alone. If a gapmap lacks it, this fails
loudly rather than falling back to the WHD-informed `seeker_archetype`.

Write the summary with `--out <file>` (UTF-8, written by Python). Do not use a
shell `>` redirect: on Windows the redirect's encoding is not guaranteed UTF-8
and has corrupted this file in practice.
"""
from __future__ import annotations

from pathlib import Path

import yaml

# Fields safe to show screening: derived from the resume/JD, never the WHD.
SAFE_REQ_FIELDS = ("id", "kind", "classification", "resume_evidence")


def summarize(gapmap: dict) -> dict:
    resume_archetype = gapmap.get("seeker_archetype_resume")
    if not resume_archetype:
        raise ValueError(
            "gapmap has no 'seeker_archetype_resume' (resume-only archetype); "
            "refusing to pass the WHD-informed 'seeker_archetype' to screening"
        )
    reqs = [
        {k: r.get(k) for k in SAFE_REQ_FIELDS}
        for r in gapmap.get("requirements", [])
    ]
    return {
        "requirements": reqs,
        "seeker_archetype_resume": resume_archetype,
        "jd_archetype": gapmap.get("jd_archetype"),
        "ats": gapmap.get("ats"),
    }


def summarize_file(path) -> dict:
    return summarize(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def dump(summary: dict) -> str:
    return yaml.safe_dump(summary, sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    import argparse

    from console import utf8_stdout

    ap = argparse.ArgumentParser(description="Screening-safe gapmap summary.")
    ap.add_argument("gapmap")
    ap.add_argument("--out", help="write the summary to this file as UTF-8")
    args = ap.parse_args()

    text = dump(summarize_file(args.gapmap))
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        utf8_stdout()
        print(text, end="")
