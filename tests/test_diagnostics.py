from aiva.diagnostics import FailureAnalyzer


def test_detects_gpu_failure() -> None:
    diagnosis = FailureAnalyzer().analyze("", "GPU device lost")
    assert diagnosis["primary_signature"] == "gpu_failure"
    assert diagnosis["category"] == "gpu"


def test_detects_timeout_flag() -> None:
    diagnosis = FailureAnalyzer().analyze("", "", timed_out=True)
    assert diagnosis["primary_signature"] == "timeout"

