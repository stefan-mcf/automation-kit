     1|# Automation Kit Companion Case-Study Architecture
     2|
     3|Date: 2026-05-06
     4|
     5|## Doctrine
     6|
     7|Automation Kit is the reusable engine. The companion repositories are client-shaped case-study projects that show Automation Kit applied to one workflow problem at a time.
     8|
     9|This is intentional. The evidence should not look like seven unrelated half-frameworks. It should read as one tested automation toolkit plus a small set of focused case studies.
    10|
    11|## Repository roles
    12|
    13|| Layer | Role | What it proves |
    14||---|---|---|
    15|| `automation-kit` | Core framework | Reusable pattern runner, deterministic fixtures, validation, CLI/API surfaces, mock adapters, low-code-to-Python translation, tests, Docker, and evidence discipline. |
    16|| Companion case-study repos | Client-shaped case studies | Stefan can take the reusable framework and apply it to a specific business workflow without live credentials or overbuilt scaffolding. |
    17|
    18|## Active spoke set
    19|
    20|| Priority | Repo | Role | Promotion target |
    21||---|---|---|---|
    22|| 1 | `api-webhook-bridge` | Universal API/webhook bridge case study | First flagship spoke; see `docs/case-studies/api-webhook-bridge.md`. |
    23|| 2 | `automation-debugger` | Broken automation diagnosis and replay proof | Second flagship spoke; see `docs/case-studies/automation-debugger.md`. |
    24|| 3 | `sheets-airtable-sync` | Sheets/Airtable validation, dedupe, and sync proof | Third complete spoke. |
    25|| 4 | `review-router` | Controlled AI steps inside auditable low-code-style workflows | Promote after first three spokes. |
    26|| 5 | `invoice-router` | Document/invoice extraction and validation workflow | Backlog spoke. |
    27|| 6 | `crm-lead-router` | GHL/HubSpot/ActiveCampaign lead routing workflow | Backlog spoke. |
    28|| 7 | `slack-discord-ops-bot` | Ops notification and command workflow | Backlog spoke. |
    29|
    30|## Spoke contract
    31|
    32|A spoke repo is ready to link in external reviews only when it has all of the following:
    33|
    34|1. Clear README positioning: "built using Automation Kit" plus the exact workflow problem.
    35|2. Thin application layer around Automation Kit; no duplicate framework.
    36|3. Synthetic input fixtures under `examples/input/` or an equivalent fixture path.
    37|4. Deterministic output examples under `examples/output/` or an equivalent evidence path.
    38|5. Tests proving the main flow and at least one failure or review path.
    39|6. A short case-study doc explaining the workflow, boundaries, and first milestone shape.
    40|7. A screenshot or text evidence package showing one verified run.
    41|8. Empty `.env.example` placeholders and no live credentials.
    42|9. No live external-service connections, cloud, payment, or delivery side effects by default.
    43|10. A external review snippet that maps the repo to the job category.
    44|
    45|If a spoke does not meet this contract, keep it unpublished and treat it as a scoped backlog repo, not a evidence link.
    46|
    47|## Build rules
    48|
    49|- Build one spoke at a time.
    50|- Do not turn a spoke into another generic toolkit.
    51|- Prefer thin wrappers, fixture-backed examples, and reviewer-readable outputs.
    52|- Keep Automation Kit as the place for reusable runner logic.
    53|- Keep spoke repos as the place for workflow-specific workflows and case-study evidence.
    54|- Promote the first three spokes before expanding the backlog.
    55|- Use the release gate before making any spoke public.
    56|
    57|## Case-study mapping
    58|
    59|| Job language | Link when ready | Proof sentence |
    60||---|---|---|
    61|| API, webhook, CRM, Shopify, Stripe, Airtable, HubSpot | `api-webhook-bridge` | API/webhook bridge built on Automation Kit with validation, mapped output, audit logs, and handoff notes. |
    62|| Zapier broken, Make scenario failing, n8n webhook not triggering, automation fix | `automation-debugger` | Fixture-backed diagnosis of malformed payloads, corrected replay, and a reviewer-readable fix report. |
    63|| Google Sheets, Airtable, CRM rows, dashboard cleanup, CSV sync | `sheets-airtable-sync` | Row validation, dedupe, rejected-row reasons, and Airtable-ready upsert output. |
    64|| Claude, OpenAI, AI workflow, n8n AI, Make AI | `review-router` | Controlled AI step inside an auditable workflow with deterministic fixtures and review paths. |
    65|| Invoice, OCR, document processing, accounting export | `invoice-router` | Document extraction pipeline with validation, review flags, and accounting-ready output. |
    66|| GHL, HubSpot, lead routing, follow-up automation | `crm-lead-router` | CRM lead routing with dedupe, stages, follow-up tasks, and audit trail. |
    67|| Slack, Discord, ops alerts, internal bot | `slack-discord-ops-bot` | Token-safe ops workflow with mock delivery adapters and verified event routing. |
    68|
    69|## Current enforcement
    70|
    71|The core docs and spoke READMEs should point back to this doctrine. The next implementation pass should add tests or simple repo checks that keep the spoke contract visible as the projects mature.
    72|