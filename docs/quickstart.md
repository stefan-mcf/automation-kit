# Quick Start Guide

## 1. Install

```bash
git clone <repo-url> automation-kit
cd automation-kit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## 2. List Patterns

```bash
auto-kit list-patterns
```

Expected output (6 patterns):

```
Found 6 pattern(s):

  calendar-bbooking          Timezone-aware calendar availability
  csv-to-crm                 Sync CSV rows to a CRM
  email-parser               Parse raw email into structured fields
  lead-enrichment            Enrich leads with company data
  slack-alerts               Send alerts to Slack or Teams
  webhook-router             Route webhooks by event type
```

## 3. Validate Everything

```bash
auto-kit validate-all
```

All 6 should pass.

## 4. Run Tests

```bash
# Full suite — library tests + per-pattern tests
python -m pytest -q tests/ patterns/
```

Expected: 90 passed.

## 5. Run a Pattern

```bash
auto-kit run patterns/csv-to-crm
```

Prints a pass/fail summary comparing actual output to expected output.

## 6. Docker

```bash
# Build
docker build -t automation-kit .

# Run inside container
docker run --rm auto-kit list-patterns
docker run --rm auto-kit validate-all
```

## 7. Explore a Pattern

Every pattern follows the same layout:

```
patterns/<name>/
  workflow.json        # Declarative workflow definition (JSON)
  README.md            # Pattern docs — what it does, how it works
  fixtures/
    input.json         # Test input data
    expected_output.json  # Expected result
    (additional data files)
  python/
    main.py            # Runnable implementation
    test_<name>.py     # Pattern-specific tests
```

To understand how a pattern works, start with its `README.md`, then open
`workflow.json` for the node graph, and `python/main.py` for the logic.
