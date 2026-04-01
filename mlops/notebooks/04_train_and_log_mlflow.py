# Databricks notebook source
# MAGIC %md
# MAGIC # MLOps — train and log to MLflow (template)
# MAGIC
# MAGIC Example: read curated **Gold** data, train a small sklearn model, log params/metrics/artifacts to **MLflow** on Databricks. Use the experiment path created by Pulumi (`/Shared/mlops-experiments-{environment}`) or your team’s shared experiment.

# COMMAND ----------

dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("experiment_path", "/Shared/mlops-experiments-dev")

catalog = dbutils.widgets.get("catalog").strip()
experiment_path = dbutils.widgets.get("experiment_path").strip()

# COMMAND ----------

import mlflow
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

mlflow.set_registry_uri("databricks")
mlflow.set_experiment(experiment_path)

gold_df = spark.table(f"{catalog}.gold.daily_region_metrics").toPandas()
if gold_df.empty:
    raise ValueError("Gold table is empty — run medallion gold notebook first.")

# Simple numeric features for a template (encode region as category codes)
gold_df = gold_df.dropna()
gold_df["region_cat"] = gold_df["region_code"].astype("category").cat.codes
gold_df["dow"] = pd.to_datetime(gold_df["event_date"]).dt.dayofweek

features = gold_df[["region_cat", "dow", "event_count"]]
target = gold_df["total_amount"]

X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.25, random_state=42
)

with mlflow.start_run(run_name="medallion-gold-baseline"):
    params = {"n_estimators": 50, "max_depth": 4, "random_state": 42}
    model = RandomForestRegressor(**params)
    model.fit(X_train, y_train)

    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    mlflow.log_params(params)
    mlflow.log_metrics({"train_r2": float(train_score), "test_r2": float(test_score)})
    mlflow.sklearn.log_model(model, artifact_path="model")

# COMMAND ----------

# MAGIC %md
# MAGIC **Next steps:** register the model in the Model Registry, add batch inference reading Silver/Gold, and wire CI/CD (for example bundle deploy + Pulumi for infra).
