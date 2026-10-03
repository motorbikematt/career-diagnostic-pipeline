"""Environment readiness report (read-only)."""
import config
import env_check


def test_reports_found_and_missing_binaries(monkeypatch):
    monkeypatch.setattr(env_check.shutil, "which",
                        lambda name: "C:/tools/pdftotext.exe" if name == "pdftotext" else None)
    rows = {r["item"]: r for r in env_check.run()}
    assert rows["pdftotext"]["ok"] is True
    assert rows["pdftotext"]["detail"] == "C:/tools/pdftotext.exe"
    assert rows["libreoffice"]["ok"] is False
    assert rows["libreoffice"]["detail"] == "not on PATH"


def test_libreoffice_found_under_either_executable_name(monkeypatch):
    monkeypatch.setattr(env_check.shutil, "which",
                        lambda name: "/usr/bin/libreoffice" if name == "libreoffice" else None)
    rows = {r["item"]: r for r in env_check.run()}
    assert rows["libreoffice"]["ok"] is True


def test_missing_data_plane_is_reported_not_raised(monkeypatch):
    def boom(*a, **k):
        raise config.DataPlaneNotConfigured("not set")

    monkeypatch.setattr(env_check.config, "data_plane_path", boom)
    rows = {r["item"]: r for r in env_check.run()}
    assert rows["data plane"]["ok"] is False
    assert rows["data plane"]["detail"] == "not set"


def test_required_libraries_importable():
    rows = {r["item"]: r for r in env_check.run()}
    assert rows["python-docx"]["ok"] is True
    assert rows["pyyaml"]["ok"] is True
