from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

DATASETS_DIR = Path(__file__).resolve().parent


def allowed_sets() -> set[str] | None:
    """
    Return set of allowed dataset names from EVAL_SETS env var.
    Returns None if all sets should be included.
    """
    raw = os.getenv("EVAL_SETS", "").strip()
    if not raw:
        return None
    return {s.strip() for s in raw.split(",") if s.strip()}


def iter_datasets(filename: str) -> Iterator[tuple[str, Path]]:
    """
    Iterate over dataset directories yielding (test_set_name, file_path)
    for each directory that contains the specified file.
    """
    allowed = allowed_sets()
    if not DATASETS_DIR.exists():
        return
    for test_set_dir in DATASETS_DIR.iterdir():
        if not test_set_dir.is_dir():
            continue
        if allowed is not None and test_set_dir.name not in allowed:
            continue
        path = test_set_dir / filename
        if path.exists():
            yield test_set_dir.name, path
