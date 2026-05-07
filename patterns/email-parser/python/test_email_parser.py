"""Tests for the Email Parser + AI pattern."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Import main.py via importlib (directory has a hyphen, so standard
# syntax like "from patterns.email_parser.python.main import ..."
# would not work).
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "email_parser_main", HERE / "python" / "main.py"
)
assert _spec is not None and _spec.loader is not None, "Could not load main.py"
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

DeterministicClassifier = _mod.DeterministicClassifier
run = _mod.run


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _load_fixture(name: str) -> dict:
    with open(HERE / "fixtures" / name) as f:
        return dict(json.load(f))


def _load_emails() -> list[dict]:
    with open(HERE / "fixtures" / "input.json") as f:
        return list(json.load(f))


# ---------------------------------------------------------------------------
# DeterministicClassifier tests
# ---------------------------------------------------------------------------


class TestDeterministicClassifier:
    """Unit tests for the keyword-based classifier."""

    def setup_method(self) -> None:
        self.classifier = DeterministicClassifier()

    def test_support_intent_detected(self) -> None:
        """Support keywords ('help', 'setup') should classify as support."""
        email = {
            "id": "t1",
            "from": "a@test.com",
            "subject": "Help with setup",
            "body": "How do I configure the API?",
            "received_at": "2025-01-01T00:00:00Z",
        }
        result = self.classifier.classify(email)
        assert result["intent"] == "support"
        assert result["queue"] == "support"
        assert result["confidence"] > 0.6

    def test_sales_intent_detected(self) -> None:
        """Pricing and plan keywords should classify as sales."""
        email = {
            "id": "t2",
            "from": "b@test.com",
            "subject": "Pricing inquiry",
            "body": "What are your subscription plan costs?",
            "received_at": "2025-01-01T00:00:00Z",
        }
        result = self.classifier.classify(email)
        assert result["intent"] == "sales"
        assert result["queue"] == "sales"
        assert result["confidence"] > 0.6

    def test_billing_intent_detected(self) -> None:
        """Invoice and refund keywords should classify as billing."""
        email = {
            "id": "t3",
            "from": "c@test.com",
            "subject": "Invoice",
            "body": "I need a refund for an overcharge on my last bill.",
            "received_at": "2025-01-01T00:00:00Z",
        }
        result = self.classifier.classify(email)
        assert result["intent"] == "billing"
        assert result["queue"] == "billing"
        assert result["confidence"] > 0.6

    def test_spam_intent_detected(self) -> None:
        """Viagra / limited-offer keywords should classify as spam."""
        email = {
            "id": "t4",
            "from": "spam@example.com",
            "subject": "Viagra",
            "body": "Limited offer! Buy now!",
            "received_at": "2025-01-01T00:00:00Z",
        }
        result = self.classifier.classify(email)
        assert result["intent"] == "spam"
        assert result["queue"] == "spam"
        assert result["confidence"] > 0.6

    def test_low_confidence_routes_to_human_review(self) -> None:
        """A vague greeting with no keywords should route to human_review."""
        email = {
            "id": "t5",
            "from": "d@test.com",
            "subject": "Hi",
            "body": "Just checking in.",
            "received_at": "2025-01-01T00:00:00Z",
        }
        result = self.classifier.classify(email)
        assert result["queue"] == "human_review"
        assert result["intent"] == "unknown"
        assert result["confidence"] < 0.6

    def test_boundary_confidence_just_below_threshold(self) -> None:
        """One weak keyword match should produce confidence < 0.6."""
        email = {
            "id": "t6",
            "from": "e@test.com",
            "subject": "Question",
            "body": "I have a question about cost.",
            "received_at": "2025-01-01T00:00:00Z",
        }
        result = self.classifier.classify(email)
        # 'cost' is a sales keyword -> 1 match -> confidence = 0.35
        assert result["confidence"] == 0.35
        assert result["queue"] == "human_review"

    def test_spam_takes_priority_over_other_intents(self) -> None:
        """If spam keywords are present, email routes to spam regardless."""
        email = {
            "id": "t7",
            "from": "f@test.com",
            "subject": "Viagra pricing plans",
            "body": "Limited offer on all subscription costs!",
            "received_at": "2025-01-01T00:00:00Z",
        }
        result = self.classifier.classify(email)
        # Contains both spam ('viagra', 'limited offer') and sales ('pricing',
        # 'plans', 'subscription', 'costs') keywords. If spam has at least
        # one match, it should be routed to spam.
        assert result["queue"] == "spam"

    def test_multiple_matches_give_full_confidence(self) -> None:
        """Three or more keyword matches yields confidence = 1.0."""
        email = {
            "id": "t8",
            "from": "g@test.com",
            "subject": "Help, error with setup",
            "body": "I have a bug. The installation guide is broken.",
            "received_at": "2025-01-01T00:00:00Z",
        }
        result = self.classifier.classify(email)
        # keywords: help, error, setup, bug, guide, broken = 6 matches
        assert result["confidence"] == 1.0
        assert result["intent"] == "support"


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

    def test_all_emails_classified(self) -> None:
        """All input emails should appear in the output."""
        n_input = len(_load_emails())
        result = run(pattern_path=str(HERE))
        assert len(result["classified_emails"]) == n_input

    def test_spam_email_routed_correctly(self) -> None:
        """The spam fixture email should be routed to spam queue."""
        result = run(pattern_path=str(HERE))
        spam = [e for e in result["classified_emails"] if e["id"] == "email_004"]
        assert len(spam) == 1
        assert spam[0]["queue"] == "spam"
        assert spam[0]["intent"] == "spam"

    def test_low_confidence_routed_correctly(self) -> None:
        """The vague fixture email should be routed to human_review."""
        result = run(pattern_path=str(HERE))
        vague = [e for e in result["classified_emails"] if e["id"] == "email_005"]
        assert len(vague) == 1
        assert vague[0]["queue"] == "human_review"
        assert vague[0]["confidence"] < 0.6
