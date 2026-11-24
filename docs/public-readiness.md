# Public Readiness

Automation Kit is public at <https://github.com/stefan-mcf/automation-kit>.

## Public package

[Companion architecture](proof-spoke-architecture.md) describes the reference projects and shared conventions.

## Cleanliness checks

- Repository name and package distribution: `automation-kit`.
- Code package and CLI: `auto_kit` / `auto-kit`.
- Fixtures are synthetic.
- `.env.example` contains empty optional credential placeholders.
- Live services are disabled by default with `AUTO_KIT_USE_LIVE_SERVICES=false`.
- Local API, MCP, and Docker Compose proof use fixture-safe endpoints only.

## Current verification bundle

Run and record before release tags or major public positioning changes:

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
PYTHONPATH=src python -m mypy src
PYTHONPATH=src python -m auto_kit.cli validate-all
PYTHONPATH=src python -m auto_kit.cli mcp-validate
docker build -t automation-kit .
docker run --rm automation-kit validate-all
docker compose config
```

## Release review

Review releases, live credentials, cloud resources, real customer data and account-context screenshots before enabling or publishing them.
