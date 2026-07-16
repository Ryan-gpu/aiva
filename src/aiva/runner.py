from __future__ import annotations

import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from .baseline import BaselineStore
from .collectors import HostTelemetryCollector
from .diagnostics import FailureAnalyzer
from .executors import LocalExecutor
from .models import ExecutionContext, RunReport, TestCase, TestResult, TestStatus
from .plugins import PluginRegistry


class ValidationRunner:
    def __init__(
        self,
        registry: PluginRegistry | None = None,
        *,
        max_workers: int = 1,
        baseline_store: BaselineStore | None = None,
        analyzer: FailureAnalyzer | None = None,
    ) -> None:
        self.registry = registry or self._default_registry(analyzer)
        self.max_workers = max(1, max_workers)
        self.baseline_store = baseline_store

    @staticmethod
    def _default_registry(analyzer: FailureAnalyzer | None) -> PluginRegistry:
        registry = PluginRegistry()
        registry.register_executor(LocalExecutor())
        registry.register_collector(HostTelemetryCollector())
        registry.register_analyzer(analyzer or FailureAnalyzer())
        return registry

    def run_suite(self, suite: str, tests: list[TestCase]) -> RunReport:
        started = datetime.now(timezone.utc).isoformat()
        run_id = uuid.uuid4().hex[:12]
        root = Path(tempfile.mkdtemp(prefix=f"aiva-{run_id}-"))
        context = ExecutionContext(run_id, suite, Path.cwd(), root / "artifacts")
        context.artifacts_dir.mkdir(parents=True, exist_ok=True)
        if self.max_workers == 1:
            results = [self.run_test(test, context) for test in tests]
        else:
            indexed: dict[object, int] = {}
            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                for index, test in enumerate(tests):
                    indexed[pool.submit(self.run_test, test, context)] = index
                completed = [(index, future.result()) for future, index in indexed.items()]
            results = [result for _, result in sorted(completed)]
        return RunReport(
            suite=suite,
            started_at=started,
            finished_at=datetime.now(timezone.utc).isoformat(),
            results=results,
            run_id=run_id,
        )

    def run_test(self, test: TestCase, context: ExecutionContext | None = None) -> TestResult:
        if context is None:
            root = Path(tempfile.mkdtemp(prefix="aiva-single-"))
            context = ExecutionContext("single", "single", Path.cwd(), root)
        executor = self.registry.executor(test.executor)
        attempts = 0
        execution = None
        evidence = []
        try:
            executor.prepare(test, context)
            for collector in self.registry.collectors:
                collector.before(test, context)
            for attempts in range(1, test.retries + 2):
                execution = executor.execute(test, context)
                if execution.exit_code == test.expected_exit_code:
                    break
            for collector in self.registry.collectors:
                evidence.append(collector.after(test, execution, context))
        finally:
            executor.cleanup(test, context)
        assert execution is not None
        if execution.timed_out:
            status = TestStatus.ERROR
        elif execution.exit_code == test.expected_exit_code:
            status = TestStatus.PASSED
        else:
            status = TestStatus.FAILED
        telemetry = next((item.data for item in evidence if item.source == "host-telemetry"), {})
        result = TestResult(
            name=test.name,
            test_id=test.id,
            status=status,
            command=test.command,
            exit_code=execution.exit_code,
            duration_seconds=execution.duration_seconds,
            attempts=attempts,
            stdout=execution.stdout,
            stderr=execution.stderr,
            telemetry=telemetry,
            evidence=evidence,
        )
        if status != TestStatus.PASSED:
            result.diagnosis = self._analyze(result, context)
        result.performance = self._evaluate_performance(test, result)
        if any(not bool(value["passed"]) for value in result.performance.values()):
            result.status = TestStatus.FAILED
        return result

    def _analyze(self, result: TestResult, context: ExecutionContext) -> dict[str, object]:
        analyses = [analyzer.analyze(result, context) for analyzer in self.registry.analyzers]
        return analyses[0] if len(analyses) == 1 else {"analyses": analyses}

    def _evaluate_performance(
        self, test: TestCase, result: TestResult
    ) -> dict[str, dict[str, float | bool | None]]:
        if not self.baseline_store:
            return {}
        thresholds = {"duration_seconds": test.performance.get("max_regression_percent")}
        return {
            metric: self.baseline_store.compare_and_record(test.id, metric, value, threshold)
            for metric, value in {"duration_seconds": result.duration_seconds}.items()
            if (threshold := thresholds.get(metric)) is not None
        }
