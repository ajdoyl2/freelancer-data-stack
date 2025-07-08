# Execute AI Agent Task

Use the DataStackEngineer AI agent to perform infrastructure management tasks.

## AI Agent Capabilities

1. **Automated Deployment**
   - Complete stack deployment and configuration
   - Service orchestration and health checking
   - Environment setup and validation

2. **Health Monitoring**
   - Real-time system health checks
   - Performance monitoring and alerting
   - Resource usage optimization

3. **Pipeline Management**
   - ELT execution (Meltano pipelines)
   - dbt transformations and testing
   - Data quality monitoring

4. **Performance Optimization**
   - Resource monitoring and tuning
   - Query performance optimization
   - Cost optimization recommendations

5. **Troubleshooting**
   - Automated issue detection
   - Root cause analysis
   - Resolution recommendations

## Task Examples

### Infrastructure Tasks
- "Deploy the complete data stack infrastructure"
- "Check system health and generate report"
- "Optimize resource allocation and performance"
- "Troubleshoot failed services"

### Pipeline Tasks
- "Run the complete ELT and transformation pipeline"
- "Validate data quality and generate metrics"
- "Execute dbt transformations with testing"
- "Monitor pipeline performance"

### Operations Tasks
- "Perform health check on all services"
- "Generate infrastructure status report"
- "Optimize DuckDB query performance"
- "Set up monitoring and alerting"

## Usage Pattern

```python
from agents.data_stack_engineer import DataStackEngineer
from agents.base_agent import WorkflowRequest

# Initialize agent
agent = DataStackEngineer()

# Execute task
result = await agent.execute_task(WorkflowRequest(
    user_prompt="YOUR_TASK_DESCRIPTION"
))

# Review results
print(f"Success: {result.output['success']}")
print(f"Details: {result.output}")
```

Specify the task you want the AI agent to perform, and it will autonomously execute the required operations.