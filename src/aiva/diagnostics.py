from __future__ import annotations

import re


RULES = (
    ("out_of_memory", re.compile(r"out of memory|oom|cannot allocate memory", re.I), "memory"),
    ("timeout", re.compile(r"timed? out|timeout", re.I), "execution"),
    ("permission_denied", re.compile(r"permission denied|access denied", re.I), "environment"),
    ("crash", re.compile(r"segmentation fault|segfault|kernel panic|core dumped", re.I), "stability"),
    ("gpu_failure", re.compile(r"gpu hang|device lost|xid error", re.I), "gpu"),
    ("assertion", re.compile(r"assertionerror|assertion failed", re.I), "functional"),
)


class FailureAnalyzer:
    """Deterministic first-pass diagnosis with an AI-ready extension point."""

    def analyze(self, stdout: str, stderr: str, *, timed_out: bool = False) -> dict[str, object]:
        text = f"{stdout}\n{stderr}"
        matches = [
            {"signature": name, "category": category}
            for name, pattern, category in RULES
            if pattern.search(text)
        ]
        if timed_out and not any(match["signature"] == "timeout" for match in matches):
            matches.append({"signature": "timeout", "category": "execution"})

        primary = matches[0] if matches else {"signature": "unknown", "category": "unknown"}
        return {
            "primary_signature": primary["signature"],
            "category": primary["category"],
            "matches": matches,
            "recommendation": self._recommend(str(primary["signature"])),
            "engine": "deterministic-rules",
        }

    @staticmethod
    def _recommend(signature: str) -> str:
        recommendations = {
            "out_of_memory": "Inspect peak memory usage, workload size, and resource cleanup.",
            "timeout": "Check for deadlock, system load, and an unrealistic timeout threshold.",
            "permission_denied": "Verify user privileges, file ownership, and device access rules.",
            "crash": "Collect a core dump and correlate the stack with recent software changes.",
            "gpu_failure": "Collect driver and kernel logs, then isolate workload, driver, and firmware.",
            "assertion": "Compare actual and expected values and inspect the first failing dependency.",
            "unknown": "Review complete logs and compare with the last known-good run.",
        }
        return recommendations[signature]

