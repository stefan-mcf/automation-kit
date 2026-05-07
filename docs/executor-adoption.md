# Executor adoption contract

Automation Kit and Workflow Automation Portfolio spokes should be easy for Executor to adopt, but they must not depend on a live Executor daemon to be useful. The project should expose a small contract that lets an operator or ARC smoke command verify and import it later.

## Boundary

Executor is the broad typed integration catalog. Automation Kit remains the fixture-safe runtime/proof/capability layer.

```text
Automation Kit project/spoke
  emits OpenAPI + policy + fixtures
Executor
  catalogs typed tools and policy-gated calls
Hermes/factory profile
  reasons, chooses tools, verifies results
Agent Runtime Control
  logs readiness/evidence/lessons
```

## Required project artifacts

Future projects should add these files when they expose an HTTP/MCP/API surface:

```text
openapi.json                         # committed only if static; otherwise documented URL
executor.policy.yaml                 # policy below
docs/executor.md                     # source namespace, base URL, smoke command, limitations
tests/test_executor_contract.py      # or equivalent fixture-safe proof
```

For dynamic FastAPI surfaces, documenting `http://127.0.0.1:<port>/openapi.json` is enough if the local server command and health check are reproducible.

## Policy template

```yaml
schema: workflow-proof-executor-policy/v1
namespace: automation_kit
source_kind: openapi
spec: http://127.0.0.1:8000/openapi.json
base_url: http://127.0.0.1:8000
fixture_safe: true
live_services_used: false
reads:
  default: allow
writes:
  default: require_operator_approval
auth:
  required: false
  secret_locations: []
smoke:
  start_command: PYTHONPATH=src uvicorn auto_kit.api:app --host 127.0.0.1 --port 8000
  health_url: http://127.0.0.1:8000/health
  read_only_expectation: pattern_count >= 1
```

## Adoption sequence

1. Run the project tests.
2. Start the local fixture-safe API/MCP surface.
3. Verify `/health` reports fixture-safe status and no live services.
4. Verify `/openapi.json` is reachable or the static `openapi.json` exists.
5. Import/register with Executor only after the fixture checks pass.
6. Run ARC readiness:

```bash
arc executor-smoke --required-sources automation_kit --check-hermes --log-event
```

7. For live read smoke, use a harmless read-only tool only. Writes remain approval-gated.

## Known caveat

Use Executor through Hermes MCP for agent work. A local 2026-05-07 check reproduced a direct shell `executor call ...` failure (`e.rawPathParts.at is not a function`) while the Hermes MCP `execute` path succeeded. Treat shell direct calls as diagnostics until re-smoked.
