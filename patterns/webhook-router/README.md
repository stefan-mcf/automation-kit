# Pattern 5: Webhook Router

Route incoming webhook payloads by event type to type-specific handlers.
Unrouteable payloads (unknown type, missing type field, missing required fields)
are directed to a dead-letter queue for later inspection and replay.

## What It Does

1. Accepts a list of webhook payload dicts, each with a `type` field
2. Routes known event types to dedicated handlers:
   - `order.created` → **order_handler**
   - `lead.captured` → **lead_handler**
   - `ticket.created` → **support_handler**
3. Validates minimal required fields per event type (signature placeholder validation)
4. Dead-letters unrouteable payloads with a descriptive reason:
   - `unknown_event_type` — no handler registered for the given type
   - `missing_event_type` — payload has no `type` field at all
   - `missing_required_fields: ...` — payload missing fields required by this handler
5. Returns a summary with routed events, dead-letter queue, and total count

## Input Format (fixtures/input.json)

```json
[
  {
    "type": "order.created",
    "order_id": "ORD-123",
    "amount": 99.95
  },
  {
    "type": "lead.captured",
    "name": "Alice",
    "email": "alice@example.com"
  },
  {
    "type": "ticket.created",
    "ticket_id": "TK-456",
    "priority": "high"
  },
  {
    "type": "unknown.action",
    "foo": "bar"
  },
  {
    "foo": "bar"
  }
]
```

## Output Format

```json
{
  "routed_events": [
    {
      "event_id": "ORD-123",
      "event_type": "order.created",
      "route": "order_handler",
      "handler": "order_handler",
      "handled": true,
      "reason": null
    }
  ],
  "dead_letter": [
    {
      "event_id": "evt-001",
      "event_type": "unknown.action",
      "route": "dead-letter",
      "handler": null,
      "handled": false,
      "reason": "unknown_event_type"
    }
  ],
  "total": 5
}
```

## Idempotency, Retries & Payload Logging

### Idempotency

Each event is processed exactly once per `route()` call. The `event_id` in
the output can be used by downstream consumers for idempotent processing:

- **Deduplication key**: Use `event_id` (e.g., `"ORD-123"`) as a uniqueness
  constraint in your database to prevent double-processing.
- **At-least-once semantics**: If a downstream handler fails and the event is
  retried, the same `event_id` allows the consumer to safely skip already-
  applied changes.

### Retries

Dead-lettered events are **not automatically retried** by this pattern. Instead,
they are collected in the `dead_letter` list for manual or scheduled replay:

- **Replay mechanism**: A separate process can inspect `dead_letter` entries,
  fix the root cause (e.g., register a new handler for an unknown type), and
  re-route them via `WebhookRouter.route()`.
- **Backoff strategy**: If implementing an automatic retry loop, use exponential
  backoff (e.g., 1s, 2s, 4s, 8s) with a maximum retry count (e.g., 3 retries)
  to avoid overwhelming downstream systems.
- **Dead-letter persistence**: In production, dead-letter entries should be
  persisted to a durable queue (SQS, RabbitMQ, Redis list) or a database table
  for observability and replay.

### Payload Logging

Consider the following when logging webhook payloads:

- **PII in payloads**: Webhook payloads may contain personally identifiable
  information (names, email addresses). Never log raw payloads to plain-text
  logs or error aggregators without redacting sensitive fields.
- **Structured logging**: Log the `event_id`, `event_type`, and `route` for
  observability. The full payload should only be stored in a secure, access-
  controlled data store (not in application logs).
- **Payload retention**: Define a retention policy for raw webhook payloads.
  GDPR and similar regulations may require deletion after a specific period.
- **Audit trail**: The `dead_letter` list provides an audit trail of all events
  that could not be routed, including the `reason` for each failure.

## Missing Data Handling

| Scenario                               | Behavior                                                |
|----------------------------------------|---------------------------------------------------------|
| Known event type, all fields present   | Routed to handler, `handled: true`                      |
| Known event type, missing required field | Dead-lettered with `reason: "missing_required_fields: ..."` |
| Unknown event type                     | Dead-lettered with `reason: "unknown_event_type"`       |
| No `type` field at all                 | Dead-lettered with `reason: "missing_event_type"`       |
| Extra unknown fields                   | Ignored by handler, payload still processed normally     |

## Files

```
patterns/webhook-router/
  fixtures/
    input.json              — Sample webhook payloads
    expected_output.json    — Expected routed output
  python/
    main.py                 — WebhookRouter class + run() orchestrator
    test_main.py            — pytest test suite
  workflow.json             — n8n-compatible workflow definition
  README.md                 — This file
```
