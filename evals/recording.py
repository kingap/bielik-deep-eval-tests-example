from __future__ import annotations

from typing import Any, Mapping
import pytest


def record_case(
    request: pytest.FixtureRequest,
    *,
    case_id: str | None = None,
    prompt: str | None = None,
    output: str | None = None,
    extra: Any = None,
) -> None:
    """
    Zapisz dane do automatycznego logowania w conftest.py.
    """
    if case_id is not None:
        request.node.user_properties.append(("case_id", case_id))
    if prompt is not None:
        request.node.user_properties.append(("prompt", prompt))
    if output is not None:
        request.node.user_properties.append(("output", output))
    if extra is not None:
        request.node.user_properties.append(("extra", extra))


def record_case_from_row(
    request: pytest.FixtureRequest,
    row: Mapping[str, Any],
    output: str,
    *,
    id_key: str = "id",
    input_key: str = "input",
    extra: Any = None,
) -> None:

    case_id = str(row.get(id_key, "no_id"))
    prompt = row.get(input_key)
    record_case(
        request,
        case_id=case_id,
        prompt=prompt,
        output=output,
        extra=extra,
    )
