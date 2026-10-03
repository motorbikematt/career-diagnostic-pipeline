"""File-size gate (TODO #19)."""
import filesize_gate


def test_small_file_fits(tmp_path):
    p = tmp_path / "r.docx"
    p.write_bytes(b"x" * 1024)
    r = filesize_gate.check(p)
    assert r["fits"] is True
    assert r["size_bytes"] == 1024


def test_exactly_at_limit_fits(tmp_path):
    p = tmp_path / "r.docx"
    p.write_bytes(b"x" * (2 * 1024 * 1024))
    assert filesize_gate.check(p)["fits"] is True


def test_over_limit_fails(tmp_path):
    p = tmp_path / "r.pdf"
    p.write_bytes(b"x" * (2 * 1024 * 1024 + 1))
    assert filesize_gate.check(p)["fits"] is False
    p.write_bytes(b"x" * (2 * 1024 * 1024 + 10_000))
    assert filesize_gate.check(p)["size_mb"] > 2.0


def test_custom_limit(tmp_path):
    p = tmp_path / "r.docx"
    p.write_bytes(b"x" * (600 * 1024))
    assert filesize_gate.check(p, max_mb=0.5)["fits"] is False
    assert filesize_gate.check(p, max_mb=1.0)["fits"] is True
