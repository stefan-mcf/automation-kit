"""Local FastAPI proof surface for fixture-safe Automation Kit patterns."""

from __future__ import annotations

import json
import re
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError

from auto_kit.pattern_runner import discover_patterns, load_workflow_json, run_pattern_module

SUPPORTED_API_RUN_PATTERNS = {"webhook-router", "csv-to-crm", "lead-enrichment"}
REPO_ROOT = Path(__file__).resolve().parents[2]
PATTERNS_ROOT = REPO_ROOT / "patterns"
SAFE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
MAX_REQUEST_BYTES = 64 * 1024

app = FastAPI(
    title="Automation Kit Local API",
    version="0.1.0",
    description="Fixture-safe local API wrapper around Automation Kit pattern proof runs.",
)


class PatternRunRequest(BaseModel):
    """Request body for a local pattern proof run."""

    fixture_name: str = "default"


class PatternRunResponse(BaseModel):
    """Stable response contract for local pattern proof runs."""

    pattern_name: str
    status: str
    output: dict[str, Any]
    validation_summary: dict[str, Any]
    errors: list[str]
    warnings: list[str] = Field(default_factory=list)
    fixture_safe: bool = True
    live_services_used: bool = False


def _validate_safe_name(value: str, field_name: str) -> str:
    """Validate a URL/body name used to select local fixture-backed assets."""

    if not SAFE_NAME_RE.fullmatch(value):
        raise HTTPException(
            status_code=422,
            detail=(
                f"{field_name} must contain only lowercase letters, numbers, "
                "hyphens, or underscores"
            ),
        )
    return value


def _pattern_path(pattern_name: str) -> Path:
    """Return a pattern path or raise a clean 404/422 for invalid pattern names."""

    safe_pattern_name = _validate_safe_name(pattern_name, "pattern_name")
    root = PATTERNS_ROOT.resolve()
    path = (root / safe_pattern_name).resolve()
    if root not in path.parents:
        raise HTTPException(status_code=422, detail="pattern_name resolves outside patterns root")
    if not path.exists() or not (path / "workflow.json").exists():
        raise HTTPException(status_code=404, detail=f"Unknown pattern: {pattern_name}")
    return path


def _pattern_summary(path: Path) -> dict[str, Any]:
    """Return workflow metadata suitable for API listing responses."""

    workflow = load_workflow_json(path)
    return {
        "name": path.name,
        "description": workflow.description,
        "nodes": len(workflow.nodes),
        "connections": len(workflow.connections),
        "metadata": workflow.metadata,
        "api_run_enabled": path.name in SUPPORTED_API_RUN_PATTERNS,
    }


async def _read_limited_json_body(request: Request) -> Any:
    """Read a JSON request body while enforcing a hard byte cap during streaming."""

    chunks: list[bytes] = []
    total_bytes = 0
    async for chunk in request.stream():
        total_bytes += len(chunk)
        if total_bytes > MAX_REQUEST_BYTES:
            raise HTTPException(status_code=413, detail="Request body is too large")
        chunks.append(chunk)
    try:
        return json.loads(b"".join(chunks) or b"{}")
    except JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="Request body must be valid JSON") from exc


async def _parse_pattern_run_request(request: Request) -> PatternRunRequest:
    """Parse and validate a request body for a fixture-backed pattern run."""

    body = await _read_limited_json_body(request)
    if not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="Request body must be a JSON object")
    try:
        run_request = PatternRunRequest.model_validate(body)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    _validate_safe_name(run_request.fixture_name, "fixture_name")
    if run_request.fixture_name != "default":
        raise HTTPException(status_code=404, detail=f"Unknown fixture: {run_request.fixture_name}")
    return run_request


@app.get("/health")
def health() -> dict[str, Any]:
    """Return local API health and safety metadata."""

    return {"status": "ok", "fixture_safe": True, "live_services_used": False}


@app.get("/patterns")
def list_patterns() -> dict[str, Any]:
    """List discoverable Automation Kit patterns."""

    return {
        "patterns": [_pattern_summary(path) for path in discover_patterns(PATTERNS_ROOT)],
        "fixture_safe": True,
        "live_services_used": False,
    }


@app.get("/patterns/{pattern_name}")
def get_pattern(pattern_name: str) -> dict[str, Any]:
    """Return metadata for one pattern."""

    path = _pattern_path(pattern_name)
    return _pattern_summary(path) | {"fixture_safe": True, "live_services_used": False}


@app.post("/patterns/{pattern_name}/run", response_model=PatternRunResponse)
async def run_pattern(pattern_name: str, request: Request) -> PatternRunResponse:
    """Run a supported pattern with local fixtures and return proof metadata."""

    path = _pattern_path(pattern_name)
    if pattern_name not in SUPPORTED_API_RUN_PATTERNS:
        raise HTTPException(
            status_code=400,
            detail=f"Pattern {pattern_name} is not enabled for API runs",
        )

    run_request = await _parse_pattern_run_request(request)
    result = run_pattern_module(path, fixture_name=run_request.fixture_name)
    status = "passed" if result.passed else "failed"
    return PatternRunResponse(
        pattern_name=result.pattern_name,
        status=status,
        output=result.actual_output or {},
        validation_summary={
            "passed": result.passed,
            "fixture_name": result.fixture_name,
        },
        errors=result.errors,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("auto_kit.api:app", host="127.0.0.1", port=8000, reload=False)
