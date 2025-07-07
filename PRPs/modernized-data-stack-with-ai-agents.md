name: "Modernized Data Stack with AI Agents PRP"
description: |

## Purpose
Complete modernization and restructuring of the freelancer-data-stack repository to create a comprehensive, AI-agent-enabled data platform where specialized agents collaborate to handle data engineering tasks through natural language prompts.

## Core Principles
1. **Agent-First Architecture**: Each data team role (Data Platform Engineer, Data Engineer, Analytics Engineer, Data Scientist, Data Analyst) is represented by specialized AI agents
2. **Context-Rich Environment**: Comprehensive documentation and examples enable agents to understand the full system
3. **Validation-Driven Development**: All agent actions are validated through executable tests and linting
4. **Progressive Enhancement**: Build on existing infrastructure while adding agent capabilities
5. **Global Rules Compliance**: Follow all rules defined in CLAUDE.md

---

## Goal
Transform the existing freelancer-data-stack into a modern, AI-agent-enabled data platform that can be deployed locally via Docker and interacted with through natural language prompts. Create specialized agents for each data team role that work collaboratively to execute complex data engineering workflows.

## Why
- **Democratize Data Engineering**: Enable non-technical users to perform complex data tasks through natural language
- **Accelerate Development**: Reduce time from requirements to implementation via AI automation
- **Improve Consistency**: Standardize data engineering practices through agent-driven workflows
- **Enable Self-Service**: Allow users to create, modify, and deploy data pipelines without deep technical knowledge
- **Reduce Maintenance Overhead**: Automated code generation and testing reduces manual maintenance

## What
A comprehensive data platform with:
- **5 Specialized AI Agents** working collaboratively
- **Docker-based deployment** for local development and production
- **Natural language interface** for all data operations
- **Comprehensive documentation** and examples for agent context
- **Automated testing and validation** for all agent-generated code
- **Multi-environment support** (local DuckDB, production Snowflake)

### Success Criteria
- [ ] Repository structure cleaned and organized with clear purpose
- [ ] All 5 AI agents implemented and functional
- [ ] Agents can collaborate on complex multi-step data workflows
- [ ] Full Docker stack deployment working locally
- [ ] Natural language prompt interface operational
- [ ] Comprehensive README with setup instructions
- [ ] All legacy/unused files removed or organized
- [ ] Agent-generated code passes all validation tests
- [ ] End-to-end data pipeline demonstrable via prompts

## All Needed Context

### Documentation & References
```yaml
# Core AI Framework Documentation
- url: https://ai.pydantic.dev/
  why: Primary framework for building type-safe AI agents
  critical: Multi-agent patterns, tool integration, dependency injection

# Data Stack Architecture Reference
- url: https://github.com/matsonj/nba-monte-carlo
  why: Example of modern data stack architecture without agents
  critical: Simple, portable approach with DuckDB + Evidence.dev

# Current MCP Server Implementation
- file: mcp-server/main.py
  why: Existing FastAPI server with data tool adapters
  critical: Adapter pattern for Dagster, dbt, Snowflake, DuckDB, DataHub

# Docker Compose Configuration
- file: docker-compose.yml
  why: Existing container orchestration setup
  critical: Service definitions, networking, volume mounts

# Project Vision and Planning
- file: PLANNING.md
  why: Strategic objectives and AI-enablement roadmap
  critical: Agent success metrics, deployment targets

# Current Project Structure
- file: README.md
  why: Current service documentation and setup instructions
  critical: Existing tooling integration patterns

# Tool-Specific Documentation
- url: https://airflow.apache.org/docs/
  section: TaskFlow API and dynamic DAG generation
  critical: Agent-driven workflow creation

- url: https://docs.datahub.com/docs/
  section: Metadata ingestion and lineage tracking
  critical: Agent-driven data catalog management

- url: https://docs.greatexpectations.io/docs/core/introduction/try_gx
  section: Programmatic expectation creation
  critical: Agent-driven data quality validation

- url: https://docs.evidence.dev/install-evidence/
  section: Programmatic report generation
  critical: Agent-driven analytics dashboard creation
```

### Current Codebase Structure
```bash
freelancer-data-stack/
├── .claude/                    # Context engineering setup
├── mcp-server/                # FastAPI server with data adapters
├── docker-compose.yml         # Container orchestration
├── meltano/                   # ELT pipeline configurations
├── transformation/dbt/        # Data transformation models
├── orchestration/airflow/     # Workflow orchestration
├── quality/great_expectations/ # Data quality validation
├── viz/                       # Evidence.dev, Metabase, Streamlit
├── catalog/datahub/          # Data catalog configuration
├── infra/terraform/          # Infrastructure as Code
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── PRPs/                     # Product Requirements Prompts
└── examples/                 # Code examples for agents
```

### Desired Codebase Structure with AI Agents
```bash
freelancer-data-stack/
├── .claude/                    # Context engineering (existing)
├── agents/                     # AI Agent implementations
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── data_platform_engineer.py # Infrastructure & deployment
│   ├── data_engineer.py       # Ingestion & pipelines
│   ├── analytics_engineer.py  # dbt transformations
│   ├── data_scientist.py      # ML models & experiments
│   ├── data_analyst.py        # Reporting & insights
│   └── orchestrator.py        # Multi-agent coordination
├── tools/                      # Agent tools and utilities
│   ├── __init__.py
│   ├── docker_tools.py        # Docker management
│   ├── dbt_tools.py           # dbt operations
│   ├── airflow_tools.py       # Airflow DAG generation
│   ├── datahub_tools.py       # Metadata management
│   └── quality_tools.py       # Data validation
├── config/                     # Agent configurations
│   ├── agent_configs.py       # Agent-specific settings
│   ├── model_configs.py       # LLM model configurations
│   └── tool_configs.py        # Tool permissions
├── interface/                  # Natural language interface
│   ├── __init__.py
│   ├── prompt_handler.py      # Natural language processing
│   ├── workflow_executor.py   # Agent workflow execution
│   └── response_formatter.py  # Output formatting
├── examples/                   # Enhanced examples for agents
│   ├── README.md
│   ├── agent_patterns/        # Agent implementation patterns
│   ├── workflow_patterns/     # Multi-agent workflows
│   └── integration_patterns/  # Tool integration examples
├── tests/                      # Comprehensive testing
│   ├── agents/                # Agent unit tests
│   ├── tools/                 # Tool integration tests
│   ├── workflows/             # End-to-end workflow tests
│   └── fixtures/              # Test data and mocks
└── (existing directories remain with cleanup)
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Pydantic AI requires specific dependency injection patterns
# Example: Agents need proper type hints for dependency resolution

# CRITICAL: Docker Compose networking requires consistent service names
# Example: Agent tools must reference services by container names

# CRITICAL: MCP Server adapter pattern already exists
# Example: Extend existing adapters rather than recreating

# CRITICAL: Poetry dependency management with groups
# Example: Agent dependencies should be organized by role/function

# CRITICAL: FastAPI async patterns for agent coordination
# Example: Agent workflows must be async to prevent blocking
```

## Implementation Blueprint

### Data Models and Structure

Core agent and workflow models for type safety and consistency:
```python
# Pydantic models for agent communication
class AgentRole(str, Enum):
    DATA_PLATFORM_ENGINEER = "data_platform_engineer"
    DATA_ENGINEER = "data_engineer"
    ANALYTICS_ENGINEER = "analytics_engineer"
    DATA_SCIENTIST = "data_scientist"
    DATA_ANALYST = "data_analyst"

class WorkflowRequest(BaseModel):
    user_prompt: str
    context: Dict[str, Any]
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    agents_involved: List[AgentRole]

class AgentResponse(BaseModel):
    agent_role: AgentRole
    status: ResponseStatus
    output: Dict[str, Any]
    next_actions: List[str]
    validation_results: List[ValidationResult]
```

### List of Tasks (Implementation Order)

```yaml
Task 1: Repository Cleanup and Organization
REVIEW entire codebase structure:
  - AUDIT all existing files and directories
  - IDENTIFY unused/legacy files for removal
  - CATEGORIZE files by purpose and relevance
  - PRESERVE essential configurations and data

RESTRUCTURE directory layout:
  - CREATE agents/ directory with proper Python package structure
  - ORGANIZE tools/ by functional category
  - CONSOLIDATE examples/ with agent-specific patterns
  - ESTABLISH clear separation between agent code and infrastructure

Task 2: Base Agent Framework
CREATE agents/base_agent.py:
  - IMPLEMENT abstract base class for all agents
  - DEFINE common agent interface and lifecycle methods
  - INTEGRATE with Pydantic AI framework
  - ESTABLISH dependency injection patterns

CREATE agents/__init__.py:
  - EXPORT all agent classes
  - DEFINE agent registry and discovery
  - IMPLEMENT agent factory patterns

Task 3: Specialized Agent Implementation
CREATE agents/data_platform_engineer.py:
  - FOCUS on Docker, Terraform, infrastructure management
  - IMPLEMENT tools for service deployment and monitoring
  - INTEGRATE with existing MCP server adapters

CREATE agents/data_engineer.py:
  - FOCUS on Meltano, Airbyte, data ingestion
  - IMPLEMENT pipeline creation and management tools
  - INTEGRATE with existing orchestration patterns

CREATE agents/analytics_engineer.py:
  - FOCUS on dbt transformations and data modeling
  - IMPLEMENT model generation and testing tools
  - INTEGRATE with existing dbt project structure

CREATE agents/data_scientist.py:
  - FOCUS on ML model development and experimentation
  - IMPLEMENT Jupyter integration and model deployment
  - INTEGRATE with existing notebook infrastructure

CREATE agents/data_analyst.py:
  - FOCUS on reporting, visualization, and insights
  - IMPLEMENT Evidence.dev and Metabase integration
  - INTEGRATE with existing visualization tools

Task 4: Agent Tools Development
CREATE tools/docker_tools.py:
  - IMPLEMENT Docker Compose management functions
  - PROVIDE service health checking and deployment
  - INTEGRATE with existing docker-compose.yml

CREATE tools/dbt_tools.py:
  - IMPLEMENT dbt command execution and parsing
  - PROVIDE model generation and testing capabilities
  - INTEGRATE with existing dbt project structure

CREATE tools/airflow_tools.py:
  - IMPLEMENT dynamic DAG generation
  - PROVIDE workflow scheduling and monitoring
  - INTEGRATE with existing Airflow setup

CREATE tools/datahub_tools.py:
  - IMPLEMENT metadata ingestion and lineage tracking
  - PROVIDE data catalog management capabilities
  - INTEGRATE with existing DataHub configuration

CREATE tools/quality_tools.py:
  - IMPLEMENT Great Expectations suite generation
  - PROVIDE data validation and profiling tools
  - INTEGRATE with existing quality framework

Task 5: Multi-Agent Orchestration
CREATE agents/orchestrator.py:
  - IMPLEMENT workflow coordination between agents
  - PROVIDE task delegation and result aggregation
  - ESTABLISH communication protocols between agents

CREATE interface/workflow_executor.py:
  - IMPLEMENT natural language prompt parsing
  - PROVIDE workflow execution engine
  - ESTABLISH result formatting and user feedback

Task 6: Natural Language Interface
CREATE interface/prompt_handler.py:
  - IMPLEMENT natural language understanding
  - PROVIDE intent classification and entity extraction
  - ESTABLISH prompt routing to appropriate agents

CREATE interface/response_formatter.py:
  - IMPLEMENT structured response generation
  - PROVIDE user-friendly output formatting
  - ESTABLISH progress tracking and status updates

Task 7: Configuration and Setup
CREATE config/agent_configs.py:
  - DEFINE agent-specific configurations
  - IMPLEMENT environment-based settings
  - ESTABLISH agent capability definitions

CREATE config/model_configs.py:
  - DEFINE LLM model configurations
  - IMPLEMENT provider-specific settings
  - ESTABLISH model selection strategies

Task 8: Enhanced Examples and Documentation
ENHANCE examples/ directory:
  - CREATE agent implementation patterns
  - PROVIDE workflow execution examples
  - DEMONSTRATE tool integration patterns

UPDATE README.md:
  - DOCUMENT agent capabilities and usage
  - PROVIDE setup and deployment instructions
  - ESTABLISH troubleshooting guide

Task 9: Comprehensive Testing
CREATE tests/agents/:
  - IMPLEMENT unit tests for each agent
  - PROVIDE mock tool integrations
  - ESTABLISH agent behavior validation

CREATE tests/workflows/:
  - IMPLEMENT end-to-end workflow tests
  - PROVIDE realistic data scenarios
  - ESTABLISH performance benchmarks

Task 10: Integration and Deployment
UPDATE docker-compose.yml:
  - INTEGRATE agent services
  - ESTABLISH service dependencies
  - PROVIDE health check configurations

CREATE deployment scripts:
  - IMPLEMENT one-command deployment
  - PROVIDE environment validation
  - ESTABLISH monitoring and logging
```

### Integration Points
```yaml
EXISTING_INFRASTRUCTURE:
  - preserve: docker-compose.yml service definitions
  - enhance: Add agent services and dependencies
  - integrate: MCP server adapters with agent tools

CONFIGURATION_MANAGEMENT:
  - preserve: .env template and environment variables
  - enhance: Agent-specific configuration sections
  - integrate: LLM provider configurations

API_ENDPOINTS:
  - preserve: MCP server REST API structure
  - enhance: Agent workflow execution endpoints
  - integrate: Natural language prompt handling

VOLUME_MOUNTS:
  - preserve: Existing volume mappings
  - enhance: Agent workspace directories
  - integrate: Shared data access patterns
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST for all agent code
ruff check agents/ tools/ interface/ config/ --fix
ruff format agents/ tools/ interface/ config/
mypy agents/ tools/ interface/ config/

# Expected: No errors. Fix any type hints or formatting issues.
```

### Level 2: Agent Unit Tests
```python
# CREATE comprehensive tests for each agent
def test_data_platform_engineer_deploy():
    """Test infrastructure deployment capabilities"""
    agent = DataPlatformEngineer()
    result = agent.deploy_service("postgres")
    assert result.status == "success"
    assert "postgres" in result.deployed_services

def test_data_engineer_pipeline_creation():
    """Test data pipeline generation"""
    agent = DataEngineer()
    result = agent.create_pipeline("csv_to_duckdb")
    assert result.pipeline_created
    assert result.meltano_config_updated

def test_analytics_engineer_model_generation():
    """Test dbt model creation"""
    agent = AnalyticsEngineer()
    result = agent.create_model("customer_summary")
    assert result.model_created
    assert result.tests_generated

def test_agent_collaboration():
    """Test multi-agent workflow execution"""
    orchestrator = AgentOrchestrator()
    result = orchestrator.execute_workflow(
        "Create a customer analytics pipeline from CSV to dashboard"
    )
    assert len(result.agents_involved) >= 3
    assert result.workflow_completed
```

```bash
# Run and iterate until passing
poetry run pytest tests/agents/ -v
poetry run pytest tests/workflows/ -v
```

### Level 3: Integration Tests
```bash
# Test Docker stack deployment
docker-compose up -d
# Wait for services to be healthy
docker-compose ps

# Test agent API endpoints
curl -X POST http://localhost:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a simple data pipeline", "context": {}}'

# Expected: {"status": "success", "workflow_id": "...", "agents_involved": [...]}
```

### Level 4: End-to-End Workflow Tests
```bash
# Test complete workflow execution
poetry run python -m interface.workflow_executor \
  --prompt "Set up a customer analytics pipeline with quality checks"

# Expected: Successfully creates pipeline, transformations, and quality checks
# Verify: Check generated files in meltano/, transformation/dbt/, quality/
```

## Final Validation Checklist
- [ ] All agent unit tests pass: `poetry run pytest tests/agents/ -v`
- [ ] All workflow tests pass: `poetry run pytest tests/workflows/ -v`
- [ ] No linting errors: `ruff check agents/ tools/ interface/ config/`
- [ ] No type errors: `mypy agents/ tools/ interface/ config/`
- [ ] Docker stack deploys successfully: `docker-compose up -d`
- [ ] Agent API endpoints respond correctly
- [ ] Natural language prompts execute workflows
- [ ] Generated code passes validation
- [ ] Documentation is comprehensive and accurate
- [ ] Repository is clean and well-organized

---

## Anti-Patterns to Avoid
- ❌ Don't duplicate existing MCP server functionality
- ❌ Don't create agents that bypass existing validation
- ❌ Don't hardcode LLM provider specifics
- ❌ Don't ignore existing Docker networking patterns
- ❌ Don't create agents without proper error handling
- ❌ Don't skip comprehensive testing for agent interactions
- ❌ Don't create overly complex agent hierarchies
- ❌ Don't ignore existing Poetry dependency management

## Confidence Score: 9/10
This PRP provides comprehensive context for implementing a sophisticated AI-agent-enabled data platform. The high confidence is based on:
- Thorough analysis of existing codebase and infrastructure
- Clear integration with proven frameworks (Pydantic AI, FastAPI)
- Detailed implementation blueprint with specific tasks
- Comprehensive validation strategy
- Preservation of existing working components
- Realistic scope and timeline expectations
