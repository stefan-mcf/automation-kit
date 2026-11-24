# Automation Kit companion architecture

Automation Kit supplies the reusable pattern runner, workflow contracts, synthetic fixtures, mock adapters and validation tools. Its CLI, API and MCP interfaces expose selected capabilities. Each companion project owns the rules, reports and examples for its workflow.

## Companion projects

| Project | Role |
| --- | --- |
| [API Webhook Bridge](case-studies/api-webhook-bridge.md) | Uses a pinned Automation Kit revision for contract loading and mock clients. The bridge handles validation, field mapping, idempotency and audit records. |
| [Automation Debugger](case-studies/automation-debugger.md) | Runs independently and uses shared conventions for failure diagnosis, controlled local replay and reviewable reports. |
| [Sheets Airtable Sync](https://github.com/stefan-mcf/sheets-airtable-sync) | Validates and deduplicates rows, then previews Airtable upserts. Its local workflow runs independently. |
| [Review Router](https://github.com/stefan-mcf/review-router) | Routes supplied classifier metadata through deterministic policy and human-review rules. |
| [Invoice Router](https://github.com/stefan-mcf/invoice-router) | Validates invoice inputs and produces review records and accounting export previews. Its local workflow runs independently. |

## Validation

- Document the implemented workflow, the Automation Kit dependency or shared conventions, and the operating limits.
- Include synthetic inputs, deterministic expected outputs, and tests for the main flow and a failure or review path.
- Provide a reproducible command and one inspectable run result.
- Use mock destinations by default and keep live credentials outside the examples.
