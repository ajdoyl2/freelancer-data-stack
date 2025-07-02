# 📊 Data Engineering Prompts Index

## Available Prompts

### Pipeline Design & Architecture
- **[pipeline_design.md](pipeline_design.md)** - End-to-end data pipeline architecture
- **[etl_design.md](etl_design.md)** - Extract, Transform, Load pattern implementation
- **[streaming_pipeline.md](streaming_pipeline.md)** - Real-time data processing design
- **[data_warehouse_design.md](data_warehouse_design.md)** - Dimensional modeling and warehouse schema

### Data Quality & Validation
- **[data_quality_checks.md](data_quality_checks.md)** - Comprehensive data validation framework
- **[schema_validation.md](schema_validation.md)** - Data schema enforcement and evolution
- **[data_profiling.md](data_profiling.md)** - Data discovery and profiling analysis
- **[anomaly_detection.md](anomaly_detection.md)** - Data anomaly identification patterns

### dbt Development
- **[dbt_model.md](dbt_model.md)** - dbt model development best practices
- **[dbt_incremental.md](dbt_incremental.md)** - Incremental model implementation
- **[dbt_testing.md](dbt_testing.md)** - dbt test creation and validation
- **[dbt_macros.md](dbt_macros.md)** - Custom dbt macro development

### Dagster Integration
- **[dagster_asset.md](dagster_asset.md)** - Dagster asset definition and management
- **[dagster_job.md](dagster_job.md)** - Job orchestration and scheduling
- **[dagster_sensors.md](dagster_sensors.md)** - Event-driven pipeline triggers
- **[dagster_resources.md](dagster_resources.md)** - Resource configuration and management

### Data Sources & Integration
- **[api_ingestion.md](api_ingestion.md)** - REST API data extraction patterns
- **[database_ingestion.md](database_ingestion.md)** - Database replication and CDC
- **[file_ingestion.md](file_ingestion.md)** - File-based data processing
- **[airbyte_connector.md](airbyte_connector.md)** - Airbyte connector configuration

### Performance & Optimization
- **[query_optimization.md](query_optimization.md)** - SQL and DuckDB performance tuning
- **[batch_processing.md](batch_processing.md)** - Efficient batch processing patterns
- **[memory_optimization.md](memory_optimization.md)** - Memory-efficient data processing
- **[partitioning_strategy.md](partitioning_strategy.md)** - Data partitioning approaches

## Quick Reference Commands

```bash
# View pipeline design prompt
cat prompts/data/pipeline_design.md

# Search for dbt-related prompts
grep -r "dbt" prompts/data/

# List all data prompts
ls prompts/data/*.md
```

## Usage Patterns

### 1. New Pipeline Development
```
1. pipeline_design.md - Overall architecture
2. dagster_asset.md - Asset implementation
3. dbt_model.md - Transformation logic
4. data_quality_checks.md - Validation rules
```

### 2. Data Quality Implementation
```
1. data_profiling.md - Understand the data
2. schema_validation.md - Define schemas
3. data_quality_checks.md - Implement checks
4. anomaly_detection.md - Monitor for issues
```

### 3. Performance Optimization
```
1. query_optimization.md - Improve query performance
2. batch_processing.md - Optimize processing patterns
3. partitioning_strategy.md - Implement partitioning
4. memory_optimization.md - Reduce memory usage
```

### 4. Integration Setup
```
1. airbyte_connector.md - Configure data sources
2. api_ingestion.md - Extract from APIs
3. database_ingestion.md - Connect databases
4. dagster_sensors.md - Set up triggers
```
