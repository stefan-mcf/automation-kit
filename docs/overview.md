# Automation Kit Overview

## What is Automation Kit?

Automation Kit is a low-code automation pattern library — a collection of reusable,
well-tested workflow patterns that solve common business automation scenarios.
Each pattern provides:

- A **declarative workflow definition** (`workflow.json`) describing inputs,
  outputs, and processing nodes.
- **Synthetic fixtures** (`fixtures/`) for repeatable, credential-free testing.
- A **Python implementation** (`python/main.py`) with a standard `run()`
  entrypoint.
- A **test suite** (`python/test_<name>.py`) covering normal paths, edge cases,
  and error handling.

## Design Principles

1. **Deterministic mocks over live APIs** — Every pattern uses mock clients
   seeded for reproducibility. No real credentials, no flaky tests, no
   rate-limit surprises.
2. **Isolated patterns** — Each pattern is self-contained under
   `patterns/<name>/`. No cross-pattern coupling.
3. **CLI-first** — The `auto-kit` CLI discovers, validates, and runs patterns
   from the terminal. No web UI, no background daemon.
4. **Testable by default** — Every pattern ships with a test file. The
   cross-pattern matrix (`tests/test_all_patterns.py`) auto-discovers all
   patterns and validates their structure.

## Pattern Lifecycle

1. **Discover** — `auto-kit list-patterns` scans `patterns/` for directories
   with `workflow.json`.
2. **Validate** — `auto-kit validate <path>` checks file structure, workflow
   JSON schema, and fixture completeness.
3. **Run** — `auto-kit run <path>` loads fixtures, executes `python/main.py`,
   and compares output to `expected_output.json`.
4. **Test** — `pytest` runs both the cross-pattern matrix and per-pattern test
   suites.

## How Mock Clients Work

All mock clients live in `src/auto_kit/mock_clients.py` and use a shared
deterministic seed (`AUTO_KIT_MOCK_SEED=42`). They return synthetic but
realistic data — no network calls, no credentials, no side effects.

| Client | Purpose |
|--------|---------|
| `MockCRMClient` | Upsert and query CRM records |
| `MockEmailClient` | Parse email text into structured fields |
| `MockLeadDataClient` | Enrich company data by domain |
| `MockCalendarClient` | Check availability and book slots |
| `MockWebhookRouter` | Route typed payloads to handlers |
| `MockSlackClient` | Send formatted channel messages |
| `MockTeamsClient` | Send adaptive card messages |

## File Layout

```
automation-kit/
  Dockerfile
  pyproject.toml
  .env.example
  .gitignore
  .dockerignore
  README.md
  src/auto_kit/
    __init__.py
    models.py
    workflow_schema.py
    fixtures.py
    pattern_runner.py
    mock_clients.py
    cli.py
  patterns/
    csv-to-crm/     fixtures/ python/ workflow.json README.md
    email-parser/   fixtures/ python/ workflow.json README.md
    lead-enrichment/ fixtures/ python/ workflow.json README.md
    calendar-booking/ fixtures/ python/ workflow.json README.md
    webhook-router/  fixtures/ python/ workflow.json README.md
    slack-alerts/    fixtures/ python/ workflow.json README.md
  tests/
    test_workflow_schema.py
    test_pattern_runner.py
    test_all_patterns.py
    test_cli.py
  docs/
    plans/
    overview.md
    quickstart.md
```
