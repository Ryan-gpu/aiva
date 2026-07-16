from __future__ import annotations

import html
import json
from pathlib import Path

from .models import RunReport, TestStatus


def write_json(report: RunReport, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return destination


def write_html(report: RunReport, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for result in report.results:
        css = "pass" if result.status == TestStatus.PASSED else "fail"
        diagnosis = result.diagnosis.get("primary_signature", "-")
        performance = next(
            (
                f"{metric}: {values.get('regression_percent')}%"
                for metric, values in result.performance.items()
                if values.get("regression_percent") is not None
            ),
            "-",
        )
        evidence = ", ".join(item.source for item in result.evidence) or "-"
        details = ""
        if result.stdout or result.stderr:
            logs = html.escape((result.stdout + "\n" + result.stderr).strip())
            details = f"<details><summary>Evidence logs</summary><pre>{logs}</pre></details>"
        rows.append(
            f"<tr><td>{html.escape(result.name)}</td><td class='{css}'>{result.status.value}</td>"
            f"<td>{result.attempts}</td><td>{result.duration_seconds:.3f}s</td>"
            f"<td>{html.escape(str(diagnosis))}</td><td>{html.escape(performance)}</td>"
            f"<td>{html.escape(evidence)}{details}</td></tr>"
        )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>AIVA report - {html.escape(report.suite)}</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 20px;color:#172033}}
h1{{margin-bottom:4px}}.summary{{display:flex;gap:16px;margin:24px 0}}.card{{padding:16px 22px;background:#f4f6fa;border-radius:10px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #dde2ea;vertical-align:top}}
.run{{color:#596579}}pre{{white-space:pre-wrap;max-width:420px;background:#101828;color:#e4e7ec;padding:10px;border-radius:6px}}
.pass{{color:#087a3e;font-weight:700}}.fail{{color:#b42318;font-weight:700}}</style></head>
<body><h1>AIVA Validation Report</h1><p>{html.escape(report.suite)}</p><p class="run">Run {html.escape(report.run_id)}</p>
<div class="summary"><div class="card">Total<br><strong>{len(report.results)}</strong></div>
<div class="card">Passed<br><strong>{report.passed}</strong></div><div class="card">Failed<br><strong>{report.failed}</strong></div></div>
<table><thead><tr><th>Test</th><th>Status</th><th>Attempts</th><th>Duration</th><th>Diagnosis</th><th>Regression</th><th>Evidence</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></body></html>"""
    destination.write_text(document, encoding="utf-8")
    return destination
