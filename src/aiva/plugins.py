from __future__ import annotations

from abc import ABC, abstractmethod

from .models import Evidence, ExecutionContext, ExecutionResult, TestCase, TestResult


class Executor(ABC):
    name: str

    def prepare(self, case: TestCase, context: ExecutionContext) -> None:
        """Allocate resources before execution."""

    @abstractmethod
    def execute(self, case: TestCase, context: ExecutionContext) -> ExecutionResult:
        """Execute one test case."""

    def cleanup(self, case: TestCase, context: ExecutionContext) -> None:
        """Release resources even when execution fails."""


class Collector(ABC):
    name: str

    @abstractmethod
    def before(self, case: TestCase, context: ExecutionContext) -> None:
        """Start evidence collection."""

    @abstractmethod
    def after(
        self, case: TestCase, execution: ExecutionResult, context: ExecutionContext
    ) -> Evidence:
        """Stop collection and return structured evidence."""


class Analyzer(ABC):
    name: str

    @abstractmethod
    def analyze(self, result: TestResult, context: ExecutionContext) -> dict[str, object]:
        """Return a structured diagnosis without mutating evidence."""


class PluginRegistry:
    def __init__(self) -> None:
        self.executors: dict[str, Executor] = {}
        self.collectors: list[Collector] = []
        self.analyzers: list[Analyzer] = []

    def register_executor(self, plugin: Executor) -> None:
        if plugin.name in self.executors:
            raise ValueError(f"Executor already registered: {plugin.name}")
        self.executors[plugin.name] = plugin

    def register_collector(self, plugin: Collector) -> None:
        self.collectors.append(plugin)

    def register_analyzer(self, plugin: Analyzer) -> None:
        self.analyzers.append(plugin)

    def executor(self, name: str) -> Executor:
        try:
            return self.executors[name]
        except KeyError as exc:
            raise ValueError(f"Unknown executor '{name}'. Available: {sorted(self.executors)}") from exc

