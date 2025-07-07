#!/usr/bin/env python3
"""
Data Pipeline Setup Example

This script demonstrates how to set up a complete data pipeline using
the AI agent system, from data ingestion to analytics dashboards.
"""

import asyncio
import logging

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from interface.workflow_executor import WorkflowExecutor


async def setup_complete_data_pipeline():
    """Set up a complete data pipeline end-to-end."""

    print("🚀 Complete Data Pipeline Setup")
    print("=" * 50)

    executor = WorkflowExecutor()

    # Step 1: Infrastructure Setup
    print("\n1. Setting up infrastructure...")
    infra_request = (
        "Deploy and configure all necessary Docker services for the data stack"
    )

    try:
        result = await executor.process_request(infra_request)
        print(f"✅ Infrastructure: {result.status}")
        print("   Services deployed: PostgreSQL, Airflow, Meltano, dbt, DataHub")
    except Exception as e:
        print(f"❌ Infrastructure setup failed: {str(e)}")
        return False

    # Step 2: Data Ingestion Setup
    print("\n2. Setting up data ingestion...")
    ingestion_request = (
        "Configure Meltano to extract data from our CSV files and load into PostgreSQL"
    )

    try:
        result = await executor.process_request(ingestion_request)
        print(f"✅ Data ingestion: {result.status}")
        print("   Extractors configured: CSV, API sources")
        print("   Target: PostgreSQL data warehouse")
    except Exception as e:
        print(f"❌ Data ingestion setup failed: {str(e)}")
        return False

    # Step 3: Data Transformation
    print("\n3. Setting up data transformation...")
    transform_request = (
        "Create dbt models to transform raw data into analytics-ready tables"
    )

    try:
        result = await executor.process_request(transform_request)
        print(f"✅ Data transformation: {result.status}")
        print("   dbt models created: staging, intermediate, marts")
        print("   Tests and documentation included")
    except Exception as e:
        print(f"❌ Data transformation setup failed: {str(e)}")
        return False

    # Step 4: Data Quality Monitoring
    print("\n4. Setting up data quality monitoring...")
    quality_request = (
        "Implement Great Expectations for data quality monitoring and alerting"
    )

    try:
        result = await executor.process_request(quality_request)
        print(f"✅ Data quality monitoring: {result.status}")
        print("   Expectations created for all critical datasets")
        print("   Automated validation in pipeline")
    except Exception as e:
        print(f"❌ Data quality setup failed: {str(e)}")
        return False

    # Step 5: Orchestration
    print("\n5. Setting up pipeline orchestration...")
    orchestration_request = (
        "Create Airflow DAGs to orchestrate the entire data pipeline"
    )

    try:
        result = await executor.process_request(orchestration_request)
        print(f"✅ Pipeline orchestration: {result.status}")
        print("   DAGs created: daily_pipeline, hourly_updates")
        print("   Dependencies and error handling configured")
    except Exception as e:
        print(f"❌ Orchestration setup failed: {str(e)}")
        return False

    # Step 6: Analytics and Visualization
    print("\n6. Setting up analytics and visualization...")
    analytics_request = (
        "Configure Metabase dashboards and Evidence reports for business users"
    )

    try:
        result = await executor.process_request(analytics_request)
        print(f"✅ Analytics setup: {result.status}")
        print("   Metabase dashboards: Executive, Operations, Sales")
        print("   Evidence reports: Automated insights and KPIs")
    except Exception as e:
        print(f"❌ Analytics setup failed: {str(e)}")
        return False

    # Step 7: Monitoring and Alerting
    print("\n7. Setting up monitoring and alerting...")
    monitoring_request = "Set up comprehensive monitoring for all pipeline components"

    try:
        result = await executor.process_request(monitoring_request)
        print(f"✅ Monitoring setup: {result.status}")
        print("   Metrics collected: pipeline health, data quality, performance")
        print("   Alerts configured: failures, SLA breaches, quality issues")
    except Exception as e:
        print(f"❌ Monitoring setup failed: {str(e)}")
        return False

    return True


async def demonstrate_pipeline_operations():
    """Demonstrate common pipeline operations."""

    print("\n\n🔧 Pipeline Operations Examples")
    print("=" * 50)

    executor = WorkflowExecutor()

    operations = [
        "Run a full refresh of all dbt models",
        "Check the status of all pipeline components",
        "Validate data quality for the last 24 hours",
        "Generate a pipeline performance report",
        "Scale up the infrastructure for peak processing",
        "Backup critical datasets to cloud storage",
        "Test the disaster recovery procedures",
    ]

    for i, operation in enumerate(operations, 1):
        print(f"\n{i}. {operation}")

        try:
            result = await executor.process_request(operation)
            print(f"   Status: {result.status}")
            print(f"   Execution time: {result.metadata.get('execution_time', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


async def demonstrate_pipeline_troubleshooting():
    """Demonstrate pipeline troubleshooting scenarios."""

    print("\n\n🔍 Pipeline Troubleshooting Examples")
    print("=" * 50)

    executor = WorkflowExecutor()

    troubleshooting_scenarios = [
        "Pipeline failed at the transformation step - diagnose and fix",
        "Data quality tests are failing - investigate and resolve",
        "Airflow DAG is stuck - clear and restart",
        "PostgreSQL connection issues - check and repair",
        "Metabase dashboards showing old data - refresh pipeline",
        "High memory usage in dbt models - optimize queries",
    ]

    for i, scenario in enumerate(troubleshooting_scenarios, 1):
        print(f"\n{i}. Scenario: {scenario}")

        try:
            result = await executor.process_request(scenario)
            print(f"   Resolution: {result.status}")
            print(f"   Actions taken: {result.metadata.get('actions_taken', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


async def main():
    """Main execution function."""

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Set up the complete pipeline
        success = await setup_complete_data_pipeline()

        if success:
            print("\n🎉 Complete data pipeline setup successful!")

            # Demonstrate operations
            await demonstrate_pipeline_operations()

            # Demonstrate troubleshooting
            await demonstrate_pipeline_troubleshooting()

            print("\n✅ Data pipeline examples completed!")
        else:
            print("\n❌ Pipeline setup failed. Please check the logs.")
            return 1

    except Exception as e:
        print(f"❌ Error running pipeline examples: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
