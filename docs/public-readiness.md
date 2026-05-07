     1|# Public Readiness
     2|
     3|Automation Kit is public at <https://github.com/stefan-mcf/automation-kit>.
     4|
     5|## Current stance
     6|
     7|- GitHub visibility: public.
     8|- Public-facing tracked docs describe Automation Kit as a reusable automation pattern library.
     9|- Private planning, marketplace-support notes, and execution plans are ignored or removed from the public tracked surface.
    10|- Public companion case studies currently linked from the Automation Factory set:
    11|  - `api-webhook-bridge`: <https://github.com/stefan-mcf/api-webhook-bridge>
    12|  - `automation-debugger`: <https://github.com/stefan-mcf/automation-debugger>
    13|  - `sheets-airtable-sync`: <https://github.com/stefan-mcf/sheets-airtable-sync>
    14|- The next build sector is `review-router`, after first-set public docs/CI/regression are reconciled.
    15|
    16|## Cleanliness checks
    17|
    18|- Repository name and package distribution: `automation-kit`.
    19|- Code package and CLI: `auto_kit` / `auto-kit`.
    20|- Fixtures are synthetic.
    21|- `.env.example` contains empty optional credential placeholders.
    22|- Live services are disabled by default with `AUTO_KIT_USE_LIVE_SERVICES=false`.
    23|- Local API, MCP, and Docker Compose proof use fixture-safe endpoints only.
    24|- No real CRM records, Slack messages, emails, calendar events, product photos, ComfyUI keys, cloud secrets, account messages, or generated customer assets are committed.
    25|
    26|## Current verification bundle
    27|
    28|Run and record before release tags or major public positioning changes:
    29|
    30|```bash
    31|PYTHONPATH=src python -m pytest -q
    32|PYTHONPATH=src python -m ruff check .
    33|PYTHONPATH=src python -m mypy src
    34|PYTHONPATH=src python -m auto_kit.cli validate-all
    35|PYTHONPATH=src python -m auto_kit.cli mcp-validate
    36|docker build -t automation-kit .
    37|docker run --rm automation-kit validate-all
    38|docker compose config
    39|git grep -n -I -E 'AKIA|sk-|ghp_|github_pat_|PRIVATE KEY|password[[:space:]]*[:=]|api[_-]?key[[:space:]]*[:=]|secret[[:space:]]*[:=]|token[[:space:]]*[:=]' -- $(git ls-files) || true
    40|```
    41|
    42|## Remaining human approval gates
    43|
    44|Stop before any of these actions:
    45|
    46|- publish a release or git tag;
    47|- connect live external-service credentials;
    48|- create cloud resources;
    49|- use real customer data;
    50|- publish screenshots containing account context;
    51|- send external/client marketplace messages.
    52|