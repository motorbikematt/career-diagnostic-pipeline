"""Real page count from Microsoft Word (the length round's deciding check).

length_budget.py estimates; Word decides. Word is the renderer a recruiter most
likely opens a .docx in, and it lays the page out with real Calibri metrics, so
its page count is the one that matters. A model within +/-0.1 page cannot make a
2-vs-3 page call at the boundary; this can.

Windows + Word only (COM through PowerShell; no pywin32 dependency). On any
other machine, or if Word cannot be driven, it reports `available: false` and
exits 3 so the caller falls back to length_budget.py's estimate and asks the
user to confirm the page count by eye. It never edits or saves the document.

Exit codes: 0 fits, 2 over budget, 3 Word unavailable.
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
from pathlib import Path

PS1 = Path(__file__).with_name("word_pages.ps1")
LINE_PT = 14  # one 11pt body line in render_docx.py's template, for the spare-room readout


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def measure(docx_path, pdf_path=None, timeout: int = 180) -> dict:
    """Return Word's measurement, or {"available": False, "reason": ...}."""
    if platform.system() != "Windows":
        return {"available": False, "reason": "Word COM needs Windows"}
    shell = _powershell()
    if shell is None:
        return {"available": False, "reason": "PowerShell not found"}
    cmd = [shell, "-NoProfile", "-NonInteractive", "-File", str(PS1),
           "-DocxPath", str(Path(docx_path).resolve())]
    if pdf_path:
        cmd += ["-PdfPath", str(Path(pdf_path).resolve())]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"available": False, "reason": f"Word did not answer within {timeout}s"}
    if proc.returncode != 0:
        return {"available": False, "reason": (proc.stderr or proc.stdout).strip()[:400]}
    data = json.loads(proc.stdout.strip().splitlines()[-1])
    data["available"] = True
    return data


def check(docx_path, max_pages: int = 2, pdf_path=None) -> dict:
    m = measure(docx_path, pdf_path=pdf_path)
    if not m["available"]:
        return m
    bottom = m["page_height"] - m["bottom_margin"]
    # Room left under the last line on the last page, in body lines.
    m["spare_lines_last_page"] = max(0, int((bottom - m["last_line_top"] - LINE_PT) // LINE_PT))
    m["max_pages"] = max_pages
    m["fits"] = m["pages"] <= max_pages
    return m


if __name__ == "__main__":
    import argparse

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description="Page count of a .docx, measured in Word.")
    ap.add_argument("docx")
    ap.add_argument("--max-pages", type=int, default=2)
    ap.add_argument("--pdf", help="also export a PDF through Word to this path")
    args = ap.parse_args()

    result = check(args.docx, max_pages=args.max_pages, pdf_path=args.pdf)
    print(json.dumps(result, indent=2))
    if not result["available"]:
        print("WORD UNAVAILABLE: use length_budget.py's estimate and confirm the page count by eye.")
        raise SystemExit(3)
    if not result["fits"]:
        print(f"OVER BUDGET IN WORD: {result['pages']} pages (target {result['max_pages']}).")
        raise SystemExit(2)
    print(f"FITS IN WORD: {result['pages']} pages, ~{result['spare_lines_last_page']} "
          "body lines spare on the last page.")
