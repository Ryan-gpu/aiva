from __future__ import annotations

import sqlite3
from pathlib import Path


class BaselineStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS measurements "
                "(test_id TEXT NOT NULL, metric TEXT NOT NULL, value REAL NOT NULL, "
                "recorded_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )

    def record(self, test_id: str, metric: str, value: float) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO measurements(test_id, metric, value) VALUES (?, ?, ?)",
                (test_id, metric, value),
            )

    def median(self, test_id: str, metric: str, limit: int = 10) -> float | None:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT value FROM measurements WHERE test_id=? AND metric=? "
                "ORDER BY recorded_at DESC LIMIT ?",
                (test_id, metric, limit),
            ).fetchall()
        values = sorted(row[0] for row in rows)
        if not values:
            return None
        middle = len(values) // 2
        return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2

    def compare_and_record(
        self, test_id: str, metric: str, value: float, max_regression_percent: float
    ) -> dict[str, float | bool | None]:
        baseline = self.median(test_id, metric)
        regression = None if baseline in (None, 0) else ((value - baseline) / baseline) * 100
        passed = regression is None or regression <= max_regression_percent
        self.record(test_id, metric, value)
        return {
            "value": value,
            "baseline": baseline,
            "regression_percent": None if regression is None else round(regression, 2),
            "threshold_percent": max_regression_percent,
            "passed": passed,
        }

