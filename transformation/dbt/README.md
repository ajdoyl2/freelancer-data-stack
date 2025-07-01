# Freelancer Analytics dbt Project

This dbt project demonstrates a complete data transformation pipeline with multi-environment support, data quality testing, and automatic DataHub integration.

## 🏗️ Architecture

### Environments

#### 1. DuckDB Local (`duckdb_local`)
- **Purpose**: Local development and testing
- **Database**: Local DuckDB file (`freelancer_analytics.duckdb`)
- **Use Case**: Fast iteration, development, and CI/CD testing

#### 2. Snowflake Production (`snowflake_prod`)
- **Purpose**: Production data warehouse
- **Database**: Snowflake cloud instance
- **Authentication**: Environment variables
- **Use Case**: Production workloads and reporting

## 📁 Project Structure

```
transformation/dbt/
├── dbt_project.yml          # Main project configuration
├── packages.yml             # dbt packages (expectations, artifacts, utils)
├── profiles.yml             # Connection profiles (in ~/.dbt/)
├── datahub_dbt_config.yml   # DataHub integration config
├── run_dbt_with_datahub.sh  # Automated run script
├── models/
│   ├── staging/             # Raw data transformations
│   │   ├── stg_freelancers.sql
│   │   ├── stg_projects.sql
│   │   └── schema.yml       # Tests and documentation
│   ├── marts/               # Business logic models
│   │   └── freelancer_project_summary.sql
│   └── incremental/         # Incremental models
│       └── daily_project_metrics.sql
├── seeds/                   # Example datasets
│   ├── freelancers.csv
│   └── projects.csv
├── macros/                  # Custom macros
│   └── datahub_registration.sql
└── tests/                   # Custom tests
```

## 🚀 Quick Start

### Prerequisites

1. **dbt installed** with DuckDB adapter:
   ```bash
   pip install dbt-duckdb
   ```

2. **For Snowflake** (optional):
   ```bash
   pip install dbt-snowflake
   ```

3. **For DataHub integration** (optional):
   ```bash
   pip install acryl-datahub
   ```

### Running the Project

#### Option 1: Use the automated script
```bash
# Run with DuckDB (default)
./run_dbt_with_datahub.sh

# Run with Snowflake (requires setup)
./run_dbt_with_datahub.sh snowflake_prod
```

#### Option 2: Manual dbt commands
```bash
# Install dependencies
dbt deps

# Seed example data
dbt seed

# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate && dbt docs serve
```

## 🔧 Configuration Details

### Environment Variables

#### For Snowflake Target
```bash
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_ROLE="ANALYST"
export SNOWFLAKE_DATABASE="FREELANCER_ANALYTICS"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
export SNOWFLAKE_SCHEMA="ANALYTICS"
```

#### For DataHub Integration
```bash
export DATAHUB_REST_URL="http://localhost:8080"
export DATAHUB_TOKEN="your-datahub-token"
```

### Profiles Configuration

The `profiles.yml` file (located in `~/.dbt/`) contains two targets:

- **`duckdb_local`**: Local DuckDB database for development
- **`snowflake_prod`**: Snowflake connection for production

## 📊 Data Models

### Staging Models
- **`stg_freelancers`**: Cleaned freelancer data with type casting
- **`stg_projects`**: Cleaned project data with type casting

### Marts Models
- **`freelancer_project_summary`**: Aggregated freelancer performance metrics

### Incremental Models
- **`daily_project_metrics`**: Daily aggregated project metrics with environment detection

## 🧪 Data Quality Testing

### dbt_expectations Tests
- Email format validation (regex)
- Numeric range validation (hourly rates, ratings, project values)
- Referential integrity checks
- Unique and not-null constraints

### Test Examples
```yaml
- name: email
  tests:
    - dbt_expectations.expect_column_values_to_match_regex:
        regex: '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
- name: hourly_rate
  tests:
    - dbt_expectations.expect_column_values_to_be_between:
        min_value: 0
        max_value: 1000
```

## 🔗 DataHub Integration

### Automatic Registration
- **When**: After every dbt run (via `on-run-end` hook)
- **What**: dbt manifest and catalog files
- **Configuration**: `datahub_dbt_config.yml`

### Manual DataHub Ingestion
```bash
# Generate manifest and catalog
dbt docs generate

# Ingest to DataHub
datahub ingest -c datahub_dbt_config.yml
```

## 📦 dbt Packages

### Included Packages
1. **`metaplane/dbt_expectations`**: Data quality testing framework
2. **`brooklyn-data/dbt_artifacts`**: dbt run metadata collection (Snowflake only)
3. **`dbt-labs/dbt_utils`**: Utility macros and functions

### Package Features Used
- Date spine generation for incremental models
- Advanced data quality expectations
- Metadata collection and lineage tracking

## 🔄 Environment Switching

### Development vs Production
The incremental model `daily_project_metrics` demonstrates environment-aware logic:

```sql
{% if target.name == 'duckdb_local' %}
'duckdb_local' as environment,
{% else %}
'snowflake_prod' as environment,
{% endif %}
```

### Variable Configuration
Environment-specific variables can be set in `dbt_project.yml`:
```yaml
vars:
  start_date: '2023-01-01'
  end_date: '2024-12-31'
```

## 🚦 CI/CD Integration

### Example GitHub Actions
```yaml
- name: Run dbt
  run: |
    dbt deps
    dbt seed --target duckdb_local
    dbt run --target duckdb_local
    dbt test --target duckdb_local
```

## 📈 Monitoring and Observability

### dbt Artifacts (Snowflake)
- Model execution times
- Test results history
- Data freshness tracking

### DataHub Lineage
- Automatic data lineage from dbt models
- Column-level lineage tracking
- Impact analysis for changes

## 🔧 Troubleshooting

### Common Issues

1. **DuckDB compatibility**: Some dbt packages (like dbt_artifacts) may not be fully compatible with DuckDB
   - **Solution**: Use `--exclude package:dbt_artifacts` when running with DuckDB

2. **Snowflake adapter not found**:
   - **Solution**: Install with `pip install dbt-snowflake`

3. **DataHub connection issues**:
   - **Solution**: Verify DATAHUB_REST_URL and DATAHUB_TOKEN environment variables

### Performance Tips

1. **Incremental models**: Use proper unique keys and filters
2. **DuckDB**: Excellent for development, consider Snowflake for large datasets
3. **Tests**: Run tests regularly to catch data quality issues early

## 📚 Additional Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Expectations Package](https://github.com/metaplane/dbt-expectations)
- [DataHub dbt Integration](https://datahubproject.io/docs/generated/ingestion/sources/dbt/)
- [DuckDB Adapter](https://github.com/duckdb/dbt-duckdb)
