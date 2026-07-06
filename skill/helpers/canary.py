"""Screening-blindness canary check (deterministic).

A unique token lives ONLY in the WHD front-matter. The screening subagent never
receives the WHD, so the token must never appear in screen.yaml. If it does, the
blindness guarantee was violated by construction and the run must fail.

An LLM instruction is a request; a missing capability is a guarantee — this scan
is the guarantee's tripwire (plan section 9).
"""
from __future__ import annotations

from pathlib import Path

import yaml


def read_canary(whd_path) -> str:
    text = Path(whd_path).read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("WHD has no front-matter; cannot read canary")
    try:
        end = lines.index("---", 1)
    except ValueError as e:
        raise ValueError("WHD front-matter is not closed") from e
    fm = yaml.safe_load("\n".join(lines[1:end])) or {}
    token = fm.get("canary")
    if not token:
        raise ValueError("WHD front-matter has no 'canary' token")
    return token


def scan_text(text: str, canary: str) -> bool:
    """Return True if the canary LEAKED (appears in text)."""
    return canary in text


def check(screen_path, whd_path) -> dict:
    canary = read_canary(whd_path)
    text = Path(screen_path).read_text(encoding="utf-8")
    return {"leaked": scan_text(text, canary), "canary": canary, "screen": str(screen_path)}


if __name__ == "__main__":
    import sys

    result = check(sys.argv[1], sys.argv[2])
    if result["leaked"]:
        print(
            f"CANARY LEAK: WHD token found in {result['screen']} "
            "-- screening blindness violated; failing the run."
        )
        sys.exit(1)
    print(f"OK: no canary leak in {result['screen']}")
