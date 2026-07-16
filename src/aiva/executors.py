from __future__ import annotations

import os
import shlex
import subprocess
import sys
import time

from .models import ExecutionContext, ExecutionResult, TestCase
from .plugins import Executor


class LocalExecutor(Executor):
    name = "local"

    def execute(self, case: TestCase, context: ExecutionContext) -> ExecutionResult:
        command = self._command(case)
        started = time.monotonic()
        try:
            process = subprocess.run(
                command,
                shell=case.shell,
                capture_output=True,
                text=True,
                timeout=case.timeout,
                env={**os.environ, **case.env},
                cwd=context.work_dir,
                check=False,
            )
            return ExecutionResult(
                process.returncode,
                process.stdout,
                process.stderr,
                round(time.monotonic() - started, 4),
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                None,
                _decode(exc.stdout),
                f"{_decode(exc.stderr)}\nTimeout after {case.timeout} seconds".strip(),
                round(time.monotonic() - started, 4),
                timed_out=True,
            )

    @staticmethod
    def _command(case: TestCase) -> str | list[str]:
        if isinstance(case.command, list):
            return [sys.executable if part == "{python}" else part for part in case.command]
        expanded = case.command.replace("{python}", shlex.quote(sys.executable))
        return expanded if case.shell else shlex.split(expanded)


def _decode(value: bytes | str | None) -> str:
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value

