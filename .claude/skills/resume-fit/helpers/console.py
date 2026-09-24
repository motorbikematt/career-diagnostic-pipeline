"""Make a helper's CLI output safe on the Windows console.

The Windows console (and any pipe or `>` redirect from a Windows shell) defaults
to cp1252. A helper that prints a non-ASCII character (an arrow, a curly quote,
an em dash it just detected) then crashes with UnicodeEncodeError. Callers must
not need `PYTHONIOENCODING=utf-8` to run a helper, so each CLI entry point that
can print non-ASCII calls `utf8_stdout()` first.
"""
from __future__ import annotations

import sys


def utf8_stdout() -> None:
    """Switch stdout/stderr to UTF-8 so non-ASCII output never crashes the CLI."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
