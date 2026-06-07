# Automation Kit

Reusable automation patterns with low-code contracts, deterministic fixtures, and tested Python implementations.

Automation Kit helps turn common business workflows — CRM imports, webhook routing, email triage, lead enrichment, calendar booking, Slack alerts, and creative-asset preparation — into repeatable automation patterns that can be inspected, tested, and run locally before connecting real services.

Each pattern includes:

- a low-code-style `workflow.json` contract
- synthetic fixtures and expected output
- a deterministic Python implementation
- regression tests
- notes on when to keep the workflow in n8n/Make/Zapier versus when to move logic into code

The repo is safe to run from a clean checkout: all shipped examples use synthetic data, mock clients, and disabled-by-default live service boundaries.

## What this is for

Use Automation Kit when you need to:

- turn a messy workflow idea into a repeatable automation pattern
- compare low-code and Python implementations before choosing a delivery path
- test CRM, webhook, email, calendar, Slack, enrichment, or creative workflows without live credentials
- package reusable automation logic for companion case-study repositories
- expose fixture-safe automation capabilities through CLI, API, Docker, or MCP

Automation Kit is not a hosted SaaS app and does not connect to live third-party accounts by default.

## Included automation patterns

| # | Pattern | Workflow problem | Output |
|---|---------|-----------------|--------|
| 1 | `csv-to-crm` | Import, normalize, dedupe, and upsert lead rows | Mock CRM upsert summary |
| 2 | `email-parser` | Classify inbound emails into support, sales, billing, spam, or review queues | Routed classification result |
| 3 | `lead-enrichment` | Enrich B2B prospect data with firmographic records | Firmographic records and manual-research flags |
| 4 | `calendar-booking` | Booking requests and availability checks | Event decision and confirmation message |
| 5 | `webhook-router` | Third-party event fan-out and dead-letter routing | Typed handler result or dead-letter queue item |
| 6 | `slack-alerts` | Ops alerts and team notifications | Severity-routed mock Slack messages |
| 7 | `product-creative-pack` | Ecommerce creative asset preparation | Prompt pack, ComfyUI manifest, mock assets, review packet |

Every pattern lives under `patterns/<name>/` with:

- `workflow.json` — declarative workflow structure.
- `fixtures/` — synthetic inputs plus `expected_output.json`.
- `python/main.py` — runnable Python equivalent.
- `python/test_*.py` — pattern-specific regression tests.
- `README.md` — implementation notes and automation fit.

See [`docs/pattern-index.md`](docs/pattern-index.md) for inputs, outputs, fit, and live-service boundaries for every pattern.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

auto-kit list-patterns
auto-kit validate-all
auto-kit run patterns/csv-to-crm
```

Expected validation result:

```text
7 pattern(s): 7 passed, 0 failed
```

Source-checkout module invocation also works without installing the console script:

```bash
PYTHONPATH=src python -m auto_kit.cli validate-all
```

## How to use it

### Use the CLI

```bash
auto-kit list-patterns
auto-kit validate patterns/webhook-router
auto-kit run patterns/webhook-router
```

### Run the local API

```bash
PYTHONPATH=src uvicorn auto_kit.api:app --host 127.0.0.1 --port 8000
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/patterns
```

OpenAPI docs are available at `http://127.0.0.1:8000/docs`.

### Run the MCP surface

```bash
auto-kit mcp-validate
auto-kit mcp-serve
```

### Run in Docker

```bash
docker build -t automation-kit .
docker run --rm automation-kit validate-all
```

## How a pattern is structured

Every pattern follows the same contract:

```text
patterns/<name>/
  workflow.json              low-code-style workflow contract
  README.md                  workflow fit, boundaries, and implementation notes
  fixtures/
    input.*                  synthetic input data
    expected_output.json     expected deterministic result
  python/
    main.py                  runnable Python equivalent
    test_<name>.py           pattern-specific regression tests
```

The repository validates this structure through `auto-kit validate-all` and `tests/test_all_patterns.py`.

## Choosing low-code vs Python

Automation Kit is designed for the decision point before implementation:

- If the workflow is simple, visual, and owned by non-developers, keep it in n8n, Make, or Zapier.
- If it needs validation, deduplication, replay safety, CI, or auditability, move the risky logic into tested Python.
- If it needs both, keep the workflow contract visible and test the risky logic locally.

Automation Kit keeps both views visible: `workflow.json` explains the low-code flow, while `python/main.py` proves the same logic can run deterministically under tests.

## Safety model

Automation Kit is safe to run from a clean checkout:

- all shipped data is synthetic
- mock clients are used by default
- live services require explicit environment opt-in
- `.env.example` contains empty credential placeholders
- API and MCP responses report `fixture_safe=true` and `live_services_used=false`
- ComfyUI/network calls are disabled unless `AUTO_KIT_USE_LIVE_SERVICES=true` and a local endpoint are explicitly supplied

### ComfyUI boundary

The `product-creative-pack` pattern models an ecommerce creative workflow: product brief, prompt pack, ComfyUI job manifest, deterministic mock assets, and a human review packet. It does not generate images by default.

Live ComfyUI calls are isolated behind `auto_kit.comfyui_client.ComfyUIClient`, which raises before any network operation unless `AUTO_KIT_USE_LIVE_SERVICES=true` and `COMFYUI_BASE_URL` are supplied in the local runtime environment.

## Companion case studies

Automation Kit is the reusable pattern layer. Companion case-study repositories apply the same pattern discipline to one concrete workflow problem at a time.

Public companion case studies include:

- [`api-webhook-bridge`](https://github.com/stefan-mcf/api-webhook-bridge) — safe API/webhook builds with validation, mapping, idempotency, audit, and dead-letter behavior.
- [`automation-debugger`](https://github.com/stefan-mcf/automation-debugger) — broken automation diagnosis, normalized event inspection, safe replay/refusal, and fix reports.

See [`docs/case-studies/api-webhook-bridge.md`](docs/case-studies/api-webhook-bridge.md) and [`docs/case-studies/automation-debugger.md`](docs/case-studies/automation-debugger.md) for the Automation Kit relationship.

## Documentation

- [`docs/pattern-index.md`](docs/pattern-index.md) — inputs, outputs, automation value, and fit for every pattern.
- [`docs/architecture.md`](docs/architecture.md) — package boundaries, runtime flow, and live-service isolation.
- [`docs/api.md`](docs/api.md) — local FastAPI/OpenAPI surface for fixture-safe pattern runs.
- [`docs/mcp.md`](docs/mcp.md) — fixture-safe MCP surface and capability registry.
- [`docs/deployment.md`](docs/deployment.md) — local Docker/API runtime, healthcheck, and cloud-free boundary.
- [`docs/public-readiness.md`](docs/public-readiness.md) — public-surface audit criteria and release hygiene checks.
- [`docs/proof-spoke-architecture.md`](docs/proof-spoke-architecture.md) — companion case-study architecture and readiness contract.
- [`EVIDENCE.md`](EVIDENCE.md) — latest verification snapshot.

## Evidence package

These screenshots show the current CLI validation, pattern outputs, architecture, quality gates, and companion case-study relationship.

[![CLI validation proof](docs/screenshots/01-cli-validation.png)](docs/screenshots/01-cli-validation.png)

[![Pattern output proof](docs/screenshots/02-pattern-output.png)](docs/screenshots/02-pattern-output.png)

[![Architecture proof](docs/screenshots/03-architecture.png)](docs/screenshots/03-architecture.png)

[![Quality gate proof](docs/screenshots/04-quality-gates.png)](docs/screenshots/04-quality-gates.png)

[![Case study proof](docs/screenshots/05-case-study-link.png)](docs/screenshots/05-case-study-link.png)

## Quality gates

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src
PYTHONPATH=src python -m auto_kit.cli validate-all
PYTHONPATH=src python -m auto_kit.cli mcp-validate
docker build -t automation-kit:local .
docker run --rm automation-kit:local validate-all
```

## Environment

See `.env.example`:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_KIT_USE_LIVE_SERVICES` | `false` | Explicit opt-in gate for live API clients. |
| `AUTO_KIT_MOCK_SEED` | `42` | Seed for deterministic mock data. |
| `COMFYUI_BASE_URL` | empty | Optional local or cloud ComfyUI base URL. |
| `COMFY_CLOUD_API_KEY` | empty | Optional Comfy Cloud key supplied only outside git. |

## Repository layout

```text
src/auto_kit/
  api.py
  capability_registry.py
  cli.py
  comfyui_client.py
  fixtures.py
  mcp_server.py
  mock_clients.py
  models.py
  pattern_runner.py
  registry/
  workflow_schema.py
patterns/
  <pattern-name>/
    workflow.json
    README.md
    fixtures/
    python/
docs/
  architecture.md
  api.md
  case-studies/
  deployment.md
  mcp.md
  pattern-index.md
  proof-spoke-architecture.md
  screenshots/
examples/
  api-requests/
  api-responses/
  mcp/
registry/
  capabilities.yaml
  sectors.yaml
```

## License

MIT License. See [`LICENSE`](LICENSE).

## Automation Tools Catalog

Part of [Stefan's automation tools catalog](https://github.com/stefan-mcf/automation-tools).
