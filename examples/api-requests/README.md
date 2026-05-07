# API Request Examples

These request examples are fixture-safe. They are intended for the local FastAPI proof surface only and do not connect to live external-service credentials.

Run the API locally:

```bash
PYTHONPATH=src uvicorn auto_kit.api:app --host 127.0.0.1 --port 8000
```

Then use the JSON files in this directory with `curl` or any API client.
