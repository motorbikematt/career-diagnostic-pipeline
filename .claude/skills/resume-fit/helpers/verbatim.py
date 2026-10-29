"""Verbatim matching of a quote against resume text (deterministic).

The screening step must quote the resume word for word (TODO 42): a recruiter
cannot weigh words that are not on the page. `canary.py --resume` fails a run
whose `escalation_quote` is not on the resume, and `density_lint.py --screen`
finds where the quote sits on the page. Both use this module so they agree on
what "the same words" means.

Matching ignores what a quote loses in transit and nothing else: markdown
emphasis and bullet markers, runs of whitespace, and curly versus straight
quotes. Case, punctuation and dashes must match.
"""
from __future__ import annotations

import re

_CURLY = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                        " ": " "})
_EMPHASIS = re.compile(r"\*\*|\*|`")
_LEADING_BULLET = re.compile(r"(?m)^\s*[-*]\s+")


def normalize(text: str) -> str:
    """Quote or resume text reduced to comparable form."""
    text = (text or "").translate(_CURLY)
    text = _LEADING_BULLET.sub("", text)
    text = _EMPHASIS.sub("", text)
    return " ".join(text.split())


def in_text(quote: str, text: str) -> bool:
    """True when `quote` appears word for word in `text` (see the module note)."""
    q = normalize(quote)
    return bool(q) and q in normalize(text)
