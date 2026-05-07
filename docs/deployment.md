# Local Deployment Proof

Automation Kit has a local only deployment proof for showing the API surface in Docker without creating accounts, cloud resources, paid infrastructure, or live external-service connections.

## Boundary

- local only;
- no cloud resources;
- no live external-service connections;
- no real customer data;
- `AUTO_KIT_USE_LIVE_SERVICES=false` by default;
- healthcheck uses the local `/health` endpoint only.

This is not a production deployment claim. It is a reproducible local proof that the FastAPI/OpenAPI wrapper can run inside the same container package used for CLI validation.

## CLI container validation

```bash
docker build -t automation-kit .
docker run --rm automation-kit validate-all
```

Expected result:

```text
7 pattern(s): 7 passed, 0 failed
```

## API mode with Docker Compose

```bash
docker compose up --build automation-kit-api
```

The Compose service overrides the image entrypoint and runs:

```bash
uvicorn auto_kit.api:app --host 0.0.0.0 --port 8000
```

Smoke checks from the host:

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/patterns
curl -fsS http://127.0.0.1:8000/openapi.json
```

The expected `/health` response includes:

```json
{"status":"ok","fixture_safe":true,"live_services_used":false}
```

## Healthcheck

`docker-compose.yml` includes a `healthcheck` that calls `http://127.0.0.1:8000/health` from inside the container with Python standard library networking. It does not require curl inside the image.

## Stop command

```bash
docker compose down
```

## Human gate

Stop and ask before any of these actions:

- deploying to Render, Fly.io, Railway, AWS, GCP, Azure, or other cloud platforms;
- adding cloud secrets or external-service credentials;
- changing repository visibility;
- publishing a release;
- using this endpoint with real customer data or external platform delivery.
