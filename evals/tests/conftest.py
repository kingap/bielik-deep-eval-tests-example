from __future__ import annotations

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(autouse=True)
def _attach_case_log_to_report(request: pytest.FixtureRequest):
    yield

    props = dict(getattr(request.node, "user_properties", []))
    case_id = props.get("case_id")
    prompt = props.get("prompt")
    output = props.get("output")
    extra = props.get("extra")

    if not (case_id or prompt or output or extra):
        return

    lines = []
    lines.append("=" * 100)
    lines.append(f"TEST: {request.node.nodeid}")
    if case_id:
        lines.append(f"CASE: {case_id}")
    lines.append("-" * 100)

    if prompt is not None:
        lines.append("PROMPT:")
        lines.append(str(prompt))
        lines.append("-" * 100)

    if output is not None:
        lines.append("OUTPUT:")
        lines.append(str(output))
        lines.append("-" * 100)

    if extra is not None:
        lines.append("EXTRA:")
        if isinstance(extra, dict):
            for k, v in extra.items():
                lines.append(f"{k}: {v}")
        else:
            lines.append(str(extra))

    lines.append("=" * 100)

    print("\n" + "\n".join(lines) + "\n")
