"""MCP server and handler functions for Automation Kit factory controls."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Any

from auto_kit.api import SUPPORTED_API_RUN_PATTERNS, _pattern_summary
from auto_kit.capability_registry import CapabilityRegistry, validate_safe_id
from auto_kit.pattern_runner import discover_patterns, run_pattern_module
from auto_kit.pattern_runner import validate_pattern as validate_path

try:  # pragma: no cover - import availability is environment-specific.
    FastMCP: Any = import_module("mcp.server.fastmcp").FastMCP
except Exception:  # pragma: no cover
    FastMCP = None


REGISTRY = CapabilityRegistry.load_default


def _registry() -> CapabilityRegistry:
    return REGISTRY()


def _safe_pattern_path(pattern_name: str) -> Path:
    safe_name = validate_safe_id(pattern_name)
    for path in discover_patterns():
        if path.name == safe_name:
            return path
    raise KeyError(f"unknown pattern: {pattern_name}")


def _base_metadata() -> dict[str, bool]:
    return {"fixture_safe": True, "live_services_used": False}


async def health() -> dict[str, Any]:
    """Report MCP server health and safety posture."""

    registry = _registry()
    return {
        "status": "ok",
        "version": "0.1.0",
        "patterns": len(discover_patterns()),
        "sectors": len(registry.list_sectors()),
        "capabilities": len(registry.list_capabilities()),
        **_base_metadata(),
    }


async def list_patterns(api_run_enabled_only: bool = False) -> dict[str, Any]:
    """Discover reusable Automation Kit patterns."""

    patterns = [_pattern_summary(path) for path in discover_patterns()]
    if api_run_enabled_only:
        patterns = [pattern for pattern in patterns if pattern["api_run_enabled"]]
    return {"patterns": patterns, **_base_metadata()}


async def get_pattern(pattern_name: str) -> dict[str, Any]:
    """Inspect one reusable Automation Kit pattern."""

    try:
        path = _safe_pattern_path(pattern_name)
    except (KeyError, ValueError) as exc:
        return {"status": "not_found", "errors": [str(exc)], **_base_metadata()}
    return {"status": "ok", **_pattern_summary(path), **_base_metadata()}


async def validate_pattern(pattern_name: str) -> dict[str, Any]:
    """Validate one pattern's file and workflow contract."""

    try:
        path = _safe_pattern_path(pattern_name)
        issues = validate_path(path)
    except (KeyError, ValueError) as exc:
        return {
            "pattern_name": pattern_name,
            "passed": False,
            "issues": [str(exc)],
            **_base_metadata(),
        }
    return {
        "pattern_name": path.name,
        "passed": not issues,
        "issues": issues,
        **_base_metadata(),
    }


async def run_pattern(pattern_name: str, fixture_name: str = "default") -> dict[str, Any]:
    """Run a fixture-safe pattern proof."""

    try:
        path = _safe_pattern_path(pattern_name)
        validate_safe_id(fixture_name)
    except (KeyError, ValueError) as exc:
        return {
            "pattern_name": pattern_name,
            "status": "not_found",
            "errors": [str(exc)],
            **_base_metadata(),
        }
    if path.name not in SUPPORTED_API_RUN_PATTERNS:
        return {
            "pattern_name": path.name,
            "status": "rejected",
            "output": {},
            "errors": [f"Pattern {path.name} is not enabled for MCP/API runs"],
            **_base_metadata(),
        }
    result = run_pattern_module(path, fixture_name=fixture_name)
    return {
        "pattern_name": result.pattern_name,
        "status": "passed" if result.passed else "failed",
        "output": result.actual_output or {},
        "expected_output": result.expected_output or {},
        "validation_summary": {"passed": result.passed, "fixture_name": result.fixture_name},
        "errors": result.errors,
        **_base_metadata(),
    }


async def validate_all() -> dict[str, Any]:
    """Validate all discoverable patterns."""

    results = []
    passed = 0
    failed = 0
    for path in discover_patterns():
        issues = validate_path(path)
        ok = not issues
        passed += int(ok)
        failed += int(not ok)
        results.append({"pattern_name": path.name, "passed": ok, "issues": issues})
    return {"passed": passed, "failed": failed, "results": results, **_base_metadata()}


async def list_sectors(include_capabilities: bool = True) -> dict[str, Any]:
    """Discover registered factory sectors."""

    registry = _registry()
    sectors = []
    for sector in registry.list_sectors():
        data = sector.to_dict()
        if include_capabilities:
            data["capabilities"] = [
                capability.capability_id
                for capability in registry.list_capabilities(sector_id=sector.sector_id)
            ]
        sectors.append(data)
    return {"sectors": sectors, **_base_metadata()}


async def list_capabilities(
    sector_id: str | None = None,
    runnable_only: bool = False,
) -> dict[str, Any]:
    """Discover callable or inspectable factory capabilities."""

    try:
        capabilities = _registry().list_capabilities(
            sector_id=sector_id,
            runnable_only=runnable_only,
        )
    except (KeyError, ValueError) as exc:
        return {"capabilities": [], "errors": [str(exc)], **_base_metadata()}
    return {
        "capabilities": [capability.to_dict() for capability in capabilities],
        **_base_metadata(),
    }


async def get_capability(capability_id: str) -> dict[str, Any]:
    """Inspect one capability's metadata and safety boundary."""

    try:
        capability = _registry().get_capability(capability_id)
    except (KeyError, ValueError) as exc:
        return {"status": "not_found", "errors": [str(exc)], **_base_metadata()}
    return {"status": "ok", "capability": capability.to_dict(), **_base_metadata()}


async def validate_capability(capability_id: str) -> dict[str, Any]:
    """Validate one capability registration and backing assets."""

    try:
        registry = _registry()
        capability = registry.get_capability(capability_id)
        registry.validate()
    except (KeyError, ValueError) as exc:
        return {
            "capability_id": capability_id,
            "passed": False,
            "issues": [str(exc)],
            **_base_metadata(),
        }
    issues: list[str] = []
    if capability.kind == "pattern":
        issues = validate_path(capability.implementation_path(registry.repo_root))
    return {
        "capability_id": capability.capability_id,
        "passed": not issues,
        "issues": issues,
        **_base_metadata(),
    }


async def run_capability(capability_id: str, fixture_name: str = "default") -> dict[str, Any]:
    """Run a fixture-safe capability when supported."""

    try:
        capability = _registry().get_capability(capability_id)
    except (KeyError, ValueError) as exc:
        return {
            "capability_id": capability_id,
            "status": "not_found",
            "errors": [str(exc)],
            **_base_metadata(),
        }

    if not capability.runnable:
        return {
            "capability_id": capability.capability_id,
            "status": "not_runnable",
            "errors": ["Capability is registered for discovery/evidence but is not runnable yet"],
            **_base_metadata(),
        }
    if capability.kind != "pattern":
        return {
            "capability_id": capability.capability_id,
            "status": "unsupported",
            "errors": [f"Runnable kind is not supported yet: {capability.kind}"],
            **_base_metadata(),
        }
    pattern_name = capability.implementation_path(_registry().repo_root).name
    result = await run_pattern(pattern_name=pattern_name, fixture_name=fixture_name)
    return {"capability_id": capability.capability_id, **result}


async def get_evidence_index(
    sector_id: str | None = None,
    capability_id: str | None = None,
) -> dict[str, Any]:
    """Return proof/evidence docs and output pointers for sectors or capabilities."""

    registry = _registry()
    evidence: list[dict[str, Any]] = []
    capabilities = registry.list_capabilities(sector_id=sector_id)
    if capability_id is not None:
        capabilities = [registry.get_capability(capability_id)]
    for capability in capabilities:
        for path in capability.evidence:
            evidence.append(
                {
                    "title": capability.capability_id,
                    "path": path,
                    "kind": "doc",
                    "status": "current",
                    "sector_id": capability.sector_id,
                    "capability_id": capability.capability_id,
                }
            )
    return {"evidence": evidence, **_base_metadata()}


def build_server() -> Any:
    """Build the stdio MCP server for Automation Kit."""

    if FastMCP is None:
        raise RuntimeError("mcp package with FastMCP support is required")
    server = FastMCP("automation-kit")
    tools: list[Callable[..., Any]] = [
        health,
        list_patterns,
        get_pattern,
        validate_pattern,
        run_pattern,
        validate_all,
        list_sectors,
        list_capabilities,
        get_capability,
        run_capability,
        validate_capability,
        get_evidence_index,
    ]
    for tool in tools:
        server.tool()(tool)
    return server


def main() -> None:
    """Run the Automation Kit MCP server over stdio."""

    build_server().run()


if __name__ == "__main__":
    main()
