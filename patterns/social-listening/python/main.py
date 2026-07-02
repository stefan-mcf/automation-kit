"""Pattern: Social Listening Triage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _matching_keywords(text: str, keywords: list[str]) -> list[str]:
    normalized = text.lower()
    return [keyword for keyword in keywords if keyword.lower() in normalized]


def _engagement(mention: dict[str, Any]) -> int:
    return int(mention.get("likes", 0)) + int(mention.get("reposts", 0))


class SocialListeningTriage:
    """Match exported social mentions and prepare deterministic review alerts."""

    def __init__(self, monitor: dict[str, Any]) -> None:
        self.monitor_name = str(monitor.get("name", "Social Monitor"))
        self.keywords = [str(keyword) for keyword in monitor.get("keywords", [])]
        self.min_engagement = int(monitor.get("min_engagement", 0))

    def process_mentions(self, mentions: list[dict[str, Any]]) -> dict[str, Any]:
        alerts: list[dict[str, Any]] = []

        for mention in mentions:
            matched_keywords = _matching_keywords(str(mention.get("text", "")), self.keywords)
            if not matched_keywords:
                continue

            engagement = _engagement(mention)
            alerts.append(
                {
                    "id": str(mention.get("id", "")),
                    "author": str(mention.get("author", "")),
                    "engagement": engagement,
                    "matched_keywords": matched_keywords,
                    "priority": engagement >= self.min_engagement,
                    "url": str(mention.get("url", "")),
                }
            )

        priority_count = sum(1 for alert in alerts if alert["priority"])
        return {
            "pattern": "social-listening",
            "fixture_safe": True,
            "live_services_used": False,
            "monitor": self.monitor_name,
            "matched_count": len(alerts),
            "priority_count": priority_count,
            "alerts": alerts,
            "summary": f"{len(alerts)} matching mentions, {priority_count} priority follow-ups",
        }


def run(pattern_path: str | None = None) -> dict[str, Any]:
    """Load the fixture batch and return social listening review output."""
    if pattern_path is None:
        pattern_path = str(Path(__file__).resolve().parent.parent)

    base = Path(pattern_path)
    with open(base / "fixtures" / "input.json") as f:
        payload = dict(json.load(f))

    triage = SocialListeningTriage(dict(payload.get("monitor", {})))
    return triage.process_mentions(list(payload.get("mentions", [])))


if __name__ == "__main__":
    import sys

    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps(result, indent=2))
