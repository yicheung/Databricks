# Gold layer

- **Purpose:** Curated, business-aligned datasets: aggregates, dimensions, and views optimized for reporting, dashboards, and ML features.

Artifacts:

- `03_gold_daily_metrics.py` — Builds `gold.daily_region_metrics` from Silver.
- `sql/02_gold_daily_metrics.sql` — Equivalent SQL `CREATE OR REPLACE TABLE` example.

Downstream **MLOps** notebooks can read Gold (or Silver) as feature inputs; see `mlops/notebooks/04_train_and_log_mlflow.py`.
