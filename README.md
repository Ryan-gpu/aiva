# AIVA

**AI-Driven Intelligent Validation & Automation Framework**

AIVA is a plugin-oriented Python validation platform for functional, performance,
stability, and system-level testing. It separates orchestration from target-specific
execution, evidence collection, and root-cause analysis.

The project is inspired by real validation work across GPU, SoC, firmware, drivers,
operating systems, and AI software stacks. It deliberately uses public, portable
examples so anyone can run the demo without proprietary hardware or internal tools.

## Why AIVA

- One YAML format for smoke, regression, stress, and fault-injection tests
- Safe command execution without a shell by default
- Pluggable executors, collectors, and analyzers
- Lifecycle guarantees: prepare, execute/retry, collect, analyze, cleanup
- Concurrent scheduling with deterministic report ordering
- Lightweight host telemetry captured for every test
- Deterministic failure signatures for GPU, crash, timeout, memory, and permission issues
- SQLite performance baselines and regression thresholds
- AI-ready analyzer contract without requiring an API key for the default demo
- JSON and standalone HTML reports
- CI validation across supported Python versions

## Architecture

```text
YAML Suite -> Concurrent Orchestrator -> Plugin Registry
                  |                       |-> Executors
                  |                       |-> Collectors
                  |                       `-> Analyzers
                  `-> Evidence + Baselines -> JSON / HTML Reports
```

See [the architecture document](docs/architecture.md) for contracts, lifecycle,
failure boundaries, and an extension example.

## Quick start

```bash
git clone https://github.com/Ryan-gpu/aiva.git
cd aiva
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
aiva run examples/demo-suite.yaml --workers 2 --baseline-db reports/history.db
```

The demo contains functional and performance samples plus injected GPU and timeout failures. AIVA
returns a non-zero exit status when a suite fails, which makes it suitable for CI.
Open `reports/report.html` to inspect the summary and automatic diagnoses.

## Example suite

```yaml
suite: smoke
tests:
  - name: Runtime check
    command: ["{python}", "-c", "print('ready')"]
    timeout: 10
    tags: [smoke]
```

`{python}` is replaced with the interpreter running AIVA, so suites remain portable
across virtual environments and CI workers.

## Roadmap

- OpenAI-compatible root-cause analysis provider with redaction controls
- SSH, Docker, and device-lab execution adapters
- PyTorch and OpenVINO workload plugins
- Dependency graphs and quarantine policies
- JUnit XML and historical trend dashboard

## Interview demo

1. Explain why orchestration depends on plugin contracts instead of target implementations.
2. Run the fault-injection suite and show that known signatures are classified automatically.
3. Open the HTML report and discuss how telemetry supports root-cause analysis.
4. Add a hardware-specific executor or collector without changing the scheduler.

## Safety and confidentiality

AIVA contains no proprietary Intel, Panasonic, or customer code, data, test plans, or
hardware details. Keep future examples synthetic and redact logs before sending them to
an external AI service.

## License

MIT
