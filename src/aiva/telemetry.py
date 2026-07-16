from __future__ import annotations

import os
import platform
import time
from dataclasses import dataclass


def _load_average() -> float | None:
    try:
        return round(os.getloadavg()[0], 3)
    except (AttributeError, OSError):
        return None


@dataclass(slots=True)
class TelemetryCollector:
    started: float = 0.0
    load_before: float | None = None

    def start(self) -> None:
        self.started = time.monotonic()
        self.load_before = _load_average()

    def stop(self) -> dict[str, object]:
        return {
            "platform": platform.system(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
            "load_1m_before": self.load_before,
            "load_1m_after": _load_average(),
            "observed_seconds": round(time.monotonic() - self.started, 4),
        }

