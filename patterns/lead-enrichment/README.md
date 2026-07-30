# Pattern 3: Lead Enrichment

Enrich raw leads (company name, domain, contact info) with firmographic data
from a lead database. Handles known and unknown domains gracefully.

## Capabilities

1. Accepts a list of leads with `company`, `domain`, `contact_name`, `email`
2. Looks up each domain in the lead database (`MockLeadDatabase.enrich()`)
3. Merges enrichment data (industry, size, region, contact_role, source_url)
4. Marks unknown domains as `needs_research` instead of dropping them
5. Returns a summary with counts

## Input Format (fixtures/input.json)

```json
[
  {
    "company": "Acme Corp",
    "domain": "acmecorp.com",
    "contact_name": "John Smith",
    "email": "john@acmecorp.com"
  }
]
```

## Output Format

```json
{
  "enriched_leads": [
    {
      "company": "Acme Corp",
      "domain": "acmecorp.com",
      "industry": "Manufacturing",
      "size": "500-1000",
      "region": "North America",
      "contact_role": "CTO",
      "source_url": "https://acmecorp.example.com",
      "contact_name": "John Smith",
      "email": "john@acmecorp.com",
      "enrichment_status": "enriched"
    }
  ],
  "total": 1,
  "enriched": 1,
  "needs_research": 0
}
```

## Privacy Caveats

- **No PII enrichment**: The lead database (`MockLeadDatabase`) returns only
  firmographic data (industry, size, region). It never stores or returns
  personal information such as email addresses or phone numbers.
- **Passthrough only**: `contact_name` and `email` are passed through from
  input to output without modification. No additional PII is sourced.
- **Downstream responsibility**: If enriched leads are written to a CRM or
  data warehouse, ensure appropriate data retention and consent policies
  are followed.

## Data Quality Caveats

- **Silent unknowns handled**: Unknown domains are explicitly marked with
  `enrichment_status: "needs_research"` rather than being silently dropped.
  Downstream systems can use this flag to trigger manual enrichment flows.
- **Null enrichment fields**: For unknown domains, all enrichment fields
  (`industry`, `size`, `region`, `contact_role`, `source_url`) are set to
  `null` instead of being omitted. Consumers should expect nullable fields.
- **Domain resolution**: The enrichment lookup is keyed strictly on domain
  (e.g., `acmecorp.com`). Variations like `www.acmecorp.com` or
  `acme-corp.com` will not match and will return `needs_research`.
- **Stale data**: The mock database is static. In production, enrichment
  data can become stale — consider adding a `last_updated` timestamp and
  a refresh cadence.

## Missing Data Handling

| Scenario               | Behavior                                                       |
|------------------------|----------------------------------------------------------------|
| Unknown domain         | `enrichment_status: "needs_research"`, all enrichment fields null |
| Empty domain           | Treated as unknown → `needs_research`                           |
| Missing contact fields | Passthrough — whatever was in input appears in output           |
| Partial match          | Not supported; only exact domain matches return enrichment       |

## Files

```
patterns/lead-enrichment/
  fixtures/
    input.json              — Sample leads to enrich
    expected_output.json    — Expected enriched output
  python/
    main.py                 — run() function: orchestrator entry point
    test_main.py            — pytest test suite
  workflow.json             — n8n-compatible workflow definition
  README.md                 — This file
```
