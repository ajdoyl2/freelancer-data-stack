"""
AI Agent-Driven Data Pipeline DAG

This DAG orchestrates the complete data pipeline for the AI agent data stack,
including Meltano ELT, dbt transformations, data quality checks, and AI agent notifications.
"""

import json
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule

# Default arguments for the DAG
default_args = {
    "owner": "ai-agent-data-stack",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

# DAG definition
dag = DAG(
    "ai_agent_data_pipeline",
    default_args=default_args,
    description="AI Agent-Driven Data Stack Pipeline",
    schedule_interval="@daily",  # Run daily at midnight
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=["ai-agents", "data-stack", "elt", "dbt", "analytics"],
    doc_md=__doc__,
)

# Configuration variables
MELTANO_PROJECT_PATH = "/app/data_stack/meltano"
DBT_PROJECT_PATH = "/app/data_stack/dbt"
TRANSACTIONS_FILE_PATH = "/app/transactions.csv"
DUCKDB_PATH = "/data/duckdb/analytics.db"
AI_AGENT_API_URL = "http://mcp-server:80"


def notify_ai_agents(**context) -> None:
    """
    Notify AI agents about pipeline completion status.

    Args:
        context: Airflow context dictionary
    """
    task_instance = context["task_instance"]
    dag_run = context["dag_run"]

    notification_data = {
        "dag_id": dag_run.dag_id,
        "run_id": dag_run.run_id,
        "execution_date": dag_run.execution_date.isoformat(),
        "state": task_instance.state,
        "task_id": task_instance.task_id,
        "timestamp": datetime.now().isoformat(),
        "data_pipeline_status": (
            "completed" if task_instance.state == "success" else "failed"
        ),
    }

    logging.info(f"Notifying AI agents: {notification_data}")

    # Store notification in XCom for agents to access
    task_instance.xcom_push(key="ai_agent_notification", value=notification_data)


def check_data_quality(**context) -> bool:
    """
    Perform data quality checks and determine if pipeline should continue.

    Args:
        context: Airflow context dictionary

    Returns:
        bool: True if data quality passes thresholds
    """
    import sys

    sys.path.append("/app")

    import asyncio

    from tools.duckdb_tools import DuckDBTools

    async def run_quality_checks():
        duckdb_tools = DuckDBTools()

        # Check if staging table exists and has data
        result = await duckdb_tools.execute_query(
            "SELECT COUNT(*) as row_count FROM main.stg_transactions",
            db_path=DUCKDB_PATH,
        )

        if not result["success"]:
            logging.error(f"Failed to check staging table: {result.get('error')}")
            return False

        row_count = result["rows"][0][0] if result["rows"] else 0
        logging.info(f"Staging table has {row_count} rows")

        if row_count == 0:
            logging.warning("Staging table is empty")
            return False

        # Get comprehensive data quality metrics
        quality_metrics = await duckdb_tools.get_data_quality_metrics(
            table_name="stg_transactions", db_path=DUCKDB_PATH
        )

        if not quality_metrics["success"]:
            logging.error(
                f"Failed to get quality metrics: {quality_metrics.get('error')}"
            )
            return False

        overall_score = quality_metrics.get("overall_score", 0)
        logging.info(f"Overall data quality score: {overall_score}")

        # Check against thresholds
        quality_threshold = 0.85  # 85% quality threshold

        if overall_score < quality_threshold:
            logging.error(
                f"Data quality score {overall_score} below threshold {quality_threshold}"
            )
            return False

        # Store quality metrics in XCom
        context["task_instance"].xcom_push(
            key="data_quality_metrics", value=quality_metrics
        )

        return True

    # Run async function
    return asyncio.run(run_quality_checks())


def generate_eda_report(**context) -> None:
    """
    Generate automated EDA report for AI agents.

    Args:
        context: Airflow context dictionary
    """
    import sys

    sys.path.append("/app")

    import asyncio

    from tools.duckdb_tools import DuckDBTools

    async def create_eda_report():
        duckdb_tools = DuckDBTools()

        # Get basic statistics
        stats_query = """
        SELECT
            COUNT(*) as total_transactions,
            COUNT(DISTINCT account_name) as unique_accounts,
            COUNT(DISTINCT category) as unique_categories,
            MIN(transaction_date) as min_date,
            MAX(transaction_date) as max_date,
            SUM(CASE WHEN transaction_flow = 'INFLOW' THEN amount ELSE 0 END) as total_inflows,
            SUM(CASE WHEN transaction_flow = 'OUTFLOW' THEN ABS(amount) ELSE 0 END) as total_outflows,
            AVG(amount_abs) as avg_transaction_amount,
            COUNT(CASE WHEN is_high_value THEN 1 END) as high_value_transactions,
            COUNT(CASE WHEN is_amount_outlier THEN 1 END) as outlier_transactions
        FROM main.stg_transactions
        """

        stats_result = await duckdb_tools.execute_query(
            stats_query, db_path=DUCKDB_PATH
        )

        if stats_result["success"]:
            row = stats_result["rows"][0]
            columns = stats_result["columns"]
            stats_dict = dict(zip(columns, row, strict=False))

            # Get category breakdown
            category_query = """
            SELECT
                category,
                COUNT(*) as transaction_count,
                SUM(amount_abs) as total_amount,
                AVG(amount_abs) as avg_amount
            FROM main.stg_transactions
            GROUP BY category
            ORDER BY total_amount DESC
            LIMIT 10
            """

            category_result = await duckdb_tools.execute_query(
                category_query, db_path=DUCKDB_PATH
            )

            eda_report = {
                "generated_at": datetime.now().isoformat(),
                "summary_statistics": stats_dict,
                "top_categories": (
                    category_result["rows"] if category_result["success"] else []
                ),
                "data_quality_passed": True,
                "recommendations": [
                    "Monitor high-value transactions for anomalies",
                    "Review outlier transactions for data quality issues",
                    "Consider additional data sources for enhanced analysis",
                ],
            }

            # Store EDA report in XCom
            context["task_instance"].xcom_push(key="eda_report", value=eda_report)
            logging.info(f"Generated EDA report: {json.dumps(eda_report, indent=2)}")
        else:
            logging.error(f"Failed to generate EDA report: {stats_result.get('error')}")

    asyncio.run(create_eda_report())


# Pipeline start
start_pipeline = DummyOperator(
    task_id="start_pipeline",
    dag=dag,
)

# Check if transaction file exists
check_transactions_file = FileSensor(
    task_id="check_transactions_file",
    filepath=TRANSACTIONS_FILE_PATH,
    fs_conn_id="fs_default",
    poke_interval=30,
    timeout=300,
    dag=dag,
)

# Health check for required services
check_duckdb_service = BashOperator(
    task_id="check_duckdb_service",
    bash_command=f"python -c \"import duckdb; conn = duckdb.connect('{DUCKDB_PATH}'); print('DuckDB connection successful')\"",
    dag=dag,
)

# Meltano ELT: Extract from CSV and Load to DuckDB
meltano_extract_load = BashOperator(
    task_id="meltano_extract_load",
    bash_command=f"""
    cd {MELTANO_PROJECT_PATH} &&
    meltano --environment=dev elt tap-csv target-duckdb
    """,
    env={
        "MELTANO_PROJECT_ROOT": MELTANO_PROJECT_PATH,
        "DUCKDB_PATH": DUCKDB_PATH,
    },
    dag=dag,
)

# Install dbt dependencies
dbt_deps = BashOperator(
    task_id="dbt_deps",
    bash_command=f"cd {DBT_PROJECT_PATH} && dbt deps --profiles-dir .",
    dag=dag,
)

# dbt compile - check SQL compilation
dbt_compile = BashOperator(
    task_id="dbt_compile",
    bash_command=f"cd {DBT_PROJECT_PATH} && dbt compile --profiles-dir .",
    dag=dag,
)

# dbt run - execute transformations
dbt_run = BashOperator(
    task_id="dbt_run",
    bash_command=f"cd {DBT_PROJECT_PATH} && dbt run --profiles-dir .",
    dag=dag,
)

# dbt test - run data quality tests
dbt_test = BashOperator(
    task_id="dbt_test",
    bash_command=f"cd {DBT_PROJECT_PATH} && dbt test --profiles-dir .",
    dag=dag,
)

# Custom data quality checks
data_quality_check = PythonOperator(
    task_id="data_quality_check",
    python_callable=check_data_quality,
    dag=dag,
)

# Generate automated EDA report
generate_eda = PythonOperator(
    task_id="generate_eda_report",
    python_callable=generate_eda_report,
    dag=dag,
)

# Optimize DuckDB database
optimize_database = BashOperator(
    task_id="optimize_database",
    bash_command=f"""
    python -c "
import asyncio
import sys
sys.path.append('/app')
from tools.duckdb_tools import DuckDBTools

async def optimize():
    tools = DuckDBTools()
    result = await tools.optimize_database('{DUCKDB_PATH}')
    print(f'Optimization result: {{result}}')

asyncio.run(optimize())
"
    """,
    dag=dag,
)

# Notify AI agents of successful completion
notify_success = PythonOperator(
    task_id="notify_ai_agents_success",
    python_callable=notify_ai_agents,
    dag=dag,
)

# Handle pipeline failure
notify_failure = PythonOperator(
    task_id="notify_ai_agents_failure",
    python_callable=notify_ai_agents,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag,
)

# Pipeline completion
end_pipeline = DummyOperator(
    task_id="end_pipeline",
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    dag=dag,
)

# Set up task dependencies
start_pipeline >> [check_transactions_file, check_duckdb_service]

check_transactions_file >> meltano_extract_load
check_duckdb_service >> dbt_deps

meltano_extract_load >> dbt_deps
dbt_deps >> dbt_compile
dbt_compile >> dbt_run
dbt_run >> dbt_test

dbt_test >> data_quality_check
data_quality_check >> generate_eda
generate_eda >> optimize_database

optimize_database >> notify_success
notify_success >> end_pipeline

# Failure handling
[meltano_extract_load, dbt_run, dbt_test, data_quality_check] >> notify_failure
notify_failure >> end_pipeline

# Add task documentation
start_pipeline.doc_md = """
## Pipeline Start
Initiates the AI agent-driven data pipeline execution.
"""

meltano_extract_load.doc_md = """
## Meltano ELT
Extracts data from transactions.csv and loads into DuckDB using Meltano.
- Extractor: tap-csv
- Loader: target-duckdb
- Environment: dev
"""

dbt_run.doc_md = """
## dbt Transformations
Executes dbt models to transform raw data into analytics-ready staging tables.
- Includes automated EDA transformations
- Applies data quality enhancements
- Creates derived features for analysis
"""

dbt_test.doc_md = """
## dbt Testing
Runs comprehensive data quality tests using dbt-expectations.
- Tests data completeness, uniqueness, and validity
- Validates business logic rules
- Ensures data integrity constraints
"""

data_quality_check.doc_md = """
## Data Quality Validation
Performs additional data quality checks using DuckDBTools.
- Calculates overall quality score
- Identifies outliers and anomalies
- Validates against quality thresholds
"""

generate_eda.doc_md = """
## Automated EDA Report
Generates exploratory data analysis report for AI agents.
- Summary statistics and insights
- Category analysis and trends
- Data quality recommendations
"""
