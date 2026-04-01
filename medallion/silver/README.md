# Silver layer

- **Purpose:** Validate, type, deduplicate, and normalize data read from Bronze (and optionally other Silver tables). This is where schema enforcement and data quality checks usually live.

Artifacts:

- `02_silver_clean_validate.py` — Reads `bronze.raw_events`, applies typing and deduplication, writes `silver.events_validated`.
- `sql/01_silver_events_validated.sql` — Declarative example using Delta merge for idempotent upserts.
