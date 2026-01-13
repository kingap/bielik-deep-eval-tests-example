from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from datetime import datetime
import shutil
import sys


TYPE_TO_TESTFILE = {
    "rules": "evals/tests/test_rules_all.py",
    "golden": "evals/tests/test_golden_all.py",
    "judge": "evals/tests/test_judge_all.py",
}


def _slug(parts: list[str]) -> str:
    if not parts:
        return "all"
    s = "+".join(parts)
    return (
        s.replace(" ", "")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(":", "-")
    )[:80]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run eval test sets with HTML+JSON reports.\n\n"
            "Examples:\n"
            "  python -m evals.run_tests\n"
            "  python -m evals.run_tests --fast\n"
            "  python -m evals.run_tests common_sense\n"
            "  python -m evals.run_tests common_sense --fast\n"
            "  python -m evals.run_tests --rules --golden\n"
            "  python -m evals.run_tests --all-tests\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # ✅ test sety jako argumenty pozycyjne (0..n)
    parser.add_argument(
        "sets",
        nargs="*",
        help="Test set names (folder names under evals/datasets). If omitted => all sets.",
    )

    # ✅ typy testów jako flagi (jak nic nie podasz => wszystkie typy)
    parser.add_argument("--rules", action="store_true", help="Run rules tests")
    parser.add_argument("--golden", action="store_true", help="Run golden tests")
    parser.add_argument("--judge", action="store_true", help="Run judge tests")

    # ✅ NOWE: szybki tryb (rules + golden)
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only fast tests (rules + golden). Equivalent to --rules --golden.",
    )

    # ✅ uruchom absolutnie wszystko co pytest znajdzie
    parser.add_argument(
        "--all-tests",
        action="store_true",
        help="Run ALL tests discovered by pytest (evals/tests), ignoring set/type selection.",
    )

    parser.add_argument(
        "--reports-dir",
        default="evals/reports",
        help="Directory for HTML/JSON reports (default: evals/reports)",
    )

    parser.add_argument(
        "--tests-dir",
        default="evals/tests",
        help="Directory where tests live (default: evals/tests). Used by --all-tests.",
    )

    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    reports = root / args.reports_dir
    reports.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # ====== MODE 1: run EVERYTHING ======
    if args.all_tests:
        label = f"alltests__{ts}"
        json_path = reports / f"pytest_report_{label}.json"
        html_path = reports / f"pytest_report_{label}.html"
        latest_json = reports / "latest_alltests.json"
        latest_html = reports / "latest_alltests.html"

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-vv",
            "--capture=tee-sys",
            "-rA",
            args.tests_dir,
            "--json-report",
            f"--json-report-file={json_path}",
            f"--html={html_path}",
            "--self-contained-html",
        ]

        print("Running ALL tests:", " ".join(str(x) for x in cmd))
        result = subprocess.run(cmd, env=os.environ.copy())

        try:
            shutil.copyfile(json_path, latest_json)
            shutil.copyfile(html_path, latest_html)
        except Exception as e:
            print(f"Warning: could not update latest reports: {e}")

        print(f"\nSaved JSON:  {json_path}")
        print(f"Saved HTML:  {html_path}")
        print(f"Latest JSON: {latest_json}")
        print(f"Latest HTML: {latest_html}")

        return result.returncode

    # ====== MODE 2: run eval suites (rules/golden/judge) + datasets ======

    # sety do uruchomienia (opcjonalnie)
    selected_sets = args.sets[:]  # puste => wszystkie

    # 1) wyznacz typy do uruchomienia
    if args.fast:
        # --fast wymusza rules+golden niezależnie od innych flag
        selected_types = ["rules", "golden"]
    else:
        selected_types: list[str] = []
        if args.rules:
            selected_types.append("rules")
        if args.golden:
            selected_types.append("golden")
        if args.judge:
            selected_types.append("judge")

        # jak nic nie podano => wszystko
        if not selected_types:
            selected_types = ["rules", "golden", "judge"]

    sets_label = _slug(selected_sets) if selected_sets else "allsets"
    types_label = _slug(selected_types) if selected_types else "alltypes"
    label = f"{sets_label}__{types_label}"

    json_path = reports / f"pytest_report_{label}_{ts}.json"
    html_path = reports / f"pytest_report_{label}_{ts}.html"
    latest_json = reports / f"latest_{label}.json"
    latest_html = reports / f"latest_{label}.html"

    # 2) pliki testowe wg typów
    test_files: list[str] = []
    for t in selected_types:
        tf = TYPE_TO_TESTFILE.get(t)
        if not tf:
            raise SystemExit(f"Unknown test type: {t}")
        test_files.append(tf)

    # 3) env do filtrowania setów po folderze (czytane przez *_all.py)
    env = os.environ.copy()
    if selected_sets:
        env["EVAL_SETS"] = ",".join(selected_sets)
    else:
        env.pop("EVAL_SETS", None)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-vv",
        "--capture=tee-sys",
        "-rA",
        *test_files,
        "--json-report",
        f"--json-report-file={json_path}",
        f"--html={html_path}",
        "--self-contained-html",
    ]

    print("Running:", " ".join(str(x) for x in cmd))
    if selected_sets:
        print("EVAL_SETS:", env["EVAL_SETS"])
    print("TYPES:", ",".join(selected_types))

    result = subprocess.run(cmd, env=env)

    try:
        shutil.copyfile(json_path, latest_json)
        shutil.copyfile(html_path, latest_html)
    except Exception as e:
        print(f"Warning: could not update latest reports: {e}")

    print(f"\nSaved JSON:  {json_path}")
    print(f"Saved HTML:  {html_path}")
    print(f"Latest JSON: {latest_json}")
    print(f"Latest HTML: {latest_html}")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
