# Quick Start Guide

## Requirements

- Python 3.11+
- Docker optional for container checks

## 1. Install

```bash
git clone https://github.com/stefan-mcf/automation-kit.git
cd automation-kit

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. List patterns

```bash
auto-kit list-patterns
```

Expected:

```text
Found 7 pattern(s):
```

Patterns:

- `calendar-booking`
- `csv-to-crm`
- `email-parser`
- `lead-enrichment`
- `product-creative-pack`
- `slack-alerts`
- `webhook-router`

## 3. Validate all patterns

```bash
auto-kit validate-all
```

Expected:

```text
7 pattern(s): 7 passed, 0 failed
```

## 4. Run a pattern

```bash
auto-kit run patterns/csv-to-crm
```

## 5. Run tests

```bash
python -m pytest -q
```

## 6. Local API

```bash
PYTHONPATH=src uvicorn auto_kit.api:app --host 127.0.0.1 --port 8000
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/patterns
```

OpenAPI docs at `http://127.0.0.1:8000/docs`.

## 7. MCP

```bash
auto-kit mcp-validate
auto-kit mcp-serve
```

## 8. Docker

```bash
docker build -t automation-kit .
docker run --rm automation-kit list-patterns
docker run --rm automation-kit validate-all
```
