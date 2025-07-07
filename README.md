# Freelancer Data Stack with AI Agents

A modernized data stack powered by specialized AI agents that can collaborate to handle complex data engineering, analytics, and machine learning workflows through natural language interfaces.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- API keys for at least one LLM provider (OpenAI, Anthropic, Google, or xAI)

### Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd freelancer-data-stack
   cp .env.example .env
   ```

2. **Configure API keys in `.env`:**
   ```bash
   # Uncomment and set at least one API key
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   XAI_API_KEY=your_xai_api_key_here
   # ... etc
   ```

3. **Install dependencies:**
   ```bash
   python -m pip install pydantic-ai anthropic openai python-dotenv
   ```

4. **Test the installation:**
   ```bash
   python test_implementation.py
   ```

## 🤖 AI Agents

The system includes 5 specialized AI agents that work together:

### Data Platform Engineer
- **Role**: Infrastructure management and deployment
- **Capabilities**: Docker, Terraform, CI/CD, monitoring setup
- **Tools**: docker_tools, terraform, monitoring_tools

### Data Engineer
- **Role**: Data pipeline development and ETL processes
- **Capabilities**: Airflow DAGs, Meltano pipelines, data quality
- **Tools**: airflow_tools, meltano, database_tools, quality_tools

### Analytics Engineer
- **Role**: Data modeling and transformation with dbt
- **Capabilities**: SQL modeling, testing, documentation
- **Tools**: dbt_tools, sql_tools, documentation_tools

### Data Scientist
- **Role**: Machine learning and statistical analysis
- **Capabilities**: Model development, experimentation, analysis
- **Tools**: jupyter_tools, ml_libraries, statistical_tools

### Data Analyst
- **Role**: Reporting and visualization
- **Capabilities**: Dashboard creation, business intelligence
- **Tools**: metabase_tools, evidence_tools, visualization_tools

## 💬 Natural Language Interface

Interact with agents using natural language:

```python
from interface.workflow_executor import WorkflowExecutor

executor = WorkflowExecutor()

# Single agent tasks
result = await executor.process_request("Deploy the Docker services")

# Multi-agent workflows
result = await executor.process_request("Set up a complete data pipeline from CSV to dashboard")
```

## 📊 Data Stack Components

### Core Infrastructure
- **PostgreSQL**: Primary data warehouse
- **Apache Airflow**: Workflow orchestration
- **Docker**: Containerization and deployment

### Data Integration
- **Meltano**: ELT pipeline framework
- **Great Expectations**: Data quality validation
- **DataHub**: Data discovery and lineage

### Analytics & ML
- **dbt**: Data transformation and modeling
- **Jupyter**: Interactive analysis and ML development
- **Evidence.dev**: Automated reporting

### Visualization
- **Metabase**: Business intelligence dashboards
- **Grafana**: Infrastructure monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Natural Lang.  │    │   AI Agents      │    │   Data Stack    │
│   Interface     │───▶│   Orchestrator   │───▶│   Components    │
│                 │    │                  │    │                 │
│ • Prompt Handler│    │ • 5 Specialized  │    │ • PostgreSQL    │
│ • Workflow Exec │    │   Agent Roles    │    │ • Airflow       │
│ • Response Form │    │ • Multi-agent    │    │ • dbt           │
└─────────────────┘    │   Coordination   │    │ • Meltano       │
                       └──────────────────┘    │ • Metabase      │
                                               └─────────────────┘
```

## 📂 Project Structure

```
freelancer-data-stack/
├── agents/                 # AI agent implementations
│   ├── base_agent.py      # Abstract base class
│   ├── data_platform_engineer.py
│   ├── data_engineer.py
│   ├── analytics_engineer.py
│   ├── data_scientist.py
│   ├── data_analyst.py
│   └── orchestrator.py    # Multi-agent coordination
├── tools/                 # Agent tool implementations
│   ├── docker_tools.py
│   ├── dbt_tools.py
│   └── ...
├── config/                # Configuration management
│   ├── agent_configs.py   # Agent settings
│   ├── model_configs.py   # LLM model configs
│   └── tool_configs.py    # Tool permissions
├── interface/             # Natural language interface
│   ├── prompt_handler.py  # NL prompt analysis
│   ├── workflow_executor.py # Task execution
│   └── response_formatter.py # Output formatting
├── examples/              # Usage examples
├── tests/                 # Test suite
├── PRPs/                  # Product Requirements Prompts
└── docker-compose.yml     # Infrastructure definition
```

## 🛠️ Configuration

### Agent Configuration
Agents can be configured per environment in `config/agent_configs.py`:

```python
# Development settings
config.timeout_seconds = 180
config.model_name = "openai:gpt-4"
config.rate_limit_requests_per_minute = 60

# Production settings
config.timeout_seconds = 600
config.model_name = "anthropic:claude-3-5-sonnet-20241022"
config.rate_limit_requests_per_minute = 30
```

### Model Selection
Choose from multiple LLM providers in `config/model_configs.py`:
- **OpenAI**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic**: Claude-3.5-sonnet, Claude-3-haiku
- **Google**: Gemini-1.5-pro
- **xAI**: Grok-beta

### Tool Permissions
Fine-grained tool access control in `config/tool_configs.py`:
- Role-based permissions (READ_ONLY, WRITE, ADMIN)
- Safety levels and rate limiting
- Environment restrictions

## 📚 Examples

See the `examples/` directory for practical usage:

- **[basic_agent_usage.py](examples/basic_agent_usage.py)** - Simple agent interactions
- **[multi_agent_workflow.py](examples/multi_agent_workflow.py)** - Coordinated workflows
- **[data_pipeline_setup.py](examples/data_pipeline_setup.py)** - End-to-end pipeline deployment

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Full validation
python test_implementation.py

# Unit tests
pytest tests/

# Agent-specific tests
python -m pytest tests/test_agents.py
```

## 🚀 Deployment

### Local Development
```bash
# Start data stack services
docker-compose up -d

# Run agents
python examples/basic_agent_usage.py
```

### Production Deployment
1. Set `ENVIRONMENT=production` in `.env`
2. Configure production API keys and settings
3. Deploy with `docker-compose -f docker-compose.prod.yml up -d`

## 🔧 Troubleshooting

### Common Issues

**API Key Errors**: Ensure `.env` file has valid API keys uncommented
```bash
# Check if keys are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

**Import Errors**: Install required dependencies
```bash
python -m pip install pydantic-ai anthropic openai python-dotenv
```

**Docker Issues**: Ensure Docker daemon is running
```bash
docker --version
docker-compose --version
```

## 📈 Monitoring

The system includes comprehensive monitoring:
- **Agent performance metrics**: Success rates, execution times
- **Workflow tracking**: Request history, status monitoring
- **Data quality metrics**: Pipeline health, validation results
- **Infrastructure monitoring**: Resource usage, service health

## 🤝 Contributing

1. Follow the coding standards in `CLAUDE.md`
2. Add tests for new features
3. Update documentation
4. Run validation: `python test_implementation.py`

## 📄 License

[Your License Here]

## 🆘 Support

For issues and feature requests, please [create an issue](link-to-issues) or consult the troubleshooting guide.

---

## 📋 Legacy Data Stack

The project also includes a comprehensive Docker Compose stack for traditional data engineering workflows:

### Services Included

1. **PostgreSQL** - Shared database for Airbyte, Metabase, and Airflow metadata
2. **Meltano** - Modern ELT platform with Singer taps and targets
3. **Apache Airflow 3.0** - Latest workflow orchestration with Celery executor and Redis
4. **DataHub + Kafka** - Data catalog and discovery platform with Kafka messaging
5. **Great Expectations** - Data quality and validation with Jupyter/Streamlit
6. **Evidence.dev** - Development server for data apps
7. **Metabase** - Business intelligence and analytics dashboards
8. **DuckDB HTTP** - DuckDB exposed via REST API
9. **Traefik** - Reverse proxy with dashboard for service management

### Legacy Quick Start

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
   - **Apache Airflow**: http://localhost:8080 (admin/[your_password])
   - **Meltano UI**: Available via CLI commands
   - **Airflow Flower (Celery Monitor)**: http://localhost:5555
   - **DataHub**: http://localhost:9002
   - **Great Expectations Jupyter**: http://localhost:8888
   - **Evidence.dev**: http://localhost:3001
   - **Metabase**: http://localhost:3002
   - **DuckDB HTTP**: http://localhost:8002
   - **Traefik Dashboard**: http://localhost:8090

---

**Built with ❤️ using Claude Code and the power of AI collaboration**
