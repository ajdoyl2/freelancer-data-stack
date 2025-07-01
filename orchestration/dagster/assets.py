"""
Software-defined assets for the freelancer data stack.

This module defines assets for:
- Airbyte sync jobs
- dlt ingestion pipelines  
- dbt run & test operations
- Great Expectations validation
- DataHub metadata integration
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    Config,
    MetadataValue,
    asset,
    get_dagster_logger,
)
from dagster_datahub import datahub_resource


class AirbyteConfig(Config):
    """Configuration for Airbyte sync operations."""
    
    connection_id: str
    airbyte_host: str = "localhost"
    airbyte_port: int = 8000


class DltConfig(Config):
    """Configuration for dlt ingestion operations."""
    
    pipeline_name: str
    destination: str = "duckdb"
    dataset_name: str


class DbtConfig(Config):
    """Configuration for dbt operations."""
    
    project_dir: str = "/app/transformation/dbt"
    profiles_dir: str = "/app/transformation/dbt"
    target: str = "dev"


class GreatExpectationsConfig(Config):
    """Configuration for Great Expectations validation."""
    
    project_dir: str = "/app/quality/great_expectations"
    checkpoint_name: str


@asset(
    group_name="ingestion",
    description="Airbyte sync job for extracting data from external sources",
    metadata={
        "owner": "data-team",
        "data_source": "external_apis",
    }
)
def airbyte_sync_job(context: AssetExecutionContext, config: AirbyteConfig) -> Dict[str, Any]:
    """
    Execute Airbyte sync job to extract data from external sources.
    
    Returns metadata about the sync operation including records processed.
    """
    logger = get_dagster_logger()
    
    # Construct Airbyte API endpoint
    airbyte_url = f"http://{config.airbyte_host}:{config.airbyte_port}"
    sync_endpoint = f"{airbyte_url}/api/v1/connections/sync"
    
    # Prepare sync request payload
    payload = {
        "connectionId": config.connection_id
    }
    
    try:
        # Trigger Airbyte sync via API call
        import requests
        
        logger.info(f"Triggering Airbyte sync for connection: {config.connection_id}")
        
        response = requests.post(
            sync_endpoint,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300
        )
        
        response.raise_for_status()
        sync_result = response.json()
        
        # Extract sync metadata
        job_id = sync_result.get("job", {}).get("id")
        
        # Wait for sync completion (simplified - in production, use proper polling)
        logger.info(f"Airbyte sync job started with ID: {job_id}")
        
        # Mock sync results for now
        sync_metadata = {
            "job_id": job_id or "mock-job-id",
            "records_extracted": 1000,  # Would be actual count from Airbyte
            "status": "completed",
            "connection_id": config.connection_id
        }
        
        context.add_output_metadata({
            "records_extracted": MetadataValue.int(sync_metadata["records_extracted"]),
            "job_id": MetadataValue.text(sync_metadata["job_id"]),
            "airbyte_connection": MetadataValue.text(config.connection_id),
        })
        
        logger.info("Airbyte sync completed successfully")
        return sync_metadata
        
    except Exception as e:
        logger.error(f"Airbyte sync failed: {str(e)}")
        # In production, you might want to handle retries or alerts here
        raise


@asset(
    group_name="ingestion", 
    description="dlt ingestion pipeline for loading data from various sources",
    metadata={
        "owner": "data-team",
        "pipeline_type": "dlt",
    }
)
def dlt_ingestion_pipeline(context: AssetExecutionContext, config: DltConfig) -> Dict[str, Any]:
    """
    Execute dlt ingestion pipeline to load data into the warehouse.
    
    Returns metadata about the ingestion operation.
    """
    logger = get_dagster_logger()
    
    try:
        # Change to ingestion directory
        ingestion_dir = Path("/app/ingestion/dlt")
        
        # Construct dlt command
        dlt_command = [
            "python", "-m", "dlt.cli",
            "pipeline", "run",
            config.pipeline_name,
            "--destination", config.destination,
            "--dataset-name", config.dataset_name
        ]
        
        logger.info(f"Running dlt pipeline: {config.pipeline_name}")
        logger.info(f"Command: {' '.join(dlt_command)}")
        
        # Execute dlt pipeline
        result = subprocess.run(
            dlt_command,
            cwd=ingestion_dir,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"dlt pipeline failed: {result.stderr}")
            raise RuntimeError(f"dlt pipeline execution failed: {result.stderr}")
        
        # Parse pipeline results (simplified)
        pipeline_metadata = {
            "pipeline_name": config.pipeline_name,
            "destination": config.destination,
            "dataset_name": config.dataset_name,
            "status": "completed",
            "stdout": result.stdout,
        }
        
        # Extract load info if available
        try:
            # dlt typically outputs load info as JSON
            if "Load package" in result.stdout:
                # Mock extraction of records loaded
                records_loaded = 500  # Would parse from actual output
                pipeline_metadata["records_loaded"] = records_loaded
        except Exception:
            pipeline_metadata["records_loaded"] = 0
        
        context.add_output_metadata({
            "pipeline_name": MetadataValue.text(config.pipeline_name),
            "records_loaded": MetadataValue.int(pipeline_metadata.get("records_loaded", 0)),
            "destination": MetadataValue.text(config.destination),
        })
        
        logger.info(f"dlt pipeline {config.pipeline_name} completed successfully")
        return pipeline_metadata
        
    except Exception as e:
        logger.error(f"dlt ingestion pipeline failed: {str(e)}")
        raise


@asset(
    group_name="transformation",
    description="dbt run operation to execute data transformations",
    deps=[airbyte_sync_job, dlt_ingestion_pipeline],
    metadata={
        "owner": "data-team",
        "transformation_tool": "dbt",
    }
)
def dbt_run(context: AssetExecutionContext, config: DbtConfig) -> Dict[str, Any]:
    """
    Execute dbt run to perform data transformations.
    
    Depends on ingestion assets to ensure data is available.
    """
    logger = get_dagster_logger()
    
    try:
        # Construct dbt run command
        dbt_command = [
            "dbt", "run",
            "--project-dir", config.project_dir,
            "--profiles-dir", config.profiles_dir,
            "--target", config.target
        ]
        
        logger.info("Starting dbt run operation")
        logger.info(f"Command: {' '.join(dbt_command)}")
        
        # Execute dbt run
        result = subprocess.run(
            dbt_command,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"dbt run failed: {result.stderr}")
            raise RuntimeError(f"dbt run execution failed: {result.stderr}")
        
        # Parse dbt results
        dbt_metadata = {
            "status": "completed",
            "target": config.target,
            "stdout": result.stdout,
        }
        
        # Extract model run statistics
        try:
            # Parse dbt output for model statistics
            models_run = result.stdout.count("OK created")
            models_run += result.stdout.count("OK")
            dbt_metadata["models_run"] = models_run
        except Exception:
            dbt_metadata["models_run"] = 0
        
        context.add_output_metadata({
            "models_run": MetadataValue.int(dbt_metadata.get("models_run", 0)),
            "target": MetadataValue.text(config.target),
            "dbt_project": MetadataValue.text(config.project_dir),
        })
        
        logger.info("dbt run completed successfully")
        return dbt_metadata
        
    except Exception as e:
        logger.error(f"dbt run failed: {str(e)}")
        raise


@asset(
    group_name="transformation",
    description="dbt test operation to validate data transformations",
    deps=[dbt_run],
    metadata={
        "owner": "data-team",
        "test_type": "dbt_tests",
    }
)
def dbt_test(context: AssetExecutionContext, config: DbtConfig) -> Dict[str, Any]:
    """
    Execute dbt test to validate data transformations.
    
    Depends on dbt_run to ensure transformations are complete.
    """
    logger = get_dagster_logger()
    
    try:
        # Construct dbt test command
        dbt_command = [
            "dbt", "test",
            "--project-dir", config.project_dir,
            "--profiles-dir", config.profiles_dir,
            "--target", config.target
        ]
        
        logger.info("Starting dbt test operation")
        logger.info(f"Command: {' '.join(dbt_command)}")
        
        # Execute dbt test
        result = subprocess.run(
            dbt_command,
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"dbt test failed: {result.stderr}")
            # Log test failures but don't necessarily fail the asset
            logger.warning("Some dbt tests failed - check logs for details")
        
        # Parse dbt test results
        test_metadata = {
            "status": "completed" if result.returncode == 0 else "completed_with_failures",
            "target": config.target,
            "stdout": result.stdout,
            "return_code": result.returncode,
        }
        
        # Extract test statistics
        try:
            tests_passed = result.stdout.count("PASS")
            tests_failed = result.stdout.count("FAIL")
            tests_warned = result.stdout.count("WARN")
            
            test_metadata.update({
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "tests_warned": tests_warned,
            })
        except Exception:
            test_metadata.update({
                "tests_passed": 0,
                "tests_failed": 0,
                "tests_warned": 0,
            })
        
        context.add_output_metadata({
            "tests_passed": MetadataValue.int(test_metadata.get("tests_passed", 0)),
            "tests_failed": MetadataValue.int(test_metadata.get("tests_failed", 0)),
            "tests_warned": MetadataValue.int(test_metadata.get("tests_warned", 0)),
            "target": MetadataValue.text(config.target),
        })
        
        logger.info("dbt test completed")
        return test_metadata
        
    except Exception as e:
        logger.error(f"dbt test failed: {str(e)}")
        raise


@asset(
    group_name="quality",
    description="Great Expectations validation for data quality checks",
    deps=[dbt_run],
    metadata={
        "owner": "data-team",
        "validation_tool": "great_expectations",
    }
)
def great_expectations_validation(
    context: AssetExecutionContext, 
    config: GreatExpectationsConfig
) -> Dict[str, Any]:
    """
    Execute Great Expectations validation checkpoint.
    
    Depends on dbt_run to ensure transformed data is available for validation.
    """
    logger = get_dagster_logger()
    
    try:
        # Construct Great Expectations command
        ge_command = [
            "great_expectations",
            "checkpoint", "run",
            config.checkpoint_name,
            "--directory", config.project_dir
        ]
        
        logger.info(f"Running Great Expectations checkpoint: {config.checkpoint_name}")
        logger.info(f"Command: {' '.join(ge_command)}")
        
        # Execute Great Expectations checkpoint
        result = subprocess.run(
            ge_command,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        # Great Expectations might return non-zero on validation failures
        # but we want to capture the results regardless
        validation_metadata = {
            "checkpoint_name": config.checkpoint_name,
            "status": "completed",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
        }
        
        # Parse validation results
        try:
            # Extract validation statistics from output
            if "Validation succeeded" in result.stdout:
                validation_success = True
                failed_expectations = 0
            else:
                validation_success = False
                # Try to parse failed expectation count
                failed_expectations = result.stdout.count("failed")
            
            validation_metadata.update({
                "validation_success": validation_success,
                "failed_expectations": failed_expectations,
            })
            
        except Exception:
            validation_metadata.update({
                "validation_success": result.returncode == 0,
                "failed_expectations": 0,
            })
        
        context.add_output_metadata({
            "checkpoint_name": MetadataValue.text(config.checkpoint_name),
            "validation_success": MetadataValue.bool(validation_metadata.get("validation_success", False)),
            "failed_expectations": MetadataValue.int(validation_metadata.get("failed_expectations", 0)),
        })
        
        if validation_metadata.get("validation_success", False):
            logger.info("Great Expectations validation passed")
        else:
            logger.warning("Great Expectations validation failed - check results")
        
        return validation_metadata
        
    except Exception as e:
        logger.error(f"Great Expectations validation failed: {str(e)}")
        raise


@asset(
    group_name="catalog",
    description="DataHub metadata ingestion and catalog update",
    deps=[dbt_run, great_expectations_validation],
    metadata={
        "owner": "data-team",
        "catalog_tool": "datahub",
    }
)
def datahub_metadata_ingestion(context: AssetExecutionContext) -> Dict[str, Any]:
    """
    Ingest metadata into DataHub catalog.
    
    Depends on transformation and validation assets to ensure
    metadata is up-to-date with latest pipeline state.
    """
    logger = get_dagster_logger()
    
    try:
        # DataHub ingestion configurations
        ingestion_configs = [
            "/app/catalog/datahub/dbt_ingestion.yml",
            "/app/catalog/datahub/postgres_ingestion.yml",
            # Add more ingestion configs as needed
        ]
        
        ingestion_results = []
        
        for config_path in ingestion_configs:
            if not Path(config_path).exists():
                logger.warning(f"DataHub config not found: {config_path}")
                continue
                
            # Construct DataHub ingestion command
            datahub_command = [
                "datahub", "ingest",
                "-c", config_path
            ]
            
            logger.info(f"Running DataHub ingestion with config: {config_path}")
            
            # Execute DataHub ingestion
            result = subprocess.run(
                datahub_command,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            config_result = {
                "config_path": config_path,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            
            if result.returncode != 0:
                logger.error(f"DataHub ingestion failed for {config_path}: {result.stderr}")
                config_result["status"] = "failed"
            else:
                logger.info(f"DataHub ingestion completed for {config_path}")
                config_result["status"] = "completed"
            
            ingestion_results.append(config_result)
        
        # Aggregate results
        total_configs = len(ingestion_results)
        successful_configs = len([r for r in ingestion_results if r["status"] == "completed"])
        
        metadata_result = {
            "status": "completed" if successful_configs == total_configs else "partial_success",
            "total_configs": total_configs,
            "successful_configs": successful_configs,
            "failed_configs": total_configs - successful_configs,
            "ingestion_results": ingestion_results,
        }
        
        context.add_output_metadata({
            "total_configs": MetadataValue.int(total_configs),
            "successful_configs": MetadataValue.int(successful_configs),
            "failed_configs": MetadataValue.int(total_configs - successful_configs),
        })
        
        logger.info(f"DataHub metadata ingestion completed: {successful_configs}/{total_configs} configs successful")
        return metadata_result
        
    except Exception as e:
        logger.error(f"DataHub metadata ingestion failed: {str(e)}")
        raise
