# AI Agent Data Stack Help

Overview of all available Claude slash commands for the AI agent-driven data stack.

## Core Operations

### `/deploy-data-stack`
Deploy the complete AI agent-driven data stack with automated validation.
- Sets up all services (PostgreSQL, Redis, Airflow, Meltano, DuckDB, Grafana)
- Configures AI agent integration
- Validates deployment with comprehensive testing
- Generates deployment report

### `/run-data-pipeline`
Execute the complete data pipeline from CSV to dashboard.
- Meltano ELT: transactions.csv → DuckDB
- dbt transformations: 31-column EDA with quality testing
- Airflow orchestration with AI agent integration
- Real-time dashboard updates

### `/validate-pipeline`
Run comprehensive end-to-end validation of the data stack.
- 10 validation test categories
- Data quality metrics (85%+ threshold)
- Performance benchmarking
- Business logic validation

## Management & Operations

### `/ai-agent-task`
Use the DataStackEngineer AI agent for autonomous infrastructure management.
- Automated deployment and configuration
- Health monitoring and alerting
- Performance optimization
- Troubleshooting and issue resolution

### `/monitor-data-stack`
Monitor infrastructure health and pipeline performance.
- Real-time dashboards (Streamlit, Grafana, Airflow)
- Service health monitoring
- Data quality tracking
- Performance metrics analysis

### `/troubleshoot-stack`
Diagnose and resolve data stack issues.
- Common issue diagnostics
- Service health checks
- Recovery procedures
- AI agent-assisted troubleshooting

## Optimization & Scaling

### `/optimize-costs`
Analyze and optimize data stack costs (~$50/month target).
- Resource utilization analysis
- Cost comparison vs traditional stacks
- Performance vs cost trade-offs
- Optimization recommendations

### `/scale-data-stack`
Scale the data stack for increased volume and performance.
- Vertical and horizontal scaling strategies
- Performance optimization techniques
- Resource allocation adjustments
- Cost-aware scaling decisions

## Planning & Execution

### `/prp-task-execute [filename]`
Execute task lists from AI data stack PRPs.
- Sequential task execution with validation
- AI agent integration for complex tasks
- Comprehensive testing framework
- Progress tracking with TodoWrite

### `/create-planning-parallel [filename]`
Create comprehensive planning documents for data stack initiatives.
- Architecture planning and design
- Cost analysis and optimization
- Technology selection and evaluation
- Implementation roadmaps

## Quick Reference

### Essential Commands for New Users
1. `/deploy-data-stack` - Get started with complete deployment
2. `/validate-pipeline` - Verify everything is working
3. `/monitor-data-stack` - Check system health
4. `/run-data-pipeline` - Execute data processing

### Daily Operations
- `/monitor-data-stack` - Morning health check
- `/run-data-pipeline` - Execute data processing
- `/validate-pipeline` - Quality assurance
- `/ai-agent-task` - Handle specific infrastructure tasks

### Troubleshooting
- `/troubleshoot-stack` - Diagnose issues
- `/ai-agent-task "diagnose system problems"` - AI-assisted diagnosis
- `/validate-pipeline --verbose` - Detailed validation
- `/monitor-data-stack` - Health overview

## Access Points

- **Streamlit Dashboard**: http://localhost:8501
- **Grafana Monitoring**: http://localhost:3000
- **Airflow UI**: http://localhost:8080
- **Metabase BI**: http://localhost:3002

## Getting Help

Each command includes detailed documentation and examples. The AI agent can also provide context-aware assistance for specific tasks and troubleshooting scenarios.

**Total Monthly Cost**: ~$50 (88-95% savings vs traditional cloud data warehouses)
**Deployment Time**: < 1 hour for complete stack
**Validation**: Comprehensive 10-test validation framework