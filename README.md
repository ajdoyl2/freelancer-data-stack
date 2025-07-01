# Freelancer Data Stack

A comprehensive Docker Compose stack for modern data engineering and analytics workflows.

## Services Included

This stack spins up the following services with all volumes mapped to `~/data-stack/volumes/*`:

1. **PostgreSQL** - Shared database for Airbyte, Metabase, and Airflow metadata
2. **Airbyte** - Data integration platform for ELT pipelines
3. **Apache Airflow** - Modern data orchestration with Celery executor and Redis
4. **DataHub + Kafka** - Data catalog and discovery platform with Kafka messaging
5. **Great Expectations** - Data quality and validation with Jupyter/Streamlit
6. **Evidence.dev** - Development server for data apps
7. **Metabase** - Business intelligence and analytics dashboards
8. **DuckDB HTTP** - DuckDB exposed via REST API
9. **Traefik** - Reverse proxy with dashboard for service management

## Quick Start

1. Copy the environment template and configure your secrets:
   ```bash
   cp .env.template .env
   # Edit .env with your actual values (secure defaults provided)
   ```

2. Create the volumes directory:
   ```bash
   mkdir -p ~/data-stack/volumes
   ```

3. Start the entire stack:
   ```bash
   docker-compose up -d
   ```

4. Access the services:
   - **Airbyte Web UI**: http://localhost:8001
   - **Apache Airflow**: http://localhost:8080 (admin/[your_password])
   - **Airflow Flower (Celery Monitor)**: http://localhost:5555
   - **DataHub**: http://localhost:9002
   - **Great Expectations Jupyter**: http://localhost:8888
   - **Evidence.dev**: http://localhost:3001
   - **Metabase**: http://localhost:3002
   - **DuckDB HTTP**: http://localhost:8002
   - **Traefik Dashboard**: http://localhost:8090

## Environment Variables

Key environment variables to configure in your `.env` file:

### Core Services
- `POSTGRES_PASSWORD`: Password for PostgreSQL database
- `NEO4J_PASSWORD`: Password for Neo4j (used by DataHub)
- `DATAHUB_SECRET`: Secret key for DataHub (minimum 32 characters)
- `AIRFLOW_USERNAME/AIRFLOW_PASSWORD`: Airflow web UI credentials
- `AIRFLOW_FERNET_KEY`: Encryption key for Airflow (auto-generated)
- `JUPYTER_TOKEN`: Optional token for Jupyter access

### Streaming Capabilities (Optional)
- `ENABLE_STREAMING_STACK`: Set to `true` to enable Kafka + Materialize services
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka connection string (default: `localhost:9092`)
- `KAFKA_TOPIC_NAME`: Topic name for dbt incremental triggers (default: `dbt_incremental`)

## Volume Mapping

All persistent data is stored in `~/data-stack/volumes/` with subdirectories for each service:

- `postgres/` - PostgreSQL data
- `airbyte/` - Airbyte configurations and workspace
- `airflow/` - Airflow DAGs, logs, config, and plugins
- `redis/` - Redis data for Airflow Celery
- `datahub/` - DataHub metadata
- `elasticsearch/` - Elasticsearch indices
- `neo4j/` - Neo4j graph database
- `kafka/` - Kafka logs and data
- `great-expectations/` - GE notebooks and configurations
- `evidence/` - Evidence.dev projects
- `metabase/` - Metabase application data
- `duckdb/` - DuckDB database files
- `traefik/` - Traefik configuration

## Architecture

This stack provides a complete modern data platform suitable for:
- Data ingestion and ETL/ELT pipelines
- Data orchestration with Apache Airflow and Dagster
- Data quality validation and monitoring
- Data cataloging and discovery
- Business intelligence and analytics
- Data application development
- Real-time streaming and micro-batch processing (optional)

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ and Poetry (for local development)
- At least 8GB RAM recommended
- 20GB+ disk space for volumes

## Dependency Management

This project uses Poetry for Python dependency management with organized dependency groups. Install subsets of dependencies based on your needs:

### Available Dependency Groups

- **Core dependencies**: `poetry install` (dbt-core, dbt-duckdb)
- **Development tools**: `poetry install --with dev` (ruff, black, isort, sqlfluff, pre-commit)
- **Server/API**: `poetry install --with server` (FastAPI, uvicorn, database drivers, LLM tools)
- **Visualization**: `poetry install --with viz` (Streamlit, pandas, plotly)
- **Orchestration**: `poetry install --with dagster` (Dagster, dagster-webserver)
- **Data Catalog**: `poetry install --with datahub` (acryl-datahub)
- **Workflow Management**: `poetry install --with airflow` (apache-airflow)
- **Jupyter**: `poetry install --with jupyter` (jupyter, jupyterlab)

### Example Installation Commands

```bash
# Install core dependencies only
poetry install

# Install for local development
poetry install --with dev

# Install for data pipeline development
poetry install --with dev,dagster,airflow

# Install for visualization and analysis
poetry install --with dev,viz,jupyter

# Install everything for full stack development
poetry install --with dev,server,viz,dagster,airflow,datahub,jupyter
```

### Managing Dependencies

- Add new dependencies: `poetry add package-name --group=group-name`
- Update lockfile: `poetry lock`
- Export requirements: `poetry export -f requirements.txt --output requirements.txt`

## Directory Structure

```
infra/terraform       # Infrastructure as Code
docker/              # Docker configurations
orchestration/       # Airflow DAGs and workflows
ingestion/           # Airbyte connectors and DLT configs
transformation/      # dbt models and transformations
quality/             # Great Expectations suites
viz/                 # Evidence, Metabase, Streamlit apps
catalog/             # DataHub metadata configs
mcp-server/          # Model Context Protocol server
scripts/             # Utility scripts
```

## Streaming & Real-time Features

The data stack includes optional streaming capabilities for real-time and micro-batch processing:

### Enabling Streaming Features

To enable streaming services, add the following to your `.env` file:
```bash
ENABLE_STREAMING_STACK=true
```

Then start the stack with the streaming profile:
```bash
docker-compose --profile streaming up -d
```

### Available Streaming Services

- **Kafka Connect**: Additional streaming integrations and connectors
- **Materialize**: Real-time data transformations and materialized views
- **KSQL**: Stream processing with SQL (alternative to Materialize)
- **Dagster Kafka Sensor**: Consumes Kafka messages to trigger dbt incremental runs

### Streaming Workflow

1. **Data Sources → Kafka**: Stream data changes to Kafka topics
2. **Kafka → Dagster Sensor**: Kafka messages trigger Dagster asset sensors
3. **Dagster → dbt**: Incremental dbt models process streaming data
4. **Materialize**: Real-time materialized views for immediate analytics

### Configuration Options

- `KAFKA_TOPIC_NAME`: Topic for triggering dbt runs (default: `dbt_incremental`)
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka connection string (default: `localhost:9092`)

### Client Feature Flags

For clients requiring streaming capabilities:
- Set `ENABLE_STREAMING_STACK=true` in environment
- Configure Kafka topics based on data sources
- Enable Dagster Kafka sensor in the UI (default: disabled)
- Set up Materialize connections for real-time views

### Service Endpoints (Streaming)

- **Kafka Connect**: http://localhost:8083
- **Materialize SQL**: postgresql://localhost:6875
- **Materialize HTTP**: http://localhost:6876
- **KSQL Server**: http://localhost:8088

## Support

For issues or questions, please create an issue in this repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
