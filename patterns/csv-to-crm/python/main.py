"""Pattern 1: CSV to CRM Sync.

Reads leads from a CSV file, dedupes by email (keeping the last occurrence),
and upserts them into a CRM via MockCRMClient.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from auto_kit.mock_clients import MockCRMClient


def run(pattern_path: str | None = None) -> dict[str, Any]:
    """Run the CSV to CRM sync pattern.

    Args:
        pattern_path: Path to the pattern directory. If None, defaults to
            the directory containing this source file's expected parent layout.

    Returns:
        Dict with 'upserted_contacts' (list of CRM records), 'total' (int),
        and 'deduped_count' (int).
    """
    if pattern_path is None:
        # Fall back to layout-relative resolution
        base = Path(__file__).resolve().parent.parent
    else:
        base = Path(pattern_path)

    csv_path = base / "fixtures" / "input.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    # Load CSV rows
    rows: list[dict[str, str]] = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))

    total_raw = len(rows)

    # Dedupe by email — keep last occurrence
    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        email = row.get("email", "").lower().strip()
        if email:
            seen[email] = row

    deduped_count = total_raw - len(seen)

    # Build payloads and upsert
    client = MockCRMClient()
    contacts: list[dict[str, Any]] = []
    for email, row in seen.items():
        contacts.append({
            "email": email,
            "name": row.get("name", ""),
            "company": row.get("company", ""),
            "phone": row.get("phone", ""),
            "source": row.get("source", ""),
        })

    upserted = client.batch_upsert(contacts)

    return {
        "upserted_contacts": upserted,
        "total": total_raw,
        "deduped_count": deduped_count,
    }
