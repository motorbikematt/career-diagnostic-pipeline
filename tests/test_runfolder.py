import runfolder


def test_slugify():
    assert runfolder.slugify("Acme Robotics, Inc.") == "acme-robotics-inc"
    assert runfolder.slugify("  Senior PM / Platform  ") == "senior-pm-platform"
    assert runfolder.slugify("!!!") == "untitled"


def test_run_folder_name_with_date():
    name = runfolder.run_folder_name("Acme Robotics", "Senior PM", on="2026-07-06")
    assert name == "acme-robotics-senior-pm-2026-07-06"


def test_create_run_folder(tmp_path):
    p = runfolder.create_run_folder(tmp_path, "Acme Robotics", "Senior PM", on="2026-07-06")
    assert p.exists() and p.is_dir()
    assert p == tmp_path / "pipeline" / "runs" / "acme-robotics-senior-pm-2026-07-06"


def test_create_run_folder_idempotent(tmp_path):
    a = runfolder.create_run_folder(tmp_path, "Co", "Role", on="2026-07-06")
    b = runfolder.create_run_folder(tmp_path, "Co", "Role", on="2026-07-06")
    assert a == b
