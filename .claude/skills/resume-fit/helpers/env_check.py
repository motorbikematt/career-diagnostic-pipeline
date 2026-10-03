"""Environment readiness report (read-only, always exits 0).

Answers "can this machine run the optional steps?" before they are planned:
`pdftotext` (poppler) for a text-extraction round trip, LibreOffice headless for
PDF export (TODO #26), the Python libraries the helpers import, and the data
plane path. It changes nothing and never fails; a missing optional tool is
reported, not raised.
"""
from __future__ import annotations

import importlib.util
import shutil

import config

# (label, executable names tried in order, what needs it)
BINARIES = (
    ("pdftotext", ("pdftotext",), "text-extraction round trip on a PDF (poppler)"),
    ("libreoffice", ("soffice", "libreoffice"), "headless PDF export (TODO #26)"),
)
# (label, import name, what needs it)
LIBRARIES = (
    ("python-docx", "docx", "render_docx.py, docx_drift.py, contact_check.py"),
    ("pyyaml", "yaml", "schemas, gapmap, preferences, validate.py"),
)


def _binary(label: str, names: tuple, needed_for: str) -> dict:
    for name in names:
        path = shutil.which(name)
        if path:
            return {"item": label, "ok": True, "detail": path, "needed_for": needed_for}
    return {"item": label, "ok": False, "detail": "not on PATH", "needed_for": needed_for}


def _library(label: str, module: str, needed_for: str) -> dict:
    found = importlib.util.find_spec(module) is not None
    return {"item": label, "ok": found,
            "detail": "importable" if found else "not installed", "needed_for": needed_for}


def _data_plane() -> dict:
    try:
        path = config.data_plane_path()
        return {"item": "data plane", "ok": True, "detail": str(path),
                "needed_for": "all runs and the master resume files"}
    except config.DataPlaneNotConfigured as e:
        return {"item": "data plane", "ok": False, "detail": str(e),
                "needed_for": "all runs and the master resume files"}


def run() -> list:
    return ([_binary(*b) for b in BINARIES]
            + [_library(*l) for l in LIBRARIES]
            + [_data_plane()])


if __name__ == "__main__":
    from console import utf8_stdout

    utf8_stdout()
    for row in run():
        mark = "ok     " if row["ok"] else "MISSING"
        print(f"{mark}  {row['item']:<12} {row['detail']}  (needed for: {row['needed_for']})")
