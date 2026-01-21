from __future__ import annotations

import pytest

from evals.datasets import iter_datasets
from evals.datasets.loaders import load_jsonl
from evals.local_bielik import call_bielik
from evals.rules import contains_any, contains_word, looks_like_refusal
from evals.recording import record_case_from_row


CASES: list[dict] = []
for test_set, path in iter_datasets("rules.jsonl"):
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
    return f"{case['test_set']}::rules::{row.get('id', 'no_id')}"


pytestmark = [pytest.mark.rules]


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_rules_all(case: dict, request: pytest.FixtureRequest):
    test_set = case["test_set"]
    filename = case["dataset"]
    row = case["row"]

    prompt = row["input"]
    out = call_bielik(prompt)

    record_case_from_row(
        request,
        row,
        out,
        extra={
            "test_set": test_set,
            "dataset": filename,
            "type": "rules",
            "must_contain_any": row.get("must_contain_any", []),
            "must_not_contain_any": row.get("must_not_contain_any", []),
            "must_contain_word": row.get("must_contain_word", []),
            "must_not_contain_word": row.get("must_not_contain_word", []),
        },
    )

    assert out.strip(), "Model returned empty output"
    assert not looks_like_refusal(out), "Model output looks like a refusal"

    # Substring matching (phrase can be part of larger text)
    must_any = row.get("must_contain_any", [])
    if must_any:
        assert contains_any(out, must_any), f"Expected output to contain any of: {must_any}"

    must_not = row.get("must_not_contain_any", [])
    if must_not:
        assert not contains_any(out, must_not), f"Output contains forbidden phrase from: {must_not}"

    # Whole word matching (word boundaries)
    must_word = row.get("must_contain_word", [])
    if must_word:
        assert contains_word(out, must_word), f"Expected output to contain word: {must_word}"

    must_not_word = row.get("must_not_contain_word", [])
    if must_not_word:
        assert not contains_word(out, must_not_word), f"Output contains forbidden word from: {must_not_word}"
