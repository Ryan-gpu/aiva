from __future__ import annotations

import re

from .models import ExecutionContext, TestResult
from .plugins import Analyzer


RULES = (
    ("out_of_memory", re.compile(r"out of memory|oom|cannot allocate memory", re.I), "memory"),
    ("timeout", re.compile(r"timed? out|timeout", re.I), "execution"),
    ("permission_denied", re.compile(r"permission denied|access denied", re.I), "environment"),
    ("crash", re.compile(r"segmentation fault|segfault|kernel panic|core dumped", re.I), "stability"),
    ("gpu_failure", re.compile(r"gpu hang|device lost|xid error", re.I), "gpu"),
    ("assertion", re.compile(r"assertionerror|assertion failed", re.I), "functional"),
)


class FailureAnalyzer(Analyzer):
    name = "failure-signatures"

    def analyze(
        self,
        result: TestResult | str,
        context: ExecutionContext | str | None = None,
        *,
        timed_out: bool = False,
    ) -> dict[str, object]:
        # String inputs preserve the small v0.1 public API.
        if isinstance(result, str):
            stdout, stderr = result, str(context or "")
            is_timeout = timed_out
        else:
            stdout, stderr = result.stdout, result.stderr
            is_timeout = result.exit_code is None and "Timeout" in result.stderr
        text = f"{stdout}\n{stderr}"
        matches = [
            {"signature": name, "category": category}
            for name, pattern, category in RULES
            if pattern.search(text)
        ]
        if is_timeout and not any(match["signature"] == "timeout" for match in matches):
            matches.append({"signature": "timeout", "category": "execution"})
        primary = matches[0] if matches else {"signature": "unknown", "category": "unknown"}
        return {
            "primary_signature": primary["signature"],
            "category": primary["category"],
            "matches": matches,
            "recommendation": self._recommend(str(primary["signature"])),
            "engine": self.name,
        }

    @staticmethod
    def _recommend(signature: str) -> str:
        return {
            "out_of_memory": "Inspect peak memory usage, workload size, and resource cleanup.",
            "timeout": "Check for deadlock, system load, and the timeout threshold.",
            "permission_denied": "Verify privileges, file ownership, and device access rules.",
            "crash": "Collect a core dump and correlate the stack with recent changes.",
            "gpu_failure": "Correlate workload, driver, firmware, and kernel evidence.",
            "assertion": "Compare expected and actual values at the first failing dependency.",
            "unknown": "Compare complete evidence with the last known-good run.",
        }[signature]

