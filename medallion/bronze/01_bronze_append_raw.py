# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze — raw landing (template)
# MAGIC
# MAGIC Aligns with the [medallion Bronze layer](https://docs.databricks.com/aws/en/lakehouse/medallion): preserve source fidelity, minimal validation, append over time.
# MAGIC
# MAGIC **Production:** replace the in-notebook sample `createDataFrame` with a `read` from your landing zone (for example S3 via `s3://` paths on AWS).

# COMMAND ----------

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "main")
catalog = dbutils.widgets.get("catalog").strip()

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.bronze")

# Sample raw rows (string-typed payload fields — typical Bronze pattern before typing in Silver)
sample = spark.createDataFrame(
    [
        ("1", "2024-01-15", "100.50", "US-WEST"),
        ("2", "2024-01-15", "200.00", "US-EAST"),
        ("2", "2024-01-15", "200.00", "US-EAST"),  # duplicate raw delivery — handled in Silver
        ("3", "2024-01-16", "50.25", "EU-CENTRAL"),
    ],
    ["event_id", "event_date", "amount_str", "region_code"],
)

bronze_df = (
    sample.withColumn("_ingested_at", F.current_timestamp())
    .withColumn("_source", F.lit("template_notebook"))
)

table = f"{catalog}.bronze.raw_events"
bronze_df.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(table)

# COMMAND ----------

# MAGIC %md
# MAGIC **Next:** run `medallion/silver/02_silver_clean_validate.py` or the full job in `databricks.yml`.
