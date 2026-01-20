from __future__ import annotations

import os
import pytest

from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.models import GPTModel

from evals.datasets import iter_datasets
from evals.datasets.loaders import load_jsonl
from evals.local_bielik import call_bielik
from evals.recording import record_case_from_row

DEFAULT_THRESHOLD = 0.60


CASES: list[dict] = []
for test_set, path in iter_datasets("judge.jsonl"):
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
    return f"{case['test_set']}::judge::{row.get('id', 'no_id')}"


pytestmark = [pytest.mark.judge]


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_judge_all(case: dict, request: pytest.FixtureRequest):
    test_set = case["test_set"]
    filename = case["dataset"]
    row = case["row"]

    prompt = row["input"]
    notes = row.get("notes")
    threshold = float(row.get("threshold", DEFAULT_THRESHOLD))

    judge_model_name = os.getenv("OLLAMA_JUDGE_MODEL") or os.getenv("OLLAMA_MODEL")
    if not judge_model_name:
        pytest.skip("Set OLLAMA_JUDGE_MODEL (recommended) or OLLAMA_MODEL in .env / environment")

    out = call_bielik(prompt)

    judge = GPTModel(model=judge_model_name)
    judge_input = prompt
    if notes:
        judge_input = (
            f"{prompt}\n\n"
            f"[NOTES FOR EVALUATION]\n"
            f"{notes}"
        )
    tc = LLMTestCase(input=judge_input, actual_output=out)

    metric = AnswerRelevancyMetric(threshold=threshold, model=judge)
    metric.measure(tc)

    record_case_from_row(
        request,
        row,
        out,
        extra={
            "test_set": test_set,
            "dataset": filename,
            "type": "judge",
            "notes": notes,
            "judge_model": judge_model_name,
            "judge_metric": "AnswerRelevancyMetric",
            "judge_score": round(metric.score, 4),
            "judge_threshold": metric.threshold,
            "judge_reason": metric.reason,
        },
    )

    assert metric.score >= metric.threshold, metric.reason
