-- Bronze schema (Unity Catalog). Replace `main` with your catalog.
-- See: https://docs.databricks.com/aws/en/lakehouse/medallion

CREATE SCHEMA IF NOT EXISTS main.bronze
COMMENT 'Raw / minimally validated landing (medallion bronze)';

-- Tables are typically created by ingestion jobs (Delta). Example CTAS after files land:
-- CREATE TABLE main.bronze.raw_events (
--   event_id STRING,
--   event_date STRING,
--   amount_str STRING,
--   region_code STRING,
--   _ingested_at TIMESTAMP,
--   _source STRING
-- ) USING DELTA;
