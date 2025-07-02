"""
Enhanced assets with DataHub lineage tracking and Great Expectations integration.
"""

import pandas as pd
from dagster import (
    AssetIn,
    AssetOut,
    MaterializeResult,
    MetadataValue,
    asset,
    get_dagster_logger,
    multi_asset,
)
from dagster_datahub import DataHubResource, build_dataset_urn
from great_expectations.data_context import DataContext

logger = get_dagster_logger()


@asset(
    compute_kind="dbt",
    metadata={
        "owner": "data-team",
        "source": "freelancer_api",
        "datahub_tags": ["raw", "ingestion", "freelancer"],
    },
)
def raw_freelancer_data(datahub: DataHubResource) -> MaterializeResult:
    """
    Raw freelancer data ingested from API with DataHub lineage tracking.
    """

    # Simulate data ingestion
    df = pd.DataFrame(
        {
            "freelancer_id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "skills": ["Python,SQL", "Java,Scala", "R,Python"],
            "hourly_rate": [50, 65, 45],
            "created_at": pd.Timestamp.now(),
        }
    )

    # Create DataHub dataset URN
    dataset_urn = build_dataset_urn(
        platform="postgres", name="freelancer_raw.freelancers", env="dev"
    )

    # Emit lineage information to DataHub
    datahub.emit_lineage(
        dataset_urn=dataset_urn,
        upstream_datasets=[],
        downstream_datasets=[
            build_dataset_urn("postgres", "freelancer_staging.stg_freelancers", "dev")
        ],
    )

    # Log metrics
    logger.info(f"Ingested {len(df)} freelancer records")

    return MaterializeResult(
        metadata={
            "num_records": len(df),
            "columns": list(df.columns),
            "datahub_urn": dataset_urn,
            "preview": MetadataValue.md(df.head().to_markdown()),
        }
    )


@multi_asset(
    outs={
        "stg_freelancers": AssetOut(
            key_prefix=["staging"],
            metadata={
                "owner": "data-team",
                "datahub_tags": ["staging", "cleaned", "freelancer"],
            },
        ),
        "stg_skills": AssetOut(
            key_prefix=["staging"],
            metadata={
                "owner": "data-team",
                "datahub_tags": ["staging", "normalized", "skills"],
            },
        ),
    },
    compute_kind="dbt",
)
def staging_transformations(
    raw_freelancer_data: pd.DataFrame, datahub: DataHubResource
) -> tuple[MaterializeResult, MaterializeResult]:
    """
    Staging transformations with DataHub lineage tracking.
    """

    # Create staging freelancers table
    stg_freelancers = raw_freelancer_data.copy()
    stg_freelancers["name_upper"] = stg_freelancers["name"].str.upper()
    stg_freelancers["skills_count"] = stg_freelancers["skills"].str.split(",").str.len()

    # Create skills dimension table
    skills_data = []
    for _, row in raw_freelancer_data.iterrows():
        skills = row["skills"].split(",")
        for skill in skills:
            skills_data.append(
                {
                    "freelancer_id": row["freelancer_id"],
                    "skill": skill.strip(),
                    "created_at": row["created_at"],
                }
            )

    stg_skills = pd.DataFrame(skills_data)

    # Create DataHub URNs
    freelancers_urn = build_dataset_urn(
        "postgres", "freelancer_staging.stg_freelancers", "dev"
    )
    skills_urn = build_dataset_urn("postgres", "freelancer_staging.stg_skills", "dev")

    # Emit lineage to DataHub
    datahub.emit_lineage(
        dataset_urn=freelancers_urn,
        upstream_datasets=[
            build_dataset_urn("postgres", "freelancer_raw.freelancers", "dev")
        ],
        downstream_datasets=[
            build_dataset_urn("postgres", "freelancer_marts.dim_freelancers", "dev")
        ],
    )

    datahub.emit_lineage(
        dataset_urn=skills_urn,
        upstream_datasets=[
            build_dataset_urn("postgres", "freelancer_raw.freelancers", "dev")
        ],
        downstream_datasets=[
            build_dataset_urn("postgres", "freelancer_marts.dim_skills", "dev")
        ],
    )

    return (
        MaterializeResult(
            asset_key=["staging", "stg_freelancers"],
            metadata={
                "num_records": len(stg_freelancers),
                "columns": list(stg_freelancers.columns),
                "datahub_urn": freelancers_urn,
                "avg_hourly_rate": stg_freelancers["hourly_rate"].mean(),
            },
        ),
        MaterializeResult(
            asset_key=["staging", "stg_skills"],
            metadata={
                "num_records": len(stg_skills),
                "unique_skills": stg_skills["skill"].nunique(),
                "datahub_urn": skills_urn,
            },
        ),
    )


@asset(
    ins={
        "stg_freelancers": AssetIn(key_prefix=["staging"]),
        "stg_skills": AssetIn(key_prefix=["staging"]),
    },
    compute_kind="dbt",
    metadata={
        "owner": "data-team",
        "datahub_tags": ["mart", "analytics", "freelancer"],
    },
)
def dim_freelancers_enhanced(
    stg_freelancers: pd.DataFrame, stg_skills: pd.DataFrame, datahub: DataHubResource
) -> MaterializeResult:
    """
    Enhanced freelancer dimension with skills aggregation and quality checks.
    """

    # Aggregate skills per freelancer
    skills_agg = (
        stg_skills.groupby("freelancer_id")
        .agg({"skill": lambda x: ",".join(sorted(x.unique()))})
        .reset_index()
    )

    # Join with staging freelancers
    dim_freelancers = stg_freelancers.merge(
        skills_agg, on="freelancer_id", how="left", suffixes=("", "_agg")
    )

    # Data quality checks using Great Expectations
    try:
        context = DataContext()

        # Create expectation suite
        suite = context.create_expectation_suite("freelancer_quality_checks")

        # Add expectations
        suite.expect_column_to_exist("freelancer_id")
        suite.expect_column_values_to_be_unique("freelancer_id")
        suite.expect_column_values_to_not_be_null("name")
        suite.expect_column_values_to_be_between(
            "hourly_rate", min_value=0, max_value=1000
        )

        # Run validation
        validation_result = context.run_checkpoint(
            checkpoint_name="daily_validation",
            validations=[
                {
                    "batch_request": {
                        "datasource_name": "postgres_warehouse",
                        "data_connector_name": "default_runtime_data_connector",
                        "data_asset_name": "dim_freelancers",
                    },
                    "expectation_suite_name": "freelancer_quality_checks",
                }
            ],
        )

        quality_success_rate = validation_result.success

    except Exception as e:
        logger.warning(f"Data quality validation failed: {e}")
        quality_success_rate = False

    # Create DataHub URN and emit lineage
    dataset_urn = build_dataset_urn(
        "postgres", "freelancer_marts.dim_freelancers", "dev"
    )

    datahub.emit_lineage(
        dataset_urn=dataset_urn,
        upstream_datasets=[
            build_dataset_urn("postgres", "freelancer_staging.stg_freelancers", "dev"),
            build_dataset_urn("postgres", "freelancer_staging.stg_skills", "dev"),
        ],
        downstream_datasets=[],
    )

    return MaterializeResult(
        metadata={
            "num_records": len(dim_freelancers),
            "quality_checks_passed": quality_success_rate,
            "datahub_urn": dataset_urn,
            "avg_skills_per_freelancer": dim_freelancers["skills_count"].mean(),
            "preview": MetadataValue.md(dim_freelancers.head().to_markdown()),
        }
    )


@asset(
    compute_kind="python",
    metadata={
        "owner": "data-team",
        "datahub_tags": ["metrics", "monitoring"],
    },
)
def data_quality_metrics(datahub: DataHubResource) -> MaterializeResult:
    """
    Generate data quality metrics for monitoring dashboard.
    """

    # Simulate Great Expectations metrics collection
    quality_metrics = {
        "validation_runs_total": 45,
        "validation_runs_passed": 42,
        "validation_runs_failed": 3,
        "success_rate": 0.933,
        "last_run_timestamp": pd.Timestamp.now(),
        "critical_failures": 0,
        "warning_failures": 3,
    }

    # Create metrics dataset URN
    dataset_urn = build_dataset_urn(
        "postgres", "monitoring.data_quality_metrics", "dev"
    )

    # Emit to DataHub
    datahub.emit_lineage(
        dataset_urn=dataset_urn,
        upstream_datasets=[
            build_dataset_urn("postgres", "freelancer_marts.dim_freelancers", "dev")
        ],
        downstream_datasets=[],
    )

    return MaterializeResult(
        metadata={
            "success_rate": quality_metrics["success_rate"],
            "total_runs": quality_metrics["validation_runs_total"],
            "failed_runs": quality_metrics["validation_runs_failed"],
            "datahub_urn": dataset_urn,
            "last_updated": quality_metrics["last_run_timestamp"].isoformat(),
        }
    )
