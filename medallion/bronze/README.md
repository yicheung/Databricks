# Bronze layer

- **Purpose:** Land raw or lightly wrapped data; keep fields as strings or semi-structured types where schema drift is possible; add lineage metadata (for example ingest time, file name).
- **Do not** use Bronze as the primary place for heavy business rules—that belongs in Silver.

Artifacts:

- `01_bronze_append_raw.py` — Databricks notebook that creates the bronze schema and appends a template `raw_events` Delta table (synthetic rows for a quick run; swap in `read` from S3 or cloud storage for production).
- `sql/00_bronze_schema.sql` — Optional SQL-only reference for creating the bronze schema.
