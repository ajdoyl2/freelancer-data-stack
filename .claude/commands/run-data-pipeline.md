# Run Data Pipeline

Execute the complete data pipeline from extraction to dashboard.

## Pipeline Architecture

1. **Data Extraction (Meltano)**
   - Source: transactions.csv
   - Extractor: tap-csv
   - Configuration: Multi-environment support

2. **Data Loading (Meltano)**
   - Target: DuckDB analytics database
   - Loader: target-duckdb
   - Destination: /data/duckdb/analytics.db

3. **Data Transformation (dbt)**
   - Source: Raw transaction data
   - Models: 31-column EDA transformation
   - Quality: dbt-expectations validation

4. **Data Visualization**
   - Streamlit dashboard
   - Real-time metrics
   - Interactive analytics

## Pipeline Execution

### Manual Execution
```bash
# 1. Run Meltano ELT
cd data_stack/meltano
meltano --environment=dev elt tap-csv target-duckdb

# 2. Run dbt transformations
cd data_stack/dbt
dbt run --profiles-dir .
dbt test --profiles-dir .

# 3. View results in dashboard
# Open http://localhost:8501
```

### Automated Execution (Airflow)
```bash
# Trigger DAG via Airflow UI
# http://localhost:8080
# DAG: ai_agent_data_pipeline

# Or trigger via CLI
docker-compose exec airflow-webserver airflow dags trigger ai_agent_data_pipeline
```

### AI Agent Execution
```python
from agents.data_stack_engineer import DataStackEngineer
from agents.base_agent import WorkflowRequest

agent = DataStackEngineer()
result = await agent.execute_task(WorkflowRequest(
    user_prompt="Run the complete ELT and transformation pipeline"
))
```

## Pipeline Stages

1. **Pre-Flight Checks**
   - Validate source data format
   - Check service health
   - Verify database connectivity

2. **Extract & Load**
   - Read transactions.csv
   - Validate data quality
   - Load to DuckDB raw tables

3. **Transform & Model**
   - Apply EDA transformations
   - Create 31-column staging model
   - Run data quality tests

4. **Validate & Report**
   - Check transformation results
   - Generate quality metrics
   - Update monitoring dashboards

## Success Criteria

- ✅ Source data processed successfully
- ✅ All records loaded to DuckDB
- ✅ dbt transformations complete
- ✅ Data quality tests pass (85%+ score)
- ✅ Dashboard updated with new data
- ✅ No errors in pipeline logs

## Monitoring & Troubleshooting

```bash
# Check pipeline status
./scripts/validate_pipeline.py

# View pipeline logs
docker-compose logs meltano
docker-compose logs airflow-worker

# Check data quality
# Access Streamlit dashboard: http://localhost:8501
```

Execute the pipeline and monitor results through the available dashboards and validation tools.