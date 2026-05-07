# Case Study: Automation Debugger

[`automation-debugger`](https://github.com/stefan-mcf/automation-debugger) is a public companion case study built on Automation Kit conventions. It applies fixture-safe automation patterns to broken Zapier, Make, n8n, webhook, and API-bridge-style events: normalize the payload, classify the failure, decide whether replay is safe, and generate reviewer-readable fix evidence.

## What it proves

- Malformed-date diagnosis with corrected local replay.
- Missing required field, duplicate event, wrong destination, unknown event type, invalid signature, retry-loop, and rate-limit refusal paths.
- Zapier, Make, and n8n export normalization into one inspected evidence shape.
- Local API endpoints for diagnose, replay, and report flows.
- Generated JSON, Markdown, and HTML fix reports from synthetic fixtures.
- Public-safe screenshot and command evidence package.

## Automation Kit relationship

Automation Kit remains the reusable core: fixture discipline, mock-first boundaries, pattern contracts, and verification standards. `automation-debugger` stays as the thin applied spoke: it shows the repair path for failed automations without becoming a second framework.

## Public boundary

The case study is fixture-safe and synthetic. It does not require live external-service credentials, cloud resources, real webhook replay, customer records, account exports, or external delivery side effects.

## Links

- Public repository: <https://github.com/stefan-mcf/automation-debugger>
- Case-study docs in that repository: <https://github.com/stefan-mcf/automation-debugger/tree/main/docs>
- Screenshots in that repository: <https://github.com/stefan-mcf/automation-debugger/tree/main/docs/screenshots>
