# Medallion layer templates

This folder mirrors the [Databricks medallion lakehouse architecture](https://docs.databricks.com/aws/en/lakehouse/medallion): **Bronze** (raw) → **Silver** (validated) → **Gold** (analytics-ready).

| Layer | Role | Typical consumers |
|-------|------|-------------------|
| **Bronze** | Raw ingestion, minimal cleanup, preserve source fidelity | Engineering jobs that build Silver |
| **Silver** | Cleansing, deduplication, typing, joins | Analysts, scientists, downstream Gold jobs |
| **Gold** | Business aggregates and curated datasets | BI, dashboards, ML feature consumers |

Schemas used in the templates default to `{catalog}.bronze`, `{catalog}.silver`, and `{catalog}.gold`. Point `catalog` at your Unity Catalog catalog (for example `main` or an ops catalog).

The sample domain is intentionally generic (event identifiers, dates, amounts, region codes)—replace tables and logic with your sources.
