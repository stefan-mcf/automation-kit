"""Exercise the actual MCP stdio boundary, beyond direct handler unit tests."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


def payload(result):
    assert not result.is_error
    return json.loads(result.content[0].text)


@pytest.mark.asyncio
async def test_stdio_initialization_discovery_and_bounded_execution() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "auto_kit.mcp_server"],
        cwd=str(ROOT),
        env={"PYTHONPATH": str(ROOT / "src"), "AUTO_KIT_USE_LIVE_SERVICES": "false"},
    )
    async with asyncio.timeout(30):
        async with stdio_client(server) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                initialized = await session.initialize()
                assert initialized.server_info.name == "automation-kit"
                tools = await session.list_tools()
                assert {"health", "list_patterns", "run_pattern", "run_capability"} <= {
                    tool.name for tool in tools.tools
                }

                health = payload(await session.call_tool("health", {}))
                assert health["status"] == "ok"
                assert health["fixture_safe"] is True
                assert health["live_services_used"] is False

                allowed = payload(
                    await session.call_tool(
                        "run_pattern", {"pattern_name": "webhook-router", "fixture_name": "default"}
                    )
                )
                assert allowed["status"] == "passed"
                assert allowed["validation_summary"]["passed"] is True
                assert allowed["live_services_used"] is False

                rejected = payload(
                    await session.call_tool(
                        "run_pattern", {"pattern_name": "product-creative-pack"}
                    )
                )
                assert rejected["status"] == "rejected"
                assert rejected["live_services_used"] is False
