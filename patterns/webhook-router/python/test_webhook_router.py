"""Tests for Pattern 5: Webhook Router."""

from __future__ import annotations

import importlib.util
from pathlib import Path

PATTERN_DIR = Path(__file__).resolve().parent.parent


def _load_main_module():
    """Dynamically load main.py (patterns dir is not a Python package)."""
    main_py = PATTERN_DIR / "python" / "main.py"
    spec = importlib.util.spec_from_file_location("webhook_router_main", main_py)
    assert spec is not None and spec.loader is not None, f"Could not load {main_py}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestWebhookRouter:
    """Test suite for webhook routing pattern."""

    def test_order_created_routes_to_order_handler(self):
        """order.created events should route to order_handler."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))

        routed = result["routed_events"]
        order = next(e for e in routed if e["event_type"] == "order.created")
        assert order["route"] == "order_handler"
        assert order["handler"] == "order_handler"
        assert order["handled"] is True
        assert order["event_id"] == "ORD-123"

    def test_lead_captured_routes_to_lead_handler(self):
        """lead.captured events should route to lead_handler."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))

        routed = result["routed_events"]
        lead = next(e for e in routed if e["event_type"] == "lead.captured")
        assert lead["route"] == "lead_handler"
        assert lead["handler"] == "lead_handler"
        assert lead["handled"] is True
        assert lead["event_id"] == "lead-Alice"

    def test_unknown_action_goes_to_dead_letter_with_reason(self):
        """Unknown event types should be dead-lettered with reason 'unknown_event_type'."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))

        dead = result["dead_letter"]
        unknown = next(e for e in dead if e["event_type"] == "unknown.action")
        assert unknown["route"] == "dead-letter"
        assert unknown["handler"] is None
        assert unknown["handled"] is False
        assert unknown["reason"] == "unknown_event_type"

    def test_missing_type_goes_to_dead_letter(self):
        """Payloads missing 'type' field should dead-letter with 'missing_event_type'."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))

        dead = result["dead_letter"]
        missing = next(e for e in dead if e["event_type"] is None)
        assert missing["route"] == "dead-letter"
        assert missing["handler"] is None
        assert missing["handled"] is False
        assert missing["reason"] == "missing_event_type"

    def test_no_crashes_on_missing_optional_fields(self):
        """Router should not crash on payloads with missing optional non-required fields."""
        mod = _load_main_module()
        router = mod.WebhookRouter()

        # Payload with right type but missing a required field — should dead-letter, not crash
        partial_order = {"type": "order.created", "order_id": "ORD-999"}
        result = router.route(partial_order)
        assert result["handled"] is False
        assert "missing_required_fields" in result["reason"]

        # Payload with extra unknown fields — should not crash
        extra_fields = {
            "type": "order.created",
            "order_id": "ORD-1000",
            "amount": 50.0,
            "extra_field_1": "unexpected",
            "extra_field_2": 42,
        }
        result2 = router.route(extra_fields)
        assert result2["handled"] is True

    def test_support_ticket_routes_to_support_handler(self):
        """ticket.created events should route to support_handler."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))

        routed = result["routed_events"]
        ticket = next(e for e in routed if e["event_type"] == "ticket.created")
        assert ticket["route"] == "support_handler"
        assert ticket["handler"] == "support_handler"
        assert ticket["handled"] is True
        assert ticket["event_id"] == "TK-456"

    def test_output_shape_has_all_keys(self):
        """Top-level result should contain routed_events, dead_letter, and total."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))

        assert set(result.keys()) == {"routed_events", "dead_letter", "total"}
        assert result["total"] == 5
        assert len(result["routed_events"]) == 3
        assert len(result["dead_letter"]) == 2

        expected_keys = {"event_id", "event_type", "route", "handler", "handled", "reason"}
        for event in result["routed_events"]:
            assert set(event.keys()) == expected_keys

        for event in result["dead_letter"]:
            assert set(event.keys()) == expected_keys
