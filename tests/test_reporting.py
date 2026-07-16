from datetime import datetime, timezone

from aiva.models import RunReport, TestResult as Result, TestStatus as Status
from aiva.reporting import write_html, write_json


def test_reports_are_created(tmp_path) -> None:
    now = datetime.now(timezone.utc).isoformat()
    report = RunReport("demo", now, now, [Result("ok", Status.PASSED, "true", 0, 0.1)])
    json_path = write_json(report, tmp_path / "report.json")
    html_path = write_html(report, tmp_path / "report.html")
    assert '"passed": 1' in json_path.read_text()
    assert "AIVA Validation Report" in html_path.read_text()
