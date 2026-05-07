"""Tests for the Slack/Teams Alert Pipeline pattern."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Import main.py via importlib (directory has a hyphen, so standard
# syntax like "from patterns.slack_alerts.python.main import ..."
# would not work).
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "slack_alerts_main", HERE / "python" / "main.py"
)
assert _spec is not None and _spec.loader is not None, "Could not load main.py"
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

AlertPipeline = _mod.AlertPipeline
run = _mod.run


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _load_fixture(name: str) -> dict:
    with open(HERE / "fixtures" / name) as f:
        return dict(json.load(f))


def _load_events() -> list[dict]:
    with open(HERE / "fixtures" / "input.json") as f:
        return list(json.load(f))


# ---------------------------------------------------------------------------
# AlertPipeline unit tests
# ---------------------------------------------------------------------------


class TestAlertPipeline:
    """Unit tests for the alert pipeline's core logic."""

    def setup_method(self) -> None:
        self.pipeline = AlertPipeline()

    def test_critical_routes_to_priority_channel(self) -> None:
        """Critical alerts should route to the priority channel."""
        channel = self.pipeline.determine_channel("critical")
        assert channel == "priority"

    def test_warning_routes_to_general_channel(self) -> None:
        """Warning alerts should route to the general channel."""
        channel = self.pipeline.determine_channel("warning")
        assert channel == "general"

    def test_info_routes_to_general_channel(self) -> None:
        """Info alerts should route to the general channel."""
        channel = self.pipeline.determine_channel("info")
        assert channel == "general"

    def test_unknown_severity_routes_to_general(self) -> None:
        """Unknown severity should fall back to the general channel."""
        channel = self.pipeline.determine_channel("debug")
        assert channel == "general"

    def test_format_alert_text(self) -> None:
        """Format alert text should include severity, event type, and detail."""
        event = {
            "event_type": "test_event",
            "severity": "warning",
            "message": "something happened",
        }
        text = self.pipeline.format_alert_text(event)
        assert "[WARNING]" in text
        assert "Test Event" in text
        assert "something happened" in text

    def test_format_alert_text_missing_message(self) -> None:
        """Format alert text should handle missing 'message' field gracefully."""
        event = {"event_type": "silent_alarm", "severity": "info"}
        text = self.pipeline.format_alert_text(event)
        assert "[INFO]" in text
        assert "Silent Alarm" in text
        assert "No details provided" in text

    def test_deduplicate_same_event_type_and_severity(self) -> None:
        """Duplicate (event_type, severity) pairs should be suppressed."""
        event_a = {"event_type": "cpu_spike", "severity": "warning"}
        event_b = {"event_type": "cpu_spike", "severity": "warning"}

        assert not self.pipeline.is_duplicate(event_a)
        assert self.pipeline.is_duplicate(event_b)

    def test_different_event_type_not_duplicate(self) -> None:
        """Different event types with the same severity are not duplicates."""
        a = {"event_type": "cpu_spike", "severity": "warning"}
        b = {"event_type": "disk_full", "severity": "warning"}

        assert not self.pipeline.is_duplicate(a)
        assert not self.pipeline.is_duplicate(b)

    def test_different_severity_not_duplicate(self) -> None:
        """Same event type with different severity are not duplicates."""
        a = {"event_type": "cpu_spike", "severity": "warning"}
        b = {"event_type": "cpu_spike", "severity": "critical"}

        assert not self.pipeline.is_duplicate(a)
        assert not self.pipeline.is_duplicate(b)

    def test_process_events_suppresses_duplicates(self) -> None:
        """process_events should suppress duplicate (event_type, severity) pairs."""
        events = [
            {"event_type": "disk_full", "severity": "warning", "message": "disk at 95%"},
            {"event_type": "disk_full", "severity": "warning", "message": "disk at 95%"},
            {"event_type": "cpu_spike", "severity": "critical", "message": "cpu at 90%"},
        ]
        result = self.pipeline.process_events(events)
        assert len(result["alerts"]) == 2  # two unique alerts
        assert len(result["suppressed"]) == 1
        assert result["total"] == 3
        assert result["suppressed"][0]["reason"] == "duplicate"

    def test_process_events_all_unique(self) -> None:
        """All unique events should all be delivered as alerts."""
        events = [
            {"event_type": "a", "severity": "info", "message": "msg a"},
            {"event_type": "b", "severity": "warning", "message": "msg b"},
            {"event_type": "c", "severity": "critical", "message": "msg c"},
        ]
        result = self.pipeline.process_events(events)
        assert len(result["alerts"]) == 3
        assert len(result["suppressed"]) == 0
        assert result["total"] == 3

    def test_send_alert_called_via_mock(self) -> None:
        """Alerts should be sent through the MockSlackClient."""
        self.pipeline.process_events(
            [{"event_type": "test", "severity": "critical", "message": "test alert"}]
        )
        assert len(self.pipeline.client.messages) == 1
        msg = self.pipeline.client.messages[0]
        assert msg["channel"] == "priority"
        assert "[CRITICAL]" in msg["text"]


# ---------------------------------------------------------------------------
# Integration test: run() matches expected_output.json
# ---------------------------------------------------------------------------


class TestRunOutput:
    """Verify that run() produces the expected output."""

    def test_run_matches_expected_output(self) -> None:
        """run() output should exactly match expected_output.json."""
        pattern_path = str(HERE)
        actual = run(pattern_path=pattern_path)
        expected = _load_fixture("expected_output.json")
        assert actual == expected, (
            f"run() output does not match expected_output.json\n"
            f"Actual:   {json.dumps(actual, indent=2)}\n"
            f"Expected: {json.dumps(expected, indent=2)}"
        )


# ---------------------------------------------------------------------------
# Edge-case tests via run()
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """End-to-end edge-case tests using the full run() pipeline."""

    def test_all_events_accounted_for(self) -> None:
        """Total should match number of input events."""
        n_input = len(_load_events())
        result = run(pattern_path=str(HERE))
        assert result["total"] == n_input

    def test_duplicate_suppressed_in_run(self) -> None:
        """The duplicate warning event should appear in suppressed list."""
        result = run(pattern_path=str(HERE))
        assert len(result["suppressed"]) >= 1
        for s in result["suppressed"]:
            assert s["reason"] == "duplicate"

    def test_critical_events_routed_to_priority(self) -> None:
        """All critical alerts should be on the priority channel."""
        result = run(pattern_path=str(HERE))
        for alert in result["alerts"]:
            if alert["severity"] == "critical":
                assert alert["channel"] == "priority"
