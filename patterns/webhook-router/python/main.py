"""Pattern 5: Webhook Router — route webhook payloads to type-specific handlers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class WebhookRouter:
    """Route webhook payloads by event type with signature validation and dead-letter support."""

    def __init__(self) -> None:
        self.handlers: dict[str, Any] = {
            "order.created": self._handle_order_created,
            "lead.captured": self._handle_lead_captured,
            "ticket.created": self._handle_ticket_created,
        }
        self.signatures: dict[str, set[str]] = {
            "order.created": {"order_id", "amount"},
            "lead.captured": {"name", "email"},
            "ticket.created": {"ticket_id", "priority"},
        }
        self.routed_events: list[dict[str, Any]] = []
        self.dead_letter: list[dict[str, Any]] = []
        self._id_counter: int = 0

    def route(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Route a single webhook payload to the appropriate handler or dead-letter.

        Args:
            payload: The incoming webhook payload dict.

        Returns:
            A result dict with event_id, event_type, route, handler, handled, reason.
        """
        event_type = payload.get("type")

        # Dead-letter: missing type field
        if event_type is None:
            result: dict[str, Any] = {
                "event_id": self._generate_event_id(),
                "event_type": None,
                "route": "dead-letter",
                "handler": None,
                "handled": False,
                "reason": "missing_event_type",
            }
            self.dead_letter.append(result)
            return result

        handler = self.handlers.get(event_type)

        # Dead-letter: unknown event type
        if handler is None:
            result = {
                "event_id": self._generate_event_id(),
                "event_type": event_type,
                "route": "dead-letter",
                "handler": None,
                "handled": False,
                "reason": "unknown_event_type",
            }
            self.dead_letter.append(result)
            return result

        # Signature validation: check for minimal required fields
        required = self.signatures.get(event_type, set())
        missing = [field for field in required if field not in payload]
        if missing:
            result = {
                "event_id": self._generate_event_id(),
                "event_type": event_type,
                "route": "dead-letter",
                "handler": None,
                "handled": False,
                "reason": f"missing_required_fields: {', '.join(sorted(missing))}",
            }
            self.dead_letter.append(result)
            return result

        # Route to the matching handler
        result = handler(payload)
        self.routed_events.append(result)
        return result

    def _handle_order_created(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle order.created events."""
        return {
            "event_id": payload.get("order_id", self._generate_event_id()),
            "event_type": "order.created",
            "route": "order_handler",
            "handler": "order_handler",
            "handled": True,
            "reason": None,
        }

    def _handle_lead_captured(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle lead.captured events."""
        return {
            "event_id": f"lead-{payload.get('name', 'unknown')}",
            "event_type": "lead.captured",
            "route": "lead_handler",
            "handler": "lead_handler",
            "handled": True,
            "reason": None,
        }

    def _handle_ticket_created(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle ticket.created events."""
        return {
            "event_id": payload.get("ticket_id", self._generate_event_id()),
            "event_type": "ticket.created",
            "route": "support_handler",
            "handler": "support_handler",
            "handled": True,
            "reason": None,
        }

    def _generate_event_id(self) -> str:
        """Generate a deterministic auto-incrementing event ID."""
        self._id_counter += 1
        return f"evt-{self._id_counter:03d}"

    def summary(self) -> dict[str, Any]:
        """Return the full routing summary with routed events, dead-letter, and total count."""
        return {
            "routed_events": self.routed_events,
            "dead_letter": self.dead_letter,
            "total": len(self.routed_events) + len(self.dead_letter),
        }


def run(pattern_path: str | None = None) -> dict[str, Any]:
    """Load webhook payloads from fixtures, route them via WebhookRouter, return summary.

    Args:
        pattern_path: Path to the pattern directory (containing fixtures/).

    Returns:
        dict with 'routed_events', 'dead_letter', and 'total'.
    """
    base = Path(pattern_path) if pattern_path else Path(__file__).resolve().parent.parent

    input_path = base / "fixtures" / "input.json"
    with open(input_path) as f:
        payloads: list[dict[str, Any]] = json.load(f)

    router = WebhookRouter()
    for payload in payloads:
        router.route(payload)

    return router.summary()
