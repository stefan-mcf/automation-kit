# Automation Kit MCP

Automation Kit exposes a fixture-safe MCP surface for Hermes/factory profiles to inspect and run reusable automation proofs.

## Boundary

Automation Kit MCP is the runtime/proof control plane:

- discover patterns, sectors, and capabilities;
- validate registry and shipped patterns;
- run explicitly enabled fixture-safe pattern capabilities;
- return evidence metadata for proof packets.

It is not the broad external integration catalog. Use Executor MCP for typed access to third-party APIs, browser machines, local apps, and credentials-bound tools. Automation Kit keeps the reusable runtime and evidence layer.

## Naming rule

Do not put business sectors in MCP tool names.

Good:

```text
list_capabilities(sector_id="ecommerce")
run_capability(capability_id="pattern.webhook-router.default")
get_evidence_index(sector_id="api-webhook")
```

Avoid:

```text
run_ecommerce_factory
run_marketing_factory
run_api_webhook_bridge
```

Sectors are registry/routing metadata. Tool names stay stable verbs so agents do not need a new tool whenever a factory sector changes.

## Local commands

```bash
PYTHONPATH=src python -m auto_kit.cli mcp-validate
PYTHONPATH=src python -m auto_kit.cli mcp-serve
```

If installed as a package:

```bash
auto-kit mcp-validate
auto-kit mcp-serve
```

## Exposed tools

- `health`
- `list_patterns`
- `get_pattern`
- `run_pattern`
- `validate_pattern`
- `validate_all`
- `list_sectors`
- `list_capabilities`
- `get_capability`
- `run_capability`
- `validate_capability`
- `get_evidence_index`

All default runnable tools are fixture-safe and report `live_services_used=false`.

## Registry files

Canonical shipped registry data lives in:

- `src/auto_kit/registry/sectors.yaml`
- `src/auto_kit/registry/capabilities.yaml`

A repo-root mirror also exists for planning readability:

- `registry/sectors.yaml`
- `registry/capabilities.yaml`

## Hermes config snippet

Example local MCP server entry:

```yaml
mcp_servers:
  automation_kit:
    command: python
    args:
      - -m
      - auto_kit.cli
      - mcp-serve
    env:
      PYTHONPATH: <repo>/src
    cwd: <repo>
```

Use a test Hermes profile first. Do not alter an active profile's MCP config without a backup.

## Executor relationship

Executor can provide a broader external tool catalog when installed in the operator environment.

Recommended layering:

```text
Hermes factory profile
  -> Automation Kit MCP: runtime/proofs/patterns/capabilities
  -> Executor MCP: broad external APIs/tools/machines/auth catalog
```

Executor adoption is contract-driven, not a hard dependency. Automation Kit and its spokes should remain fixture-safe from a clean checkout, while also emitting enough metadata for Executor to adopt them automatically after local proof:

```text
openapi.json or documented local OpenAPI URL
executor.policy.yaml
docs/executor.md
fixture-safe smoke command
```

Reads default to allowed only for fixture-safe/local sources. Writes default to explicit operator approval. See `docs/executor-adoption.md` for the project contract and smoke sequence.

`api-webhook-bridge` starts as a registered Automation Kit capability/spoke. Promote it to its own MCP only if it becomes an independent runtime or product surface.
