"""Email parser + AI pattern: classify incoming emails by intent using keyword-based
DeterministicClassifier, then route to appropriate queue (support/sales/billing/spam/human_review).

Usage:
    from auto_kit.pattern_runner import run_pattern_module
    result = run_pattern_module("patterns/email-parser")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# DeterministicClassifier — keyword matching + confidence scoring
# ---------------------------------------------------------------------------


class DeterministicClassifier:
    """Classify email intent using keyword matching with confidence scoring.

    Scores each intent category by counting how many of its keywords appear
    as substrings (case-insensitive) in the concatenated subject + body.
    Confidence is derived from the top score: min(1.0, score * 0.35).
    Emails below the confidence threshold or with no matches are routed to
    human_review.

    Spam is checked first, before non-spam intent scoring. If any spam
    keywords match, the email is immediately routed to the spam queue,
    regardless of other intents.
    """

    INTENT_KEYWORDS: dict[str, list[str]] = {
        "support": [
            "setup",
            "help",
            "how do i",
            "install",
            "error",
            "bug",
            "issue",
            "problem",
            "troubleshoot",
            "configure",
            "not working",
            "broken",
            "guide",
            "tutorial",
        ],
        "sales": [
            "pricing",
            "price",
            "quote",
            "cost",
            "how much",
            "subscription",
            "plan",
            "plans",
            "license",
            "buy",
            "purchase",
            "upgrade",
            "trial",
            "sales call",
        ],
        "billing": [
            "invoice",
            "bill",
            "payment",
            "charge",
            "receipt",
            "refund",
            "billing",
            "paid",
            "credit card",
            "overcharge",
            "statement",
        ],
        "spam": [
            "viagra",
            "cialis",
            "enlarge",
            "click here",
            "limited offer",
            "free money",
            "congratulations",
            "winner",
            "lottery",
            "buy now",
            "act now",
            "investment opportunity",
            "earn money fast",
            "weight loss",
            "miracle cure",
        ],
    }

    CONFIDENCE_THRESHOLD: float = 0.6

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, email: dict[str, Any]) -> dict[str, Any]:
        """Classify a single email and return the routing result.

        Spam detection runs first — if any spam keywords match, the email
        is immediately routed to the spam queue.  Non-spam intents are only
        considered if no spam keywords are found.
        """
        text = self._combine_text(email)

        # 1. Spam check — takes priority over everything else
        spam_score = self._score_single_intent("spam", text)
        if spam_score > 0:
            return {
                "id": email["id"],
                "intent": "spam",
                "confidence": min(1.0, spam_score * 0.35),
                "queue": "spam",
                "summary": self._build_spam_summary(email),
            }

        # 2. Score non-spam intents
        scores = self._score_non_spam(text)
        top_intent, top_score = self._top_scoring(scores)

        confidence = min(1.0, top_score * 0.35) if top_score > 0 else 0.0

        # When all scores are 0, top_intent is "unknown"
        intent = top_intent if top_score > 0 else "unknown"
        queue = self._determine_queue(intent, confidence)

        return {
            "id": email["id"],
            "intent": intent,
            "confidence": confidence,
            "queue": queue,
            "summary": self._build_summary(queue, intent, email),
        }

    def classify_many(
        self, emails: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Classify a list of emails."""
        return [self.classify(e) for e in emails]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _combine_text(email: dict[str, Any]) -> str:
        subject = email.get("subject", "")
        body = email.get("body", "")
        return f"{subject} {body}".lower()

    def _score_single_intent(self, intent: str, text: str) -> int:
        """Count keyword matches for a single intent category."""
        keywords = self.INTENT_KEYWORDS.get(intent, [])
        return sum(1 for kw in keywords if kw in text)

    def _score_non_spam(self, text: str) -> dict[str, int]:
        """Score all non-spam intents."""
        scores: dict[str, int] = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if intent == "spam":
                continue
            count = sum(1 for kw in keywords if kw in text)
            scores[intent] = count
        return scores

    @staticmethod
    def _top_scoring(
        scores: dict[str, int],
    ) -> tuple[str, int]:
        """Return (intent_name, score) for the highest-scoring intent.

        If all scores are 0 this returns ("unknown", 0).
        """
        best_intent = "unknown"
        best_score = -1
        for intent, score in scores.items():
            if score > best_score:
                best_score = score
                best_intent = intent
        return best_intent, best_score

    @staticmethod
    def _determine_queue(intent: str, confidence: float) -> str:
        """Determine the routing queue based on intent and confidence."""
        if confidence < 0.6:
            return "human_review"
        return intent

    @staticmethod
    def _build_summary(
        queue: str, intent: str, email: dict[str, Any]
    ) -> str:
        """Build a short human-readable summary of the routing decision."""
        subject = email.get("subject", "no subject")
        if queue == "human_review":
            return (
                f"Routed to human_review: low confidence "
                f"(no actionable keywords detected) — \"{subject}\""
            )
        if queue == "spam":
            return (
                f"Routed to spam: unsolicited advertisement detected "
                f"— \"{subject}\""
            )
        return f"Routed to {queue}: \"{subject}\""

    @staticmethod
    def _build_spam_summary(email: dict[str, Any]) -> str:
        """Build summary for spam-routed emails."""
        subject = email.get("subject", "no subject")
        return (
            f"Routed to spam: unsolicited advertisement detected "
            f"— \"{subject}\""
        )


# ---------------------------------------------------------------------------
# Pattern run entry point
# ---------------------------------------------------------------------------


def run(pattern_path: str | None = None) -> dict[str, Any]:
    """Load input.json, classify each email, return classified results.

    This function is called by the pattern runner (auto_kit.pattern_runner)
    with pattern_path pointing to the pattern's root directory.
    """
    if pattern_path is None:
        pattern_path = str(Path(__file__).resolve().parent.parent)

    base = Path(pattern_path)
    input_path = base / "fixtures" / "input.json"

    with open(input_path) as f:
        emails: list[dict[str, Any]] = json.load(f)

    classifier = DeterministicClassifier()
    classified = classifier.classify_many(emails)

    return {"classified_emails": classified}


# ---------------------------------------------------------------------------
# CLI shortcut
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps(result, indent=2))
