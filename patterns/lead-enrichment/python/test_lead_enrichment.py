"""Tests for Pattern 3: Lead Enrichment."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

PATTERN_DIR = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PATTERN_DIR / "fixtures"


def _load_main_module():
    """Dynamically load main.py (patterns dir is not a Python package)."""
    main_py = PATTERN_DIR / "python" / "main.py"
    spec = importlib.util.spec_from_file_location("lead_enrichment_main", main_py)
    assert spec is not None and spec.loader is not None, f"Could not load {main_py}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_fixture(name: str) -> Any:
    path = FIXTURES_DIR / name
    with open(path) as f:
        return json.load(f)


class TestLeadEnrichment:
    """Test suite for lead enrichment pattern."""

    def test_known_companies_return_full_enrichment(self):
        """Known companies should return full enrichment data."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))

        # Acme Corp
        acme = next(rec for rec in result["enriched_leads"] if rec["domain"] == "acmecorp.com")
        assert acme["industry"] == "Manufacturing"
        assert acme["size"] == "500-1000"
        assert acme["region"] == "North America"
        assert acme["contact_role"] == "CTO"
        assert acme["source_url"] == "https://acmecorp.example.com"
        assert acme["enrichment_status"] == "enriched"
        assert acme["contact_name"] == "John Smith"
        assert acme["email"] == "john@acmecorp.com"

        # Globex
        globex = next(rec for rec in result["enriched_leads"] if rec["domain"] == "globex.io")
        assert globex["industry"] == "Software"
        assert globex["size"] == "50-200"
        assert globex["region"] == "Europe"
        assert globex["contact_role"] == "VP Engineering"
        assert globex["source_url"] == "https://globex.example.io"
        assert globex["enrichment_status"] == "enriched"

        # Initech
        initech = next(rec for rec in result["enriched_leads"] if rec["domain"] == "initech.org")
        assert initech["industry"] == "Technology"
        assert initech["size"] == "200-500"
        assert initech["region"] == "North America"
        assert initech["contact_role"] == "CTO"
        assert initech["source_url"] == "https://initech.example.org"
        assert initech["enrichment_status"] == "enriched"

    def test_missing_company_marked_needs_research(self):
        """Unknown domains should be marked needs_research, not silently dropped."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))

        unknown = next(
            (rec for rec in result["enriched_leads"] if rec["domain"] == "unknowncorp.xyz"),
            None,
        )
        assert unknown is not None, "Unknown domain should NOT be silently dropped"
        assert unknown["enrichment_status"] == "needs_research"
        assert unknown["industry"] is None
        assert unknown["size"] is None
        assert unknown["region"] is None
        assert unknown["contact_role"] is None
        assert unknown["source_url"] is None
        # Contact info from input should still be present
        assert unknown["contact_name"] == "Alice Wonder"
        assert unknown["email"] == "alice@unknowncorp.xyz"
        assert unknown["company"] == "Unknown Corp"

    def test_output_shape_matches_expected(self):
        """Output shape should match the expected output structure."""
        mod = _load_main_module()
        result = mod.run(pattern_path=str(PATTERN_DIR))
        expected = _load_fixture("expected_output.json")

        # Same top-level keys
        assert set(result.keys()) == {"enriched_leads", "total", "enriched", "needs_research"}

        # Same counts
        assert result["total"] == expected["total"] == 4
        assert result["enriched"] == expected["enriched"] == 3
        assert result["needs_research"] == expected["needs_research"] == 1
        assert len(result["enriched_leads"]) == len(expected["enriched_leads"]) == 4

        # Each record has the same keys
        required_keys = {
            "company", "domain", "industry", "size", "region",
            "contact_role", "source_url", "contact_name", "email",
            "enrichment_status",
        }
        for record in result["enriched_leads"]:
            assert set(record.keys()) == required_keys, (
                f"Record for {record.get('domain')} has unexpected keys"
            )
