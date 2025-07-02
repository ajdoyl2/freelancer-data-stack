"""
Main definitions module for the freelancer data stack Dagster deployment.

This module combines all assets, jobs, schedules, sensors, and resources
into a complete Dagster deployment with DataHub integration.
"""

import os

from dagster import (
    ConfigurableResource,
    Definitions,
    InitResourceContext,
    load_assets_from_modules,
)

# from dagster_datahub import DataHubResource
from . import assets, jobs, schedules_sensors


class FreelancerDataStackResource(ConfigurableResource):
    """
    Custom resource for the freelancer data stack configuration.

    Provides centralized configuration management for the entire stack.
    """

    # Environment configuration
    environment: str = "dev"

    # Airbyte configuration
    airbyte_host: str = "localhost"
    airbyte_port: int = 8000
    airbyte_connection_id: str = "default-connection"

    # dlt configuration
    dlt_pipeline_name: str = "freelancer_data"
    dlt_destination: str = "duckdb"
    dlt_dataset_name: str = "freelancer_raw"

    # dbt configuration
    dbt_project_dir: str = "/app/transformation/dbt"
    dbt_profiles_dir: str = "/app/transformation/dbt"
    dbt_target: str = "dev"

    # Great Expectations configuration
    ge_project_dir: str = "/app/quality/great_expectations"
    ge_checkpoint_name: str = "daily_validation"

    # DataHub configuration
    datahub_gms_url: str = "http://localhost:8080"
    datahub_gms_token: str = ""

    # GitHub configuration
    github_repo: str = ""
    github_token: str = ""

    def setup_for_execution(
        self, context: InitResourceContext
    ) -> "FreelancerDataStackResource":
        """Set up the resource for execution with environment-specific configs."""
        return self


# DataHub resource for metadata integration (disabled for now)
# datahub_resource = DataHubResource(
#     gms_url=EnvVar("DATAHUB_GMS_URL").default("http://localhost:8080"),
#     gms_token=EnvVar("DATAHUB_GMS_TOKEN").default(""),
# )


# Custom resource for the freelancer data stack
freelancer_stack_resource = FreelancerDataStackResource(
    environment=os.getenv("DAGSTER_ENV", "dev"),
    # Airbyte configuration
    airbyte_host=os.getenv("AIRBYTE_HOST", "localhost"),
    airbyte_port=int(os.getenv("AIRBYTE_PORT", "8000")),
    airbyte_connection_id=os.getenv("AIRBYTE_CONNECTION_ID", "default-connection"),
    # dlt configuration
    dlt_pipeline_name=os.getenv("DLT_PIPELINE_NAME", "freelancer_data"),
    dlt_destination=os.getenv("DLT_DESTINATION", "duckdb"),
    dlt_dataset_name=os.getenv("DLT_DATASET_NAME", "freelancer_raw"),
    # dbt configuration
    dbt_project_dir=os.getenv("DBT_PROJECT_DIR", "/app/transformation/dbt"),
    dbt_profiles_dir=os.getenv("DBT_PROFILES_DIR", "/app/transformation/dbt"),
    dbt_target=os.getenv("DBT_TARGET", "dev"),
    # Great Expectations configuration
    ge_project_dir=os.getenv("GE_PROJECT_DIR", "/app/quality/great_expectations"),
    ge_checkpoint_name=os.getenv("GE_CHECKPOINT_NAME", "daily_validation"),
    # GitHub configuration
    github_repo=os.getenv("GITHUB_REPO", ""),
    github_token=os.getenv("GITHUB_TOKEN", ""),
)


# Load all assets from the assets module
all_assets = load_assets_from_modules([assets])


# Collect all schedules and sensors
all_schedules = [
    schedules_sensors.daily_pipeline_schedule,
    schedules_sensors.incremental_sync_schedule,
]

all_sensors = [
    schedules_sensors.kafka_db_trigger_sensor,
    schedules_sensors.github_release_sensor,
    schedules_sensors.data_quality_alert_sensor,
    schedules_sensors.file_arrival_sensor,
]


# Main Dagster definitions
defs = Definitions(
    assets=all_assets,
    jobs=jobs.ALL_JOBS,
    schedules=all_schedules,
    sensors=all_sensors,
    resources={
        # "datahub": datahub_resource,  # Disabled for now
        "freelancer_stack": freelancer_stack_resource,
    },
)


# Export for use in deployment
__all__ = ["defs"]
