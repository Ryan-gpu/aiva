from __future__ import annotations

import argparse
from pathlib import Path

from .baseline import BaselineStore
from .config import ConfigurationError, load_suite
from .reporting import write_html, write_json
from .runner import ValidationRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aiva", description="AI-driven validation automation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run a validation suite")
    run.add_argument("suite", help="path to a YAML suite")
    run.add_argument("--output", default="reports", help="report directory")
    run.add_argument("--workers", type=int, default=1, help="parallel test workers")
    run.add_argument("--baseline-db", help="SQLite database for performance baselines")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        try:
            suite_name, tests = load_suite(args.suite)
        except ConfigurationError as exc:
            print(f"Configuration error: {exc}")
            return 2
        baseline = BaselineStore(args.baseline_db) if args.baseline_db else None
        report = ValidationRunner(max_workers=args.workers, baseline_store=baseline).run_suite(
            suite_name, tests
        )
        output = Path(args.output)
        json_path = write_json(report, output / "report.json")
        html_path = write_html(report, output / "report.html")
        print(f"AIVA: {report.passed}/{len(report.results)} passed")
        print(f"JSON: {json_path}\nHTML: {html_path}")
        return 0 if report.failed == 0 else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
