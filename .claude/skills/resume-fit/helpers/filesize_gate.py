"""File-size gate for a rendered resume (deterministic).

Evidence (docs/research/resume-fit-guidance.md section 1): Google caps uploads at
2 MB [S3] and Greenhouse stops parsing above 2.5 MB [S1]. A single 2 MB gate
satisfies both. Works on any file (.docx now, .pdf if PDF output is added later).

The size check is exact, so Python owns it. It fails; it does not shrink anything.
"""
from __future__ import annotations

from pathlib import Path

MB = 1024 * 1024
DEFAULT_MAX_MB = 2.0


def check(path, max_mb: float = DEFAULT_MAX_MB) -> dict:
    size = Path(path).stat().st_size
    return {
        "path": str(path),
        "size_bytes": size,
        "size_mb": round(size / MB, 3),
        "max_mb": max_mb,
        "fits": size <= max_mb * MB,
        "note": "Google caps uploads at 2 MB [S3]; Greenhouse stops parsing above "
                "2.5 MB [S1]. The 2 MB gate covers both.",
    }


if __name__ == "__main__":
    import argparse
    import json
    import sys

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description="Fail if a rendered resume exceeds the size cap.")
    ap.add_argument("path")
    ap.add_argument("--max-mb", type=float, default=DEFAULT_MAX_MB)
    args = ap.parse_args()

    result = check(args.path, max_mb=args.max_mb)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["fits"]:
        print(f"OVER SIZE LIMIT: {result['size_mb']} MB (limit {result['max_mb']} MB)")
        sys.exit(1)
