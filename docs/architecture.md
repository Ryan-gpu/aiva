# AIVA v0.2 architecture

## Design goals

AIVA separates orchestration from target-specific behavior. The core owns lifecycle,
scheduling, status, evidence, and reporting. Plugins own execution environments,
telemetry sources, and analysis strategies.

```text
Suite YAML
   |
Config Loader
   |
Concurrent Orchestrator
   +-- prepare -> execute/retry -> collect -> analyze -> cleanup
   |
Plugin Registry
   +-- Executors: local | future SSH, Docker, device lab
   +-- Collectors: host telemetry | future GPU, thermal, kernel logs
   +-- Analyzers: signatures | future baseline correlation, LLM RCA
   |
Evidence + SQLite Baselines -> JSON / HTML report
```

## Core contracts

- `Executor`: prepares a target, executes one case, and always cleans up resources.
- `Collector`: captures evidence before and after execution without deciding pass/fail.
- `Analyzer`: consumes immutable result evidence and returns a structured diagnosis.
- `PluginRegistry`: resolves named executors and composes collectors and analyzers.
- `BaselineStore`: retains measurements and evaluates regressions against recent medians.

## Lifecycle and failure boundaries

1. Resolve the executor before acquiring resources.
2. Run executor `prepare` once.
3. Start every collector.
4. Execute with bounded retries.
5. Stop collectors and attach evidence.
6. Analyze failures; never send logs externally by default.
7. Evaluate performance thresholds.
8. Run executor `cleanup` in `finally`, including timeout and exception paths.

## Security decisions

Commands are tokenized and executed without a shell by default. A test must explicitly
set `shell: true` when shell behavior is required. AI analysis is an optional plugin;
the default analyzer is deterministic and keeps all evidence local.

## Extension example

```python
class SshExecutor(Executor):
    name = "ssh"

    def prepare(self, case, context): ...
    def execute(self, case, context): ...
    def cleanup(self, case, context): ...

registry.register_executor(SshExecutor())
```

