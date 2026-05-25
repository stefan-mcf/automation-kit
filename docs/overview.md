# Automation Kit Overview

Automation Kit is a reusable automation pattern library. It packages common workflow shapes as low-code-style contracts, deterministic fixtures, and tested Python equivalents.

## Core idea

Each pattern answers four questions:

1. What workflow is being modeled?
2. What synthetic input proves the flow?
3. What deterministic output should be produced?
4. When should this stay in low-code vs move into Python?

## Included surfaces

- CLI: discover, validate, and run patterns.
- Pattern contracts: `workflow.json` files for low-code-style review.
- Python equivalents: deterministic `run()` implementations.
- Fixtures: synthetic inputs and expected outputs.
- Local API: fixture-safe FastAPI wrapper.
- MCP: fixture-safe agent/tool control surface.
- Docker: local container runtime for validation/API use.

## Pattern lifecycle

1. Discover with `auto-kit list-patterns`.
2. Validate with `auto-kit validate <path>`.
3. Run with `auto-kit run <path>`.
4. Test with `python -m pytest -q`.
5. Package or promote into a companion case-study repo when the workflow becomes buyer/client-shaped.

## Safety model

No shipped command needs real CRM records, Slack channels, inboxes, calendars, product photos, ComfyUI servers, paid APIs, or credentials.

## How mock clients work

All mock clients live in `src/auto_kit/mock_clients.py` and use a shared deterministic seed (`AUTO_KIT_MOCK_SEED=42`). They return synthetic but realistic data — no network calls, no credentials, no side effects.

| Client | Purpose |
|--------|---------|
| `MockCRMClient` | Upsert and query CRM records |
| `MockEmailClient` | Send email previews |
| `MockSlackClient` | Send formatted channel messages |
| `MockCalendarClient` | Check availability and book slots |
| `MockLeadDatabase` | Enrich company data by domain |

## File layout

```text
automation-kit/
  Dockerfile
  pyproject.toml
  .env.example
  .gitignore
  .dockerignore
  README.md
  src/auto_kit/
    __init__.py
    models.py
    workflow_schema.py
    fixtures.py
    pattern_runner.py
    mock_clients.py
    cli.py
    api.py
    mcp_server.py
    capability_registry.py
    comfyui_client.py
    registry/
      capabilities.yaml
      sectors.yaml
  patterns/
    calendar-booking/    fixtures/ python/ workflow.json README.md
    csv-to-crm/          fixtures/ python/ workflow.json README.md
    email-parser/        fixtures/ python/ workflow.json README.md
    lead-enrichment/     fixtures/ python/ workflow.json README.md
    product-creative-pack/ fixtures/ python/ workflow.json README.md
    slack-alerts/        fixtures/ python/ workflow.json README.md
    webhook-router/      fixtures/ python/ workflow.json README.md
  tests/
    test_all_patterns.py
    test_cli.py
    test_api.py
    test_mcp_server.py
    test_pattern_runner.py
    test_workflow_schema.py
    test_comfyui_client.py
    test_capability_registry.py
    test_executor_adoption.py
    test_proof_package.py
  docs/
    quickstart.md
    pattern-index.md
    architecture.md
    api.md
    mcp.md
    deployment.md
    overview.md
    proof-spoke-architecture.md
    case-studies/
      api-webhook-bridge.md
      automation-debugger.md
    screenshots/
```
