# MLOps templates (Databricks + AWS)

This folder complements the **medallion** pipelines: models typically consume **Gold** (or **Silver**) tables as features, while training artifacts and batch outputs often land in **S3** provisioned under `infra/` (see root `README.md`).

| Piece | In this repo |
|-------|----------------|
| **Tracking / registry** | Databricks-managed MLflow (workspace); shared experiment path created by Pulumi |
| **Compute** | Jobs (serverless or classic per your workspace); optional SQL warehouse for monitoring |
| **Storage** | S3 bucket from Pulumi for artifacts and exports |

Notebook:

- `notebooks/04_train_and_log_mlflow.py` — Minimal sklearn + MLflow run that reads Gold metrics as a feature source (template only).

Deploy the medallion + training sequence with [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html) via `databricks bundle deploy` using `databricks.yml` at the repository root.
