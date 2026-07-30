# Case Study: API Webhook Bridge

[`api-webhook-bridge`](https://github.com/stefan-mcf/api-webhook-bridge) is a public companion case study built on Automation Kit. It applies the reusable webhook-routing and fixture-safety patterns to a concrete FastAPI bridge with mapped outputs, idempotency, audit logs, dead-letter handling, OpenAPI docs, sandbox responses, and screenshots.

## Engineering controls

- HubSpot-like contact -> Airtable-style upsert.
- Shopify-like order -> Slack-style ops alert plus CRM note.
- Stripe-like payment -> payment audit record plus Slack-style notification with duplicate delivery proof.
- Visible source-to-destination mapping configs.
- FastAPI/OpenAPI inspection surface.
- JSONL audit/dead-letter proof.
- Public-safe screenshot and sandbox evidence package.

## Automation Kit relationship

Automation Kit remains the reusable core: pattern contracts, fixture discipline, mock-first boundaries, and verification standards. `api-webhook-bridge` stays as the thin applied spoke: it uses those standards to show one specific API/webhook workflow end to end without turning into a second framework.

## Public boundary

The case study is fixture-safe and synthetic. It does not require live external-service credentials, cloud resources, payment operations, real customer records, or external delivery side effects.

## Links

- Public repository: <https://github.com/stefan-mcf/api-webhook-bridge>
- Case-study docs in that repository: <https://github.com/stefan-mcf/api-webhook-bridge/tree/main/docs>
- Screenshots in that repository: <https://github.com/stefan-mcf/api-webhook-bridge/tree/main/docs/screenshots>
