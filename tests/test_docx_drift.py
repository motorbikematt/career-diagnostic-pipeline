"""md vs docx drift detection (TODO #3)."""
import os

from docx import Document

import docx_drift
import render_docx

from conftest import RUN


def _render(tmp_path):
    md = tmp_path / "resume_candidate.md"
    md.write_text((RUN / "resume.md").read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "resume_candidate.docx"
    render_docx.render(md, out)
    return md, out


def test_fresh_render_is_in_sync(tmp_path):
    md, docx = _render(tmp_path)
    r = docx_drift.compare(md, docx)
    assert r["in_sync"] is True, r["diff"]


def test_word_edit_is_detected(tmp_path):
    md, docx = _render(tmp_path)
    doc = Document(str(docx))
    target = next(p for p in doc.paragraphs if "30+ experiments" in p.text)
    for run in target.runs:
        run.text = run.text.replace("30+", "40+")
    doc.save(str(docx))
    os.utime(docx, (md.stat().st_mtime + 10, md.stat().st_mtime + 10))

    r = docx_drift.compare(md, docx)
    assert r["in_sync"] is False
    assert r["docx_newer"] is True
    assert any("40+" in line for line in r["only_in_docx"])
    assert any("30+" in line for line in r["only_in_md"])


def test_pull_round_trips_visible_text(tmp_path):
    md, docx = _render(tmp_path)
    pulled = tmp_path / "pulled.md"
    pulled.write_text(docx_drift.docx_to_md(docx), encoding="utf-8")
    assert docx_drift.compare(pulled, docx)["in_sync"] is True
    text = pulled.read_text(encoding="utf-8")
    assert "# Alex Rivera" in text
    assert "## Experience" in text
    assert "### Nimbus Labs" in text
    assert "- Stood up an A/B testing program" in text
