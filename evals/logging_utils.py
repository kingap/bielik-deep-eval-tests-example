def print_case(case_id: str, prompt: str, output: str, extra: dict | None = None) -> None:
    print("\n" + "=" * 100)
    print(f"CASE: {case_id}")
    print("-" * 100)
    print("PROMPT:")
    print(prompt)
    print("-" * 100)
    print("OUTPUT:")
    print(output)
    if extra:
        print("-" * 100)
        print("EXTRA:")
        for k, v in extra.items():
            print(f"{k}: {v}")
    print("=" * 100 + "\n")
