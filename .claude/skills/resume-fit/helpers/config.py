"""Data-plane path resolution.

The skill is user-agnostic: the data-plane location comes from configuration,
NEVER a hardcoded path. Resolution order:
  1. $RESUME_FIT_DATA_PLANE
  2. config file at $XDG_CONFIG_HOME/resume-fit/config.yaml (or
     ~/.config/resume-fit/config.yaml), key: data_plane

Raises DataPlaneNotConfigured if neither is set — the skill runs a first-run
setup prompt and calls set_data_plane() to persist the choice.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

ENV_VAR = "RESUME_FIT_DATA_PLANE"


class DataPlaneNotConfigured(RuntimeError):
    pass


def config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / "resume-fit" / "config.yaml"


def _from_config_file():
    p = config_path()
    if p.exists():
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        dp = data.get("data_plane")
        if dp:
            return Path(dp)
    return None


def data_plane_path(require_exists: bool = True) -> Path:
    dp = os.environ.get(ENV_VAR)
    path = Path(dp) if dp else _from_config_file()
    if path is None:
        raise DataPlaneNotConfigured(
            f"Data plane not configured. Set ${ENV_VAR} or write "
            f"'data_plane: <path>' to {config_path()}."
        )
    if require_exists and not path.exists():
        raise DataPlaneNotConfigured(f"Configured data plane does not exist: {path}")
    return path


def set_data_plane(path) -> Path:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if p.exists():
        existing = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    existing["data_plane"] = str(Path(path))
    p.write_text(yaml.safe_dump(existing, sort_keys=False), encoding="utf-8")
    return p


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2 and sys.argv[1] == "set":
        print(set_data_plane(sys.argv[2]))
    else:
        try:
            print(data_plane_path())
        except DataPlaneNotConfigured as e:
            print(e)
            sys.exit(1)
