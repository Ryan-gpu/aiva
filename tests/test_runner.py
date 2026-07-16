import sys

from aiva.models import TestCase as Case, TestStatus as Status
from aiva.runner import ValidationRunner


def test_runner_passes_expected_command() -> None:
    test = Case(name="pass", command=f'{sys.executable} -c "print(42)"')
    result = ValidationRunner().run_test(test)
    assert result.status == Status.PASSED
    assert "42" in result.stdout
    assert result.telemetry["cpu_count"]


def test_runner_diagnoses_failure() -> None:
    command = f'{sys.executable} -c "import sys; print(\'Out of memory\', file=sys.stderr); sys.exit(1)"'
    result = ValidationRunner().run_test(Case(name="oom", command=command))
    assert result.status == Status.FAILED
    assert result.diagnosis["primary_signature"] == "out_of_memory"
