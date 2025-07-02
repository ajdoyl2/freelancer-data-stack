"""
Tests for the Dagster orchestration setup.

This module contains basic tests to verify that assets, jobs, schedules,
and sensors are properly defined and can be executed.
"""

import pytest
from dagster.core.test_utils import instance_for_test

from .definitions import defs


def test_assets_can_be_loaded():
    """Test that all assets can be loaded without errors."""
    assert len(defs.get_all_asset_specs()) > 0

    # Check that key assets are present
    asset_keys = [spec.key.to_user_string() for spec in defs.get_all_asset_specs()]

    expected_assets = [
        "airbyte_sync_job",
        "dlt_ingestion_pipeline",
        "dbt_run",
        "dbt_test",
        "great_expectations_validation",
        "datahub_metadata_ingestion",
    ]

    for asset_name in expected_assets:
        assert asset_name in asset_keys, f"Asset {asset_name} not found in definitions"


def test_jobs_can_be_loaded():
    """Test that all jobs can be loaded without errors."""
    job_names = [job.name for job in defs.get_all_job_defs()]

    expected_jobs = [
        "daily_data_pipeline",
        "incremental_sync_pipeline",
        "transformation_pipeline",
        "data_quality_pipeline",
        "release_triggered_pipeline",
    ]

    for job_name in expected_jobs:
        assert job_name in job_names, f"Job {job_name} not found in definitions"


def test_schedules_can_be_loaded():
    """Test that schedules can be loaded without errors."""
    schedule_names = [schedule.name for schedule in defs.get_all_schedule_defs()]

    expected_schedules = [
        "daily_pipeline_schedule",
        "incremental_sync_schedule",
    ]

    for schedule_name in expected_schedules:
        assert schedule_name in schedule_names, f"Schedule {schedule_name} not found"


def test_sensors_can_be_loaded():
    """Test that sensors can be loaded without errors."""
    sensor_names = [sensor.name for sensor in defs.get_all_sensor_defs()]

    expected_sensors = [
        "github_release_sensor",
        "data_quality_alert_sensor",
        "file_arrival_sensor",
    ]

    for sensor_name in expected_sensors:
        assert sensor_name in sensor_names, f"Sensor {sensor_name} not found"


def test_asset_dependencies():
    """Test that asset dependencies are correctly defined."""
    # Note: Asset dependency validation would require more complex setup
    # For now, just verify the asset graph can be retrieved
    asset_graph = defs.get_asset_graph()
    assert asset_graph is not None


def test_job_execution_plan():
    """Test that jobs can generate execution plans."""
    with instance_for_test():
        # Test daily pipeline job
        daily_job = defs.get_job_def("daily_data_pipeline")

        # Should be able to create execution plan
        execution_plan = daily_job.get_execution_plan({})
        assert execution_plan is not None
        assert len(execution_plan.get_steps_to_execute()) > 0


@pytest.mark.integration
def test_asset_materialization_dry_run():
    """
    Integration test for asset materialization (dry run).

    This test requires actual connections to be configured.
    Run with: pytest -m integration
    """
    with instance_for_test() as instance:
        # Mock configuration for testing
        test_config = {
            "ops": {
                "airbyte_sync_job": {
                    "config": {
                        "connection_id": "test-connection",
                        "airbyte_host": "localhost",
                        "airbyte_port": 8000,
                    }
                },
                "dlt_ingestion_pipeline": {
                    "config": {
                        "pipeline_name": "test_pipeline",
                        "destination": "duckdb",
                        "dataset_name": "test_dataset",
                    }
                },
                "dbt_run": {
                    "config": {
                        "project_dir": "/tmp/test_dbt",
                        "profiles_dir": "/tmp/test_dbt",
                        "target": "test",
                    }
                },
                "dbt_test": {
                    "config": {
                        "project_dir": "/tmp/test_dbt",
                        "profiles_dir": "/tmp/test_dbt",
                        "target": "test",
                    }
                },
                "great_expectations_validation": {
                    "config": {
                        "project_dir": "/tmp/test_ge",
                        "checkpoint_name": "test_checkpoint",
                    }
                },
            }
        }

        # This would attempt actual materialization in integration environment
        # For now, just verify the job can be configured
        daily_job = defs.get_job_def("daily_data_pipeline")
        assert daily_job.execute_in_process(run_config=test_config, instance=instance)


def test_sensor_evaluation():
    """Test that sensors can be evaluated without errors."""
    from .schedules_sensors import github_release_sensor

    # Create mock context
    class MockSensorContext:
        def __init__(self):
            self.cursor = None

    context = MockSensorContext()

    # Should not raise exceptions during evaluation
    # Note: Will likely return SkipReason due to missing GitHub token
    result = github_release_sensor(context)
    assert result is not None


def test_resource_configuration():
    """Test that resources are properly configured."""
    resources = defs.get_all_resource_defs()

    expected_resources = ["datahub", "freelancer_stack"]

    for resource_name in expected_resources:
        assert resource_name in resources, f"Resource {resource_name} not found"


if __name__ == "__main__":
    # Run basic tests
    test_assets_can_be_loaded()
    test_jobs_can_be_loaded()
    test_schedules_can_be_loaded()
    test_sensors_can_be_loaded()
    test_resource_configuration()

    print("All basic tests passed!")
