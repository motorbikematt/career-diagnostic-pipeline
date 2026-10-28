"""Run-folder scaffolding and slugging (plumbing, zero tokens).

One folder per application: <data_plane>/pipeline/runs/<company>-<role>-<date>/
The top level holds only what the user opens: report.md, appendix.md and, after
sign-off, the final .docx. Every pipeline artifact (YAML, drafts, the candidate
resume, patches.yaml) lives in its work/ subfolder.
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


PREFERENCES_REL = Path("pipeline") / "whd" / "preferences.yaml"
PREFERENCES_SNAPSHOT = "preferences.snapshot.yaml"
WORK = "work"


def work_dir(run) -> Path:
    """The folder holding a run's pipeline artifacts. Runs made before the
    work/ layout (and the flat examples/ fixture) keep them at the top level."""
    run = Path(run)
    return run / WORK if (run / WORK).is_dir() else run


def create_run_folder(data_plane, company: str, role: str, on: str | None = None) -> Path:
    path = Path(data_plane) / "pipeline" / "runs" / run_folder_name(company, role, on)
    (path / WORK).mkdir(parents=True, exist_ok=True)
    # Snapshot the candidate's preferences so this run's Gate 1 verdict stays
    # explainable after the rules change. Never overwrite an existing snapshot.
    prefs = Path(data_plane) / PREFERENCES_REL
    snap = path / WORK / PREFERENCES_SNAPSHOT
    if prefs.exists() and not snap.exists():
        snap.write_bytes(prefs.read_bytes())
    return path


if __name__ == "__main__":
    import sys

    from config import data_plane_path

    company, role = sys.argv[1], sys.argv[2]
    print(create_run_folder(data_plane_path(), company, role))
