from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime, timezone

from .diagnostics import FailureAnalyzer
from .models import RunReport, TestCase, TestResult, TestStatus
from .telemetry import TelemetryCollector


class ValidationRunner:
    def __init__(self, analyzer: FailureAnalyzer | None = None) -> None:
        self.analyzer = analyzer or FailureAnalyzer()

    def run_suite(self, suite: str, tests: list[TestCase]) -> RunReport:
        started = datetime.now(timezone.utc).isoformat()
        results = [self.run_test(test) for test in tests]
        return RunReport(
            suite=suite,
            started_at=started,
            finished_at=datetime.now(timezone.utc).isoformat(),
            results=results,
        )

    def run_test(self, test: TestCase) -> TestResult:
        collector = TelemetryCollector()
        collector.start()
        started = time.monotonic()
        timed_out = False
        try:
            command = test.command.replace("{python}", _shell_quote(sys.executable))
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=test.timeout,
                env={**os.environ, **test.env},
                check=False,
            )
            exit_code = process.returncode
            stdout, stderr = process.stdout, process.stderr
            status = TestStatus.PASSED if exit_code == test.expected_exit_code else TestStatus.FAILED
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            exit_code = None
            stdout = _decode(exc.stdout)
            stderr = f"{_decode(exc.stderr)}\nTimeout after {test.timeout} seconds".strip()
            status = TestStatus.ERROR

        diagnosis = {}
        if status != TestStatus.PASSED:
            diagnosis = self.analyzer.analyze(stdout, stderr, timed_out=timed_out)
        return TestResult(
            name=test.name,
            status=status,
            command=test.command,
            exit_code=exit_code,
            duration_seconds=round(time.monotonic() - started, 4),
            stdout=stdout,
            stderr=stderr,
            telemetry=collector.stop(),
            diagnosis=diagnosis,
        )


def _decode(value: bytes | str | None) -> str:
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value


def _shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"
