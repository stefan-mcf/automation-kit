"""Tests for the Social Listening Triage pattern."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "social_listening_main", HERE / "python" / "main.py"
)
assert _spec is not None and _spec.loader is not None, "Could not load main.py"
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

SocialListeningTriage = _mod.SocialListeningTriage
run = _mod.run


def _load_fixture(name: str) -> dict:
    with open(HERE / "fixtures" / name) as f:
        return dict(json.load(f))


class TestSocialListeningTriage:
    """Unit tests for mention matching and priority scoring."""

    def setup_method(self) -> None:
        self.triage = SocialListeningTriage(
            {"name": "Test Monitor", "keywords": ["xquik"], "min_engagement": 10}
        )

    def test_matches_keywords_case_insensitively(self) -> None:
        result = self.triage.process_mentions(
            [
                {
                    "id": "1",
                    "author": "tester",
                    "text": "XQUIK launch notes",
                    "likes": 5,
                    "reposts": 5,
                    "url": "https://x.com/tester/status/1",
                }
            ]
        )

        assert result["matched_count"] == 1
        assert result["alerts"][0]["matched_keywords"] == ["xquik"]

    def test_ignores_non_matching_mentions(self) -> None:
        result = self.triage.process_mentions(
            [
                {
                    "id": "2",
                    "author": "tester",
                    "text": "unrelated automation note",
                    "likes": 100,
                    "reposts": 100,
                    "url": "https://x.com/tester/status/2",
                }
            ]
        )

        assert result["matched_count"] == 0
        assert result["priority_count"] == 0

    def test_scores_priority_from_likes_and_reposts(self) -> None:
        result = self.triage.process_mentions(
            [
                {
                    "id": "3",
                    "author": "tester",
                    "text": "xquik monitoring",
                    "likes": 8,
                    "reposts": 3,
                    "url": "https://x.com/tester/status/3",
                }
            ]
        )

        assert result["alerts"][0]["engagement"] == 11
        assert result["alerts"][0]["priority"] is True


class TestRunOutput:
    """Verify run() matches expected_output.json."""

    def test_run_matches_expected_fixture(self) -> None:
        expected = _load_fixture("expected_output.json")
        actual = run(str(HERE))

        assert actual == expected
