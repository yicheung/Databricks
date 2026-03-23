"""
Starter Pulumi stack: AWS storage + Databricks MLOps-oriented defaults.

MLflow: Tracking + Model Registry are built into the workspace (no separate MLflow server).
This stack optionally creates a workspace MLflow experiment; UC-managed registry stays in
platform settings.

Serverless: SQL warehouses can use enable_serverless_compute (no customer-managed EC2).
Jobs/notebooks serverless and Model Serving are workspace features—enable in UI or add Job /
ModelServing resources when you have a model config. Databricks still runs compute in their
cloud; you do not provision EC2 instances in your AWS account for those paths.

The cluster policy below applies only to classic (VM-backed) job/all-purpose clusters.
"""
import json
import pulumi
import pulumi_aws as aws
import pulumi_databricks as databricks

cfg = pulumi.Config()
dbc_cfg = pulumi.Config("databricks")
env = cfg.get("environment") or "dev"
region = aws.get_region().name

# --- Databricks provider (workspace PAT or env: DATABRICKS_HOST + DATABRICKS_TOKEN) ---
databricks_provider = databricks.Provider(
    "databricks-workspace",
    host=dbc_cfg.require("host"),
    token=dbc_cfg.get_secret("token"),
)

tags = {
    "Environment": env,
    "ManagedBy": "pulumi",
    "Purpose": "databricks-mlops",
}

# --- S3: model artifacts, batch scoring outputs, optional Unity Catalog roots ---
artifacts_bucket = aws.s3.BucketV2(
    f"ml-artifacts-{env}",
    tags=tags | {"Name": f"ml-artifacts-{env}"},
)

aws.s3.BucketVersioningConfigurationV2(
    f"ml-artifacts-versioning-{env}",
    bucket=artifacts_bucket.id,
    versioning_configuration=aws.s3.BucketVersioningConfigurationV2VersioningConfigurationArgs(
        status="Enabled",
    ),
)

aws.s3.BucketServerSideEncryptionConfigurationV2(
    f"ml-artifacts-sse-{env}",
    bucket=artifacts_bucket.id,
    rules=[
        aws.s3.BucketServerSideEncryptionConfigurationV2RuleArgs(
            apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationV2RuleApplyServerSideEncryptionByDefaultArgs(
                sse_algorithm="AES256",
            ),
            bucket_key_enabled=True,
        )
    ],
)

aws.s3.BucketPublicAccessBlock(
    f"ml-artifacts-pab-{env}",
    bucket=artifacts_bucket.id,
    block_public_acls=True,
    block_public_policy=True,
    ignore_public_acls=True,
    restrict_public_buckets=True,
)

# --- MLflow: managed tracking in workspace; experiment for shared MLOps runs ---
mlflow_experiment = databricks.MlflowExperiment(
    f"mlops-experiment-{env}",
    name=f"/Shared/mlops-experiments-{env}",
    opts=pulumi.ResourceOptions(provider=databricks_provider),
)

# --- Serverless SQL warehouse (analytics / monitoring / SQL on Delta; no instance profile) ---
ml_sql_warehouse = databricks.SqlEndpoint(
    f"mlops-serverless-sql-{env}",
    name=f"mlops-serverless-sql-{env}",
    cluster_size="Small",
    min_num_clusters=1,
    max_num_clusters=1,
    auto_stop_mins=30,
    enable_serverless_compute=True,
    warehouse_type="PRO",
    tags=databricks.SqlEndpointTagsArgs(
        custom_tags=[
            databricks.SqlEndpointTagsCustomTagArgs(key="Environment", value=env),
            databricks.SqlEndpointTagsCustomTagArgs(key="Purpose", value="mlops"),
        ],
    ),
    opts=pulumi.ResourceOptions(provider=databricks_provider),
)

# --- Example cluster policy: cap spend / enforce tags on job clusters ---
_job_cluster_policy_definition = {
    "node_type_id": {"type": "allowlist", "values": ["i3.xlarge", "i3.2xlarge", "i4i.xlarge"]},
    "autoscale.min_workers": {"type": "range", "maxValue": 1, "defaultValue": 1},
    "autoscale.max_workers": {"type": "range", "maxValue": 8, "defaultValue": 2},
    "custom_tags.Environment": {"type": "fixed", "value": env},
}

ml_job_cluster_policy = databricks.ClusterPolicy(
    f"ml-job-policy-{env}",
    name=f"mlops-job-{env}",
    definition=json.dumps(_job_cluster_policy_definition),
    opts=pulumi.ResourceOptions(provider=databricks_provider),
)

pulumi.export("aws_region", region)
pulumi.export("ml_artifacts_bucket", artifacts_bucket.id)
pulumi.export("mlflow_experiment_id", mlflow_experiment.experiment_id)
pulumi.export("serverless_sql_warehouse_id", ml_sql_warehouse.id)
pulumi.export("ml_job_cluster_policy_id", ml_job_cluster_policy.policy_id)
