import pytest
import config
from config import DataPlaneNotConfigured


def test_env_var_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("RESUME_FIT_DATA_PLANE", str(tmp_path))
    assert config.data_plane_path() == tmp_path


def test_config_file_roundtrip(tmp_path, monkeypatch):
    monkeypatch.delenv("RESUME_FIT_DATA_PLANE", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    dp = tmp_path / "data-plane"
    dp.mkdir()
    written = config.set_data_plane(dp)
    assert written.exists()
    assert config.data_plane_path() == dp


def test_unconfigured_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("RESUME_FIT_DATA_PLANE", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "empty"))
    with pytest.raises(DataPlaneNotConfigured):
        config.data_plane_path()


def test_configured_but_missing_path_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("RESUME_FIT_DATA_PLANE", str(tmp_path / "does-not-exist"))
    with pytest.raises(DataPlaneNotConfigured):
        config.data_plane_path()
