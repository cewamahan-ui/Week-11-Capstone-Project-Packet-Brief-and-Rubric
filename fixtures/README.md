# Fixtures

Teaching dataset for the AfyaPlus Module 4 Capstone.

| File | Rows | Purpose |
|------|------|---------|
| `triage_messages_sample.jsonl` | 300 | Synthetic triage cases + gold labels (clinical line) |
| `catalog_listings_sample.jsonl` | 200 | Synthetic medical-supply listings (marketplace line) |

Both files stay inside the required **200-500 row** band per file.

## No scraping rule

- Nothing here was scraped. Both files are generated locally by
  `scripts/make_fixtures.py` from a fixed random seed (`seed=42`),
  with no network access anywhere in the generator.
- Do not add production or scraped data to this directory. If the
  dataset ever needs to grow, extend the generator - not a crawler.
- Regenerate with:

```bash
python scripts/make_fixtures.py
```

## No PII rule

- Triage rows carry synthetic clinical fields only: `id`, `age`,
  `symptoms`, `urgency_level`, `vitals`, gold labels (`expected_urgency`,
  `expected_recommendation`, `expected_department`) and a
  `source` marker. No names, phone numbers, emails, national IDs or
  addresses - `tests/test_security_smoke.py` enforces this on every run.
- Catalog rows are marketplace listings (`item_id`, `item_name`,
  `category`, `supplier`, `county`, `unit_price_usd`, `stock`) with
  **no clinical fields at all**.
- Clinical and marketplace rows live in separate files and are never
  mixed, so the two data lines cannot leak into each other.

## Gold label provenance

`expected_urgency`, `expected_recommendation` and
`expected_department` are produced by
`src/afyaplus.triage.policy` - the same module the runtime executes.
That guarantees the fixture and the service cannot drift apart
silently; the drift that once separated them is documented in
`docs/incidents/2026-10-13-fixture-label-drift.md`.
