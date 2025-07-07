# AI Agent Examples

This directory contains practical examples of using the AI agent system for common data stack operations.

## Quick Start Examples

### Basic Agent Usage
```python
from agents import get_agent
from agents.base_agent import AgentRole

# Create a data platform engineer agent
agent = get_agent(AgentRole.DATA_PLATFORM_ENGINEER)

# Execute a simple task
result = await agent.execute_task("Check Docker container status")
print(result.content)
```

### Natural Language Interface
```python
from interface.workflow_executor import WorkflowExecutor

# Initialize the workflow executor
executor = WorkflowExecutor()

# Process natural language requests
result = await executor.process_request("Deploy the data pipeline services")
print(result.formatted_response)
```

## Example Scripts

1. **[basic_agent_usage.py](basic_agent_usage.py)** - Simple agent interaction
2. **[multi_agent_workflow.py](multi_agent_workflow.py)** - Coordinated multi-agent tasks
3. **[data_pipeline_setup.py](data_pipeline_setup.py)** - Complete pipeline deployment
4. **[monitoring_dashboard.py](monitoring_dashboard.py)** - Health monitoring setup
5. **[dbt_model_generation.py](dbt_model_generation.py)** - Analytics model creation

## Configuration Examples

- **[agent_config_examples.py](agent_config_examples.py)** - Agent configuration patterns
- **[model_selection_examples.py](model_selection_examples.py)** - Model selection strategies
- **[tool_permission_examples.py](tool_permission_examples.py)** - Tool access management

## Use Case Examples

- **[data_ingestion_workflow.py](data_ingestion_workflow.py)** - End-to-end data ingestion
- **[analytics_reporting.py](analytics_reporting.py)** - Automated report generation
- **[ml_pipeline_setup.py](ml_pipeline_setup.py)** - Machine learning pipeline deployment

See individual files for detailed implementation examples.
