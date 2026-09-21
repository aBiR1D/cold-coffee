#!/usr/bin/env python3
"""
cold-coffee test runner

Evaluates AI-generated pipeline code against the prompt test suite.
Reads test definitions from tests/prompt_test_suite.yml and scores
outputs (from files or stdin) against expected/anti patterns.

Usage:
    # Score a single output file against a specific test
    python -m runner.evaluate --test incremental_events_basic --file output.sql

    # Score all outputs in benchmarks/outputs/
    python -m runner.evaluate --all

    # Pipe output directly
    echo "SELECT * FROM ..." | python -m runner.evaluate --test incremental_events_basic

    # Generate a results summary
    python -m runner.evaluate --all --format yaml > benchmarks/results/benchmark_results.yml
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

from runner.scoring import score_output, format_report, format_yaml_results


ROOT = Path(__file__).resolve().parent.parent
TEST_SUITE = ROOT / "tests" / "prompt_test_suite.yml"
OUTPUTS_DIR = ROOT / "benchmarks" / "outputs"

# Map test IDs to their output files
OUTPUT_FILE_MAP = {
    "incremental_events_basic": "test1_incremental_events.md",
    "scd_type2_customers": "test2_scd_type2.md",
    "airflow_daily_dag": "test3_airflow_dag.md",
    "ambiguous_mau": "test4_ambiguous_mau.md",
    "schema_migration_impact": "test5_schema_migration.md",
}


def load_test_suite() -> list[dict]:
    with open(TEST_SUITE) as f:
        data = yaml.safe_load(f)
    return data["tests"]


def find_test(tests: list[dict], test_id: str) -> dict | None:
    for t in tests:
        if t["id"] == test_id:
            return t
    return None


def load_output(test_id: str, file_path: str | None = None) -> str:
    if file_path:
        return Path(file_path).read_text()

    default = OUTPUTS_DIR / OUTPUT_FILE_MAP.get(test_id, "")
    if default.exists():
        return default.read_text()

    raise FileNotFoundError(
        f"No output file for test '{test_id}'. "
        f"Pass --file or add {default}"
    )


def run_single(test_id: str, file_path: str | None, from_stdin: bool) -> dict:
    tests = load_test_suite()
    test = find_test(tests, test_id)
    if not test:
        print(f"Error: test '{test_id}' not found in suite", file=sys.stderr)
        print(f"Available: {[t['id'] for t in tests]}", file=sys.stderr)
        sys.exit(1)

    if from_stdin:
        output_text = sys.stdin.read()
    else:
        output_text = load_output(test_id, file_path)

    result = score_output(test, output_text)
    print(format_report(test, result))
    return result


def run_all(output_format: str = "text") -> list[dict]:
    tests = load_test_suite()
    results = []

    for test in tests:
        test_id = test["id"]
        output_file = OUTPUTS_DIR / OUTPUT_FILE_MAP.get(test_id, "")

        if not output_file.exists():
            print(f"⏭  Skipping {test_id} — no output file at {output_file}")
            results.append({
                "test_id": test_id,
                "name": test["name"],
                "status": "skipped",
            })
            continue

        output_text = output_file.read_text()
        result = score_output(test, output_text)
        results.append(result)

        if output_format == "text":
            print(format_report(test, result))
            print()

    if output_format == "yaml":
        print(format_yaml_results(results))
    elif output_format == "text":
        passed = sum(1 for r in results if r.get("total_score", 0) > 0)
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        total = len(results)
        print("=" * 60)
        print(f"Results: {passed}/{total - skipped} passed, {skipped} skipped")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Score AI-generated pipeline outputs against the cold-coffee test suite"
    )
    parser.add_argument(
        "--test", "-t",
        help="Test ID to evaluate (e.g. incremental_events_basic)",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to output file to score",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Evaluate all tests with outputs in benchmarks/outputs/",
    )
    parser.add_argument(
        "--format",
        choices=["text", "yaml"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if args.all:
        run_all(args.format)
    elif args.test:
        from_stdin = not sys.stdin.isatty() and not args.file
        run_single(args.test, args.file, from_stdin)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
