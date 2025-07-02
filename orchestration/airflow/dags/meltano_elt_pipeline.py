"""
Airflow DAG for orchestrating Meltano ELT pipeline

This DAG orchestrates:
1. Extract data using tap-csv
2. Load data into DuckDB using target-duckdb
3. Transform data using dbt
4. Run data quality tests
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor

# Default arguments for the DAG
default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    "meltano_elt_pipeline",
    default_args=default_args,
    description="Meltano ELT pipeline with dbt transformations",
    schedule_interval="@daily",
    catchup=False,
    tags=["meltano", "elt", "dbt", "data-pipeline"],
)

# Check if CSV file exists before starting pipeline
csv_sensor = FileSensor(
    task_id="wait_for_csv_file",
    filepath="/app/meltano/extract/sample_data.csv",
    fs_conn_id="fs_default",
    poke_interval=30,
    timeout=300,
    dag=dag,
)

# Extract and Load using Meltano
meltano_el = BashOperator(
    task_id="meltano_extract_load",
    bash_command="""
    cd /app/meltano && \
    meltano run tap-csv target-duckdb
    """,
    dag=dag,
)

# Transform using dbt via Meltano
meltano_transform = BashOperator(
    task_id="meltano_dbt_transform",
    bash_command="""
    cd /app/meltano && \
    meltano invoke dbt-duckdb run
    """,
    dag=dag,
)

# Test using dbt via Meltano
meltano_test = BashOperator(
    task_id="meltano_dbt_test",
    bash_command="""
    cd /app/meltano && \
    meltano invoke dbt-duckdb test
    """,
    dag=dag,
)

# Data quality checks using duckdb
data_quality_check = BashOperator(
    task_id="data_quality_check",
    bash_command="""
    cd /app/meltano && \
    python -c "
import duckdb
conn = duckdb.connect('/data/duckdb/meltano.db')
result = conn.execute('SELECT COUNT(*) FROM raw.sample_data').fetchone()
print(f'Records in raw.sample_data: {result[0]}')
assert result[0] > 0, 'No data found in sample_data table'
conn.close()
print('Data quality check passed!')
"
    """,
    dag=dag,
)

# Set task dependencies
csv_sensor >> meltano_el >> meltano_transform >> meltano_test >> data_quality_check
