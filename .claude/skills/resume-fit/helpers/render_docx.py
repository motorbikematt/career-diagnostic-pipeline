"""Render clean resume markdown to an ATS-safe .docx.

ATS-safe template (plan / decisions): single column, one standard font, simple
bold headings, bullet lists — NO tables, text boxes, headers/footers, or columns,
which resume parsers mangle. Only call this on a CLEAN draft (tags.py reports
clean); tags are not stripped here.

Markdown supported: # name, ## section, ### subsection, - bullets, **bold**,
*italic*, and plain paragraphs. `---` and blank lines are skipped.

Length levers (finishing-loop length round, in this order before content cuts):
`--margin 0.5` (narrow margins, the conventional floor) then `--body-pt 10.5`.
Both leave the extracted text identical; heading sizes never shrink, so the
hierarchy holds. Pass the same values to length_budget.py and word_pages.py.

Metadata and the Word save: the template's python-docx metadata (author, 2013
timestamps, revision, thumbnail) is replaced with the candidate's name (the `#`
heading) and the current time, then the file is opened and saved in Word so Word
itself writes the app properties and statistics and the file leaves
Compatibility Mode. That last step needs Windows + Word; without them the CLI
reports it and exits 3 (the .docx is still rendered). `--no-word-save` skips it.
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

FONT = "Calibri"
BODY_PT = 11
MIN_BODY_PT = 10   # readability floor (10-12pt is the usual body range)
MIN_MARGIN_IN = 0.5  # narrow-margin floor
MARGIN_IN = 0.6  # tightened from python-docx's 1in default; ATS-safe, compact.


def _add_runs(paragraph, text: str):
    for part in re.split(r"(\*\*.+?\*\*|\*.+?\*)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and part.endswith("*"):
            paragraph.add_run(part[1:-1]).italic = True
        else:
            paragraph.add_run(part)


class DocxDriftError(RuntimeError):
    """The existing .docx was edited after it was rendered (likely in Word)."""


# render() stamps a hash of the document's visible text into the .docx core
# property `identifier`; Word keeps core properties on save. The guard compares
# the file against its own stamp, so it catches Word edits however the markdown
# has changed since. Unstamped (older) files fall back to a markdown comparison.
SNAPSHOT_PREFIX = "render-sha256:"


def _text_hash(lines: list) -> str:
    import hashlib

    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _guard_overwrite(md_path, out: Path) -> None:
    """Refuse to overwrite a .docx edited since it was rendered: the edits are
    usually the user's own work in Word, and overwriting destroys them (it
    happened 2026-10-09). Pull them first with `docx_drift.py --pull`, or pass
    force=True / --force when the overwrite is intended."""
    if not out.exists():
        return
    from docx_drift import compare, docx_visible_lines

    stamp = Document(str(out)).core_properties.identifier or ""
    if stamp.startswith(SNAPSHOT_PREFIX):
        if _text_hash(docx_visible_lines(out)) != stamp[len(SNAPSHOT_PREFIX):]:
            raise DocxDriftError(
                f"{out.name} was edited after it was rendered; not overwriting. "
                "Run docx_drift.py --pull to keep those edits, or --force to discard them.")
        return
    drift = compare(md_path, out)
    if not drift["in_sync"]:
        raise DocxDriftError(
            f"{out.name} (unstamped) differs from {Path(md_path).name} "
            f"({len(drift['only_in_docx'])} line(s) only in the docx); not overwriting. "
            "Run docx_drift.py --pull to keep those edits, or --force to discard them.")


RESAVE_PS1 = Path(__file__).with_name("word_resave.ps1")


def _clean_core(doc, author: str) -> None:
    """Replace python-docx's template metadata (author "python-docx", 2013
    timestamps, revision, thumbnail) with the candidate's own. `identifier` is
    left alone: render() stamps it afterwards for the drift guard."""
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None)
    cp = doc.core_properties
    cp.author = cp.last_modified_by = author
    cp.title = cp.subject = cp.keywords = cp.comments = cp.category = cp.content_status = ""
    cp.revision = 1
    cp.created = cp.modified = now
    pkg = doc.part.package
    for rid, rel in list(pkg.rels.items()):
        if rel.reltype.endswith("/thumbnail"):
            pkg.rels.pop(rid)


def word_resave(docx_path, timeout: int = 180) -> dict:
    """Open and save the .docx in Word so Word writes its own app properties and
    statistics, and leave Compatibility Mode. Returns Word's JSON report, or
    {"available": False, "reason": ...} when Word cannot be driven."""
    import json
    import platform
    import shutil
    import subprocess

    if platform.system() != "Windows":
        return {"available": False, "reason": "Word COM needs Windows"}
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        return {"available": False, "reason": "PowerShell not found"}
    cmd = [shell, "-NoProfile", "-NonInteractive", "-File", str(RESAVE_PS1),
           "-DocxPath", str(Path(docx_path).resolve()), "-Convert"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"available": False, "reason": f"Word did not answer within {timeout}s"}
    if proc.returncode != 0:
        return {"available": False, "reason": (proc.stderr or proc.stdout).strip()[:400]}
    data = json.loads(proc.stdout.strip().splitlines()[-1])
    data["available"] = True
    return data


def render(md_path, out_path, margin_in: float = MARGIN_IN, body_pt: float = BODY_PT,
           force: bool = False):
    if body_pt < MIN_BODY_PT:
        raise ValueError(f"body_pt {body_pt} is below the {MIN_BODY_PT}pt readability floor")
    if margin_in < MIN_MARGIN_IN:
        raise ValueError(f"margin {margin_in}in is below the {MIN_MARGIN_IN}in floor")
    doc = Document()
    normal = doc.styles["Normal"].font
    normal.name = FONT
    normal.size = Pt(body_pt)

    # Tighten margins (all four) and default paragraph spacing so a genuinely
    # 2-page-worth of content renders to 2 pages. Still single-column, no tables.
    for section in doc.sections:
        section.top_margin = Inches(margin_in)
        section.bottom_margin = Inches(margin_in)
        section.left_margin = Inches(margin_in)
        section.right_margin = Inches(margin_in)
    normal_para = doc.styles["Normal"].paragraph_format
    normal_para.space_after = Pt(2)
    normal_para.line_spacing = 1.05

    lines = Path(md_path).read_text(encoding="utf-8").splitlines()
    name = next((ln[2:].strip() for ln in lines if ln.startswith("# ")), "")
    _clean_core(doc, name)

    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or line.strip() == "---":
            continue
        if line.startswith("# "):
            p = doc.add_paragraph()
            r = p.add_run(line[2:].strip())
            r.bold = True
            r.font.size = Pt(20)
        elif line.startswith("## "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            r = p.add_run(line[3:].strip())
            r.bold = True
            r.font.size = Pt(13)
        elif line.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            r = p.add_run(line[4:].strip())
            r.bold = True
            r.font.size = Pt(body_pt)
        elif re.match(r"^[-*] ", line):
            _add_runs(doc.add_paragraph(style="List Bullet"), line[2:].strip())
        else:
            _add_runs(doc.add_paragraph(), line.strip())

    out = Path(out_path)
    if not force:
        _guard_overwrite(md_path, out)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    from docx_drift import docx_visible_lines

    doc.core_properties.identifier = SNAPSHOT_PREFIX + _text_hash(docx_visible_lines(out))
    doc.save(str(out))
    return out


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Render clean resume markdown to an ATS-safe .docx.")
    ap.add_argument("md")
    ap.add_argument("out")
    ap.add_argument("--margin", type=float, default=MARGIN_IN,
                    help=f"all four margins, inches (floor {MIN_MARGIN_IN})")
    ap.add_argument("--body-pt", type=float, default=BODY_PT,
                    help=f"body and role-title size (floor {MIN_BODY_PT}); headings unchanged")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing .docx even if its text differs from the markdown")
    ap.add_argument("--no-word-save", action="store_true",
                    help="skip the final open-and-save in Word (Word then does not write app properties)")
    args = ap.parse_args()
    try:
        out = render(args.md, args.out, margin_in=args.margin, body_pt=args.body_pt,
                     force=args.force)
    except DocxDriftError as e:
        print(f"REFUSED: {e}")
        raise SystemExit(2)
    print(out)
    if not args.no_word_save:
        report = word_resave(out)
        if report["available"]:
            print(f"Saved by Word (compatibility mode {report['compat_before']} -> "
                  f"{report['compat_after']}).")
        else:
            print(f"WORD UNAVAILABLE: {report['reason']}. The .docx is rendered but was not "
                  "saved by Word; its app properties are still python-docx's.")
            raise SystemExit(3)
