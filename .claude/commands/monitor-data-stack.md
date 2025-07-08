# Monitor Data Stack Health

Monitor the AI agent data stack infrastructure and pipeline health.

## Monitoring Components

1. **Real-Time Dashboards**
   - Streamlit Data Dashboard (http://localhost:8501)
   - Grafana Infrastructure (http://localhost:3000)
   - Airflow UI (http://localhost:8080)

2. **Metrics Collection**
   - Prometheus metrics collection
   - Service health monitoring
   - Performance metrics tracking
   - Data quality metrics

3. **Alerting System**
   - Service availability alerts
   - Data quality threshold alerts
   - Performance degradation alerts
   - Resource usage alerts

## Key Metrics

### Infrastructure Metrics
- Service uptime and availability
- CPU, memory, and disk usage
- Container health and status
- Network connectivity

### Data Pipeline Metrics
- Pipeline execution times
- Data quality scores
- Record processing rates
- Error rates and failures

### AI Agent Metrics
- Agent response times
- Task success rates
- Automation effectiveness
- Cost optimization metrics

## Monitoring Tasks

1. **Check Overall Health**
   - Service status verification
   - Performance benchmarking
   - Resource utilization review
   - Alert status check

2. **Data Quality Monitoring**
   - Quality score tracking
   - Schema compliance validation
   - Business logic verification
   - Outlier detection

3. **Performance Analysis**
   - Query execution analysis
   - Pipeline performance review
   - Resource optimization opportunities
   - Cost analysis

## Access Points

```bash
# Quick health check
./scripts/validate_pipeline.py --verbose

# View service status
docker-compose ps

# Check service logs
docker-compose logs airflow-webserver
docker-compose logs meltano
docker-compose logs grafana

# Access dashboards
echo "Streamlit: http://localhost:8501"
echo "Grafana: http://localhost:3000"
echo "Airflow: http://localhost:8080"
```

## Health Indicators

- ✅ All services running
- ✅ Data quality ≥ 85%
- ✅ Pipeline execution < 30 minutes
- ✅ No critical alerts
- ✅ Resource usage < 80%