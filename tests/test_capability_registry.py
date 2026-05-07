from __future__ import annotations

from pathlib import Path

import pytest

from auto_kit.capability_registry import (
    CapabilityRegistry,
    RegistryValidationError,
    validate_safe_id,
)


def test_registry_loads_sectors_and_capabilities() -> None:
    registry = CapabilityRegistry.load_default()

    sector_ids = {sector.sector_id for sector in registry.list_sectors()}
    capability_ids = {capability.capability_id for capability in registry.list_capabilities()}

    assert "core-runtime" in sector_ids
    assert "api-webhook" in sector_ids
    assert "pattern.webhook-router.default" in capability_ids
    assert "spoke.api-webhook-bridge.shopify-order-to-airtable-slack" in capability_ids


def test_registry_filters_capabilities_by_sector() -> None:
    registry = CapabilityRegistry.load_default()

    capabilities = registry.list_capabilities(sector_id="core-runtime")

    assert capabilities
    assert {capability.sector_id for capability in capabilities} == {"core-runtime"}
    capability_ids = {capability.capability_id for capability in capabilities}
    assert "pattern.webhook-router.default" in capability_ids


def test_registry_validation_requires_known_sectors() -> None:
    registry = CapabilityRegistry(
        repo_root=Path.cwd(),
        sectors_yaml={"sectors": [{"sector_id": "known", "label": "Known", "status": "active"}]},
        capabilities_yaml={
            "capabilities": [
                {
                    "capability_id": "pattern.unknown.default",
                    "sector_id": "missing",
                    "kind": "pattern",
                    "implementation": "patterns/webhook-router",
                    "runnable": True,
                    "fixture_safe": True,
                    "live_services_used": False,
                    "description": "Broken registration.",
                }
            ]
        },
    )

    with pytest.raises(RegistryValidationError, match="unknown sector"):
        registry.validate()


def test_validate_safe_id_rejects_path_traversal() -> None:
    with pytest.raises(ValueError, match="unsafe"):
        validate_safe_id("../patterns/webhook-router")
