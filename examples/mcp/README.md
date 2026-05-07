# Automation Kit MCP example

Run the MCP server locally from the repo root:

```bash
PYTHONPATH=src python -m auto_kit.cli mcp-validate
PYTHONPATH=src python -m auto_kit.cli mcp-serve
```

Hermes test-profile config example:

```yaml
mcp_servers:
  automation_kit:
    command: python
    args: ["-m", "auto_kit.cli", "mcp-serve"]
    env:
      PYTHONPATH: <repo>/src
    cwd: <repo>
```

Smoke target after configuration:

1. discover tools;
2. call `health`;
3. call `list_patterns`;
4. call `run_capability` with `capability_id="pattern.webhook-router.default"`.

Expected safety metadata:

```json
{
  "fixture_safe": true,
  "live_services_used": false
}
```
