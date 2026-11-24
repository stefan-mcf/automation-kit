# Automation Kit

Reusable workflow contracts and tested Python implementations for imports, webhook routing, email triage, booking and alerts. Inspect and exercise the same bounded patterns through CLI, API or MCP.

**Status:** local reference toolkit with synthetic fixtures and mock clients.

**My contribution:** pattern contracts, capability registry, Python services, tool interfaces, tests and operating documentation.

[Pattern index](docs/pattern-index.md) · [Architecture](docs/architecture.md) · [MCP interface](docs/mcp.md)

## Six rows become five contacts

The [sample CSV](patterns/csv-to-crm/fixtures/input.csv) repeats one email with updated contact details. The importer keeps the later values and produces five mock contacts, with one duplicate recorded in the [expected output](patterns/csv-to-crm/fixtures/expected_output.json). After [setup](#usage), run `auto-kit run patterns/csv-to-crm` to check the fixture against that output.

## How it works

Each pattern contains a `workflow.json` contract, synthetic inputs, expected output, a Python implementation and regression tests. The registry separates discoverable capabilities from the smaller set enabled for API/MCP execution.

Seven patterns cover CRM import, email parsing, lead enrichment, calendar booking, webhook routing, Slack alerts and creative-asset preparation. The [pattern index](docs/pattern-index.md) documents inputs, outputs and low-code versus Python fit.

The framework supplies the reusable layer for [API Webhook Bridge](https://github.com/stefan-mcf/api-webhook-bridge) and [Automation Debugger](https://github.com/stefan-mcf/automation-debugger). Those repos remain focused on their integration and diagnosis contracts.

## Usage

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
auto-kit list-patterns
auto-kit validate-all
auto-kit run patterns/csv-to-crm
```

The supplied pattern validation returns `7 pattern(s): 7 passed, 0 failed`.

Start the API with `uvicorn auto_kit.api:app --host 127.0.0.1 --port 8000`; local health and OpenAPI documentation are at `/health` and `/docs`.

For MCP, run `auto-kit mcp-validate` or `auto-kit mcp-serve`. The server uses the official MCP Python SDK 2.x over stdio. The transport regression starts a real subprocess, initializes the client, discovers tools and checks allowed and rejected fixture executions.

Docker is also available:

```bash
docker build -t automation-kit .
docker run --rm automation-kit validate-all
```

## Validation

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src
PYTHONPATH=src python -m auto_kit.cli validate-all
PYTHONPATH=src python -m auto_kit.cli mcp-validate
```

Run `python -m pytest -q tests/test_mcp_transport.py` to isolate the protocol-level check. It complements the direct handler tests.

## Scope and current state

Shipped examples use synthetic data and mock clients. API/MCP outputs report `fixture_safe=true` and `live_services_used=false`. Only allowlisted patterns are runnable through these interfaces.

Live ComfyUI use requires both `AUTO_KIT_USE_LIVE_SERVICES=true` and an explicit endpoint; the creative pattern does not generate images by default. See [.env.example](.env.example) and the [deployment guide](docs/deployment.md) before supplying local configuration.

This is a toolkit, not a hosted service or a general autonomous agent. Development-agent workflow examples are separate from runtime tool execution.

## Documentation

- [Agent-assisted engineering workflow](docs/engineering-workflow.md)
- [Pattern index](docs/pattern-index.md) and [architecture](docs/architecture.md)
- [API](docs/api.md), [MCP](docs/mcp.md) and [deployment](docs/deployment.md)
- [Companion architecture](docs/proof-spoke-architecture.md)
- [API Bridge case study](docs/case-studies/api-webhook-bridge.md) and [Debugger case study](docs/case-studies/automation-debugger.md)
- [Verification index](EVIDENCE.md), [historical generated panels](docs/screenshots/README.md) and [readiness checks](docs/public-readiness.md)

MIT. See [LICENSE](LICENSE).
