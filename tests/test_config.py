from pathlib import Path

import pytest

from aiva.config import ConfigurationError, load_suite


def test_load_suite(tmp_path: Path) -> None:
    suite = tmp_path / "suite.yaml"
    suite.write_text("suite: smoke\ntests:\n  - name: ok\n    command: echo ok\n", encoding="utf-8")
    name, tests = load_suite(suite)
    assert name == "smoke"
    assert tests[0].command == "echo ok"


def test_loads_structured_v2_fields(tmp_path: Path) -> None:
    suite = tmp_path / "suite.yaml"
    suite.write_text(
        "suite: v2\ntests:\n  - id: perf\n    name: perf\n"
        "    command: ['{python}', '-c', 'print(1)']\n    retries: 2\n"
        "    performance:\n      max_regression_percent: 10\n",
        encoding="utf-8",
    )
    _, tests = load_suite(suite)
    assert tests[0].id == "perf"
    assert tests[0].retries == 2
    assert tests[0].performance["max_regression_percent"] == 10


def test_rejects_empty_suite(tmp_path: Path) -> None:
    suite = tmp_path / "suite.yaml"
    suite.write_text("suite: empty\ntests: []\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_suite(suite)
