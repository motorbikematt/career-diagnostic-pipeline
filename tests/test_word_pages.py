"""word_pages.py: Word's page count decides the length round. These tests never
launch Word; they cover the unavailable fallback and the result arithmetic."""
import json
import subprocess

import word_pages


def test_non_windows_reports_unavailable(monkeypatch):
    monkeypatch.setattr(word_pages.platform, "system", lambda: "Linux")
    m = word_pages.measure("resume.docx")
    assert m["available"] is False
    assert "Windows" in m["reason"]


def _fake_word(monkeypatch, payload, returncode=0):
    monkeypatch.setattr(word_pages.platform, "system", lambda: "Windows")
    monkeypatch.setattr(word_pages, "_powershell", lambda: "pwsh")

    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, returncode, stdout=json.dumps(payload), stderr="boom")

    monkeypatch.setattr(word_pages.subprocess, "run", run)


def test_three_pages_is_over_a_two_page_budget(monkeypatch):
    _fake_word(monkeypatch, {"pages": 3, "last_line_top": 86, "page_height": 792, "bottom_margin": 43.2})
    r = word_pages.check("resume.docx", max_pages=2)
    assert r["available"] is True
    assert r["fits"] is False


def test_spare_lines_counted_from_bottom_margin(monkeypatch):
    # 0.5in margins: bottom of text area at 756pt; last line top at 707pt.
    _fake_word(monkeypatch, {"pages": 2, "last_line_top": 707, "page_height": 792, "bottom_margin": 36})
    r = word_pages.check("resume.docx", max_pages=2)
    assert r["fits"] is True
    assert r["spare_lines_last_page"] == 2


def test_word_error_reports_unavailable(monkeypatch):
    _fake_word(monkeypatch, {}, returncode=1)
    m = word_pages.measure("resume.docx")
    assert m["available"] is False
