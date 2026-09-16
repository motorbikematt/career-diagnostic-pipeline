"""Run-folder scaffolding and slugging (plumbing, zero tokens).

One folder per application: <data_plane>/pipeline/runs/<company>-<role>-<date>/
"""
from __future__ import annotations

import re
from datetime import date as _date
from pathlib import Path


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "untitled"


def run_folder_name(company: str, role: str, on: str | None = None) -> str:
    on = on or _date.today().isoformat()
    return f"{slugify(company)}-{slugify(role)}-{on}"


def create_run_folder(data_plane, company: str, role: str, on: str | None = None) -> Path:
    path = Path(data_plane) / "pipeline" / "runs" / run_folder_name(company, role, on)
    path.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    import sys

    from config import data_plane_path

    company, role = sys.argv[1], sys.argv[2]
    print(create_run_folder(data_plane_path(), company, role))
