"""Tests for CSV to CRM Sync pattern."""

from __future__ import annotations

import json
from pathlib import Path

from auto_kit.mock_clients import MockCRMClient

HERE = Path(__file__).resolve().parent.parent
FIXTURES = HERE / "fixtures"


def _load_csv_rows() -> list[dict[str, str]]:
    """Helper to load CSV as list of dicts."""
    import csv

    rows: list[dict[str, str]] = []
    with open(FIXTURES / "input.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def _run_main() -> dict:
    """Run the pattern's main function."""
    import sys

    sys.path.insert(0, str(HERE / "python"))
    from main import run as pattern_run

    return pattern_run(pattern_path=str(HERE))


class TestCsvDedup:
    """Tests for CSV parsing and email deduplication."""

    def test_csv_parsed_correct_row_count(self):
        """CSV should parse to 6 rows."""
        rows = _load_csv_rows()
        assert len(rows) == 6

    def test_csv_has_expected_columns(self):
        """CSV should have the expected column headers."""
        rows = _load_csv_rows()
        expected_columns = {"name", "email", "company", "phone", "source"}
        assert set(rows[0].keys()) == expected_columns

    def test_dedup_keeps_last_occurrence(self):
        """Duplicate emails should be deduped, keeping the last occurrence."""
        rows = _load_csv_rows()

        seen: dict[str, dict[str, str]] = {}
        for row in rows:
            email = row.get("email", "").lower().strip()
            if email:
                seen[email] = row

        # alice@acmecorp.com appears twice — last row has company "Acme Corp Updated"
        alice = seen.get("alice@acmecorp.com")
        assert alice is not None
        assert alice["company"] == "Acme Corp Updated"
        assert alice["phone"] == "+1-555-0105"
        assert alice["source"] == "email"

    def test_dedup_count_is_correct(self):
        """Should report exactly 1 duplicate email removed."""
        result = _run_main()
        assert result["deduped_count"] == 1
        assert result["total"] == 6

    def test_unique_emails_preserved(self):
        """Non-duplicate emails should all be present after dedup."""
        result = _run_main()
        upserted = result["upserted_contacts"]
        emails = {c["email"] for c in upserted}
        expected = {
            "alice@acmecorp.com",
            "bob@globex.io",
            "charlie@initech.org",
            "diana@acmecorp.com",
            "eve@initech.org",
        }
        assert emails == expected

    def test_upserted_count_matches_deduped(self):
        """Number of upserted contacts should equal total minus deduped count."""
        result = _run_main()
        assert len(result["upserted_contacts"]) == result["total"] - result["deduped_count"]


class TestUpsertPayload:
    """Tests for upsert payload generation and MockCRMClient integration."""

    def test_batch_upsert_returns_records_with_ids(self):
        """batch_upsert should return records with id fields."""
        client = MockCRMClient()
        contacts = [
            {"email": "test@example.com", "name": "Test User", "company": "TestCo"},
        ]
        result = client.batch_upsert(contacts)
        assert len(result) == 1
        assert "id" in result[0]
        assert result[0]["email"] == "test@example.com"

    def test_upserted_contacts_have_contact_id(self):
        """CRM records should include a contact_id (id field)."""
        result = _run_main()
        for contact in result["upserted_contacts"]:
            assert "id" in contact
            assert len(contact["id"]) == 8

    def test_output_matches_expected_json(self):
        """run() output should exactly match expected_output.json."""
        with open(FIXTURES / "expected_output.json") as f:
            expected = json.load(f)
        result = _run_main()
        assert result == expected

    def test_mock_crm_client_tracks_history(self):
        """MockCRMClient should record upsert history."""
        client = MockCRMClient()
        client.batch_upsert([
            {"email": "a@b.com", "name": "A"},
            {"email": "c@d.com", "name": "C"},
        ])
        assert len(client.upsert_history) == 2
        assert client.upsert_history[0]["action"] == "upsert"
        assert client.upsert_history[0]["email"] == "a@b.com"


class TestEdgeCases:
    """Edge case tests for CSV parsing and dedup."""

    def test_empty_email_skipped(self):
        """Rows with empty email should not be upserted."""
        # This test uses a synthetic edge case inline
        rows = [
            {"email": "", "name": "No Email"},
            {"email": "valid@test.com", "name": "Valid"},
        ]
        seen: dict[str, dict[str, str]] = {}
        for row in rows:
            email = row.get("email", "").lower().strip()
            if email:
                seen[email] = row
        assert "valid@test.com" in seen
        assert "" not in seen
