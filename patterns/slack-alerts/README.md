# Pattern 6: Slack/Teams Alert Pipeline

Deduplicate monitor events, route them by severity to the appropriate Slack
channel, and send formatted alert messages via `MockSlackClient`.

- **Critical** alerts → `#priority` channel
- **Warning / Info** alerts → `#general` channel

---

## How it works

1. **Monitor Trigger** polls a monitoring system (or reads from `input.json`
   in test/fixture mode) and emits raw events.
2. **Filter** deduplicates events by `(event_type, severity)` — only the
   first occurrence of each pair is allowed through.
3. **Format Message** builds a human-readable alert string and determines
   the target channel based on severity.
4. **Send Slack Mock** delivers the formatted alert via `MockSlackClient`,
   which records the message for later inspection.

---

## Files

```
patterns/slack-alerts/
├── fixtures/
│   ├── input.json              # Sample monitor events (critical, warning, info, duplicate)
│   └── expected_output.json    # Expected pipeline output
├── python/
│   ├── main.py                 # AlertPipeline class + run() entry point
│   └── test_main.py            # Unit tests + integration test
├── workflow.json               # n8n-compatible workflow definition
└── README.md                   # This file
```

---

## Running

```bash
# Activate venv
source .venv/bin/activate

# Run the pattern's tests
python -m pytest patterns/slack-alerts/python/test_main.py -v

# Run the pattern directly
python -c "
import json
from patterns.slack_alerts.python.main import run
result = run()
print(json.dumps(result, indent=2))
"
```

---

## Pitfalls & production considerations

### Alert fatigue

- **Duplicate suppression is batch-scoped.** The current implementation only
  deduplicates within a single `process_events()` call. In production, you
  need a persistent dedup cache (e.g., Redis with a TTL of 5–15 minutes) to
  prevent the same alert from firing across multiple polling cycles.
- **Severity-based routing can be too coarse.** A high volume of warning-
  level alerts from a noisy component can still flood `#general`. Consider
  adding per-component rate limits or a separate "low-priority" channel for
  non-critical alerts.
- **Throttling and batching.** When many events fire at once (e.g., after a
  deployment rolling restart), send a single aggregated summary instead of N
  individual messages. The current pipeline sends one message per alert,
  which is appropriate for low volume but can overwhelm chat channels during
  incidents.

### Escalation pitfalls

- **No escalation logic.** This pipeline routes by severity but does not
  implement escalation: if a critical alert remains unacknowledged for N
  minutes, it should page on-call engineers via PagerDuty/Opsgenie.
- **Silent failures.** If `MockSlackClient` is replaced with a real webhook,
  ensure there is a retry-with-backoff mechanism. A transient network glitch
  could cause a critical alert to be lost silently.
- **Acknowledge tracking.** In a real deployment, alerts should support an
  "acknowledged" state so that duplicate alerts from the same root cause
  are not continuously re-sent. This pipeline treats each batch
  independently and has no memory of previous acknowledgements.

### Deduplication scope

- The current dedup key is `(event_type, severity)`. This is intentionally
  broad: it prevents the exact same class of alert from appearing multiple
  times in one batch. However, it can also suppress genuinely distinct
  occurrences (e.g., two different servers reporting `disk_full` at the
  same `warning` severity). For production, consider widening the dedup key
  to include a resource identifier (hostname, service name) so that
  distinct affected resources are not collapsed.

### Channel routing

- The severity-to-channel mapping is hardcoded. In production, make it
  configurable via environment variables or a settings file so that teams
  can define their own channel structure (e.g., `critical` → `#oncall`).
- Consider a "digest" mode for info alerts: instead of sending one message
  per info event, batch them into a periodic summary (every 5 minutes) to
  reduce noise.

### Testing with MockSlackClient

- `MockSlackClient` stores messages in memory. For integration tests that
  span multiple pipeline runs, remember to reset the client's `messages`
  list between runs, or create a fresh `AlertPipeline` instance (which
  creates a fresh `MockSlackClient`).
- If you need to assert that a specific alert was *not* sent, check that
  `MockSlackClient.messages` does not contain a matching record. The
  `suppressed` list in the pipeline output provides this directly.
