from pathlib import Path

import pytest

from aiva.config import ConfigurationError, load_suite


def test_load_suite(tmp_path: Path) -> None:
    suite = tmp_path / "suite.yaml"
    suite.write_text("suite: smoke\ntests:\n  - name: ok\n    command: echo ok\n", encoding="utf-8")
    name, tests = load_suite(suite)
    assert name == "smoke"
    assert tests[0].command == "echo ok"


def test_rejects_empty_suite(tmp_path: Path) -> None:
    suite = tmp_path / "suite.yaml"
    suite.write_text("suite: empty\ntests: []\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_suite(suite)

