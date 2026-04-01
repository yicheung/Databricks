# Databricks notebook source
# MAGIC %md
# MAGIC # Silver — clean and validate (template)
# MAGIC
# MAGIC Implements common Silver responsibilities from the [medallion docs](https://docs.databricks.com/aws/en/lakehouse/medallion): typing, deduplication, and a validated row-level table for downstream use.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import Window

dbutils.widgets.text("catalog", "main")
catalog = dbutils.widgets.get("catalog").strip()

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.silver")

bronze = spark.table(f"{catalog}.bronze.raw_events")

typed = (
    bronze.select(
        F.col("event_id").cast("long").alias("event_id"),
        F.to_date(F.col("event_date"), "yyyy-MM-dd").alias("event_date"),
        F.col("amount_str").cast("decimal(18,2)").alias("amount"),
        F.trim(F.upper(F.col("region_code"))).alias("region_code"),
        F.col("_ingested_at"),
        F.col("_source"),
    )
    .where(F.col("event_id").isNotNull() & F.col("event_date").isNotNull())
)

w = Window.partitionBy("event_id").orderBy(F.col("_ingested_at").desc())
deduped = typed.withColumn("_rn", F.row_number().over(w)).where(F.col("_rn") == 1).drop("_rn")

out = f"{catalog}.silver.events_validated"
deduped.write.format("delta").mode("overwrite").saveAsTable(out)

# COMMAND ----------

display(spark.table(out).limit(20))
