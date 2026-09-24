"""Shared pytest fixtures and paths."""
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
EXAMPLES = REPO / "examples"
RUN = EXAMPLES / "acme-robotics-senior-pm"


def data_plane_runs() -> Path:
    """The configured data plane's runs folder, resolved like the skill does.

    Real-data regression tests skip when it is unconfigured; a missing path then
    simply fails their existence check.
    """
    import config

    try:
        return config.data_plane_path() / "pipeline" / "runs"
    except config.DataPlaneNotConfigured:
        return REPO / "__data_plane_not_configured__"


def _load(name):
    return yaml.safe_load((RUN / name).read_text(encoding="utf-8"))


@pytest.fixture
def gapmap():
    return _load("gapmap.yaml")


@pytest.fixture
def requirements():
    return _load("requirements.yaml")


@pytest.fixture
def resume_text():
    return (RUN / "resume.md").read_text(encoding="utf-8")


@pytest.fixture
def synthetic_whd():
    return (EXAMPLES / "synthetic-whd.md").read_text(encoding="utf-8")
