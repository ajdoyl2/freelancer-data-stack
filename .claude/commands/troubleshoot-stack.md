# Troubleshoot Data Stack Issues

Diagnose and resolve issues in the AI agent data stack.

## Common Issues & Solutions

### Docker Service Issues

**Issue: Services won't start**
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs [service-name]

# Restart services
docker-compose down && docker-compose up -d

# Rebuild if needed
docker-compose build --no-cache [service-name]
```

**Issue: Container health checks failing**
```bash
# Check health status
docker-compose ps

# Inspect specific container
docker inspect [container-name]

# Check resource usage
docker stats
```

### Database Connection Issues

**Issue: DuckDB connection failures**
```bash
# Check DuckDB container
docker-compose logs duckdb-http

# Test database connectivity
python -c "import duckdb; duckdb.connect('/data/duckdb/analytics.db').execute('SELECT 1')"

# Verify file permissions
ls -la /data/duckdb/
```

**Issue: PostgreSQL connection problems**
```bash
# Check PostgreSQL health
docker-compose exec postgres pg_isready -U postgres

# Test connection
docker-compose exec postgres psql -U postgres -c "SELECT version();"

# Check logs
docker-compose logs postgres
```

### Pipeline Execution Issues

**Issue: Meltano ELT failures**
```bash
# Check Meltano logs
docker-compose logs meltano

# Test tap connection
cd data_stack/meltano
meltano invoke tap-csv --test

# Validate configuration
meltano config tap-csv list
```

**Issue: dbt transformation errors**
```bash
# Check dbt compilation
cd data_stack/dbt
dbt compile --profiles-dir .

# Run with debug
dbt run --profiles-dir . --debug

# Check model dependencies
dbt deps --profiles-dir .
```

### Airflow DAG Issues

**Issue: DAGs not loading**
```bash
# Check Airflow logs
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler

# List DAGs
docker-compose exec airflow-webserver airflow dags list

# Check DAG syntax
python data_stack/airflow/dags/data_pipeline_dag.py
```

**Issue: Task failures**
```bash
# Check task logs in Airflow UI
# http://localhost:8080

# Manual task test
docker-compose exec airflow-webserver airflow tasks test ai_agent_data_pipeline [task_id] [date]
```

## Diagnostic Commands

### Quick Health Check
```bash
# Run complete validation
./scripts/validate_pipeline.py --verbose

# Check deployment status
./scripts/deploy_stack.py --dry-run

# Service status overview
docker-compose ps
```

### Detailed Diagnostics
```bash
# System resources
df -h
free -h
docker system df

# Network connectivity
docker network ls
docker network inspect freelancer-data-stack_data-stack

# Container inspection
docker inspect [container-name]
```

### Data Quality Issues
```bash
# Check data quality metrics
./scripts/validate_pipeline.py --data-quality-threshold=0.8

# Validate source data
python -c "import pandas as pd; df = pd.read_csv('transactions.csv'); print(df.info())"

# Check transformation results
# Access Streamlit dashboard: http://localhost:8501
```

## Recovery Procedures

### Complete Stack Reset
```bash
# Stop all services
docker-compose down

# Clean volumes (CAUTION: Data loss)
docker-compose down -v

# Remove containers and images
docker system prune -a

# Redeploy
./scripts/deploy_stack.py --force-rebuild
```

### Partial Service Recovery
```bash
# Restart specific service
docker-compose restart [service-name]

# Recreate problematic container
docker-compose up -d --force-recreate [service-name]
```

### Data Recovery
```bash
# Backup current data
cp -r /data/duckdb /backup/duckdb-$(date +%Y%m%d)

# Restore from backup if needed
# cp -r /backup/duckdb-YYYYMMDD /data/duckdb
```

## Escalation

If issues persist after troubleshooting:

1. **Collect Diagnostic Information**
   - Service logs
   - Configuration files
   - System resource usage
   - Error messages

2. **Use AI Agent for Analysis**
   ```python
   agent = DataStackEngineer()
   result = await agent.execute_task(WorkflowRequest(
       user_prompt="Diagnose and troubleshoot system issues"
   ))
   ```

3. **Generate Support Bundle**
   ```bash
   # Create support bundle
   tar -czf support-bundle-$(date +%Y%m%d).tar.gz \
     docker-compose.yml \
     /data/logs/ \
     validation_report.json
   ```

The AI agent can often automatically detect and resolve common issues.