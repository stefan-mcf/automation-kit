# Pattern Index

Automation Kit contains seven local-safe automation patterns. Each pattern pairs a declarative `workflow.json` with a tested Python implementation, synthetic fixtures, and pattern-specific documentation.

| Pattern | Inputs | Outputs | Low-code value | Python value | External automation fit | Live services required |
|---------|--------|---------|----------------|--------------|----------------|------------------------|
| `calendar-booking` | booking request JSON | availability decision, event record, confirmation email | Models webhook → calendar → email flow with timezone checks | Shows deterministic conflict handling and alternative-slot suggestions | calendar automation, Calendly/Google Calendar handoffs | No |
| `csv-to-crm` | lead CSV | deduplicated CRM upsert summary | Classic Zapier/Make CSV import pattern with idempotent upserts | Testable parsing, normalization, and mock CRM boundary | CRM cleanup, list import, lead ops | No |
| `email-parser` | raw email JSON | intent classification and routed queue record | Turns inbox triggers into structured support/sales/billing routes | Transparent keyword classifier and spam/manual-review branches | helpdesk triage, lead routing, mailbox ops | No |
| `lead-enrichment` | lead JSON | enriched firmographic lead records | Matches low-code enrichment steps with fallback for unknown domains | Deterministic mock provider and manual-research flags | B2B prospect enrichment, CRM hygiene | No |
| `product-creative-pack` | synthetic product brief JSON | prompt pack, ComfyUI manifest, mock asset records, review packet | Maps ecommerce creative ops into prompt, asset, and review stages | Isolates ComfyUI behind a non-executing manifest and disabled client | product listing creative, ad asset prep, human review | No by default; live ComfyUI is gated |
| `slack-alerts` | event JSON | deduplicated channel messages via mock Slack client | Represents alert routing from monitoring/event triggers | Tests formatting, severity routes, and deduplication | ops alerts, incident notifications, team reporting | No |
| `webhook-router` | webhook JSON | typed handler response or dead-letter queue item | Represents a central webhook fan-out/router pattern | Explicit unknown-type and missing-field handling | third-party webhook integrations, event routing | No |

## Verification contract

Every pattern must keep this artifact set:

- `workflow.json` for low-code-style structure and review.
- `README.md` explaining the workflow boundary.
- `fixtures/expected_output.json` plus at least one input fixture.
- `python/main.py` with a deterministic `run()` entrypoint.
- `python/test_*.py` with pattern-level regression tests.

The repository enforces this with `tests/test_all_patterns.py` and the CLI matrix in `tests/test_cli.py`.


## Case-study links

Use case-study docs when a reviewer needs one specific example instead of the whole framework:

- `docs/case-studies/api-webhook-bridge.md` for API, webhook, CRM-style, ecommerce-style, payment-style, Airtable-style, or Slack-style integration workflows.

Case studies stay fixture-safe by default and do not authorize live credentials or external delivery.

## Companion proof repositories

Automation Kit is the reusable pattern layer. Companion repositories are promoted only when they show a concrete workflow using this toolkit. Keep reusable runner logic here; keep workflow-shaped fixtures, outputs, case studies, and evidence notes in the spoke repo.

See `docs/proof-spoke-architecture.md` for the spoke readiness contract and promotion order.
