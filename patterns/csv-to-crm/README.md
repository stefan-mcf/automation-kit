# CSV to CRM Sync

Load a CSV of leads, deduplicate by email (keeping the last occurrence), and
upsert into a CRM using `MockCRMClient`.

## Files

| Path | Purpose |
|------|---------|
| `fixtures/input.csv` | Sample leads CSV (6 rows, 1 duplicate email) |
| `fixtures/expected_output.json` | Expected result from `run()` |
| `python/main.py` | Python implementation — `run(pattern_path)` |
| `python/test_main.py` | Pytest suite — CSV parse, dedup, payload gen |
| `workflow.json` | n8n-compatible workflow definition |

## Low-Code vs Python Tradeoffs

### Low-code (n8n workflow.json)

**Pros**
- Visual drag-and-drop editing (n8n, Node-RED, etc.)
- No coding required for basic transformations
- Built-in error handling with retry nodes
- Easy to share with non-technical stakeholders

**Cons**
- Hard to debug complex dedup logic
- Limited to built-in node capabilities
- Performance degrades with large CSVs (>10k rows)
- No unit testing — must rely on manual verification

### Python (main.py)

**Pros**
- Fully deterministic, testable behavior
- Easy to add custom logic (validation, enrichment, logging)
- Can handle large datasets efficiently
- Version-controlled code with CI/CD

**Cons**
- Requires Python knowledge to modify
- No visual representation of the flow
- Deployment needs an execution environment

## Error Handling

The `run()` function raises `FileNotFoundError` if `input.csv` is missing.
The dedup step silently skips rows with empty/whitespace-only email fields.
`MockCRMClient.batch_upsert` pops the `email` key from each payload — ensure
the email is in the payload dict.

For production, wrap `run()` in a try/except and log failures.

## Import / Usage

### Python
```python
from patterns.csv_to_crm.python.main import run

result = run(pattern_path="patterns/csv-to-crm")
print(result["upserted_contacts"])
```

### n8n
1. Create a new workflow
2. Click **Import** → **From JSON**
3. Select `patterns/csv-to-crm/workflow.json`
4. Replace the "Read CSV" node's file path with your actual CSV location
5. Replace `MockCRMClient` with your CRM API node (HubSpot, Salesforce, etc.)

### Automation Kit CLI
```bash
python -c "
from auto_kit.pattern_runner import run_pattern_module
result = run_pattern_module('patterns/csv-to-crm')
print(result.summary())
"
```
