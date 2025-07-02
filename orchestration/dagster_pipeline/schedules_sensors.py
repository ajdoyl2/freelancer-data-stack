"""
Schedules and sensors for the freelancer data stack.

This module defines:
- Daily schedule for the demo pipeline
- GitHub release sensor for triggering pipeline on new releases
- Other event-driven sensors as needed
"""

import json
import os

import requests
from dagster import (
    DefaultSensorStatus,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    get_dagster_logger,
    schedule,
    sensor,
)

try:
    from kafka import KafkaConsumer

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


@schedule(
    cron_schedule="0 2 * * *",  # Daily at 2 AM UTC
    job_name="daily_data_pipeline",
    execution_timezone="UTC",
)
def daily_pipeline_schedule(context):
    """
    Daily schedule for the complete data pipeline.

    Runs at 2 AM UTC to ensure data freshness for business hours.
    Configures the pipeline with default parameters.
    """
    return RunRequest(
        run_key=f"daily_pipeline_{context.scheduled_execution_time.strftime('%Y%m%d')}",
        run_config={
            "ops": {
                "airbyte_sync_job": {
                    "config": {
                        "connection_id": os.getenv(
                            "AIRBYTE_CONNECTION_ID", "default-connection"
                        ),
                        "airbyte_host": os.getenv("AIRBYTE_HOST", "localhost"),
                        "airbyte_port": int(os.getenv("AIRBYTE_PORT", "8000")),
                    }
                },
                "dlt_ingestion_pipeline": {
                    "config": {
                        "pipeline_name": os.getenv(
                            "DLT_PIPELINE_NAME", "freelancer_data"
                        ),
                        "destination": os.getenv("DLT_DESTINATION", "duckdb"),
                        "dataset_name": os.getenv("DLT_DATASET_NAME", "freelancer_raw"),
                    }
                },
                "dbt_run": {
                    "config": {
                        "project_dir": "/app/transformation/dbt",
                        "profiles_dir": "/app/transformation/dbt",
                        "target": os.getenv("DBT_TARGET", "prod"),
                    }
                },
                "dbt_test": {
                    "config": {
                        "project_dir": "/app/transformation/dbt",
                        "profiles_dir": "/app/transformation/dbt",
                        "target": os.getenv("DBT_TARGET", "prod"),
                    }
                },
                "great_expectations_validation": {
                    "config": {
                        "project_dir": "/app/quality/great_expectations",
                        "checkpoint_name": os.getenv(
                            "GE_CHECKPOINT_NAME", "daily_validation"
                        ),
                    }
                },
            }
        },
        tags={
            "schedule": "daily",
            "pipeline_type": "full",
            "environment": os.getenv("DAGSTER_ENV", "prod"),
        },
    )


@schedule(
    cron_schedule="0 */6 * * *",  # Every 6 hours
    job_name="incremental_sync_pipeline",
    execution_timezone="UTC",
)
def incremental_sync_schedule(context):
    """
    Incremental sync schedule for frequently updated data sources.

    Runs every 6 hours for near real-time data updates.
    Only runs Airbyte sync and lightweight transformations.
    """
    return RunRequest(
        run_key=f"incremental_sync_{context.scheduled_execution_time.strftime('%Y%m%d_%H%M')}",
        run_config={
            "ops": {
                "airbyte_sync_job": {
                    "config": {
                        "connection_id": os.getenv(
                            "AIRBYTE_INCREMENTAL_CONNECTION_ID",
                            "incremental-connection",
                        ),
                        "airbyte_host": os.getenv("AIRBYTE_HOST", "localhost"),
                        "airbyte_port": int(os.getenv("AIRBYTE_PORT", "8000")),
                    }
                },
                # Only run lightweight transformations for incremental updates
                "dbt_run": {
                    "config": {
                        "project_dir": "/app/transformation/dbt",
                        "profiles_dir": "/app/transformation/dbt",
                        "target": os.getenv("DBT_TARGET", "prod"),
                    }
                },
            }
        },
        tags={
            "schedule": "incremental",
            "pipeline_type": "sync_only",
            "environment": os.getenv("DAGSTER_ENV", "prod"),
        },
    )


@sensor(
    name="kafka_db_trigger_sensor",
    job_name="transformation_pipeline",
    default_status=DefaultSensorStatus.STOPPED,
    description="Consumes Kafka messages to trigger dbt incremental runs",
)
def kafka_db_trigger_sensor(context: SensorEvaluationContext):
    """
    Sensor to consume messages from a Kafka topic and trigger dbt incremental.
    """
    logger = get_dagster_logger()

    if not KAFKA_AVAILABLE:
        return SkipReason("Kafka package not available")

    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name = os.getenv("KAFKA_TOPIC_NAME", "dbt_incremental")

    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=kafka_bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )

        for message in consumer:
            message_value: dict = json.loads(message.value)
            logger.info(f"Received Kafka message: {message_value}")

            # Trigger dbt incremental
            run_config = {
                "ops": {
                    "dbt_run": {
                        "config": {
                            "project_dir": "/app/transformation/dbt",
                            "profiles_dir": "/app/transformation/dbt",
                            "select": message_value.get("model", "*"),
                        }
                    }
                }
            }

            consumer.commit()  # Commit message offset
            return RunRequest(
                run_key=f"kafka_trigger_{message.offset}",
                run_config=run_config,
                tags={
                    "trigger": "kafka_message",
                    "message_offset": message.offset,
                },
            )

    except Exception as e:
        logger.error(f"Kafka sensor error: {str(e)})")
        return SkipReason(f"Sensor error: {str(e)})")


@sensor(
    name="github_release_sensor",
    job_name="release_triggered_pipeline",
    default_status=DefaultSensorStatus.RUNNING,
    description="Monitors GitHub releases and triggers pipeline on new releases",
)
def github_release_sensor(context: SensorEvaluationContext):
    """
    Sensor that monitors GitHub releases and triggers the pipeline on new releases.

    This sensor polls the GitHub API for new releases and triggers a pipeline run
    when a new release is detected. Useful for data pipelines that need to process
    release-related data or update documentation/catalogs.
    """
    logger = get_dagster_logger()

    # GitHub repository configuration
    github_repo = os.getenv("GITHUB_REPO", "your-org/your-repo")
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        return SkipReason("GitHub token not configured")

    if not github_repo:
        return SkipReason("GitHub repository not configured")

    try:
        # Get the latest release from GitHub API
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        url = f"https://api.github.com/repos/{github_repo}/releases/latest"
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 404:
            return SkipReason("No releases found for repository")

        response.raise_for_status()
        release_data = response.json()

        # Extract release information
        release_id = release_data["id"]
        release_tag = release_data["tag_name"]
        release_name = release_data["name"]
        # Check if this release has already been processed
        last_processed_release_id = context.cursor or "0"

        if str(release_id) == last_processed_release_id:
            return SkipReason(f"Release {release_tag} already processed")

        logger.info(f"New GitHub release detected: {release_tag} ({release_name})")

        # Trigger pipeline run for the new release
        run_config = {
            "ops": {
                "airbyte_sync_job": {
                    "config": {
                        "connection_id": os.getenv(
                            "AIRBYTE_CONNECTION_ID", "default-connection"
                        ),
                        "airbyte_host": os.getenv("AIRBYTE_HOST", "localhost"),
                        "airbyte_port": int(os.getenv("AIRBYTE_PORT", "8000")),
                    }
                },
                "dlt_ingestion_pipeline": {
                    "config": {
                        "pipeline_name": os.getenv(
                            "DLT_PIPELINE_NAME", "freelancer_data"
                        ),
                        "destination": os.getenv("DLT_DESTINATION", "duckdb"),
                        "dataset_name": f"release_{release_tag.replace('.', '_')}",
                    }
                },
                "dbt_run": {
                    "config": {
                        "project_dir": "/app/transformation/dbt",
                        "profiles_dir": "/app/transformation/dbt",
                        "target": "release",
                    }
                },
                "datahub_metadata_ingestion": {"config": {}},
            }
        }

        return RunRequest(
            run_key=f"github_release_{release_tag}_{release_id}",
            run_config=run_config,
            tags={
                "trigger": "github_release",
                "release_tag": release_tag,
                "release_id": str(release_id),
                "release_name": release_name,
                "repository": github_repo,
            },
        ).with_replaced_cursor(str(release_id))

    except requests.RequestException as e:
        logger.error(f"Failed to fetch GitHub releases: {str(e)}")
        return SkipReason(f"GitHub API request failed: {str(e)})")

    except Exception as e:
        logger.error(f"GitHub release sensor error: {str(e)})")
        return SkipReason(f"Sensor error: {str(e)})")


@sensor(
    name="data_quality_alert_sensor",
    job_name="data_quality_remediation_pipeline",
    default_status=DefaultSensorStatus.STOPPED,  # Manual activation
    description="Monitors data quality alerts and triggers remediation pipeline",
)
def data_quality_alert_sensor(context: SensorEvaluationContext):
    """
    Sensor that monitors data quality alerts and triggers remediation actions.

    This sensor can be used to monitor data quality metrics and trigger
    remediation pipelines when quality thresholds are breached.
    """
    logger = get_dagster_logger()

    # Check for quality alerts from various sources
    # This could monitor:
    # - Great Expectations validation results
    # - Custom data quality metrics
    # - External monitoring systems

    try:
        # Example: Check for quality alert files
        alert_dir = "/app/quality/alerts"
        if not os.path.exists(alert_dir):
            return SkipReason("Alert directory does not exist")

        alert_files = [f for f in os.listdir(alert_dir) if f.endswith(".json")]

        if not alert_files:
            return SkipReason("No quality alerts found")

        # Process the latest alert
        latest_alert_file = max(
            alert_files, key=lambda f: os.path.getctime(os.path.join(alert_dir, f))
        )
        alert_path = os.path.join(alert_dir, latest_alert_file)

        # Check if this alert has been processed
        alert_mtime = os.path.getmtime(alert_path)
        last_processed_time = float(context.cursor or "0")

        if alert_mtime <= last_processed_time:
            return SkipReason("No new quality alerts")

        # Read alert details
        with open(alert_path) as f:
            alert_data = json.load(f)

        alert_type = alert_data.get("type", "unknown")
        alert_severity = alert_data.get("severity", "medium")
        alert_description = alert_data.get("description", "Data quality issue detected")

        logger.warning(f"Data quality alert triggered: {alert_description}")

        # Configure remediation pipeline based on alert
        run_config = {
            "ops": {
                "great_expectations_validation": {
                    "config": {
                        "project_dir": "/app/quality/great_expectations",
                        "checkpoint_name": "remediation_validation",
                    }
                },
                # Could include data repair or re-processing steps
            }
        }

        return RunRequest(
            run_key=f"quality_alert_{int(alert_mtime)}_{alert_type}",
            run_config=run_config,
            tags={
                "trigger": "data_quality_alert",
                "alert_type": alert_type,
                "alert_severity": alert_severity,
                "alert_file": latest_alert_file,
            },
        ).with_replaced_cursor(str(alert_mtime))

    except Exception as e:
        logger.error(f"Data quality alert sensor error: {str(e)}")
        return SkipReason(f"Sensor error: {str(e)}")


@sensor(
    name="file_arrival_sensor",
    job_name="file_processing_pipeline",
    default_status=DefaultSensorStatus.STOPPED,  # Manual activation
    description="Monitors file system for new data files and triggers processing",
)
def file_arrival_sensor(context: SensorEvaluationContext):
    """
    Sensor that monitors file system for new data files.

    Useful for batch processing scenarios where files are dropped
    into a specific directory for processing.
    """
    logger = get_dagster_logger()

    # Directory to monitor for new files
    watch_dir = os.getenv("FILE_WATCH_DIR", "/app/data/incoming")

    if not os.path.exists(watch_dir):
        return SkipReason(f"Watch directory does not exist: {watch_dir}")

    try:
        # Look for files matching patterns
        import glob

        file_patterns = [
            "*.csv",
            "*.json",
            "*.parquet",
        ]

        new_files = []
        for pattern in file_patterns:
            pattern_path = os.path.join(watch_dir, pattern)
            new_files.extend(glob.glob(pattern_path))

        if not new_files:
            return SkipReason("No new files found")

        # Get the most recent file
        latest_file = max(new_files, key=os.path.getctime)
        file_mtime = os.path.getctime(latest_file)

        # Check if this file has been processed
        last_processed_time = float(context.cursor or "0")

        if file_mtime <= last_processed_time:
            return SkipReason("No new files since last check")

        filename = os.path.basename(latest_file)
        logger.info(f"New file detected for processing: {filename}")

        # Configure pipeline for file processing
        run_config = {
            "ops": {
                "dlt_ingestion_pipeline": {
                    "config": {
                        "pipeline_name": "file_processor",
                        "destination": "duckdb",
                        "dataset_name": f"file_batch_{int(file_mtime)}",
                    }
                },
                "dbt_run": {
                    "config": {
                        "project_dir": "/app/transformation/dbt",
                        "profiles_dir": "/app/transformation/dbt",
                        "target": "batch",
                    }
                },
            }
        }

        return RunRequest(
            run_key=f"file_arrival_{int(file_mtime)}_{filename}",
            run_config=run_config,
            tags={
                "trigger": "file_arrival",
                "filename": filename,
                "file_path": latest_file,
                "file_size": str(os.path.getsize(latest_file)),
            },
        ).with_replaced_cursor(str(file_mtime))

    except Exception as e:
        logger.error(f"File arrival sensor error: {str(e)}")
        return SkipReason(f"Sensor error: {str(e)}")
