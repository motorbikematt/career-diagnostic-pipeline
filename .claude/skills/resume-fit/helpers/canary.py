"""Screening-blindness canary check (deterministic).

A unique token lives ONLY in the WHD front-matter. The screening subagent never
receives the WHD, so the token must never appear in screen.yaml. If it does, the
blindness guarantee was violated by construction and the run must fail.

An LLM instruction is a request; a missing capability is a guarantee — this scan
is the guarantee's tripwire (plan section 9).

The token must be unique per WHD. `init` writes a random one into the WHD
front-matter; the scan refuses to run while the template placeholder is still in
place, because a shared, published placeholder proves nothing.
"""
from __future__ import annotations

import secrets
from pathlib import Path

from whd_io import read_front_matter, read_whd, set_front_matter_key, write_whd

# The template's placeholder (templates/whd-template.md). Never a valid canary.
PLACEHOLDER_PREFIX = "WHD-CANARY-REPLACE"


def read_canary(whd_path) -> str:
    text, _ = read_whd(whd_path)
    try:
        fm = read_front_matter(text)
    except ValueError as e:
        raise ValueError(f"{e}; cannot read canary") from e
    token = fm.get("canary")
    if not token:
        raise ValueError("WHD front-matter has no 'canary' token")
    if str(token).startswith(PLACEHOLDER_PREFIX):
        raise ValueError(
            "WHD canary is still the template placeholder; run "
            "`canary.py init <whd.md>` to generate a unique token"
        )
    return token


def new_token() -> str:
    return f"WHD-CANARY-{secrets.token_hex(8).upper()}-DO-NOT-OUTPUT"


def init_canary(whd_path, force: bool = False) -> dict:
    """Write a fresh random canary into the WHD front-matter.

    Replaces a missing or placeholder token. An existing real token is kept
    unless `force` is set, so re-running init never silently rotates it.
    Line endings and the rest of the front-matter are preserved (whd_io).
    """
    text, eol = read_whd(whd_path)
    current = read_front_matter(text).get("canary")
    if current and not str(current).startswith(PLACEHOLDER_PREFIX) and not force:
        return {"changed": False, "canary": current}
    token = new_token()
    write_whd(whd_path, set_front_matter_key(text, "canary", token), eol)
    return {"changed": True, "canary": token}


def scan_text(text: str, canary: str) -> bool:
    """Return True if the canary LEAKED (appears in text)."""
    return canary in text


def check(screen_path, whd_path) -> dict:
    canary = read_canary(whd_path)
    text = Path(screen_path).read_text(encoding="utf-8")
    return {"leaked": scan_text(text, canary), "canary": canary, "screen": str(screen_path)}


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "init":
        result = init_canary(sys.argv[2], force="--force" in sys.argv[3:])
        state = "generated" if result["changed"] else "kept existing"
        print(f"{state} canary in {sys.argv[2]}")
        sys.exit(0)

    result = check(sys.argv[1], sys.argv[2])
    if result["leaked"]:
        print(
            f"CANARY LEAK: WHD token found in {result['screen']} "
            "-- screening blindness violated; failing the run."
        )
        sys.exit(1)
    print(f"OK: no canary leak in {result['screen']}")
