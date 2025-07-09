"""
Example Data Pipeline DAG for Freelancer Data Stack

This DAG demonstrates a basic data pipeline workflow with:
1. Data extraction from a source
2. Data transformation
3. Data quality checks with Great Expectations
4. Loading to DuckDB for analytics

Author: Freelancer Data Stack
Created: 2024-06-30
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2024, 6, 30),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    "example_data_pipeline",
    default_args=default_args,
    description="Example data pipeline for the freelancer data stack",
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=["example", "data-pipeline", "freelancer-stack"],
)

# Task 1: Start pipeline
start_pipeline = DummyOperator(
    task_id="start_pipeline",
    dag=dag,
)

# Task 2: Extract data (example using Airbyte)
extract_data = BashOperator(
    task_id="extract_data",
    bash_command="""
    echo "Starting data extraction..."
    # Example: Trigger Airbyte sync via API
    # curl -X POST "http://airbyte-server:8001/api/v1/connections/sync" \
    #      -H "Content-Type: application/json" \
    #      -d '{"connectionId": "your-connection-id"}'
    echo "Data extraction completed"
    """,
    dag=dag,
)


# Task 3: Transform data (example using dbt or custom Python)
def transform_data():
    """
    Example data transformation function
    In production, this would run dbt models or custom transformations
    """
    print("Starting data transformation...")
    # Example transformation logic here
    print("Data transformation completed")
    return "transformation_complete"


transform_data_task = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    dag=dag,
)

# Task 4: Data quality checks with Great Expectations
validate_data = BashOperator(
    task_id="validate_data",
    bash_command="""
    echo "Running data quality checks..."
    # Example: Run Great Expectations validation
    # great_expectations checkpoint run my_checkpoint
    echo "Data quality validation completed"
    """,
    dag=dag,
)

# Task 5: Load to DuckDB for analytics
load_to_analytics = BashOperator(
    task_id="load_to_analytics",
    bash_command="""
    echo "Loading data to DuckDB for analytics..."
    # Example: Load data to DuckDB via HTTP API
    # curl -X POST "http://duckdb-http:8080/query" \
    #      -H "Content-Type: application/json" \
    #      -d '{"query": "INSERT INTO analytics_table SELECT * FROM staging_table"}'
    echo "Data loaded to analytics store"
    """,
    dag=dag,
)

# Task 6: Update DataHub metadata
update_catalog = BashOperator(
    task_id="update_catalog",
    bash_command="""
    echo "Updating data catalog..."
    # Example: Push metadata to DataHub
    # datahub ingest -c datahub_config.yml
    echo "Data catalog updated"
    """,
    dag=dag,
)

# Task 7: End pipeline
end_pipeline = DummyOperator(
    task_id="end_pipeline",
    dag=dag,
)

# Define task dependencies
(
    start_pipeline
    >> extract_data
    >> transform_data_task
    >> validate_data
    >> load_to_analytics
    >> update_catalog
    >> end_pipeline
)
