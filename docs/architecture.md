# Architecture

Automation Kit is a local-first automation pattern library for modeling workflow contracts, deterministic fixtures, Python equivalents, and safe runtime surfaces in one place.

## System shape

```text
patterns/<name>/
  workflow.json          low-code-style workflow contract
  README.md              pattern explanation and fit
  fixtures/              synthetic inputs and expected outputs
  python/main.py         deterministic Python equivalent
  python/test_*.py       pattern-level regression tests

src/auto_kit/
  cli.py                 auto-kit terminal commands
  pattern_runner.py      discovery, validation, and output comparison
  workflow_schema.py     Pydantic workflow JSON validation
  fixtures.py            JSON, JSONL, and CSV fixture helpers
  mock_clients.py        deterministic third-party-style adapters
  comfyui_client.py      disabled-by-default ComfyUI boundary
  api.py                 FastAPI local API
  mcp_server.py          MCP stdio server
  capability_registry.py sector/capability registry loading
  registry/              packaged registry data
```

## Why pair low-code JSON with Python

Low-code tools are strongest when the workflow is easy to inspect, hand off, and adapt inside tools such as n8n, Make, or Zapier. Python is strongest when the workflow needs deterministic tests, data normalization, edge-case handling, or reusable adapters. Automation Kit keeps both views side by side so a reviewer can see the automation decision, not just a script.

## Runtime boundary

The default path is fully local and deterministic:

1. `auto-kit list-patterns` discovers pattern directories.
2. `auto-kit validate <path>` checks required files and validates `workflow.json`.
3. `auto-kit run <path>` executes `python/main.py` and compares output with `fixtures/expected_output.json`.
4. `auto-kit validate-all` checks the full pattern set.

No command needs real CRM records, Slack channels, inboxes, calendars, product photos, ComfyUI servers, paid APIs, or credentials.

## ComfyUI isolation

`product-creative-pack` includes a ComfyUI job manifest and prompt pack, but the normal run creates deterministic mock asset records and a human review packet. The shared `auto_kit.comfyui_client.ComfyUIClient` raises before any network call unless `AUTO_KIT_USE_LIVE_SERVICES=true` and `COMFYUI_BASE_URL` are explicitly supplied at runtime.

This gives reviewers concrete evidence for image-generation workflow design without silently generating assets, spending cloud credits, or publishing unreviewed outputs.

## Verification gates

The repository is considered healthy when these commands pass from a clean checkout:

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src
PYTHONPATH=src python -m auto_kit.cli validate-all
docker build -t automation-kit:local .
docker run --rm automation-kit:local validate-all
```
