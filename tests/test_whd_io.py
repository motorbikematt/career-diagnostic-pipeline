"""Line-ending preservation and preferences snapshot (TODO #10, #11)."""
import canary
import runfolder
import whd_io

TEMPLATE_WHD = (
    "---\ndocument: Work History Document\n"
    'canary: "WHD-CANARY-REPLACE-WITH-UNIQUE-TOKEN-DO-NOT-OUTPUT"\n'
    "roles: []\n---\n\n# Body\n"
)


def test_canary_init_preserves_crlf(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_bytes(TEMPLATE_WHD.replace("\n", "\r\n").encode("utf-8"))
    canary.init_canary(whd)
    raw = whd.read_bytes()
    assert raw.count(b"\n") == raw.count(b"\r\n")
    assert b"# Body" in raw


def test_canary_init_keeps_lf(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_bytes(TEMPLATE_WHD.encode("utf-8"))
    canary.init_canary(whd)
    assert b"\r\n" not in whd.read_bytes()


def test_set_front_matter_key_appends_when_missing():
    out = whd_io.set_front_matter_key("---\na: 1\n---\nbody\n", "b", "2")
    assert whd_io.read_front_matter(out) == {"a": 1, "b": "2"}
    assert out.endswith("---\nbody\n")


def test_preferences_snapshot_copied_once(tmp_path):
    whd_dir = tmp_path / "pipeline" / "whd"
    whd_dir.mkdir(parents=True)
    (whd_dir / "preferences.yaml").write_text("home: A\n", encoding="utf-8")
    run = runfolder.create_run_folder(tmp_path, "Co", "Role", on="2026-09-24")
    snap = run / "preferences.snapshot.yaml"
    assert snap.read_text(encoding="utf-8") == "home: A\n"
    (whd_dir / "preferences.yaml").write_text("home: B\n", encoding="utf-8")
    runfolder.create_run_folder(tmp_path, "Co", "Role", on="2026-09-24")
    assert snap.read_text(encoding="utf-8") == "home: A\n"  # never overwritten


def test_no_preferences_no_snapshot(tmp_path):
    run = runfolder.create_run_folder(tmp_path, "Co", "Role", on="2026-09-24")
    assert not (run / "preferences.snapshot.yaml").exists()
