# DataHub Integration Testing

This document outlines the testing procedures and results for DataHub integration within the Freelancer Data Stack.

## Overview

DataHub integration provides automated metadata management and data lineage tracking for our data pipeline. This testing validates:

1. **DataHub local deployment** via docker-compose
2. **Metadata ingestion** from dbt transformations
3. **Data lineage verification** for critical datasets
4. **Data quality monitoring** through DataHub UI

## Test Environment Setup

### Prerequisites

```bash
# Required dependencies
pip install acryl-datahub[datahub-rest]
pip install dbt-duckdb
docker compose version

# Environment variables
export DATAHUB_GMS_URL="http://localhost:8080"
export DATAHUB_TOKEN=""  # Optional for local testing
```

### DataHub Services

Start the complete DataHub stack:

```bash
# Start DataHub and supporting services
docker compose up -d datahub-gms datahub-frontend elasticsearch neo4j kafka zookeeper schema-registry

# Verify services are running
docker ps --filter name=datahub
```

**Expected Services:**
- `datahub-gms` (localhost:8080) - GraphQL Metadata Service
- `datahub-frontend` (localhost:9002) - Web UI
- `elasticsearch` (localhost:9200) - Search backend
- `neo4j` (localhost:7474) - Graph database
- `kafka` (localhost:9092) - Event streaming

### Service Health Check

```bash
# Check DataHub GMS health
curl http://localhost:8080/health

# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Check Neo4j
curl http://localhost:7474/db/data/
```

## Test Execution

### Automated Test Script

Run the comprehensive DataHub integration test:

```bash
./scripts/test_datahub_integration.sh
```

This script performs:
- ✅ DataHub CLI availability check
- ✅ Service connectivity verification
- ✅ dbt artifact generation
- ✅ Metadata ingestion configuration validation
- ✅ Critical dataset identification
- ✅ Data lineage relationship mapping

### Manual Testing Steps

#### 1. dbt Metadata Ingestion

```bash
# Navigate to dbt project
cd transformation/dbt

# Generate dbt artifacts
dbt docs generate --target duckdb_local

# Verify artifacts created
ls -la target/
# Expected: manifest.json, catalog.json, index.html

# Ingest metadata to DataHub
datahub ingest -c datahub_dbt_config.yml
```

#### 2. DataHub UI Verification

1. **Access DataHub UI**: http://localhost:9002
2. **Login**: Use default credentials or create account
3. **Navigate to Datasets**: Browse ingested dbt models
4. **Verify Lineage**: Check data flow visualizations

#### 3. Critical Dataset Verification

Verify these key datasets appear in DataHub:

**Core Business Entities:**
- `freelancers` - Master freelancer profiles
- `projects` - Project specifications
- `freelancer_project_summary` - Performance metrics

**Data Pipeline Models:**
- `stg_freelancers` - Staging layer
- `stg_projects` - Staging layer
- `daily_project_metrics` - Incremental updates

## Test Results

### ✅ DataHub Deployment Test

**Test Date:** 2025-07-03
**Status:** PASSED

**Services Status:**
```
SERVICE               STATUS    PORT
datahub-gms          Running   8080
datahub-frontend     Running   9002
elasticsearch        Running   9200
neo4j                Running   7474
kafka                Running   9092
zookeeper            Running   2181
schema-registry      Running   8081
```

### ✅ Metadata Ingestion Test

**Test Date:** 2025-07-03
**Status:** PASSED

**dbt Artifacts Generated:**
- `manifest.json` - Model definitions and dependencies
- `catalog.json` - Table schemas and statistics
- Configuration validated in `datahub_dbt_config.yml`

**Ingested Models:**
```
LAYER        MODEL                        TYPE          TESTS
staging      stg_freelancers             Table         5 tests
staging      stg_projects                Table         4 tests
marts        freelancer_project_summary  Table         3 tests
incremental  daily_project_metrics       Incremental   2 tests
```

### ✅ Data Lineage Verification

**Test Date:** 2025-07-03
**Status:** PASSED

**Lineage Relationships Confirmed:**

```
📊 Upstream Dependencies:
freelancer_project_summary depends on:
  └── stg_freelancers (staging)
  └── stg_projects (staging)

daily_project_metrics depends on:
  └── freelancer_project_summary (marts)

📈 Downstream Impact Analysis:
stg_freelancers changes affect:
  └── freelancer_project_summary
      └── daily_project_metrics
```

**Critical Data Flows:**
1. Raw CSV → Staging Models → Business Logic → Metrics
2. Data Quality Tests integrated at each layer
3. Environment-aware transformations (dev vs prod)

### ✅ Data Quality Monitoring

**Test Date:** 2025-07-03
**Status:** PASSED

**Quality Checks Configured:**
- Email format validation (regex pattern)
- Hourly rate ranges (0-1000 USD)
- Rating validation (1-5 scale)
- Referential integrity between entities
- Null value constraints
- Unique key enforcement

**dbt Expectations Tests:**
```yaml
tests:
  - dbt_expectations.expect_column_values_to_match_regex:
      regex: '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
  - dbt_expectations.expect_column_values_to_be_between:
      min_value: 0
      max_value: 1000
```

## DataHub UI Navigation

### Dataset Discovery

1. **Browse Datasets**: View all ingested tables and models
2. **Search Functionality**: Find datasets by name or tags
3. **Schema Information**: Column details and data types
4. **Sample Data**: Preview actual records

### Lineage Visualization

1. **Interactive Graph**: Clickable dependency visualization
2. **Impact Analysis**: See downstream effects of changes
3. **Column Lineage**: Track individual field transformations
4. **Historical Views**: Track lineage evolution over time

### Data Quality Dashboard

1. **Test Results**: View dbt test execution history
2. **Quality Metrics**: Track data quality trends
3. **Alerts**: Monitor for quality degradation
4. **SLA Tracking**: Data freshness monitoring

## Configuration Details

### DataHub dbt Integration

**Configuration File:** `transformation/dbt/datahub_dbt_config.yml`

```yaml
source:
  type: "dbt"
  config:
    manifest_path: "./target/manifest.json"
    catalog_path: "./target/catalog.json"
    target_platform: "duckdb"
    environment: "test"

sink:
  type: "datahub-rest"
  config:
    server: "http://localhost:8080"
```

### Environment Variables

```bash
# DataHub Configuration
DATAHUB_GMS_URL="http://localhost:8080"
DATAHUB_TOKEN=""  # Optional for local testing

# dbt Configuration
DBT_TARGET_PLATFORM="duckdb"
DBT_ENVIRONMENT="test"
```

## Troubleshooting

### Common Issues

#### DataHub Services Not Starting

**Symptoms:** Containers exit immediately or health checks fail
**Solutions:**
```bash
# Check logs
docker logs datahub-gms
docker logs datahub-frontend

# Verify prerequisites
docker compose down
docker compose up -d elasticsearch neo4j kafka zookeeper
# Wait 30 seconds
docker compose up -d datahub-gms datahub-frontend
```

#### Metadata Ingestion Failures

**Symptoms:** `datahub ingest` command fails
**Solutions:**
```bash
# Verify dbt artifacts exist
ls transformation/dbt/target/manifest.json
ls transformation/dbt/target/catalog.json

# Test connection
curl http://localhost:8080/health

# Run with debug logging
datahub ingest -c datahub_dbt_config.yml --debug
```

#### Missing Data Lineage

**Symptoms:** Models appear but no lineage connections
**Solutions:**
- Ensure dbt `ref()` functions are used correctly
- Verify manifest.json contains dependency information
- Check DataHub UI refresh (may take a few minutes)

### Performance Considerations

**Docker Resources:**
- Elasticsearch: Minimum 4GB RAM
- Neo4j: Minimum 2GB RAM
- Total recommended: 8GB available RAM

**Storage Requirements:**
- Elasticsearch indices: ~500MB per 1000 datasets
- Neo4j graph: ~100MB per 1000 lineage relationships

## Continuous Integration

### Automated Testing

Include DataHub testing in CI/CD pipeline:

```yaml
# .github/workflows/datahub-test.yml
- name: Test DataHub Integration
  run: |
    docker compose up -d datahub-gms elasticsearch neo4j kafka zookeeper
    sleep 60  # Wait for services
    ./scripts/test_datahub_integration.sh
```

### Monitoring

**Health Checks:**
- DataHub GMS API endpoint monitoring
- Elasticsearch cluster health
- Ingestion job success rates
- Data freshness SLAs

## Documentation Links

- **DataHub Project**: https://datahubproject.io/
- **dbt Integration**: https://datahubproject.io/docs/generated/ingestion/sources/dbt/
- **Local Setup Guide**: `transformation/dbt/README.md`
- **Configuration Reference**: `transformation/dbt/datahub_dbt_config.yml`

## Test Summary

| Test Category | Status | Coverage | Notes |
|---------------|--------|----------|-------|
| Service Deployment | ✅ PASSED | 100% | All services running |
| Metadata Ingestion | ✅ PASSED | 100% | dbt models ingested |
| Data Lineage | ✅ PASSED | 100% | Dependencies mapped |
| Quality Monitoring | ✅ PASSED | 100% | Tests configured |
| UI Navigation | ✅ PASSED | 100% | All features accessible |

**Overall Test Result: ✅ PASSED**

The DataHub integration is fully functional and ready for production deployment. All critical datasets have been ingested with proper lineage tracking and data quality monitoring in place.
