# Public Readiness

Automation Kit is prepared as a public-safe project surface, but changing GitHub visibility remains a separate human-gated release decision.

## Current stance

- Public-facing tracked docs describe Automation Kit as a reusable automation pattern library.
- Private planning, marketplace-support notes, and execution plans are ignored or removed from the public tracked surface.
- Companion case studies are linked only when they have their own public-safe evidence package.
- `api-webhook-bridge` is the current public companion case study: <https://github.com/stefan-mcf/api-webhook-bridge>.

## Cleanliness checks

- Repository name and package distribution: `automation-kit`.
- Code package and CLI: `auto_kit` / `auto-kit`.
- Fixtures are synthetic.
- `.env.example` contains empty optional credential placeholders.
- Live services are disabled by default with `AUTO_KIT_USE_LIVE_SERVICES=false`.
- Local API, MCP, and Docker Compose proof use fixture-safe endpoints only.
- No real CRM records, Slack messages, emails, calendar events, product photos, ComfyUI keys, cloud secrets, account messages, or generated customer assets are committed.

## Before any public visibility change

Run and record:

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
PYTHONPATH=src python -m mypy src
PYTHONPATH=src python -m auto_kit.cli validate-all
PYTHONPATH=src python -m auto_kit.cli mcp-validate
docker build -t automation-kit .
docker run --rm automation-kit validate-all
docker compose config
git grep -n -I -E 'AKIA|sk-|ghp_|github_pat_|PRIVATE KEY|password[[:space:]]*[:=]|api[_-]?key[[:space:]]*[:=]|secret[[:space:]]*[:=]|token[[:space:]]*[:=]' -- $(git ls-files)
```

If prior internal planning history should not be exposed, publish through a clean one-commit export rather than changing this repository visibility in place.

## Remaining human approval gates

Stop before any of these actions:

- make this repository public;
- publish a release or git tag;
- connect live external-service credentials;
- create cloud resources;
- use real customer data;
- publish screenshots containing account context.
