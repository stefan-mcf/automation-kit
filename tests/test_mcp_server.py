from __future__ import annotations

import pytest

from auto_kit import mcp_server


@pytest.mark.asyncio
async def test_mcp_list_patterns_returns_fixture_safe_metadata() -> None:
    result = await mcp_server.list_patterns()

    assert result["fixture_safe"] is True
    assert result["live_services_used"] is False
    assert "webhook-router" in {pattern["name"] for pattern in result["patterns"]}


@pytest.mark.asyncio
async def test_mcp_run_pattern_routes_to_existing_runner() -> None:
    result = await mcp_server.run_pattern(pattern_name="webhook-router", fixture_name="default")

    assert result["pattern_name"] == "webhook-router"
    assert result["status"] == "passed"
    assert result["fixture_safe"] is True
    assert result["live_services_used"] is False


@pytest.mark.asyncio
async def test_mcp_run_pattern_rejects_non_enabled_pattern() -> None:
    result = await mcp_server.run_pattern(
        pattern_name="product-creative-pack",
        fixture_name="default",
    )

    assert result["status"] == "rejected"
    assert "not enabled" in result["errors"][0]
    assert result["live_services_used"] is False


@pytest.mark.asyncio
async def test_mcp_list_capabilities_can_filter_by_sector() -> None:
    result = await mcp_server.list_capabilities(sector_id="api-webhook", runnable_only=False)

    assert result["fixture_safe"] is True
    assert result["capabilities"]
    assert {capability["sector_id"] for capability in result["capabilities"]} == {"api-webhook"}


@pytest.mark.asyncio
async def test_mcp_run_capability_runs_pattern_capability() -> None:
    result = await mcp_server.run_capability(
        capability_id="pattern.webhook-router.default",
        fixture_name="default",
    )

    assert result["capability_id"] == "pattern.webhook-router.default"
    assert result["status"] == "passed"
    assert result["pattern_name"] == "webhook-router"


@pytest.mark.asyncio
async def test_mcp_run_capability_reports_planned_spoke_without_execution() -> None:
    result = await mcp_server.run_capability(
        capability_id="spoke.api-webhook-bridge.shopify-order-to-airtable-slack",
        fixture_name="default",
    )

    assert result["status"] == "not_runnable"
    assert result["fixture_safe"] is True
    assert result["live_services_used"] is False
