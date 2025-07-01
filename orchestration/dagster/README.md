# Dagster Orchestration for Freelancer Data Stack

This directory contains the Dagster orchestration setup for the freelancer data stack, implementing software-defined assets for the complete data pipeline.

## Overview

The Dagster orchestration provides:

- **Software-defined assets** for each pipeline component
- **Scheduled execution** with daily and incremental sync patterns
- **Event-driven sensors** for GitHub releases and data quality alerts
- **DataHub integration** for metadata management and lineage tracking
- **Comprehensive monitoring** and alerting capabilities

## Architecture

### Assets

The pipeline is organized into asset groups:

#### Ingestion Assets
- `airbyte_sync_job` - Airbyte data extraction from external sources
- `dlt_ingestion_pipeline` - dlt pipeline for data loading

#### Transformation Assets  
- `dbt_run` - dbt transformations and model execution
- `dbt_test` - dbt data quality tests

#### Quality Assets
- `great_expectations_validation` - Data validation checkpoints

#### Catalog Assets
- `datahub_metadata_ingestion` - Metadata catalog updates

### Jobs

Multiple job definitions for different execution patterns:

- `daily_data_pipeline` - Complete daily pipeline
- `incremental_sync_pipeline` - Frequent incremental updates
- `transformation_pipeline` - Transformation and testing only
- `data_quality_pipeline` - Quality validation and monitoring
- `release_triggered_pipeline` - Triggered by GitHub releases
- `emergency_data_refresh` - Emergency pipeline with validation bypassing

### Schedules

- **Daily Schedule** - Runs complete pipeline at 2 AM UTC
- **Incremental Schedule** - Runs every 6 hours for fresh data

### Sensors

- **GitHub Release Sensor** - Monitors releases and triggers pipeline
- **Data Quality Alert Sensor** - Responds to quality issues
- **File Arrival Sensor** - Processes uploaded batch files

## Configuration

### Environment Variables

Set these environment variables for proper operation:

```bash
# Dagster Configuration
DAGSTER_ENV=prod
DAGSTER_POSTGRES_URL=postgresql://user:pass@host:5432/dagster

# Airbyte Configuration
AIRBYTE_HOST=localhost
AIRBYTE_PORT=8000
AIRBYTE_CONNECTION_ID=your-connection-id

# dlt Configuration  
DLT_PIPELINE_NAME=freelancer_data
DLT_DESTINATION=duckdb
DLT_DATASET_NAME=freelancer_raw

# dbt Configuration
DBT_PROJECT_DIR=/app/transformation/dbt
DBT_PROFILES_DIR=/app/transformation/dbt
DBT_TARGET=prod

# Great Expectations Configuration
GE_PROJECT_DIR=/app/quality/great_expectations
GE_CHECKPOINT_NAME=daily_validation

# DataHub Configuration
DATAHUB_GMS_URL=http://localhost:8080
DATAHUB_GMS_TOKEN=your-datahub-token

# GitHub Configuration (for release sensor)
GITHUB_REPO=your-org/your-repo
GITHUB_TOKEN=your-github-token
```

### DataHub Integration

The Dagster assets are automatically mapped to DataHub via the `dagster-datahub` integration:

- Asset lineage is tracked and visualized
- Metadata including owners, descriptions, and tags
- Usage statistics and operational metrics
- Data quality results and validation status

## Deployment

### Development

1. Install dependencies:
```bash
pip install dagster dagster-webserver dagster-datahub
```

2. Set environment variables in `.env` file

3. Start Dagster development server:
```bash
dagster dev -f orchestration/dagster/definitions.py
```

4. Access UI at http://localhost:3000

### Production

1. Configure `dagster.yaml` with appropriate storage backends

2. Deploy using Docker:
```bash
docker-compose -f docker-compose.yml up dagster-daemon dagster-webserver
```

3. Configure monitoring and alerting

## Usage Examples

### Manual Pipeline Execution

```python
from dagster import DagsterInstance
from orchestration.dagster.definitions import defs

# Get Dagster instance
instance = DagsterInstance.get()

# Execute daily pipeline
result = defs.get_job_def("daily_data_pipeline").execute_in_process(
    instance=instance
)
```

### Asset Materialization

```python
# Materialize specific assets
from dagster import materialize

result = materialize(
    [airbyte_sync_job, dbt_run],
    instance=instance
)
```

### Schedule Management

```python
# Start daily schedule
instance.start_schedule("daily_pipeline_schedule")

# Stop schedule
instance.stop_schedule("daily_pipeline_schedule")
```

### Sensor Management

```python
# Start GitHub release sensor
instance.start_sensor("github_release_sensor")

# Check sensor status
sensor_state = instance.get_sensor_state("github_release_sensor")
```

## Monitoring and Alerting

### Pipeline Monitoring

The `pipeline_monitoring` job performs health checks on:
- Airbyte connectivity
- DuckDB connectivity  
- DataHub API access
- GitHub API access

Schedule this job to run every 15 minutes:

```python
@schedule(
    cron_schedule="*/15 * * * *",
    job_name="pipeline_monitoring"
)
def monitoring_schedule(context):
    return RunRequest()
```

### Data Quality Alerts

Configure the data quality alert sensor to monitor:
- Great Expectations validation failures
- dbt test failures
- Custom data quality metrics

Place alert files in `/app/quality/alerts/` to trigger remediation.

### Operational Metrics

Dagster provides built-in metrics for:
- Asset materialization success/failure rates
- Pipeline execution times
- Resource utilization
- Backfill progress

## Asset Dependencies

The assets are organized with clear dependencies:

```
airbyte_sync_job ──┐
                   ├── dbt_run ──── dbt_test
dlt_ingestion_pipeline ──┘              │
                                        ├── great_expectations_validation
                                        │                  │
                                        └──────────────────┼── datahub_metadata_ingestion
```

## Customization

### Adding New Assets

1. Define asset in `assets.py`:
```python
@asset(
    group_name="my_group",
    description="My custom asset"
)
def my_custom_asset():
    # Implementation
    pass
```

2. Add to job selection in `jobs.py`

3. Update DataHub mappings in `dagster_ingestion.yml`

### Adding New Sensors

1. Define sensor in `schedules_sensors.py`:
```python
@sensor(name="my_sensor", job_name="my_job")
def my_custom_sensor(context):
    # Implementation
    pass
```

2. Add to sensor list in `definitions.py`

### Custom Resources

Define custom resources for external integrations:

```python
class MyServiceResource(ConfigurableResource):
    api_key: str
    base_url: str
    
    def get_client(self):
        return MyServiceClient(self.api_key, self.base_url)
```

## Troubleshooting

### Common Issues

1. **Asset Materialization Failures**
   - Check asset dependencies are satisfied
   - Verify configuration and credentials
   - Review logs in Dagster UI

2. **Schedule Not Running**
   - Ensure `dagster-daemon` is running
   - Check schedule is started in UI
   - Verify cron expression syntax

3. **Sensor Not Triggering**
   - Check sensor is running (not stopped)
   - Verify external dependencies (GitHub API, file paths)
   - Review sensor evaluation logs

4. **DataHub Integration Issues**
   - Verify DataHub URL and token
   - Check network connectivity
   - Review ingestion configuration

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Use Dagster's built-in logging:

```python
from dagster import get_dagster_logger

logger = get_dagster_logger()
logger.info("Debug message")
```

## Performance Optimization

### Asset Partitioning

For large datasets, consider partitioning assets:

```python
@asset(partitions_def=DailyPartitionsDefinition(start_date="2024-01-01"))
def partitioned_asset():
    pass
```

### Parallel Execution

Configure parallel execution in `dagster.yaml`:

```yaml
run_coordinator:
  config:
    max_concurrent_runs: 10
```

### Resource Optimization

Use appropriate compute resources:

```python
@asset(
    required_resource_keys={"compute"},
    compute_kind="high_memory"
)
def memory_intensive_asset():
    pass
```

This orchestration setup provides a robust, scalable foundation for managing the freelancer data stack with comprehensive monitoring, quality controls, and metadata management.
