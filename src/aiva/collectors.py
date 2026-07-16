from __future__ import annotations

import os
import platform
import time

from .models import Evidence, ExecutionContext, ExecutionResult, TestCase
from .plugins import Collector


class HostTelemetryCollector(Collector):
    name = "host-telemetry"

    def __init__(self) -> None:
        self._started: dict[str, tuple[float, float | None]] = {}

    def before(self, case: TestCase, context: ExecutionContext) -> None:
        self._started[case.id] = (time.monotonic(), _load_average())

    def after(
        self, case: TestCase, execution: ExecutionResult, context: ExecutionContext
    ) -> Evidence:
        started, load_before = self._started.pop(case.id, (time.monotonic(), None))
        return Evidence(
            source=self.name,
            data={
                "platform": platform.system(),
                "machine": platform.machine(),
                "cpu_count": os.cpu_count(),
                "load_1m_before": load_before,
                "load_1m_after": _load_average(),
                "observed_seconds": round(time.monotonic() - started, 4),
            },
        )


def _load_average() -> float | None:
    try:
        return round(os.getloadavg()[0], 3)
    except (AttributeError, OSError):
        return None

