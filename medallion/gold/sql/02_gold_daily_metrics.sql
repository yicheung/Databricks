-- Gold: daily metrics by region (curated for BI / features)
-- Replace `main` with your catalog.

CREATE SCHEMA IF NOT EXISTS main.gold;

CREATE OR REPLACE TABLE main.gold.daily_region_metrics AS
SELECT
  event_date,
  region_code,
  COUNT(*) AS event_count,
  SUM(amount) AS total_amount,
  AVG(amount) AS avg_amount
FROM main.silver.events_validated
GROUP BY event_date, region_code;
