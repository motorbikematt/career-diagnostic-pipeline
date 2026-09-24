"""Helpers must not crash on a cp1252 Windows console (TODO #5, #6)."""
import os
import subprocess
import sys

import yaml

from conftest import REPO, RUN

HELPERS = REPO / ".claude" / "skills" / "resume-fit" / "helpers"


def _run(args, tmp_path):
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    return subprocess.run([sys.executable, *args], capture_output=True,
                          env=env, cwd=HELPERS)


def test_ats_chars_prints_non_ascii_on_cp1252(tmp_path):
    f = tmp_path / "r.md"
    f.write_text("- Grew revenue → 3x — fast\n", encoding="utf-8")
    p = _run([str(HELPERS / "ats_chars.py"), str(f)], tmp_path)
    assert b"UnicodeEncodeError" not in p.stderr
    assert p.returncode == 1  # violations found, not a crash


def test_gapmap_summary_out_writes_utf8(tmp_path):
    gm = yaml.safe_load((RUN / "gapmap.yaml").read_text(encoding="utf-8"))
    gm["seeker_archetype_resume"] = "product manager → platform"
    src = tmp_path / "gapmap.yaml"
    src.write_text(yaml.safe_dump(gm, allow_unicode=True), encoding="utf-8")
    out = tmp_path / "gapmap.summary.yaml"
    p = _run([str(HELPERS / "gapmap_summary.py"), str(src), "--out", str(out)], tmp_path)
    assert p.returncode == 0, p.stderr
    assert "→" in out.read_text(encoding="utf-8")
