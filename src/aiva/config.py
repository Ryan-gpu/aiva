from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import TestCase


class ConfigurationError(ValueError):
    pass


def load_suite(path: str | Path) -> tuple[str, list[TestCase]]:
    source = Path(path)
    try:
        data: dict[str, Any] = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Unable to read suite {source}: {exc}") from exc

    suite_name = str(data.get("suite", source.stem))
    raw_tests = data.get("tests")
    if not isinstance(raw_tests, list) or not raw_tests:
        raise ConfigurationError("A suite must contain a non-empty 'tests' list")

    tests: list[TestCase] = []
    for index, item in enumerate(raw_tests, start=1):
        if not isinstance(item, dict) or not item.get("name") or not item.get("command"):
            raise ConfigurationError(f"Test #{index} requires 'name' and 'command'")
        tests.append(
            TestCase(
                name=str(item["name"]),
                command=str(item["command"]),
                timeout=float(item.get("timeout", 60)),
                expected_exit_code=int(item.get("expected_exit_code", 0)),
                tags=[str(tag) for tag in item.get("tags", [])],
                env={str(key): str(value) for key, value in item.get("env", {}).items()},
            )
        )
    return suite_name, tests

