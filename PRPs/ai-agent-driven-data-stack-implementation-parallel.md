# AI Agent-Driven Data Stack Implementation PRP

## Goal
Implement a comprehensive AI agent-driven modern data stack that can autonomously perform data engineering, analytics, and visualization tasks using Claude AI agents, Docker Compose orchestration, and open-source tools. The system should process the transactions.csv demonstration file and scale to handle diverse data sources while maintaining cost efficiency under $50/month.

## Why
- **Business Value**: Enables autonomous data operations through AI agents, reducing manual data engineering overhead by 80-90%
- **Cost Efficiency**: Open-source stack saves $150-200/month compared to proprietary solutions (Snowflake + commercial tools)
- **Scalability**: Architecture supports growth from small test datasets to enterprise-scale data processing
- **Integration**: Leverages existing agent framework, tools, and infrastructure patterns already established in the codebase
- **AI-First Design**: Claude agents can autonomously coordinate, validate, and optimize the entire data pipeline

## What
A complete data stack implementation that:
- Processes transactions.csv and other data sources through Meltano ELT pipelines
- Performs transformations using dbt with automated data quality testing
- Orchestrates workflows through Apache Airflow with AI agent control
- Stores data in DuckDB for cost-effective analytics
- Generates dashboards via Streamlit and Evidence.dev
- Monitors system health through Prometheus and Grafana
- Enables Claude AI agents to autonomously manage all operations

### Success Criteria
- [ ] Complete data pipeline from transactions.csv to dashboard in under 5 minutes
- [ ] AI agents can autonomously deploy, monitor, and troubleshoot the stack
- [ ] System passes comprehensive data quality tests with >95% success rate
- [ ] Monthly operational cost remains under $50
- [ ] Stack handles 10x data volume increase without architecture changes
- [ ] All components integrate seamlessly with existing agent framework

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://airflow.apache.org/docs/apache-airflow/stable/
  why: Core orchestration patterns, DAG creation, and AI agent integration via MCP

- url: https://docs.getdbt.com/docs/core/about-dbt-core
  why: Transformation patterns, testing framework, and dbt-expectations integration

- url: https://docs.meltano.com/getting-started
  why: ELT pipeline configuration, Singer connectors, and CLI patterns

- url: https://duckdb.org/docs/
  why: Embedded analytics database, performance optimization, and Python integration

- url: https://docs.anthropic.com/en/api/model-context-protocol
  why: MCP integration for AI agent tool access and coordination

- file: /Users/ajdoyle/data-stack/freelancer-data-stack/agents/base_agent.py
  why: Core agent framework patterns, async execution, and response structures

- file: /Users/ajdoyle/data-stack/freelancer-data-stack/tools/dbt_tools.py
  why: Existing dbt integration patterns and async command execution

- file: /Users/ajdoyle/data-stack/freelancer-data-stack/tools/docker_tools.py
  why: Container management patterns and health monitoring

- file: /Users/ajdoyle/data-stack/freelancer-data-stack/docker-compose.yml
  why: Service orchestration patterns and dependency management

- docfile: /Users/ajdoyle/data-stack/freelancer-data-stack/data-stack-plans/ai-agent-driven-data-stack-architecture-plan.md
  why: Complete architecture blueprint with cost analysis and implementation roadmap

- docfile: /Users/ajdoyle/data-stack/freelancer-data-stack/PRPs/modernized-data-stack-with-ai-agents.md
  why: Existing PRP with validation patterns and agent-first architecture
```

### Current Codebase Tree
```bash
/Users/ajdoyle/data-stack/freelancer-data-stack/
├── agents/
│   ├── base_agent.py           # Core agent framework
│   ├── data_engineer.py        # Data engineering agent
│   ├── data_analyst.py         # Analytics agent
│   └── orchestrator.py         # Multi-agent coordination
├── tools/
│   ├── dbt_tools.py           # dbt integration
│   ├── airflow_tools.py       # Airflow integration
│   └── docker_tools.py        # Container management
├── config/
│   ├── agent_configs.py       # Agent configuration
│   └── tool_configs.py        # Tool permissions
├── interface/
│   └── workflow_executor.py   # Natural language processing
├── docker-compose.yml         # Service orchestration
├── pyproject.toml            # Dependencies and dev tools
└── transactions.csv          # Test dataset
```

### Desired Codebase Tree with New Components
```bash
/Users/ajdoyle/data-stack/freelancer-data-stack/
├── data_stack/
│   ├── __init__.py
│   ├── meltano/               # ELT pipeline configuration
│   │   ├── meltano.yml
│   │   ├── extractors/
│   │   └── loaders/
│   ├── dbt/                   # Data transformations
│   │   ├── dbt_project.yml
│   │   ├── models/
│   │   ├── tests/
│   │   └── macros/
│   ├── airflow/               # Orchestration DAGs
│   │   ├── dags/
│   │   ├── plugins/
│   │   └── config/
│   ├── dashboards/            # Visualization apps
│   │   ├── streamlit/
│   │   └── evidence/
│   └── monitoring/            # Observability config
│       ├── prometheus/
│       └── grafana/
├── agents/
│   ├── data_stack_engineer.py # Stack-specific agent
│   └── analytics_engineer.py  # Enhanced analytics agent
├── tools/
│   ├── meltano_tools.py       # Meltano integration
│   ├── duckdb_tools.py        # Database tools
│   └── monitoring_tools.py    # Observability tools
└── scripts/
    ├── deploy_stack.py        # Deployment automation
    ├── validate_pipeline.py   # E2E validation
    └── health_check.py        # System monitoring
```

### Known Gotchas of Our Codebase & Library Quirks
```python
# CRITICAL: pydantic-ai requires async context for agent execution
# All agent methods must use 'await' for proper execution

# CRITICAL: Docker Compose services need health checks for dependency management
# Use 'depends_on' with 'condition: service_healthy' pattern

# GOTCHA: Airflow SQLAlchemy conflicts with Meltano dependencies
# Manage separately in different containers/environments

# GOTCHA: dbt-duckdb requires specific connection configuration
# Use file-based connections, not URI-based for embedded DuckDB

# CRITICAL: Agent tools require proper permission configuration
# Use tool_configs.py patterns for safety levels and environment restrictions

# GOTCHA: Great Expectations images have availability issues
# Use dbt-expectations as primary data quality framework

# PATTERN: All async tools use subprocess.run with capture_output=True
# Follow existing patterns in tools/ directory for consistency
```

## Implementation Blueprint

### Data Models and Structure

Create core data models ensuring type safety and consistency with existing agent framework:

```python
# Agent models for data stack operations
from pydantic import BaseModel
from enum import Enum

class DataStackComponent(str, Enum):
    MELTANO = "meltano"
    DBT = "dbt"
    DUCKDB = "duckdb"
    AIRFLOW = "airflow"
    STREAMLIT = "streamlit"
    GRAFANA = "grafana"

class PipelineStatus(BaseModel):
    component: DataStackComponent
    status: str
    last_run: Optional[datetime]
    error_message: Optional[str]
    health_score: float

class DataQualityResult(BaseModel):
    table_name: str
    tests_passed: int
    tests_failed: int
    quality_score: float
    failed_tests: List[str]
```

### List of Tasks in Implementation Order

```yaml
Task 1:
CREATE data_stack/meltano/meltano.yml:
  - FOLLOW pattern from: https://docs.meltano.com/getting-started
  - CONFIGURE tap-csv for transactions.csv ingestion
  - SET target-duckdb for local analytics database
  - INCLUDE environment-specific settings

Task 2:
CREATE tools/meltano_tools.py:
  - MIRROR pattern from: tools/dbt_tools.py
  - IMPLEMENT async command execution for Meltano CLI
  - ADD extraction, loading, and status monitoring functions
  - PRESERVE error handling patterns from existing tools

Task 3:
CREATE data_stack/dbt/dbt_project.yml:
  - CONFIGURE dbt-duckdb adapter
  - SET up automated testing with dbt-expectations
  - INCLUDE Great Expectations integration patterns
  - MIRROR configuration from existing dbt patterns

Task 4:
CREATE data_stack/dbt/models/staging/stg_transactions.sql:
  - IMPLEMENT EDA-driven transformation
  - ADD automated data profiling
  - INCLUDE data quality tests in schema.yml
  - FOLLOW existing SQL patterns and style

Task 5:
CREATE tools/duckdb_tools.py:
  - IMPLEMENT database connection management
  - ADD query execution and monitoring functions
  - INCLUDE performance optimization helpers
  - FOLLOW async patterns from existing tools

Task 6:
CREATE data_stack/airflow/dags/data_pipeline_dag.py:
  - CONFIGURE Meltano and dbt task orchestration
  - IMPLEMENT AI agent integration via MCP
  - ADD health monitoring and alerting
  - FOLLOW DAG patterns from research

Task 7:
MODIFY docker-compose.yml:
  - ADD Airflow services (webserver, scheduler, worker)
  - CONFIGURE DuckDB and Meltano containers
  - SET UP monitoring stack (Prometheus, Grafana)
  - PRESERVE existing service patterns

Task 8:
CREATE agents/data_stack_engineer.py:
  - EXTEND base_agent.py framework
  - IMPLEMENT stack deployment and monitoring capabilities
  - ADD integration with new tools (meltano_tools, duckdb_tools)
  - FOLLOW existing agent patterns

Task 9:
CREATE data_stack/dashboards/streamlit/app.py:
  - IMPLEMENT automated dashboard generation
  - CONNECT to DuckDB for real-time data access
  - ADD transaction analysis visualizations
  - FOLLOW existing Streamlit patterns

Task 10:
CREATE scripts/deploy_stack.py:
  - IMPLEMENT automated deployment workflow
  - ADD health checking and validation
  - INCLUDE rollback capabilities
  - FOLLOW existing script patterns

Task 11:
CREATE scripts/validate_pipeline.py:
  - IMPLEMENT E2E pipeline testing
  - ADD data quality validation
  - INCLUDE performance benchmarking
  - MIRROR test patterns from tests/

Task 12:
CREATE data_stack/monitoring/grafana/dashboard.json:
  - CONFIGURE data stack monitoring dashboard
  - ADD performance and health metrics
  - INCLUDE alerting rules
  - FOLLOW monitoring best practices
```

### Per Task Pseudocode

```python
# Task 2: Meltano Tools Implementation
async def extract_load_data(extractor: str, loader: str) -> CommandResult:
    # PATTERN: Use existing async subprocess pattern
    command = ["meltano", "elt", extractor, loader]

    # GOTCHA: Meltano requires specific working directory
    result = await subprocess.run(
        command,
        cwd="data_stack/meltano",
        capture_output=True,
        text=True
    )

    # PATTERN: Parse output for status and errors
    return parse_meltano_output(result)

# Task 5: DuckDB Tools Implementation
async def execute_query(query: str) -> QueryResult:
    # CRITICAL: Use connection pooling for performance
    async with get_duckdb_connection() as conn:
        # GOTCHA: DuckDB Python API requires specific patterns
        result = conn.execute(query).fetchall()

        # PATTERN: Standardized response format
        return format_query_result(result)

# Task 8: Data Stack Engineer Agent
async def deploy_data_stack(self, request: WorkflowRequest) -> AgentResponse:
    # PATTERN: Use tool integration from base agent
    deployment_steps = [
        ("Start containers", self.docker_tools.start_services),
        ("Initialize Meltano", self.meltano_tools.initialize_project),
        ("Run dbt models", self.dbt_tools.run_models),
        ("Validate pipeline", self.validate_data_quality)
    ]

    # PATTERN: Sequential execution with validation
    for step_name, step_function in deployment_steps:
        result = await step_function()
        if not result.success:
            return AgentResponse(
                content=f"Deployment failed at: {step_name}",
                confidence=0.3,
                validation_results=[result]
            )

    return AgentResponse(
        content="Data stack deployed successfully",
        confidence=0.95,
        next_actions=["Run health checks", "Monitor pipeline"]
    )
```

### Integration Points
```yaml
DATABASE:
  - connection: "DuckDB file-based connection in data_stack/duckdb/"
  - schema: "Create staging and marts schemas for dbt models"

CONFIG:
  - add to: config/agent_configs.py
  - pattern: "DATA_STACK_ENGINEER config with extended timeout and tool permissions"

DOCKER:
  - extend: docker-compose.yml
  - services: "airflow-webserver, airflow-scheduler, duckdb, meltano, grafana, prometheus"

AGENTS:
  - register: agents/orchestrator.py
  - new_agent: "DATA_STACK_ENGINEER with infrastructure management capabilities"

TOOLS:
  - register: config/tool_configs.py
  - permissions: "meltano_tools, duckdb_tools with appropriate safety levels"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
poetry run ruff check data_stack/ tools/ agents/ --fix
poetry run mypy data_stack/ tools/ agents/
poetry run black data_stack/ tools/ agents/

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# CREATE test_data_stack_tools.py with these test cases:
@pytest.mark.asyncio
async def test_meltano_extract_load():
    """Test Meltano ELT pipeline execution"""
    tools = MeltanoTools()
    result = await tools.extract_load_data("tap-csv", "target-duckdb")
    assert result.success
    assert "extracted" in result.output.lower()

@pytest.mark.asyncio
async def test_duckdb_query():
    """Test DuckDB query execution"""
    tools = DuckDBTools()
    result = await tools.execute_query("SELECT COUNT(*) FROM transactions")
    assert result.success
    assert len(result.data) > 0

@pytest.mark.asyncio
async def test_data_stack_engineer_deployment():
    """Test agent can deploy data stack"""
    agent = DataStackEngineer()
    request = WorkflowRequest(user_prompt="Deploy data stack")
    result = await agent.execute_task(request)
    assert result.confidence > 0.8
    assert "deployed" in result.content.lower()

@pytest.mark.asyncio
async def test_pipeline_health_check():
    """Test comprehensive pipeline validation"""
    validator = PipelineValidator()
    health = await validator.check_pipeline_health()
    assert health.overall_score > 0.9
    assert all(component.status == "healthy" for component in health.components)
```

```bash
# Run and iterate until passing:
poetry run pytest tests/test_data_stack* -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start the complete data stack
docker-compose up -d

# Wait for services to be healthy
./scripts/health_check.py --wait-timeout=300

# Run E2E pipeline test
poetry run python scripts/validate_pipeline.py

# Test AI agent interaction
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_role": "data_stack_engineer",
    "user_prompt": "Process transactions.csv and create dashboard"
  }'

# Expected: Complete pipeline execution with dashboard URL
# If error: Check logs at docker-compose logs airflow-webserver
```

### Level 4: Performance Validation
```bash
# Run performance benchmarks
poetry run python scripts/benchmark_pipeline.py

# Check resource utilization
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Validate data quality scores
poetry run python -c "
from tools.duckdb_tools import DuckDBTools
import asyncio
async def check():
    tools = DuckDBTools()
    quality = await tools.get_data_quality_metrics()
    assert quality.overall_score > 0.95
    print(f'Data quality score: {quality.overall_score}')
asyncio.run(check())
"

# Expected: Data quality > 95%, memory usage < 80%, pipeline < 5 minutes
```

## Final Validation Checklist
- [ ] All tests pass: `poetry run pytest tests/ -v`
- [ ] No linting errors: `poetry run ruff check .`
- [ ] No type errors: `poetry run mypy .`
- [ ] Docker services healthy: `docker-compose ps` shows all "Up (healthy)"
- [ ] E2E pipeline successful: `poetry run python scripts/validate_pipeline.py`
- [ ] AI agents respond correctly: Agent API integration test passes
- [ ] Dashboards accessible: Streamlit and Grafana URLs responding
- [ ] Cost tracking under budget: Monthly cost projection < $50
- [ ] Performance targets met: Pipeline execution < 5 minutes
- [ ] Data quality high: >95% tests passing
- [ ] Monitoring active: Grafana dashboards showing metrics
- [ ] Documentation updated: README.md reflects new capabilities

## Research Quality Metrics

**Context Richness**: 10/10 - Comprehensive research across all 4 domains with specific file references and implementation examples

**Implementation Clarity**: 9/10 - Clear step-by-step tasks with existing patterns to follow and specific integration points

**Validation Completeness**: 10/10 - Multi-layer testing strategy from unit tests to E2E validation with performance benchmarks

**One-Pass Success Probability**: 9/10 - High confidence due to leveraging existing agent framework and proven patterns

## Anti-Patterns to Avoid
- ❌ Don't create new agent patterns when base_agent.py framework exists
- ❌ Don't skip health checks in Docker Compose - services must be healthy
- ❌ Don't use sync functions with async agents - maintain async consistency
- ❌ Don't ignore data quality test failures - fix underlying data issues
- ❌ Don't hardcode database connections - use configuration patterns
- ❌ Don't mix container environments - keep Airflow and Meltano separate if conflicts arise
- ❌ Don't bypass tool permission system - maintain security boundaries
- ❌ Don't skip cost monitoring - implement budget tracking from day one
