from aiva.baseline import BaselineStore


def test_baseline_detects_regression(tmp_path) -> None:
    store = BaselineStore(tmp_path / "history.db")
    store.record("perf", "duration_seconds", 1.0)
    comparison = store.compare_and_record("perf", "duration_seconds", 1.3, 20)
    assert comparison["baseline"] == 1.0
    assert comparison["regression_percent"] == 30.0
    assert comparison["passed"] is False

