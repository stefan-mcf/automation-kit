"""Mock external-service clients for deterministic pattern testing (no live credentials)."""

from __future__ import annotations

import hashlib
from typing import Any


class MockCRMClient:
    """Simulates a CRM API client (HubSpot, Salesforce, etc.)."""

    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}
        self.upsert_history: list[dict[str, Any]] = []

    def upsert_contact(self, email: str, data: dict[str, Any]) -> dict[str, Any]:
        """Upsert a contact by email. Returns the contact record."""
        key = email.lower().strip()
        record = {"email": key, **data, "id": hashlib.md5(key.encode()).hexdigest()[:8]}
        self.records[key] = record
        self.upsert_history.append({"action": "upsert", "email": key, "data": data})
        return dict(record)

    def batch_upsert(self, contacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Batch upsert contacts."""
        return [self.upsert_contact(c.pop("email", "unknown@example.com"), c) for c in contacts]


class MockEmailClient:
    """Simulates an email client / inbox."""

    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    def send(self, to: str, subject: str, body: str) -> dict[str, Any]:
        record = {"to": to, "subject": subject, "body_preview": body[:100]}
        self.sent.append(record)
        return record


class MockSlackClient:
    """Simulates a Slack/Teams webhook sender."""

    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []

    def send_alert(self, channel: str, text: str, severity: str = "info") -> dict[str, Any]:
        record = {"channel": channel, "text": text, "severity": severity}
        self.messages.append(record)
        return record


class MockCalendarClient:
    """Simulates a calendar API (Google Calendar, Outlook, etc.)."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.created_events: list[dict[str, Any]] = []


class MockLeadDatabase:
    """Simulates a lead enrichment data source."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {
            "acmecorp.com": {
                "company": "Acme Corp",
                "industry": "Manufacturing",
                "size": "500-1000",
                "region": "North America",
                "contact_role": "CTO",
                "source_url": "https://acmecorp.example.com",
            },
            "globex.io": {
                "company": "Globex Inc.",
                "industry": "Software",
                "size": "50-200",
                "region": "Europe",
                "contact_role": "VP Engineering",
                "source_url": "https://globex.example.io",
            },
            "initech.org": {
                "company": "Initech",
                "industry": "Technology",
                "size": "200-500",
                "region": "North America",
                "contact_role": "CTO",
                "source_url": "https://initech.example.org",
            },
        }

    def enrich(self, domain: str) -> dict[str, Any] | None:
        """Look up enrichment data by domain. Returns None for unknown domains."""
        return self._data.get(domain.lower().strip())
