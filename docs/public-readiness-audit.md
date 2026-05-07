# Public Readiness Audit

Generated: 2026-05-07 UTC

## Verdict

Automation Kit has been cleaned for a public-safe tracked surface while remaining private. The repository now presents itself as a reusable automation framework with a linked public case study instead of a marketplace/planning workbench.

Do not change visibility, create a release, connect live services, create cloud resources, or publish externally without a separate human approval gate.

## Completed remediation

- Rewrote the `api-webhook-bridge` case-study reference to link the public repository: <https://github.com/stefan-mcf/api-webhook-bridge>.
- Added `docs/screenshots/05-case-study-link.png` as the Automation Kit framework-to-case-study proof panel.
- Documented that the full bridge screenshot package stays in the bridge repository instead of being duplicated here.
- Removed internal planning/checkpoint/marketplace-support docs from tracking and added precise ignore rules so they remain local-only.
- Rewrote README, EVIDENCE, pattern index, API/MCP/deployment, architecture, public-readiness, and spoke-architecture docs for public-safe package language.
- Added `.gitattributes` for text/binary clone hygiene.
- Integrated the MCP surface into public docs and quality gates.
- Updated GitHub topics to capability terms and removed public-unfriendly sales-proof topics.

## Current GitHub topics

- automation
- low-code
- make
- n8n
- python
- zapier
- docker
- fastapi
- openapi
- webhooks
- fixture-safe
- mcp
- workflow-automation

## Verification bundle

Run before any future publication decision:

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
PYTHONPATH=src python -m mypy src
PYTHONPATH=src python -m auto_kit.cli validate-all
PYTHONPATH=src python -m auto_kit.cli mcp-validate
git diff --check
git ls-files --others --exclude-standard
git ls-files -ci --exclude-standard
```

## Local-only plan

The full generated audit/remediation plan is local-only and ignored at:

```text
docs/plans/2026-05-07-github-public-prep.md
```

That file records findings F-01 through F-06 and the completed tranches. It is intentionally not part of the tracked public surface.
