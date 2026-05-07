"""Pattern 4: Calendar Booking — timezone-aware availability check with
alternative slot suggestion.

A TimeSlotManager checks a requested slot against existing calendar events,
detects overlaps, and suggests alternative time slots when a conflict is found.

Usage:
    from auto_kit.pattern_runner import run_pattern_module
    result = run_pattern_module("patterns/calendar-booking")
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


class Slot:
    """A time slot with timezone-aware boundaries."""

    __slots__ = ("start", "end")

    def __init__(self, start: datetime, end: datetime) -> None:
        self.start = start
        self.end = end

    def overlaps_with(self, other: Slot) -> bool:
        """Check if two time slots overlap.

        Overlap occurs when one slot starts before the other ends AND
        ends after the other starts.
        """
        return self.start < other.end and self.end > other.start


# ---------------------------------------------------------------------------
# TimeSlotManager
# ---------------------------------------------------------------------------


class TimeSlotManager:
    """Check calendar availability and suggest alternative slots.

    Converts all times to timezone-aware datetimes for proper comparison,
    even when timezone offsets differ (e.g. EDT vs EST).
    """

    def __init__(
        self, requested_slot: dict[str, Any], existing_events: list[dict[str, Any]]
    ) -> None:
        self.requested_slot = requested_slot
        self.existing_events = existing_events

    def check_availability(self) -> dict[str, Any]:
        """Check if the requested slot is available.

        Returns:
            dict with fields:
                - available (bool): True if no conflicts
                - suggested_slots (list): alternative slots when unavailable
                - event (dict|None): the created event when available
                - conflict_reason (str|None): description of conflict
        """
        tz_str = self.requested_slot.get("timezone", "UTC")
        tz = ZoneInfo(tz_str)

        # Parse the requested slot boundaries
        req_start = datetime.fromisoformat(
            f"{self.requested_slot['date']}T{self.requested_slot['start_time']}"
        ).replace(tzinfo=tz)
        req_end = datetime.fromisoformat(
            f"{self.requested_slot['date']}T{self.requested_slot['end_time']}"
        ).replace(tzinfo=tz)

        requested = Slot(start=req_start, end=req_end)
        duration = req_end - req_start

        # Check each existing event for overlap
        for event in self.existing_events:
            evt_start = datetime.fromisoformat(event["start"])
            evt_end = datetime.fromisoformat(event["end"])

            existing = Slot(start=evt_start, end=evt_end)

            if requested.overlaps_with(existing):
                # Conflict found — generate alternative suggestions
                suggested = self._suggest_alternatives(
                    requested=requested,
                    duration=duration,
                    conflicting_event=event,
                    tz=tz,
                )
                return {
                    "available": False,
                    "suggested_slots": suggested,
                    "event": None,
                    "conflict_reason": (
                        f"Time slot overlaps with existing event: {event['summary']}"
                    ),
                }

        # No conflict — slot is available
        event_payload = {
            "summary": "Booked Appointment",
            "start": req_start.isoformat(),
            "end": req_end.isoformat(),
            "attendee": {
                "name": self.requested_slot.get("attendee_name", ""),
                "email": self.requested_slot.get("attendee_email", ""),
            },
        }

        return {
            "available": True,
            "suggested_slots": [],
            "event": event_payload,
            "conflict_reason": None,
        }

    def _suggest_alternatives(
        self,
        requested: Slot,
        duration: timedelta,
        conflicting_event: dict[str, Any],
        tz: ZoneInfo,
    ) -> list[dict[str, str]]:
        """Suggest up to 3 alternative time slots when a conflict is found.

        Strategy:
          1. Slot right after the conflicting event (same day)
          2. Slot right before the conflicting event (same day)
          3. Same time on the next calendar day

        Each suggestion checks it doesn't overlap with *any* existing event
        before including it.
        """
        suggestions: list[dict[str, str]] = []

        # Convert existing events to Slot objects for overlap checks
        existing_slots = [
            Slot(
                start=datetime.fromisoformat(e["start"]),
                end=datetime.fromisoformat(e["end"]),
            )
            for e in self.existing_events
        ]

        candidates: list[Slot] = []

        # 1. Slot after the conflicting event
        conflict_end = datetime.fromisoformat(conflicting_event["end"])
        after = Slot(start=conflict_end, end=conflict_end + duration)
        candidates.append(after)

        # 2. Slot before the conflicting event
        conflict_start = datetime.fromisoformat(conflicting_event["start"])
        before = Slot(start=conflict_start - duration, end=conflict_start)
        candidates.append(before)

        # 3. Same time, next calendar day
        next_day_start = requested.start + timedelta(days=1)
        next_day = Slot(
            start=next_day_start,
            end=next_day_start + duration,
        )
        candidates.append(next_day)

        for slot in candidates:
            if self._is_free(slot, existing_slots):
                suggestions.append(self._slot_to_dict(slot, tz))

        return suggestions

    @staticmethod
    def _is_free(slot: Slot, existing_slots: list[Slot]) -> bool:
        """Check if a candidate slot does not overlap with any existing event."""
        return not any(slot.overlaps_with(ex) for ex in existing_slots)

    @staticmethod
    def _slot_to_dict(slot: Slot, tz: ZoneInfo) -> dict[str, str]:
        """Convert a Slot to the output dictionary format.

        The slot times are converted to the target timezone and rendered
        as date / time strings matching the input format.
        """
        local_start = slot.start.astimezone(tz)
        local_end = slot.end.astimezone(tz)
        return {
            "date": local_start.strftime("%Y-%m-%d"),
            "start_time": local_start.strftime("%H:%M"),
            "end_time": local_end.strftime("%H:%M"),
            "timezone": str(tz),
        }


# ---------------------------------------------------------------------------
# Pattern run entry point
# ---------------------------------------------------------------------------


def run(pattern_path: str | None = None) -> dict[str, Any]:
    """Load input.json fixture, run availability check, return result.

    This function is called by the pattern runner (auto_kit.pattern_runner)
    with pattern_path pointing to the pattern's root directory.
    """
    if pattern_path is None:
        pattern_path = str(Path(__file__).resolve().parent.parent)

    base = Path(pattern_path)
    input_path = base / "fixtures" / "input.json"

    with open(input_path) as f:
        data: dict[str, Any] = json.load(f)

    # Extract attendee info into slot for event creation
    attendee = data.get("attendee", {})
    requested_slot = dict(data["requested_slot"])
    requested_slot["attendee_name"] = attendee.get("name", "")
    requested_slot["attendee_email"] = attendee.get("email", "")

    manager = TimeSlotManager(
        requested_slot=requested_slot,
        existing_events=data.get("existing_events", []),
    )

    return manager.check_availability()


# ---------------------------------------------------------------------------
# CLI shortcut
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps(result, indent=2))
