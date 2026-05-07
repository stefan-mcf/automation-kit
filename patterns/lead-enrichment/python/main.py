"""Pattern 3: Lead Enrichment — enrich raw leads against MockLeadDatabase."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from auto_kit.mock_clients import MockLeadDatabase


def run(pattern_path: str | None = None) -> dict[str, Any]:
    """Load input leads, enrich via MockLeadDatabase, return summary.

    Args:
        pattern_path: Path to the pattern directory (containing fixtures/).

    Returns:
        dict with 'enriched_leads', 'total', 'enriched', 'needs_research'.
    """
    base = Path(pattern_path) if pattern_path else Path(__file__).resolve().parent.parent

    # Load input fixtures
    input_path = base / "fixtures" / "input.json"
    with open(input_path) as f:
        leads: list[dict[str, Any]] = json.load(f)

    db = MockLeadDatabase()
    enriched_leads: list[dict[str, Any]] = []
    enriched_count = 0
    needs_research_count = 0

    for lead in leads:
        domain = lead.get("domain", "")
        enrichment = db.enrich(domain)

        if enrichment is not None:
            record = {
                "company": enrichment.get("company", lead.get("company")),
                "domain": domain,
                "industry": enrichment.get("industry"),
                "size": enrichment.get("size"),
                "region": enrichment.get("region"),
                "contact_role": enrichment.get("contact_role"),
                "source_url": enrichment.get("source_url"),
                "contact_name": lead.get("contact_name"),
                "email": lead.get("email"),
                "enrichment_status": "enriched",
            }
            enriched_count += 1
        else:
            record = {
                "company": lead.get("company"),
                "domain": domain,
                "industry": None,
                "size": None,
                "region": None,
                "contact_role": None,
                "source_url": None,
                "contact_name": lead.get("contact_name"),
                "email": lead.get("email"),
                "enrichment_status": "needs_research",
            }
            needs_research_count += 1

        enriched_leads.append(record)

    return {
        "enriched_leads": enriched_leads,
        "total": len(leads),
        "enriched": enriched_count,
        "needs_research": needs_research_count,
    }
