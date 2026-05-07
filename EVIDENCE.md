# Automation Kit Evidence Package

Generated: 2026-05-07 UTC
Repository: `stefan-mcf/automation-kit`
Branch: `main`

## Summary

| Metric | Value |
|--------|-------|
| Distribution package | `automation-kit` 0.1.0 |
| Python package / CLI | `auto_kit` / `auto-kit` |
| Patterns | 7 |
| API proof surface | FastAPI/OpenAPI local wrapper for fixture-safe pattern runs |
| MCP proof surface | Fixture-safe sector/capability registry and MCP handler surface |
| Deployment proof | Docker image plus local Docker Compose API mode |
| Public companion case study | `api-webhook-bridge` |
| Test suite | 147 passed, 1 known httpx deprecation warning |
| Ruff | Clean |
| Mypy src/ | Clean |
| CLI validation | 7/7 passed |
| MCP validation | 9 sectors, 6 capabilities |
| Docker | Build and container smoke verified in the final commit gate when Docker is available |

## Pattern inventory

| Pattern | Validate | Primary fixture proof |
|---------|----------|-----------------------|
| `calendar-booking` | PASS | synthetic booking request and expected scheduling decision |
| `csv-to-crm` | PASS | synthetic lead CSV and expected CRM upsert summary |
| `email-parser` | PASS | synthetic email payload and expected route classification |
| `lead-enrichment` | PASS | synthetic lead data and expected firmographic enrichment |
| `product-creative-pack` | PASS | synthetic product brief and expected prompt/review packet |
| `slack-alerts` | PASS | synthetic events and expected mock Slack messages |
| `webhook-router` | PASS | synthetic webhook payloads and expected routing/dead-letter output |

## API proof

Local API docs:

- `docs/api.md`
- `examples/api-requests/`
- `examples/api-responses/`

Required endpoints implemented:

- `GET /health`
- `GET /patterns`
- `GET /patterns/{pattern_name}`
- `POST /patterns/{pattern_name}/run`

API responses include `fixture_safe=true` and `live_services_used=false`.

## MCP proof

Local MCP docs:

- `docs/mcp.md`
- `examples/mcp/README.md`
- `registry/capabilities.yaml`
- `registry/sectors.yaml`

The MCP surface exposes stable verbs for health, pattern discovery, validation, fixture-safe runs, sector discovery, capability lookup, and evidence metadata. Runnable defaults are synthetic and report `live_services_used=false`.

## Public companion case study

| Repo | Current role | Evidence |
|---|---|---|
| [`api-webhook-bridge`](https://github.com/stefan-mcf/api-webhook-bridge) | API/webhook bridge case study | fixture-safe event mapping, Airtable-style upsert, idempotency, audit/dead-letter proof, tests, screenshots, sandbox responses, case study |

Automation Kit keeps the reusable engine layer. Companion case studies keep workflow-specific mapping, API, and evidence packages.

## CLI commands

```text
PYTHONPATH=src python -m auto_kit.cli list-patterns
PYTHONPATH=src python -m auto_kit.cli validate patterns/csv-to-crm
PYTHONPATH=src python -m auto_kit.cli run patterns/csv-to-crm
PYTHONPATH=src python -m auto_kit.cli run patterns/product-creative-pack
PYTHONPATH=src python -m auto_kit.cli validate-all
PYTHONPATH=src python -m auto_kit.cli mcp-validate
```

Expected result: seven patterns discovered and `7 pattern(s): 7 passed, 0 failed`.

## Quality gates

```text
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
PYTHONPATH=src python -m mypy src
PYTHONPATH=src python -m auto_kit.cli validate-all
PYTHONPATH=src python -m auto_kit.cli mcp-validate
docker build -t automation-kit .
docker run --rm automation-kit validate-all
docker compose config
```

## Safety evidence

- `.env.example` uses empty optional credential placeholders.
- Live services are disabled by default with `AUTO_KIT_USE_LIVE_SERVICES=false`.
- API, MCP, and Compose proof stay local and fixture-safe by default.
- ComfyUI calls raise before network access unless explicitly enabled at runtime.
- No real third-party records, emails, leads, calendar events, chat messages, product photos, ComfyUI keys, generated customer assets, or paid/cloud side effects are required for tests or examples.
- Live n8n, Make, Zapier, ComfyUI, Slack, CRM, calendar, email, cloud, or account-specific actions are intentionally human-gated.

## Visual evidence

Committed proof panels live under `docs/screenshots/`:

- `01-cli-validation.png`
- `02-pattern-output.png`
- `03-architecture.png`
- `04-quality-gates.png`
- `05-case-study-link.png` — case-study proof panel

The full `api-webhook-bridge` screenshot package stays in that case-study repository; Automation Kit links to it rather than duplicating it.
