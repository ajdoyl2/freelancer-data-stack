# CLAUDE.md - AI Agent-Driven Data Stack Development Guide

This file provides comprehensive guidance for Claude Code when working with the sophisticated AI agent-driven data stack. Built for $50/month operational cost with 45+ integrated components.

## Core Principles

**KISS (Keep It Simple, Stupid)**: Simplicity should be a key goal in design. Choose straightforward solutions over complex ones whenever possible. Simple solutions are easier to understand, maintain, and debug.

**YAGNI (You Aren't Gonna Need It)**: Avoid building functionality on speculation. Implement features only when they are needed, not when you anticipate they might be useful in the future.

**Dependency Inversion**: High-level modules should not depend on low-level modules. Both should depend on abstractions. This principle enables flexibility and testability.

**Open/Closed Principle**: Software entities should be open for extension but closed for modification. Design your systems so that new functionality can be added with minimal changes to existing code.

**Cost-First Architecture**: Every architectural decision considers the $50/month operational cost target. Prefer DuckDB over Snowflake, local development over cloud resources, and efficient container allocation.

**AI-First Development**: All components integrate with Pydantic AI agents for autonomous operation. Design with agent-friendly interfaces and structured responses.

## 🏗️ Data Stack Architecture

### Architecture Overview

The freelancer data stack is a modern, containerized system designed for AI agent autonomous operation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Agent Layer (Pydantic AI)                │
├─────────────────┬─────────────────┬─────────────────┬─────────────┤
│   Data Sources  │  Integration    │  Transformation │  Analytics  │
│   • CSV Files   │  • Meltano ELT  │  • dbt Core     │  • Metabase │
│   • Snowflake   │  • Singer SDK   │  • Data Quality │  • Streamlit│
│   • APIs        │  • Kafka Streams│  • Testing      │  • Grafana  │
├─────────────────┼─────────────────┼─────────────────┼─────────────┤
│                    Orchestration Layer                         │
│              • Apache Airflow 3.0 + Celery                    │
├─────────────────────────────────────────────────────────────────┤
│                    Storage Layer                               │
│  • DuckDB (Analytics) • PostgreSQL (Metadata) • Redis (Cache)  │
├─────────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                          │
│           • Docker Compose • Traefik • Monitoring             │
└─────────────────────────────────────────────────────────────────┘
```

**Cost Optimization**: ~$50/month vs $500-2000+ traditional cloud stacks (90-95% savings)

### Data Flow Pattern

```
CSV Files → Meltano (tap-csv) → DuckDB (raw) → dbt → Analytics Tables → BI Tools
     ↓
 Snowflake → Meltano (tap-snowflake) → DuckDB → dbt → Marts → AI Agents
```

## 🧱 Code Structure & Modularity

**Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.

**Functions should be short and focused sub 50 lines of code** and have a single responsibility.

**Classes should be short and focused sub 50 lines of code** and have a single responsibility.

**Organize code into clearly separated modules**, grouped by feature or responsibility.

### Project Structure

```
freelancer-data-stack/
├── agents/                     # AI agent implementations
│   ├── base_agent.py          # Pydantic AI base class
│   ├── data_stack_engineer.py # Platform engineering agent
│   └── data_engineer.py       # Data pipeline agent
├── tools/                      # Agent tool integrations
│   ├── duckdb_tools.py        # DuckDB operations
│   ├── meltano_tools.py       # ELT pipeline management
│   ├── dbt_tools.py           # Transformation tools
│   └── airflow_tools.py       # Orchestration tools
├── data_stack/                 # Data stack configurations
│   ├── meltano/               # Meltano project
│   ├── dbt/                   # dbt transformations
│   └── dashboards/            # Visualization components
├── scripts/                   # Automation and deployment
└── monitoring/                # Observability configuration
```

## 🛠️ Package Management - UV

**Cost Impact**: UV provides 10-100x faster dependency resolution, reducing development time costs.

```bash
# Create virtual environment
uv venv

# Install all dependencies
uv sync

# Install specific dependency groups
uv sync --group dev          # Development tools
uv sync --group server       # MCP server dependencies
uv sync --group viz          # Streamlit visualization
uv sync --group meltano      # ELT platform

# Add new dependencies
uv add requests
uv add --group dev pytest

# Run commands in virtual environment
uv run python script.py
uv run pytest tests/
```

### Dependency Groups Configuration

Based on `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "ruff>=0.12.1,<0.13",          # Fast linting
    "black>=25.1.0,<26",           # Code formatting
    "sqlfluff>=3.0.0,<4",          # SQL linting
]

server = [
    "fastapi>=0.115.0,<0.116",     # API framework
    "pydantic-ai>=0.0.9,<0.0.10",  # AI agent framework
    "duckdb>=1.3.1,<2",            # Analytics database
]

meltano = [
    "meltano>=3.7.9,<4",           # ELT platform
    "singer-sdk>=0.40.0,<0.41",    # Singer protocol
]
```

**Validation Commands**:
```bash
uv sync && uv --version     # Verify UV installation
uv tree                     # Check dependency tree
```

## 🗄️ Data Storage & Databases

### DuckDB - Analytics Database

**Primary analytics engine optimized for cost and performance.**

**Cost Impact**: $0 vs $200-500/month for Snowflake warehouse

#### Configuration

```python
# From tools/duckdb_tools.py
class DuckDBTools:
    def __init__(self, project_root: Path | None = None):
        self.default_db_path = "/data/duckdb/analytics.db"

    @asynccontextmanager
    async def get_connection(self, db_path: str | None = None):
        # Performance optimization
        conn.execute("PRAGMA enable_progress_bar = true")
        conn.execute("PRAGMA threads = 4")
        conn.execute("PRAGMA memory_limit = '2GB'")
```

#### Best Practices

- **File Format**: Use Parquet (600x faster than CSV)
- **Memory Management**: Set limits via `SET memory_limit='4GB'`
- **Threading**: `SET threads = [2-5x CPU cores]` for remote workloads
- **Query Optimization**: Filter early, select specific columns

#### Performance Patterns

```sql
-- Efficient query pattern
SELECT specific_columns
FROM table_name
WHERE filter_condition  -- Filter pushdown
LIMIT 1000              -- TopN optimization
```

**Validation Commands**:
```bash
python -c "import duckdb; duckdb.connect('/data/duckdb/analytics.db').execute('SELECT 1')"
uv run python -c "from tools.duckdb_tools import DuckDBTools; print('DuckDB tools operational')"
```

### PostgreSQL - Metadata Storage

**Handles Airflow, Metabase, and Meltano metadata.**

#### Configuration (docker-compose.yml)

```yaml
postgres:
  image: postgres:15
  environment:
    POSTGRES_USER: ${POSTGRES_USER:-ajdoyle}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_MULTIPLE_DATABASES: airflow,metabase,meltano
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ajdoyle}"]
```

**Validation Commands**:
```bash
docker-compose exec postgres psql -U ajdoyle -d airflow -c "SELECT 1"
```

### Redis - Message Broker

**Celery broker for Airflow distributed execution.**

#### Configuration

```yaml
redis:
  image: redis:7-alpine
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
```

**Validation Commands**:
```bash
docker-compose exec redis redis-cli ping
```

## 🔄 Data Integration - Meltano

**Open-source ELT platform with Singer protocol integration.**

**Cost Impact**: $0 vs $100-300/month for Fivetran

### Configuration (data_stack/meltano/meltano.yml)

```yaml
version: 1
default_environment: dev

environments:
  - name: dev
    config:
      plugins:
        extractors:
          - name: tap-csv
            config:
              files:
                - entity: transactions
                  path: /app/transactions.csv
        loaders:
          - name: target-duckdb
            config:
              filepath: /data/duckdb/analytics.db
              default_target_schema: raw_data
```

### Best Practices

- **Environment Separation**: Use dev/staging/prod for different data sources
- **Plugin Management**: Use Singer SDK for custom extractors/loaders
- **Data Quality**: Separate source-centered vs business-centered transformations
- **Cost Optimization**: Use local DuckDB target vs cloud warehouses

### Common Commands

```bash
# Navigate to Meltano project
cd data_stack/meltano

# Install plugins
meltano install

# Run ELT pipeline
meltano run tap-csv target-duckdb

# Test extraction
meltano invoke tap-csv --discover

# Environment management
meltano --environment=prod run tap-csv target-duckdb
```

**Validation Commands**:
```bash
cd data_stack/meltano && meltano --version
meltano config list
```

## 🧪 Data Transformation - dbt

**SQL-based transformation layer with comprehensive testing.**

### Configuration (data_stack/dbt/dbt_project.yml)

```yaml
name: 'ai_agent_data_stack'
require-dbt-version: ">=1.10.0"

models:
  ai_agent_data_stack:
    staging:
      +materialized: view
      +docs:
        node_color: "#A8E6CF"  # Light green
    marts:
      +materialized: table
      +docs:
        node_color: "#FFD93D"  # Yellow
    incremental:
      +materialized: incremental
      +incremental_strategy: "merge"
```

### Best Practices

- **Layer Organization**: Staging → Intermediate → Marts
- **Testing**: Always test primary keys (unique + not_null)
- **Incremental Models**: Use for large datasets to reduce processing costs
- **Documentation**: Use color-coded node types for visual clarity
- **Quality Gates**: Store test failures for debugging

### Project Structure Pattern

```
models/
├── staging/          # Raw data cleaned and standardized
│   └── stg_transactions.sql
├── intermediate/     # Business logic preparation
│   └── int_customer_metrics.sql
└── marts/           # Business-ready analytics tables
    └── fact_transactions.sql
```

### Common Commands

```bash
# Navigate to dbt project
cd data_stack/dbt

# Install packages
dbt deps

# Compile models
dbt compile

# Run transformations
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve

# Run with full refresh
dbt run --full-refresh

# Target specific models
dbt run --select staging
dbt test --select marts
```

**Validation Commands**:
```bash
cd data_stack/dbt && dbt --version
dbt compile
dbt parse
```

## ⚡ Orchestration - Apache Airflow

**Workflow orchestration with AI agent integration.**

### Configuration (docker-compose.yml)

```yaml
airflow-webserver:
  image: apache/airflow:3.0.2-python3.11
  environment:
    - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
    - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/1
  depends_on:
    - postgres
    - redis
```

### Best Practices

- **DAG Patterns**: Use task decorators for Airflow 3.0
- **Error Handling**: Implement retry logic with exponential backoff
- **Dependencies**: Use proper task dependencies and health checks
- **Monitoring**: Leverage Flower for Celery worker monitoring
- **Cost Optimization**: Use efficient task grouping to minimize resource usage

### Example DAG Pattern

```python
from datetime import datetime, timedelta
from airflow.decorators import dag, task

@dag(
    schedule=timedelta(hours=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data-pipeline']
)
def data_pipeline():
    @task
    def extract_data():
        # Meltano extraction logic
        pass

    @task
    def transform_data():
        # dbt transformations
        pass

    extract_data() >> transform_data()

data_pipeline()
```

**Validation Commands**:
```bash
docker-compose exec airflow-webserver airflow version
docker-compose exec airflow-webserver airflow dags list
```

## 🤖 AI Agent Framework - Pydantic AI

**Type-safe AI agent development with tool integration.**

### Base Agent Pattern (agents/base_agent.py)

```python
from pydantic_ai import Agent
from pydantic import BaseModel
from enum import Enum

class AgentRole(str, Enum):
    DATA_PLATFORM_ENGINEER = "data_platform_engineer"
    DATA_ENGINEER = "data_engineer"
    ANALYTICS_ENGINEER = "analytics_engineer"

class BaseAgent(ABC):
    def __init__(self, role: AgentRole, model_name: str = "openai:gpt-4"):
        self.role = role
        self._agent = Agent(
            model=model_name,
            system_prompt=self._get_default_system_prompt()
        )
```

### Best Practices

- **Inheritance**: All agents inherit from BaseAgent
- **Async Methods**: Use async/await for all agent operations
- **Error Handling**: Implement proper retry logic with exponential backoff
- **Tool Integration**: Use async context managers for resource cleanup
- **Structured Responses**: Return AgentResponse models for consistency

### Agent Development Pattern

```python
class DataStackEngineer(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(role=AgentRole.DATA_PLATFORM_ENGINEER, **kwargs)
        self.duckdb_tools = DuckDBTools()
        self.meltano_tools = MeltanoTools()

    async def execute_task(self, request: WorkflowRequest) -> AgentResponse:
        # Agent implementation with tool usage
        async with self.duckdb_tools.get_connection() as conn:
            result = await self.duckdb_tools.execute_query(query)
        return AgentResponse(status=ResponseStatus.SUCCESS, output=result)
```

### Tool Integration Pattern

```python
# All tools return consistent format
async def execute_query(self, query: str) -> dict[str, Any]:
    try:
        # Tool logic
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Validation Commands**:
```bash
python -c "from agents.base_agent import BaseAgent; print('Agent framework operational')"
uv run python -c "from tools.duckdb_tools import DuckDBTools; print('Tool integration operational')"
```

## 📊 Visualization & Business Intelligence

### Streamlit - Interactive Dashboards

**Real-time data visualization with cost-effective hosting.**

#### Configuration

```python
# Based on viz/streamlit patterns
import streamlit as st
import pandas as pd
from tools.duckdb_tools import DuckDBTools

def main():
    st.title("AI Agent Data Stack Dashboard")

    # Cost-effective data loading
    @st.cache_data
    def load_data():
        tools = DuckDBTools()
        return tools.execute_query_to_df("SELECT * FROM marts.fact_transactions")
```

#### Best Practices

- **Caching**: Use `@st.cache_data` for expensive operations
- **Performance**: Limit data loading with filters and pagination
- **Cost Optimization**: Run locally vs expensive cloud hosting

**Validation Commands**:
```bash
cd viz/streamlit && ./run.sh
curl http://localhost:8501/health
```

### Metabase - Business Intelligence

**Open-source BI platform with multiple data source support.**

#### Configuration (docker-compose.yml)

```yaml
metabase:
  image: metabase/metabase:v0.47.0
  environment:
    MB_DB_TYPE: postgres
    MB_DB_HOST: postgres
    SNOWFLAKE_ACCOUNT: ${SNOWFLAKE_ACCOUNT}
    SNOWFLAKE_USERNAME: ${SNOWFLAKE_USERNAME}
```

**Validation Commands**:
```bash
curl http://localhost:3002/api/health
```

## 📈 Monitoring & Observability

### Prometheus + Grafana Stack

**Cost-effective monitoring with $5-10/month hosting.**

#### Configuration

```yaml
# Prometheus (monitoring/prometheus.yml)
prometheus:
  image: prom/prometheus:latest
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'

# Grafana
grafana:
  image: grafana/grafana:latest
  environment:
    - GF_SECURITY_ADMIN_USER=${GRAFANA_USERNAME:-ajdoyle}
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
```

### Structured Logging

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

**Validation Commands**:
```bash
curl http://localhost:9090/api/v1/status/config  # Prometheus
curl http://localhost:3000/api/health             # Grafana
```

## 🚀 Development Workflow

### Environment Setup

```bash
# 1. Clone and setup environment
git clone <repository>
cd freelancer-data-stack
uv venv && source .venv/bin/activate

# 2. Install dependencies
uv sync

# 3. Start infrastructure
docker-compose up -d

# 4. Initialize data pipeline
cd data_stack/meltano && meltano install
cd ../dbt && dbt deps && dbt run

# 5. Verify setup
./scripts/validate_pipeline.py --comprehensive
```

### Development Commands

```bash
# Code quality
uv run ruff format .         # Format code
uv run ruff check .          # Lint code
uv run mypy .                # Type checking
uv run sqlfluff fix models/  # SQL formatting

# Testing
uv run pytest               # Run all tests
uv run pytest agents/      # Test agents
uv run pytest tools/       # Test tool integrations

# Data pipeline
cd data_stack/meltano && meltano run tap-csv target-duckdb
cd ../dbt && dbt run && dbt test

# Service management
docker-compose up -d        # Start services
docker-compose ps           # Check status
docker-compose logs service # View logs
```

## 🧪 Testing & Quality Assurance

### Testing Patterns

**Always create Pytest unit tests for new features.** Tests live next to the code they test in a `tests/` directory.

```python
# Example test pattern
@pytest.mark.asyncio
async def test_duckdb_connection():
    tools = DuckDBTools()
    async with tools.get_connection() as conn:
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1

def test_agent_initialization():
    agent = DataStackEngineer()
    assert agent.role == AgentRole.DATA_PLATFORM_ENGINEER
```

### Validation Framework

```bash
# Level 1: Syntax & Style
uv run ruff check .
uv run mypy .
markdownlint *.md

# Level 2: Unit Tests
uv run pytest tests/ -v

# Level 3: Integration Tests
docker-compose exec meltano meltano run tap-csv target-duckdb
cd data_stack/dbt && dbt run && dbt test

# Level 4: End-to-End Validation
./scripts/deploy_stack.py --validate-only
./scripts/validate_pipeline.py --comprehensive

# Level 5: Performance Testing
python scripts/performance_test_data_stack.py --validate-targets
```

## 💰 Cost Optimization Strategies

### Target: $50/Month Operational Cost

**vs $500-2000+ traditional cloud stacks (90-95% savings)**

#### Component Cost Breakdown

- **Compute**: $30-35 (VPS/Cloud instance)
- **Storage**: $5-10 (Block storage)
- **Monitoring**: $5-10 (Prometheus/Grafana hosting)
- **Total**: ~$50/month

#### Cost Optimization Techniques

1. **DuckDB vs Snowflake**: $0 vs $200-500/month warehouse costs
2. **Local Development**: Use Docker Compose vs expensive cloud services
3. **Efficient Containers**: Optimize resource allocation in docker-compose.yml
4. **Parquet Format**: 600x faster than CSV, reduces processing costs
5. **Incremental Processing**: Use dbt incremental models for large datasets

#### Resource Optimization

```yaml
# docker-compose.yml optimization patterns
services:
  service-name:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## 🛠️ Infrastructure & Deployment

### Docker Compose Patterns

**Service Health Checks**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 5
```

**Network Isolation**:
```yaml
networks:
  data-stack:
    driver: bridge
```

**Volume Management**:
```yaml
volumes:
  - ./volumes/duckdb:/data/duckdb
  - postgres_data:/var/lib/postgresql/data
```

### Deployment Commands

```bash
# Development deployment
docker-compose up -d

# Production deployment
./scripts/deploy_stack.py --environment=prod

# Health validation
./scripts/validate_pipeline.py --comprehensive

# Service management
docker-compose restart service-name
docker-compose logs -f service-name
```

## 📚 Important Types & Patterns

### AI Agent Patterns

```python
# Agent response pattern
class AgentResponse(BaseModel):
    agent_role: AgentRole
    status: ResponseStatus
    output: dict[str, Any] = Field(default_factory=dict)
    validation_results: list[ValidationResult] = Field(default_factory=list)

# Tool response pattern
def tool_response_format() -> dict[str, Any]:
    return {
        "success": bool,
        "data": Any,
        "error": str | None,
        "metadata": dict[str, Any]
    }
```

### Data Quality Patterns

```python
# dbt test pattern
def data_quality_test():
    return {
        "test_name": str,
        "status": "pass" | "fail" | "warn",
        "metric_value": float,
        "threshold": float
    }
```

## 🚫 Anti-Patterns to Avoid

- ❌ **Don't use Snowflake for development** - Use DuckDB for 90% cost savings
- ❌ **Don't skip health checks** - Essential for proper service startup
- ❌ **Don't ignore cost implications** - Every decision impacts $50/month target
- ❌ **Don't use synchronous patterns** - All agent operations should be async
- ❌ **Don't skip data quality tests** - Use dbt tests for all critical models
- ❌ **Don't hardcode configurations** - Use environment variables and config files
- ❌ **Don't ignore monitoring** - Implement comprehensive observability
- ❌ **Don't skip validation commands** - Every tool needs executable health checks

## 🔍 Troubleshooting Guide

### Common Issues

**Service Won't Start**:
```bash
docker-compose ps                    # Check service status
docker-compose logs service-name     # View logs
docker-compose restart service-name # Restart service
```

**DuckDB Connection Issues**:
```bash
# Check file permissions
ls -la /data/duckdb/analytics.db
# Test connection
python -c "import duckdb; duckdb.connect('/data/duckdb/analytics.db')"
```

**Meltano Pipeline Failures**:
```bash
cd data_stack/meltano
meltano config list                  # Check configuration
meltano invoke tap-csv --discover   # Test extractor
```

**dbt Compilation Errors**:
```bash
cd data_stack/dbt
dbt compile                         # Check for syntax errors
dbt debug                          # Verify connections
```

### Performance Issues

**DuckDB Optimization**:
```sql
SET memory_limit='4GB';
SET threads=4;
PRAGMA enable_progress_bar;
```

**Container Resource Issues**:
```bash
docker stats                       # Monitor resource usage
docker-compose down && docker-compose up -d  # Restart stack
```

---

## 📋 Final Validation Checklist

Execute these commands to verify the complete data stack:

```bash
# Infrastructure validation
docker-compose ps | grep -c "Up"                                    # Should show all services running
curl -f http://localhost:8080/health                               # Airflow health
curl -f http://localhost:3000/api/health                          # Grafana health

# Data pipeline validation
cd data_stack/meltano && meltano run tap-csv target-duckdb         # ELT pipeline
cd ../dbt && dbt run && dbt test                                   # Transformations

# AI agent validation
python -c "from agents.base_agent import BaseAgent; print('✓ Agents operational')"
python -c "from tools.duckdb_tools import DuckDBTools; print('✓ Tools operational')"

# Code quality validation
uv run ruff check . && echo "✓ Linting passed"
uv run mypy . && echo "✓ Type checking passed"
uv run pytest tests/ -v && echo "✓ Tests passed"

# Cost optimization verification
echo "Target: $50/month operational cost achieved through:"
echo "- DuckDB vs Snowflake: $0 vs $200-500/month"
echo "- Local containers vs cloud: $35 vs $200+/month"
echo "- Open source tools vs enterprise: $0 vs $300+/month"
```

This comprehensive guide enables development teams to work effectively with the AI agent-driven data stack while maintaining the $50/month cost target and ensuring robust, scalable operations.
