# Deploy AI Agent Data Stack

Automatically deploy the complete AI agent-driven data stack with validation.

## Deployment Process

1. **Environment Setup**
   - Validate prerequisites (Docker, Python 3.11+)
   - Check available resources (4GB RAM, 10GB disk)
   - Verify configuration files

2. **Infrastructure Deployment**
   - Run automated deployment script
   - Start Docker services (PostgreSQL, Redis, Airflow, Meltano, DuckDB)
   - Configure AI agent integration
   - Set up monitoring (Prometheus, Grafana)

3. **Data Pipeline Initialization**
   - Initialize DuckDB schemas
   - Configure Meltano ELT pipeline
   - Deploy dbt transformations
   - Set up Airflow DAGs

4. **Validation & Verification**
   - Run end-to-end pipeline validation
   - Verify data quality metrics (85%+ threshold)
   - Check service health and monitoring
   - Generate deployment report

## Commands to Execute

```bash
# Deploy the complete stack
./scripts/deploy_stack.py --environment=dev --verbose

# Validate deployment
./scripts/validate_pipeline.py --verbose --output-format=console

# Check service status
docker-compose ps
```

## Success Criteria

- All services running and healthy
- Data pipeline processes transactions.csv successfully
- Streamlit dashboard accessible at http://localhost:8501
- Grafana monitoring at http://localhost:3000
- Airflow UI at http://localhost:8080
- Data quality score ≥ 85%