import pytest

from aiva.executors import LocalExecutor
from aiva.plugins import PluginRegistry


def test_registry_resolves_executor() -> None:
    registry = PluginRegistry()
    registry.register_executor(LocalExecutor())
    assert registry.executor("local").name == "local"


def test_registry_rejects_duplicate_executor() -> None:
    registry = PluginRegistry()
    registry.register_executor(LocalExecutor())
    with pytest.raises(ValueError, match="already registered"):
        registry.register_executor(LocalExecutor())

