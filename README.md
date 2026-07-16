# AIVA

**AI-Driven Intelligent Validation & Automation Framework**

AIVA is a portable Python framework for functional, performance, stability, and
system-level validation. It turns declarative test suites into reproducible runs,
collects telemetry, classifies failures, and produces interview-friendly reports.

The project is inspired by real validation work across GPU, SoC, firmware, drivers,
operating systems, and AI software stacks. It deliberately uses public, portable
examples so anyone can run the demo without proprietary hardware or internal tools.

## Why AIVA

- One YAML format for smoke, regression, stress, and fault-injection tests
- Command execution with environment overrides and timeouts
- Lightweight host telemetry captured for every test
- Deterministic failure signatures for GPU, crash, timeout, memory, and permission issues
- AI-ready analyzer interface without requiring an API key for the default demo
- JSON and standalone HTML reports
- CI validation across supported Python versions

## Architecture

```text
YAML Suite -> Config Loader -> Validation Runner -> Command Adapter
                                      |-> Telemetry Collector
                                      |-> Failure Analyzer
                                      `-> JSON / HTML Reports
```

## Quick start

```bash
git clone https://github.com/Ryan-gpu/aiva.git
cd aiva
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
aiva run examples/demo-suite.yaml
```

The demo intentionally contains one passing test and two injected failures. AIVA
returns a non-zero exit status when a suite fails, which makes it suitable for CI.
Open `reports/report.html` to inspect the summary and automatic diagnoses.

## Example suite

```yaml
suite: smoke
tests:
  - name: Runtime check
    command: "{python} -c \"print('ready')\""
    timeout: 10
    tags: [smoke]
```

`{python}` is replaced with the interpreter running AIVA, so suites remain portable
across virtual environments and CI workers.

## Roadmap

- OpenAI-compatible root-cause analysis provider with redaction controls
- Performance baselines and regression thresholds
- SSH, Docker, and device-lab execution adapters
- PyTorch and OpenVINO workload plugins
- Parallel scheduling, retries, and quarantine policies
- JUnit XML and historical trend dashboard

## Interview demo

1. Explain how the runner separates configuration, execution, telemetry, diagnosis, and reporting.
2. Run the fault-injection suite and show that known signatures are classified automatically.
3. Open the HTML report and discuss how telemetry supports root-cause analysis.
4. Extend `FailureAnalyzer` or add a hardware-specific execution adapter live.

## Safety and confidentiality

AIVA contains no proprietary Intel, Panasonic, or customer code, data, test plans, or
hardware details. Keep future examples synthetic and redact logs before sending them to
an external AI service.

## License

MIT
