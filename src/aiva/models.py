from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass(slots=True)
class TestCase:
    name: str
    command: str | list[str]
    id: str = ""
    executor: str = "local"
    timeout: float = 60.0
    expected_exit_code: int = 0
    tags: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    retries: int = 0
    shell: bool = False
    performance: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = self.name.lower().replace(" ", "-")


@dataclass(slots=True)
class ExecutionContext:
    run_id: str
    suite: str
    work_dir: Path
    artifacts_dir: Path
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionResult:
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False


@dataclass(slots=True)
class Evidence:
    source: str
    data: dict[str, Any]


@dataclass(slots=True)
class TestResult:
    name: str
    status: TestStatus
    command: str | list[str]
    exit_code: int | None
    duration_seconds: float
    test_id: str = ""
    attempts: int = 1
    stdout: str = ""
    stderr: str = ""
    telemetry: dict[str, Any] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    diagnosis: dict[str, Any] = field(default_factory=dict)
    performance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RunReport:
    suite: str
    started_at: str
    finished_at: str
    results: list[TestResult]
    run_id: str = ""

    @property
    def passed(self) -> int:
        return sum(result.status == TestStatus.PASSED for result in self.results)

    @property
    def failed(self) -> int:
        return sum(result.status in {TestStatus.FAILED, TestStatus.ERROR} for result in self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "suite": self.suite,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "summary": {"total": len(self.results), "passed": self.passed, "failed": self.failed},
            "results": [result.to_dict() for result in self.results],
        }

