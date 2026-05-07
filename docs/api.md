# Automation Kit Local API

Automation Kit includes a fixture-safe FastAPI wrapper for local proof runs. It is designed to make API/webhook work easier to show in external reviews without connecting live external-service credentials.

## Safety boundary

- Local only by default.
- Synthetic fixtures only.
- `fixture_safe` is always `true` for shipped API responses.
- `live_services_used` is always `false` for shipped API responses.
- No Shopify, Stripe, HubSpot, GHL, Airtable, Slack, Google, Zapier, Make, n8n, or OpenAI credentials are required.

## Run locally

```bash
PYTHONPATH=src uvicorn auto_kit.api:app --host 127.0.0.1 --port 8000
```

OpenAPI docs are available locally at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | API health and safety metadata. |
| `GET` | `/patterns` | List discovered patterns and whether API runs are enabled. |
| `GET` | `/patterns/{pattern_name}` | Inspect one pattern's workflow metadata. |
| `POST` | `/patterns/{pattern_name}/run` | Run a supported pattern against local fixtures. |

## Initial API-run patterns

- `webhook-router`
- `csv-to-crm`
- `lead-enrichment`

Other patterns are listed for discovery but return a clean `400` response if run through the API before they are enabled.

## Request shape

```json
{
  "fixture_name": "default",
  "input": {
    "type": "order.created",
    "order_id": "ORD-123",
    "amount": 199.0
  }
}
```

The `input` field is accepted for API-shaped proof requests. Current shipped pattern implementations still run deterministic repository fixtures so local behavior is reproducible.

## Response shape

```json
{
  "pattern_name": "webhook-router",
  "status": "passed",
  "output": {},
  "validation_summary": {
    "passed": true,
    "fixture_name": "default",
    "errors": [],
    "input_received": true
  },
  "warnings": [],
  "fixture_safe": true,
  "live_services_used": false
}
```

See:

- `examples/api-requests/webhook-router-request.json`
- `examples/api-requests/csv-to-crm-request.json`
- `examples/api-responses/webhook-router-response.json`
- `examples/api-responses/csv-to-crm-response.json`

## Smoke commands

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/patterns
curl -fsS -X POST http://127.0.0.1:8000/patterns/webhook-router/run   -H 'content-type: application/json'   --data @examples/api-requests/webhook-router-request.json
```
