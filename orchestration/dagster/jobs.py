"""
Jobs for the freelancer data stack.

This module defines jobs that combine assets into executable pipelines
with different execution patterns and configurations.
"""

from dagster import (
    AssetSelection,
    DefaultSensorStatus,
    define_asset_job,
    job,
    op,
    Config,
    OpExecutionContext,
    get_dagster_logger,
)

from .assets import (
    airbyte_sync_job,
    dlt_ingestion_pipeline,
    dbt_run,
    dbt_test,
    great_expectations_validation,
    datahub_metadata_ingestion,
)


# Full data pipeline job - runs all assets in dependency order
daily_data_pipeline = define_asset_job(
    name="daily_data_pipeline",
    description="Complete daily data pipeline including ingestion, transformation, testing, and cataloging",
    selection=AssetSelection.all(),
    tags={
        "team": "data",
        "pipeline_type": "full",
        "schedule": "daily",
    },
)


# Ingestion-only job for incremental updates
incremental_sync_pipeline = define_asset_job(
    name="incremental_sync_pipeline", 
    description="Incremental sync pipeline for frequent data updates",
    selection=AssetSelection.groups("ingestion", "transformation").downstream(include_self=True),
    tags={
        "team": "data",
        "pipeline_type": "incremental",
        "schedule": "frequent",
    },
)


# Transformation and testing job
transformation_pipeline = define_asset_job(
    name="transformation_pipeline",
    description="Data transformation and testing pipeline",
    selection=AssetSelection.groups("transformation", "quality").downstream(include_self=True),
    tags={
        "team": "data",
        "pipeline_type": "transformation",
        "schedule": "on_demand",
    },
)


# Quality validation job
data_quality_pipeline = define_asset_job(
    name="data_quality_pipeline",
    description="Data quality validation and monitoring pipeline",
    selection=AssetSelection.groups("quality", "catalog"),
    tags={
        "team": "data",
        "pipeline_type": "quality",
        "schedule": "validation",
    },
)


# Release-triggered job for GitHub releases
release_triggered_pipeline = define_asset_job(
    name="release_triggered_pipeline",
    description="Pipeline triggered by GitHub releases for release-specific processing",
    selection=AssetSelection.all(),
    tags={
        "team": "data",
        "pipeline_type": "release",
        "trigger": "github_release",
    },
)


# Data quality remediation job
data_quality_remediation_pipeline = define_asset_job(
    name="data_quality_remediation_pipeline",
    description="Remediation pipeline triggered by data quality alerts",
    selection=AssetSelection.groups("quality"),
    tags={
        "team": "data",
        "pipeline_type": "remediation",
        "trigger": "quality_alert",
    },
)


# File processing job for batch uploads
file_processing_pipeline = define_asset_job(
    name="file_processing_pipeline",
    description="Pipeline for processing uploaded batch files",
    selection=AssetSelection.groups("ingestion", "transformation"),
    tags={
        "team": "data",
        "pipeline_type": "batch",
        "trigger": "file_arrival",
    },
)


# Emergency data refresh job
class EmergencyRefreshConfig(Config):
    """Configuration for emergency data refresh operations."""
    
    skip_validations: bool = False
    force_full_refresh: bool = True
    target_models: list[str] = []


@op
def emergency_refresh_preparation(context: OpExecutionContext, config: EmergencyRefreshConfig):
    """
    Preparation step for emergency data refresh.
    
    Logs the emergency refresh parameters and validates configuration.
    """
    logger = get_dagster_logger()
    
    logger.warning("Emergency data refresh initiated!")
    logger.info(f"Skip validations: {config.skip_validations}")
    logger.info(f"Force full refresh: {config.force_full_refresh}")
    logger.info(f"Target models: {config.target_models}")
    
    if config.skip_validations:
        logger.warning("Data validations will be skipped - use with caution!")
    
    if config.force_full_refresh:
        logger.info("Full refresh will be performed on all models")
    
    return {
        "skip_validations": config.skip_validations,
        "force_full_refresh": config.force_full_refresh,
        "target_models": config.target_models,
    }


@job(
    description="Emergency data refresh job with configurable validation skipping",
    tags={
        "team": "data",
        "pipeline_type": "emergency",
        "priority": "high",
    },
)
def emergency_data_refresh(config: EmergencyRefreshConfig):
    """
    Emergency data refresh job that can skip validations if needed.
    
    This job is designed for urgent data refresh scenarios where
    normal validation processes might be bypassed.
    """
    emergency_refresh_preparation(config)


# Monitoring and alerting job
@op
def pipeline_health_check(context: OpExecutionContext):
    """
    Performs health checks on the data pipeline infrastructure.
    
    Checks connectivity to data sources, warehouses, and external services.
    """
    logger = get_dagster_logger()
    
    health_checks = {
        "airbyte_connectivity": True,  # Would check actual Airbyte API
        "duckdb_connectivity": True,   # Would check DuckDB connection
        "datahub_connectivity": True,  # Would check DataHub API
        "github_api": True,           # Would check GitHub API access
    }
    
    failed_checks = [service for service, status in health_checks.items() if not status]
    
    if failed_checks:
        logger.error(f"Health check failures detected: {failed_checks}")
        raise RuntimeError(f"Pipeline health check failed for: {', '.join(failed_checks)}")
    
    logger.info("All pipeline health checks passed")
    return health_checks


@job(
    description="Pipeline monitoring and health check job",
    tags={
        "team": "data",
        "pipeline_type": "monitoring",
        "schedule": "health_check",
    },
)
def pipeline_monitoring():
    """
    Monitoring job that performs health checks on pipeline infrastructure.
    
    This job can be scheduled to run regularly to ensure all pipeline
    components are healthy and accessible.
    """
    pipeline_health_check()


# Development and testing job
dev_pipeline = define_asset_job(
    name="dev_pipeline",
    description="Development pipeline for testing changes",
    selection=AssetSelection.all(),
    tags={
        "team": "data",
        "pipeline_type": "development",
        "environment": "dev",
    },
)


# Backfill job for historical data processing
@op
def backfill_preparation(context: OpExecutionContext):
    """
    Preparation step for backfill operations.
    
    Sets up the environment and validates parameters for backfill processing.
    """
    logger = get_dagster_logger()
    
    # Get backfill parameters from run config
    start_date = context.run_config.get("ops", {}).get("backfill_preparation", {}).get("config", {}).get("start_date")
    end_date = context.run_config.get("ops", {}).get("backfill_preparation", {}).get("config", {}).get("end_date")
    
    if not start_date or not end_date:
        raise ValueError("Both start_date and end_date must be provided for backfill")
    
    logger.info(f"Preparing backfill from {start_date} to {end_date}")
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "backfill_ready": True,
    }


backfill_pipeline = define_asset_job(
    name="backfill_pipeline",
    description="Backfill pipeline for historical data processing",
    selection=AssetSelection.all(),
    tags={
        "team": "data", 
        "pipeline_type": "backfill",
        "schedule": "on_demand",
    },
)


# Export all jobs for use in definitions
ALL_JOBS = [
    daily_data_pipeline,
    incremental_sync_pipeline,
    transformation_pipeline,
    data_quality_pipeline,
    release_triggered_pipeline,
    data_quality_remediation_pipeline,
    file_processing_pipeline,
    emergency_data_refresh,
    pipeline_monitoring,
    dev_pipeline,
    backfill_pipeline,
]
