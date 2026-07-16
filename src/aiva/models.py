from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass(slots=True)
class TestCase:
    name: str
    command: str
    timeout: float = 60.0
    expected_exit_code: int = 0
    tags: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class TestResult:
    name: str
    status: TestStatus
    command: str
    exit_code: int | None
    duration_seconds: float
    stdout: str = ""
    stderr: str = ""
    telemetry: dict[str, Any] = field(default_factory=dict)
    diagnosis: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RunReport:
    suite: str
    started_at: str
    finished_at: str
    results: list[TestResult]

    @property
    def passed(self) -> int:
        return sum(result.status == TestStatus.PASSED for result in self.results)

    @property
    def failed(self) -> int:
        return len(self.results) - self.passed

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite": self.suite,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "summary": {"total": len(self.results), "passed": self.passed, "failed": self.failed},
            "results": [result.to_dict() for result in self.results],
        }

