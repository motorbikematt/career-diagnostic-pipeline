"""Shared pytest fixtures and paths."""
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
EXAMPLES = REPO / "examples"
RUN = EXAMPLES / "acme-robotics-senior-pm"


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
