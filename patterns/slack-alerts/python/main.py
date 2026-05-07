"""Pattern 6: Slack/Teams Alert Pipeline — deduplicate, route, and send alerts via MockSlackClient.

Usage:
    from auto_kit.pattern_runner import run_pattern_module
    result = run_pattern_module("patterns/slack-alerts")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from auto_kit.mock_clients import MockSlackClient

# ---------------------------------------------------------------------------
# Channel routing: severity -> Slack channel name
# ---------------------------------------------------------------------------

SEVERITY_CHANNEL_MAP: dict[str, str] = {
    "critical": "priority",
    "warning": "general",
    "info": "general",
}


# ---------------------------------------------------------------------------
# Alert Pipeline
# ---------------------------------------------------------------------------


class AlertPipeline:
    """Process monitor events: format alerts, deduplicate, route to channels.

    Deduplication is performed by (event_type, severity) pairs within a
    single batch.  The first occurrence of a given pair is sent; subsequent
    identical pairs are suppressed.
    """

    def __init__(self) -> None:
        self.client = MockSlackClient()
        self._seen: set[tuple[str, str]] = set()
        self.alerts: list[dict[str, Any]] = []
        self.suppressed: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_events(
        self, events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Run the full pipeline over a list of monitor events.

        Returns:
            dict with keys:
                alerts     — list of successfully sent alert records
                suppressed — list of suppressed event summaries
                total      — total number of input events
        """
        self._reset()
        for event in events:
            self._process_single(event)
        return self._summary()

    def format_alert_text(self, event: dict[str, Any]) -> str:
        """Build a human-readable alert message string."""
        severity = event.get("severity", "info").upper()
        event_type = event.get("event_type", "unknown")
        # Human-readable label
        label = event_type.replace("_", " ").title()
        # Use the event's 'message' field if present, otherwise fall back
        detail = event.get("message", "No details provided")
        return f"[{severity}] {label}: {detail}"

    def determine_channel(self, severity: str) -> str:
        """Map severity to the target Slack channel."""
        return SEVERITY_CHANNEL_MAP.get(severity, "general")

    def is_duplicate(self, event: dict[str, Any]) -> bool:
        """Check whether (event_type, severity) has already been seen."""
        key = (event.get("event_type", ""), event.get("severity", ""))
        if key in self._seen:
            return True
        self._seen.add(key)
        return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        self._seen.clear()
        self.alerts.clear()
        self.suppressed.clear()

    def _process_single(self, event: dict[str, Any]) -> None:
        if self.is_duplicate(event):
            self.suppressed.append(
                {
                    "event_type": event.get("event_type", ""),
                    "severity": event.get("severity", ""),
                    "reason": "duplicate",
                }
            )
            return

        severity = event.get("severity", "info")
        channel = self.determine_channel(severity)
        text = self.format_alert_text(event)
        record = self.client.send_alert(
            channel=channel, text=text, severity=severity
        )
        self.alerts.append(record)

    def _summary(self) -> dict[str, Any]:
        return {
            "alerts": list(self.alerts),
            "suppressed": list(self.suppressed),
            "total": len(self.alerts) + len(self.suppressed),
        }


# ---------------------------------------------------------------------------
# Pattern run entry point
# ---------------------------------------------------------------------------


def run(pattern_path: str | None = None) -> dict[str, Any]:
    """Load input.json, process events through AlertPipeline, return results.

    This function is called by the pattern runner (auto_kit.pattern_runner)
    with pattern_path pointing to the pattern's root directory.
    """
    if pattern_path is None:
        pattern_path = str(Path(__file__).resolve().parent.parent)

    base = Path(pattern_path)
    input_path = base / "fixtures" / "input.json"

    with open(input_path) as f:
        events: list[dict[str, Any]] = json.load(f)

    pipeline = AlertPipeline()
    return pipeline.process_events(events)


# ---------------------------------------------------------------------------
# CLI shortcut
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps(result, indent=2))
