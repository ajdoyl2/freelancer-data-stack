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

- `POSTGRES_PASSWORD`: Password for PostgreSQL database
- `NEO4J_PASSWORD`: Password for Neo4j (used by DataHub)
- `DATAHUB_SECRET`: Secret key for DataHub (minimum 32 characters)
- `AIRFLOW_USERNAME/AIRFLOW_PASSWORD`: Airflow web UI credentials
- `AIRFLOW_FERNET_KEY`: Encryption key for Airflow (auto-generated)
- `JUPYTER_TOKEN`: Optional token for Jupyter access

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
- Data orchestration with Apache Airflow
- Data quality validation and monitoring
- Data cataloging and discovery
- Business intelligence and analytics
- Data application development

## Prerequisites

- Docker and Docker Compose
- At least 8GB RAM recommended
- 20GB+ disk space for volumes

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

## Support

For issues or questions, please create an issue in this repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
