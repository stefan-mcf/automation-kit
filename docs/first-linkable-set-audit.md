# First Linkable Set Audit

Generated: 2026-05-07 UTC

## Verdict

The Automation Factory first public case-study set is live and ready for final CI/documentation reconciliation before the next sector build.

The public set is:

| Repo | GitHub visibility | Role | Current status |
|---|---|---|---|
| `automation-kit` | Public | Core runtime: CLI, API/OpenAPI, MCP, Docker, fixture-safe patterns | Public and CI-backed. |
| `api-webhook-bridge` | Public | Universal API/webhook bridge case study | Public; CI workflow added in this reconciliation tranche. |
| `automation-debugger` | Public | Broken automation diagnosis/replay case study | Public; CI workflow added in this reconciliation tranche. |
| `sheets-airtable-sync` | Public | Sheets/Airtable validation, dedupe, mock upsert case study | Public and CI-backed. |

## Roadmap reconciliation

The older checkpoints that described the first set as private are superseded by live GitHub state. The build order now reads:

1. `automation-kit` core runtime — public baseline exists.
2. `automation-debugger` — public baseline exists.
3. `api-webhook-bridge` — public baseline exists.
4. `sheets-airtable-sync` — public baseline exists.
5. First-set evidence/control-surface audit — this document plus per-repo CI/readiness updates.
6. Next build sector — `lowcode-ai-workflows`.

## Boundaries still in force

Public repository visibility is no longer the gate for the first set. The remaining gates are external side effects:

- no live SaaS credentials;
- no cloud resources;
- no release tags without a separate release decision;
- no real customer/client data;
- no external/client marketplace message submission from this repo work.

## Done means for this reconciliation tranche

- Stale private/public checkpoint language is corrected or superseded.
- `api-webhook-bridge` and `automation-debugger` have CI workflows.
- Local verification passes in all first-set repos.
- Pushed public HEADs are verified.
- CI is green for repos with workflows.
- The next build project is clearly identified as `lowcode-ai-workflows`.
