# Automation Kit Spoke Proof Architecture

Date: 2026-05-06

## Doctrine

Automation Kit is the reusable engine. The companion repositories are client-shaped proof projects that show Automation Kit applied to one workflow problem at a time.

This is intentional. The evidence should not look like seven unrelated half-frameworks. It should read as one tested automation toolkit plus a small set of focused case studies.

## Repository roles

| Layer | Role | What it proves |
|---|---|---|
| `automation-kit` | Core framework | Reusable pattern runner, deterministic fixtures, validation, CLI/API surfaces, mock adapters, low-code-to-Python translation, tests, Docker, and evidence discipline. |
| Spoke proof repos | Client-shaped case studies | Stefan can take the reusable framework and apply it to a specific business workflow without live credentials or overbuilt scaffolding. |

## Active spoke set

| Priority | Repo | Role | Promotion target |
|---|---|---|---|
| 1 | `api-webhook-bridge` | Universal API/webhook bridge case study | First flagship spoke; see `docs/case-studies/api-webhook-bridge.md`. |
| 2 | `automation-debugger` | Broken automation diagnosis and replay proof | Second complete spoke. |
| 3 | `sheets-airtable-sync` | Sheets/Airtable validation, dedupe, and sync proof | Third complete spoke. |
| 4 | `lowcode-ai-workflows` | Controlled AI steps inside auditable low-code-style workflows | Promote after first three spokes. |
| 5 | `invoice-workflow-extractor` | Document/invoice extraction and validation workflow | Backlog spoke. |
| 6 | `crm-lead-router` | GHL/HubSpot/ActiveCampaign lead routing workflow | Backlog spoke. |
| 7 | `slack-discord-ops-bot` | Ops notification and command workflow | Backlog spoke. |

## Spoke contract

A spoke repo is ready to link in external reviews only when it has all of the following:

1. Clear README positioning: "built using Automation Kit" plus the exact workflow problem.
2. Thin application layer around Automation Kit; no duplicate framework.
3. Synthetic input fixtures under `examples/input/` or an equivalent fixture path.
4. Deterministic output examples under `examples/output/` or an equivalent evidence path.
5. Tests proving the main flow and at least one failure or review path.
6. A short case-study doc explaining the workflow, boundaries, and first milestone shape.
7. A screenshot or text evidence package showing one verified run.
8. Empty `.env.example` placeholders and no live credentials.
9. No live external-service connections, cloud, payment, or delivery side effects by default.
10. A external review snippet that maps the repo to the job category.

If a spoke does not meet this contract, keep it unpublished and treat it as a scoped backlog repo, not a evidence link.

## Build rules

- Build one spoke at a time.
- Do not turn a spoke into another generic toolkit.
- Prefer thin wrappers, fixture-backed examples, and reviewer-readable outputs.
- Keep Automation Kit as the place for reusable runner logic.
- Keep spoke repos as the place for workflow-specific workflows and case-study evidence.
- Promote the first three spokes before expanding the backlog.
- Use the release gate before making any spoke public.

## Case-study mapping

| Job language | Link when ready | Proof sentence |
|---|---|---|
| API, webhook, CRM, Shopify, Stripe, Airtable, HubSpot | `api-webhook-bridge` | API/webhook bridge built on Automation Kit with validation, mapped output, audit logs, and handoff notes. |
| Zapier broken, Make scenario failing, n8n webhook not triggering, automation fix | `automation-debugger` | Fixture-backed diagnosis of malformed payloads, corrected replay, and a reviewer-readable fix report. |
| Google Sheets, Airtable, CRM rows, dashboard cleanup, CSV sync | `sheets-airtable-sync` | Row validation, dedupe, rejected-row reasons, and Airtable-ready upsert output. |
| Claude, OpenAI, AI workflow, n8n AI, Make AI | `lowcode-ai-workflows` | Controlled AI step inside an auditable workflow with deterministic fixtures and review paths. |
| Invoice, OCR, document processing, accounting export | `invoice-workflow-extractor` | Document extraction pipeline with validation, review flags, and accounting-ready output. |
| GHL, HubSpot, lead routing, follow-up automation | `crm-lead-router` | CRM lead routing with dedupe, stages, follow-up tasks, and audit trail. |
| Slack, Discord, ops alerts, internal bot | `slack-discord-ops-bot` | Token-safe ops workflow with mock delivery adapters and verified event routing. |

## Current enforcement

The core docs and spoke READMEs should point back to this doctrine. The next implementation pass should add tests or simple repo checks that keep the spoke contract visible as the projects mature.
