from __future__ import annotations

from pathlib import Path
import os
import pytest

from evals.datasets.loaders import load_jsonl
from evals.local_bielik import call_bielik
from evals.golden import token_f1
from evals.recording import record_case_from_row

DATASETS_DIR = Path(__file__).resolve().parents[1] / "datasets"
DEFAULT_F1_THRESHOLD = 0.40


def _allowed_sets() -> set[str] | None:
    raw = os.getenv("EVAL_SETS", "").strip()
    if not raw:
        return None
    return {s.strip() for s in raw.split(",") if s.strip()}


def iter_golden_datasets():
    allowed = _allowed_sets()
    if not DATASETS_DIR.exists():
        return
    for test_set_dir in DATASETS_DIR.iterdir():
        if not test_set_dir.is_dir():
            continue
        if allowed is not None and test_set_dir.name not in allowed:
            continue
        path = test_set_dir / "golden.jsonl"
        if path.exists():
            yield test_set_dir.name, path


CASES: list[dict] = []
for test_set, path in iter_golden_datasets():
    for row in load_jsonl(path):
        CASES.append(
            {
                "test_set": test_set,
                "dataset": path.name,
                "row": row,
            }
        )


def _case_id(case: dict) -> str:
    row = case["row"]
    return f"{case['test_set']}::golden::{row.get('id', 'no_id')}"


pytestmark = [pytest.mark.golden]


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_golden_all(case: dict, request: pytest.FixtureRequest):
    test_set = case["test_set"]
    filename = case["dataset"]
    row = case["row"]

    prompt = row["input"]
    expected = row["expected"]
    threshold = float(row.get("f1_threshold", DEFAULT_F1_THRESHOLD))

    out = call_bielik(prompt)
    f1, p, r = token_f1(out, expected)

    record_case_from_row(
        request,
        row,
        out,
        extra={
            "test_set": test_set,
            "dataset": filename,
            "type": "golden",
            "expected": expected,
            "f1": round(f1, 4),
            "precision": round(p, 4),
            "recall": round(r, 4),
            "threshold": threshold,
        },
    )

    assert out.strip(), "Model returned empty output"
    assert f1 >= threshold, f"Golden mismatch: f1={f1:.3f} < threshold={threshold:.3f}"
