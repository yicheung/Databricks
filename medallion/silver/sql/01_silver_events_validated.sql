-- Silver: validated events (example merge pattern on Delta)
-- Adjust catalog and keys for your domain.

CREATE SCHEMA IF NOT EXISTS main.silver;

CREATE OR REPLACE TABLE main.silver.events_validated (
  event_id BIGINT,
  event_date DATE,
  amount DECIMAL(18,2),
  region_code STRING,
  _ingested_at TIMESTAMP,
  _source STRING
) USING DELTA;

MERGE INTO main.silver.events_validated AS t
USING (
  SELECT
    CAST(event_id AS BIGINT) AS event_id,
    TO_DATE(event_date, 'yyyy-MM-dd') AS event_date,
    CAST(amount_str AS DECIMAL(18,2)) AS amount,
    TRIM(UPPER(region_code)) AS region_code,
    _ingested_at,
    _source
  FROM main.bronze.raw_events
  WHERE event_id IS NOT NULL AND event_date IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY _ingested_at DESC) = 1
) s
ON t.event_id = s.event_id
WHEN MATCHED AND s._ingested_at > t._ingested_at THEN UPDATE SET
  event_date = s.event_date,
  amount = s.amount,
  region_code = s.region_code,
  _ingested_at = s._ingested_at,
  _source = s._source
WHEN NOT MATCHED THEN INSERT (
  event_id, event_date, amount, region_code, _ingested_at, _source
) VALUES (
  s.event_id, s.event_date, s.amount, s.region_code, s._ingested_at, s._source
);
