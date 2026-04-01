# Databricks notebook source
# MAGIC %md
# MAGIC # Gold — analytics-ready aggregates (template)
# MAGIC
# MAGIC Matches the Gold layer in the [medallion architecture](https://docs.databricks.com/aws/en/lakehouse/medallion): curated metrics for BI and ML feature consumers.

# COMMAND ----------

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "main")
catalog = dbutils.widgets.get("catalog").strip()

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.gold")

src = spark.table(f"{catalog}.silver.events_validated")

daily = (
    src.groupBy("event_date", "region_code")
    .agg(
        F.count("*").alias("event_count"),
        F.sum("amount").alias("total_amount"),
        F.avg("amount").alias("avg_amount"),
    )
)

out = f"{catalog}.gold.daily_region_metrics"
daily.write.format("delta").mode("overwrite").saveAsTable(out)

# COMMAND ----------

display(spark.table(out).orderBy("event_date", "region_code"))
