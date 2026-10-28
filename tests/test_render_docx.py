import zipfile

import render_docx
from docx import Document


def test_render_ats_safe(tmp_path):
    md = tmp_path / "resume.md"
    md.write_text(
        "# Jane Candidate\n\n"
        "## Experience\n\n"
        "### Acme — Product Manager\n\n"
        "- Owned the **growth** roadmap and shipped features.\n"
        "- Ran *A/B testing* across the funnel.\n",
        encoding="utf-8",
    )
    out = tmp_path / "resume.docx"
    render_docx.render(md, out)
    assert out.exists()

    doc = Document(str(out))
    texts = [p.text for p in doc.paragraphs]
    assert "Jane Candidate" in texts
    assert any("growth" in t for t in texts)
    # ATS-safe: no tables in the rendered document.
    assert doc.tables == []
    # Bold inline run survived.
    growth_para = next(p for p in doc.paragraphs if "growth" in p.text)
    assert any(r.bold and "growth" in r.text for r in growth_para.runs)


def test_margin_and_body_size_options(tmp_path):
    from docx.shared import Inches, Pt

    md = tmp_path / "r.md"
    md.write_text("# Jane\n\n## Experience\n\n### Acme\n\n- Did a thing.\n", encoding="utf-8")
    out = tmp_path / "r.docx"
    render_docx.render(md, out, margin_in=0.5, body_pt=10.5)
    doc = Document(str(out))
    s = doc.sections[0]
    assert s.left_margin == s.top_margin == Inches(0.5)
    assert doc.styles["Normal"].font.size == Pt(10.5)
    sizes = {p.text: p.runs[0].font.size for p in doc.paragraphs if p.runs}
    assert sizes["Jane"] == Pt(20) and sizes["Experience"] == Pt(13)  # headings unchanged
    assert sizes["Acme"] == Pt(10.5)  # role title follows body, never below it


def test_readability_floors_refused(tmp_path):
    import pytest

    md = tmp_path / "r.md"
    md.write_text("# Jane\n", encoding="utf-8")
    with pytest.raises(ValueError):
        render_docx.render(md, tmp_path / "a.docx", body_pt=9.5)
    with pytest.raises(ValueError):
        render_docx.render(md, tmp_path / "b.docx", margin_in=0.4)


def test_refuses_to_overwrite_a_docx_with_different_text(tmp_path):
    """A .docx whose text differs from the markdown (the user's Word edits) is
    never silently overwritten; force=True is the explicit escape hatch."""
    import pytest

    md = tmp_path / "r.md"
    md.write_text("# Jane\n\n- Did a thing.\n", encoding="utf-8")
    out = tmp_path / "r.docx"
    render_docx.render(md, out)
    doc = Document(str(out))
    doc.add_paragraph("A line the user typed in Word.")
    doc.save(str(out))

    with pytest.raises(render_docx.DocxDriftError):
        render_docx.render(md, out, margin_in=0.5)
    assert "A line the user typed in Word." in [p.text for p in Document(str(out)).paragraphs]

    render_docx.render(md, out, margin_in=0.5, force=True)
    assert "A line the user typed in Word." not in [p.text for p in Document(str(out)).paragraphs]


def test_markdown_edit_rerenders_over_an_untouched_docx(tmp_path):
    """The guard compares the docx to its own render-time stamp, so editing the
    markdown on purpose and re-rendering is never blocked."""
    md = tmp_path / "r.md"
    md.write_text("# Jane\n\n- Did a thing.\n", encoding="utf-8")
    out = tmp_path / "r.docx"
    render_docx.render(md, out)
    assert Document(str(out)).core_properties.identifier.startswith(render_docx.SNAPSHOT_PREFIX)
    md.write_text("# Jane\n\n- Did a better thing.\n", encoding="utf-8")
    render_docx.render(md, out)
    assert "Did a better thing." in [p.text for p in Document(str(out)).paragraphs]


def test_unstamped_docx_falls_back_to_markdown_comparison(tmp_path):
    import pytest

    md = tmp_path / "r.md"
    md.write_text("# Jane\n", encoding="utf-8")
    out = tmp_path / "r.docx"
    doc = Document()
    doc.add_paragraph("Something else entirely")
    doc.save(str(out))
    with pytest.raises(render_docx.DocxDriftError):
        render_docx.render(md, out)


def test_core_properties_are_the_candidates_not_the_template(tmp_path):
    """python-docx's template author, 2013 timestamps and thumbnail must not
    leak into the output; the drift stamp must survive the cleanup."""
    md = tmp_path / "r.md"
    md.write_text("# Jane Candidate\n\n- Did a thing.\n", encoding="utf-8")
    out = tmp_path / "r.docx"
    render_docx.render(md, out)

    cp = Document(str(out)).core_properties
    assert cp.author == cp.last_modified_by == "Jane Candidate"
    assert cp.title == cp.subject == cp.keywords == cp.comments == ""
    assert cp.revision == 1
    assert cp.created.year >= 2026 and cp.modified.year >= 2026
    assert cp.identifier.startswith(render_docx.SNAPSHOT_PREFIX)
    with zipfile.ZipFile(out) as z:
        assert not any("thumbnail" in n.lower() for n in z.namelist())


def test_word_resave_reports_unavailable_off_windows(tmp_path, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    report = render_docx.word_resave(tmp_path / "x.docx")
    assert report["available"] is False and "Windows" in report["reason"]


def test_rerender_over_an_in_sync_docx_is_allowed(tmp_path):
    md = tmp_path / "r.md"
    md.write_text("# Jane\n\n- Did a thing.\n", encoding="utf-8")
    out = tmp_path / "r.docx"
    render_docx.render(md, out)
    render_docx.render(md, out, margin_in=0.5)  # same text: no refusal
