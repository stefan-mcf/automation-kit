"""Tests for the Calendar Booking pattern."""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------
# Import main.py via importlib (directory has a hyphen)
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "calendar_booking_main", HERE / "python" / "main.py"
)
assert _spec is not None and _spec.loader is not None, "Could not load main.py"
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TimeSlotManager = _mod.TimeSlotManager
Slot = _mod.Slot
run = _mod.run


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _load_fixture(name: str) -> dict:
    with open(HERE / "fixtures" / name) as f:
        return dict(json.load(f))


def _load_input() -> dict:
    return _load_fixture("input.json")


# ---------------------------------------------------------------------------
# Slot overlap tests (unit)
# ---------------------------------------------------------------------------


class TestSlot:
    """Unit tests for the Slot dataclass overlap logic."""

    def setup_method(self) -> None:
        self.tz = ZoneInfo("America/New_York")

    def test_overlapping_slots(self) -> None:
        """Two slots that overlap should return True."""
        a = Slot(
            start=datetime(2025, 6, 15, 14, 0, tzinfo=self.tz),
            end=datetime(2025, 6, 15, 15, 0, tzinfo=self.tz),
        )
        b = Slot(
            start=datetime(2025, 6, 15, 14, 30, tzinfo=self.tz),
            end=datetime(2025, 6, 15, 15, 30, tzinfo=self.tz),
        )
        assert a.overlaps_with(b) is True

    def test_non_overlapping_slots(self) -> None:
        """Two adjacent slots should NOT overlap."""
        a = Slot(
            start=datetime(2025, 6, 15, 14, 0, tzinfo=self.tz),
            end=datetime(2025, 6, 15, 15, 0, tzinfo=self.tz),
        )
        b = Slot(
            start=datetime(2025, 6, 15, 15, 0, tzinfo=self.tz),
            end=datetime(2025, 6, 15, 16, 0, tzinfo=self.tz),
        )
        assert a.overlaps_with(b) is False

    def test_exact_equal_slots_overlap(self) -> None:
        """Two identical slots should overlap."""
        a = Slot(
            start=datetime(2025, 6, 15, 14, 0, tzinfo=self.tz),
            end=datetime(2025, 6, 15, 15, 0, tzinfo=self.tz),
        )
        b = Slot(
            start=datetime(2025, 6, 15, 14, 0, tzinfo=self.tz),
            end=datetime(2025, 6, 15, 15, 0, tzinfo=self.tz),
        )
        assert a.overlaps_with(b) is True

    def test_different_timezone_overlap(self) -> None:
        """Slots in different timezones that represent the same instant should overlap."""
        a = Slot(
            start=datetime(2025, 6, 15, 14, 0, tzinfo=ZoneInfo("America/New_York")),
            end=datetime(2025, 6, 15, 15, 0, tzinfo=ZoneInfo("America/New_York")),
        )
        # 14:00 EDT = 18:00 UTC
        b = Slot(
            start=datetime(2025, 6, 15, 18, 0, tzinfo=ZoneInfo("UTC")),
            end=datetime(2025, 6, 15, 19, 0, tzinfo=ZoneInfo("UTC")),
        )
        assert a.overlaps_with(b) is True


# ---------------------------------------------------------------------------
# TimeSlotManager tests
# ---------------------------------------------------------------------------


class TestTimeSlotManager:
    """Tests for the TimeSlotManager availability check."""

    def test_available_slot_returns_available_true(self) -> None:
        """A slot with no conflicts should return available=True with an event."""
        manager = TimeSlotManager(
            requested_slot={
                "date": "2025-06-15",
                "start_time": "10:00",
                "end_time": "11:00",
                "timezone": "America/New_York",
                "attendee_name": "Jane Doe",
                "attendee_email": "jane@example.com",
            },
            existing_events=[
                {
                    "summary": "Morning Standup",
                    "start": "2025-06-15T09:00:00-04:00",
                    "end": "2025-06-15T09:30:00-04:00",
                },
            ],
        )
        result = manager.check_availability()
        assert result["available"] is True
        assert result["event"] is not None
        assert result["conflict_reason"] is None
        assert result["suggested_slots"] == []
        assert "Booked Appointment" in result["event"]["summary"]

    def test_conflicting_slot_returns_available_false(self) -> None:
        """A slot overlapping an existing event should return available=False."""
        manager = TimeSlotManager(
            requested_slot={
                "date": "2025-06-15",
                "start_time": "14:00",
                "end_time": "15:00",
                "timezone": "America/New_York",
            },
            existing_events=[
                {
                    "summary": "Existing Meeting",
                    "start": "2025-06-15T14:00:00-04:00",
                    "end": "2025-06-15T15:00:00-04:00",
                },
            ],
        )
        result = manager.check_availability()
        assert result["available"] is False
        assert result["event"] is None
        assert result["conflict_reason"] is not None
        assert "Existing Meeting" in result["conflict_reason"]

    def test_conflict_suggests_alternative_slots(self) -> None:
        """A conflicting slot should include suggested_slots."""
        manager = TimeSlotManager(
            requested_slot={
                "date": "2025-06-15",
                "start_time": "14:00",
                "end_time": "15:00",
                "timezone": "America/New_York",
            },
            existing_events=[
                {
                    "summary": "Existing Meeting",
                    "start": "2025-06-15T14:00:00-04:00",
                    "end": "2025-06-15T15:00:00-04:00",
                },
            ],
        )
        result = manager.check_availability()
        assert len(result["suggested_slots"]) > 0

    def test_slot_fully_contained_in_existing_event(self) -> None:
        """A requested slot fully inside an existing event should conflict."""
        manager = TimeSlotManager(
            requested_slot={
                "date": "2025-06-15",
                "start_time": "14:30",
                "end_time": "14:45",
                "timezone": "America/New_York",
            },
            existing_events=[
                {
                    "summary": "Long Meeting",
                    "start": "2025-06-15T14:00:00-04:00",
                    "end": "2025-06-15T16:00:00-04:00",
                },
            ],
        )
        result = manager.check_availability()
        assert result["available"] is False

    def test_no_existing_events_is_available(self) -> None:
        """A slot with no existing events at all should be available."""
        manager = TimeSlotManager(
            requested_slot={
                "date": "2025-06-15",
                "start_time": "14:00",
                "end_time": "15:00",
                "timezone": "America/New_York",
            },
            existing_events=[],
        )
        result = manager.check_availability()
        assert result["available"] is True
        assert result["event"] is not None


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

    def test_input_has_required_keys(self) -> None:
        """The input fixture should have all required keys."""
        data = _load_input()
        assert "requested_slot" in data
        assert "attendee" in data
        assert "existing_events" in data

    def test_output_has_required_keys(self) -> None:
        """The run() output should have all required keys."""
        result = run(pattern_path=str(HERE))
        assert "available" in result
        assert "suggested_slots" in result
        assert "event" in result
        assert "conflict_reason" in result

    def test_conflict_scenario_from_fixture(self) -> None:
        """The fixture's conflicting slot should return available=False."""
        result = run(pattern_path=str(HERE))
        assert result["available"] is False
        assert result["conflict_reason"] is not None
        assert len(result["suggested_slots"]) > 0
