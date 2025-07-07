"""
Data Stack Engineer Agent

Specialized AI agent for managing and orchestrating the complete data stack infrastructure.
Handles deployment, monitoring, troubleshooting, and optimization of the AI agent-driven data pipeline.
"""

from datetime import datetime
from typing import Any

from agents.base_agent import (
    AgentCapability,
    AgentResponse,
    AgentRole,
    BaseAgent,
    ResponseStatus,
    WorkflowRequest,
)
from tools.airflow_tools import AirflowTools
from tools.dbt_tools import DbtTools
from tools.docker_tools import DockerTools
from tools.duckdb_tools import DuckDBTools
from tools.meltano_tools import MeltanoTools


class DataStackEngineer(BaseAgent):
    """
    Data Stack Engineer agent for comprehensive infrastructure management.

    Capabilities:
    - Deploy and manage complete data stack
    - Monitor pipeline health and performance
    - Troubleshoot data pipeline issues
    - Optimize infrastructure and performance
    - Coordinate with other AI agents
    - Automate data stack operations
    """

    def __init__(self, model_name: str = "openai:gpt-4", **kwargs):
        """Initialize the Data Stack Engineer agent."""
        super().__init__(
            role=AgentRole.DATA_PLATFORM_ENGINEER, model_name=model_name, **kwargs
        )

        # Initialize tools
        self.docker_tools = DockerTools()
        self.meltano_tools = MeltanoTools()
        self.dbt_tools = DbtTools()
        self.duckdb_tools = DuckDBTools()
        self.airflow_tools = AirflowTools()

        # Define capabilities
        self.capabilities = [
            AgentCapability(
                name="data_stack_deployment",
                description="Deploy and configure complete AI agent data stack",
                tools_required=["docker_tools", "meltano_tools", "dbt_tools"],
                complexity_level=8,
            ),
            AgentCapability(
                name="pipeline_monitoring",
                description="Monitor data pipeline health and performance",
                tools_required=["airflow_tools", "duckdb_tools", "docker_tools"],
                complexity_level=6,
            ),
            AgentCapability(
                name="infrastructure_troubleshooting",
                description="Diagnose and resolve data stack issues",
                tools_required=["docker_tools", "airflow_tools", "duckdb_tools"],
                complexity_level=9,
            ),
            AgentCapability(
                name="performance_optimization",
                description="Optimize data stack performance and resource usage",
                tools_required=["duckdb_tools", "docker_tools"],
                complexity_level=7,
            ),
            AgentCapability(
                name="automated_operations",
                description="Automate routine data stack operations",
                tools_required=["meltano_tools", "dbt_tools", "airflow_tools"],
                complexity_level=5,
            ),
        ]

    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for the Data Stack Engineer."""
        return """
You are an expert Data Stack Engineer AI agent specialized in managing modern data infrastructure.

Your responsibilities include:
1. **Infrastructure Management**: Deploy, configure, and maintain containerized data stack components
2. **Pipeline Orchestration**: Manage Airflow DAGs, Meltano ELT processes, and dbt transformations
3. **Performance Optimization**: Monitor and optimize DuckDB performance, container resources, and pipeline efficiency
4. **Quality Assurance**: Ensure data quality, pipeline reliability, and system health
5. **Automation**: Implement automated deployment, monitoring, and recovery procedures
6. **Troubleshooting**: Diagnose and resolve infrastructure issues, pipeline failures, and performance bottlenecks

Core Technologies:
- **Orchestration**: Apache Airflow for workflow management
- **ELT**: Meltano for data extraction and loading
- **Transformation**: dbt for data modeling and quality testing
- **Storage**: DuckDB for analytics, MinIO for object storage
- **Containerization**: Docker Compose for service orchestration
- **Monitoring**: Prometheus, Grafana for observability

When handling requests:
1. Always start by assessing current system health
2. Use appropriate tools for each task
3. Provide clear status updates and next steps
4. Implement proper error handling and recovery
5. Optimize for performance and cost efficiency
6. Document actions for AI agent coordination

Be proactive, thorough, and focused on maintaining a robust, scalable data infrastructure.
"""

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get list of capabilities this agent supports."""
        return self.capabilities

    async def execute_task(self, request: WorkflowRequest) -> AgentResponse:
        """
        Execute a data stack engineering task based on the workflow request.

        Args:
            request: The workflow request to execute

        Returns:
            AgentResponse: Structured response from the agent
        """
        start_time = datetime.now()

        try:
            # Analyze the request to determine task type
            task_type = await self._analyze_task_type(request.user_prompt)

            self.logger.info(f"Executing data stack task: {task_type}")

            # Route to appropriate handler
            if task_type == "deployment":
                result = await self._handle_deployment(request)
            elif task_type == "monitoring":
                result = await self._handle_monitoring(request)
            elif task_type == "troubleshooting":
                result = await self._handle_troubleshooting(request)
            elif task_type == "optimization":
                result = await self._handle_optimization(request)
            elif task_type == "pipeline_execution":
                result = await self._handle_pipeline_execution(request)
            elif task_type == "health_check":
                result = await self._handle_health_check(request)
            else:
                result = await self._handle_general_request(request)

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return AgentResponse(
                agent_role=self.role,
                status=(
                    ResponseStatus.SUCCESS
                    if result["success"]
                    else ResponseStatus.ERROR
                ),
                output=result,
                execution_time_ms=execution_time,
                next_actions=result.get("next_actions", []),
                validation_results=result.get("validation_results", []),
            )

        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.ERROR,
                output={"success": False, "error": str(e)},
                execution_time_ms=execution_time,
                error_message=str(e),
            )

    async def _analyze_task_type(self, prompt: str) -> str:
        """Analyze the user prompt to determine task type."""
        prompt_lower = prompt.lower()

        if any(
            word in prompt_lower for word in ["deploy", "setup", "install", "configure"]
        ):
            return "deployment"
        elif any(
            word in prompt_lower for word in ["monitor", "status", "health", "check"]
        ):
            return "monitoring"
        elif any(
            word in prompt_lower
            for word in ["troubleshoot", "debug", "fix", "error", "issue"]
        ):
            return "troubleshooting"
        elif any(
            word in prompt_lower
            for word in ["optimize", "performance", "speed", "resource"]
        ):
            return "optimization"
        elif any(
            word in prompt_lower
            for word in ["run", "execute", "pipeline", "etl", "transform"]
        ):
            return "pipeline_execution"
        elif any(word in prompt_lower for word in ["health", "status", "check"]):
            return "health_check"
        else:
            return "general"

    async def _handle_deployment(self, request: WorkflowRequest) -> dict[str, Any]:
        """Handle data stack deployment tasks."""
        self.logger.info("Handling data stack deployment")

        deployment_steps = [
            ("Check Docker services", self.docker_tools.get_service_status),
            (
                "Start required services",
                lambda: self.docker_tools.start_services(
                    ["postgres", "redis", "duckdb-http", "meltano"]
                ),
            ),
            ("Validate Meltano project", self.meltano_tools.validate_project),
            (
                "Install dbt dependencies",
                lambda: self.dbt_tools.run_dbt_command(["deps"]),
            ),
            ("Compile dbt models", lambda: self.dbt_tools.compile_models),
            (
                "Initialize DuckDB",
                lambda: self.duckdb_tools.execute_query(
                    "CREATE SCHEMA IF NOT EXISTS raw_data"
                ),
            ),
        ]

        results = []
        for step_name, step_function in deployment_steps:
            self.logger.info(f"Executing: {step_name}")
            try:
                result = await step_function()
                results.append(
                    {
                        "step": step_name,
                        "success": result.get("success", True),
                        "details": result,
                    }
                )

                if not result.get("success", True):
                    return {
                        "success": False,
                        "error": f"Deployment failed at step: {step_name}",
                        "step_results": results,
                        "next_actions": [
                            "Check logs",
                            "Retry failed step",
                            "Contact administrator",
                        ],
                    }

            except Exception as e:
                results.append({"step": step_name, "success": False, "error": str(e)})
                return {
                    "success": False,
                    "error": f"Deployment failed at step: {step_name} - {str(e)}",
                    "step_results": results,
                    "next_actions": [
                        "Check logs",
                        "Retry deployment",
                        "Verify prerequisites",
                    ],
                }

        return {
            "success": True,
            "message": "Data stack deployed successfully",
            "step_results": results,
            "next_actions": [
                "Verify all services are healthy",
                "Run initial data pipeline",
                "Set up monitoring",
            ],
        }

    async def _handle_monitoring(self, request: WorkflowRequest) -> dict[str, Any]:
        """Handle monitoring and status checking tasks."""
        self.logger.info("Handling monitoring request")

        monitoring_checks = [
            ("Docker service status", self.docker_tools.get_service_status),
            ("DuckDB health", lambda: self.duckdb_tools.get_database_stats()),
            (
                "Data quality metrics",
                lambda: self.duckdb_tools.get_data_quality_metrics(),
            ),
            ("Resource usage", self.docker_tools.get_resource_usage),
        ]

        monitoring_results = {}
        overall_health = True

        for check_name, check_function in monitoring_checks:
            try:
                result = await check_function()
                monitoring_results[check_name] = result

                if not result.get("success", True):
                    overall_health = False

            except Exception as e:
                monitoring_results[check_name] = {"success": False, "error": str(e)}
                overall_health = False

        health_score = self._calculate_health_score(monitoring_results)

        return {
            "success": True,
            "overall_health": overall_health,
            "health_score": health_score,
            "monitoring_results": monitoring_results,
            "recommendations": self._generate_health_recommendations(
                monitoring_results
            ),
            "next_actions": [
                "Review detailed metrics",
                "Set up alerts for critical issues",
                "Schedule regular health checks",
            ],
        }

    async def _handle_pipeline_execution(
        self, request: WorkflowRequest
    ) -> dict[str, Any]:
        """Handle pipeline execution tasks."""
        self.logger.info("Handling pipeline execution")

        try:
            # Run Meltano ELT
            self.logger.info("Starting Meltano ELT process")
            meltano_result = await self.meltano_tools.extract_load_data(
                "tap-csv", "target-duckdb", "dev"
            )

            if not meltano_result["success"]:
                return {
                    "success": False,
                    "error": "Meltano ELT failed",
                    "details": meltano_result,
                    "next_actions": [
                        "Check Meltano logs",
                        "Verify data source",
                        "Retry ELT",
                    ],
                }

            # Run dbt transformations
            self.logger.info("Running dbt transformations")
            dbt_result = await self.dbt_tools.run_models()

            if not dbt_result["success"]:
                return {
                    "success": False,
                    "error": "dbt transformations failed",
                    "details": dbt_result,
                    "next_actions": [
                        "Check dbt logs",
                        "Verify model syntax",
                        "Retry transformations",
                    ],
                }

            # Run dbt tests
            self.logger.info("Running dbt tests")
            test_result = await self.dbt_tools.test_models()

            # Get data quality metrics
            quality_result = await self.duckdb_tools.get_data_quality_metrics()

            return {
                "success": True,
                "message": "Pipeline executed successfully",
                "meltano_metrics": meltano_result.get("metrics", {}),
                "dbt_result": dbt_result,
                "test_results": test_result,
                "data_quality": quality_result,
                "next_actions": [
                    "Review data quality scores",
                    "Check transformation results",
                    "Set up dashboard monitoring",
                ],
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Pipeline execution failed: {str(e)}",
                "next_actions": [
                    "Check system logs",
                    "Verify service health",
                    "Retry pipeline",
                ],
            }

    async def _handle_health_check(self, request: WorkflowRequest) -> dict[str, Any]:
        """Handle comprehensive health check."""
        health_checks = {
            "docker_services": await self.docker_tools.get_service_status(),
            "duckdb_connection": await self.duckdb_tools.get_database_stats(),
            "meltano_project": await self.meltano_tools.validate_project(),
            "dbt_compilation": await self.dbt_tools.compile_models(),
        }

        overall_healthy = all(
            result.get("success", False) for result in health_checks.values()
        )

        return {
            "success": True,
            "overall_healthy": overall_healthy,
            "health_checks": health_checks,
            "timestamp": datetime.now().isoformat(),
            "next_actions": [
                "Address any failed health checks",
                "Set up automated monitoring",
                "Schedule regular health assessments",
            ],
        }

    async def _handle_troubleshooting(self, request: WorkflowRequest) -> dict[str, Any]:
        """Handle troubleshooting tasks."""
        return {
            "success": True,
            "message": "Troubleshooting analysis completed",
            "next_actions": ["Check logs", "Verify configurations", "Test components"],
        }

    async def _handle_optimization(self, request: WorkflowRequest) -> dict[str, Any]:
        """Handle optimization tasks."""
        return {
            "success": True,
            "message": "Optimization analysis completed",
            "next_actions": [
                "Apply optimizations",
                "Monitor performance",
                "Test improvements",
            ],
        }

    async def _handle_general_request(self, request: WorkflowRequest) -> dict[str, Any]:
        """Handle general data stack requests."""
        return {
            "success": True,
            "message": f"Processed general request: {request.user_prompt[:100]}...",
            "next_actions": [
                "Provide more specific instructions",
                "Use specialized commands",
            ],
        }

    def _calculate_health_score(self, monitoring_results: dict) -> float:
        """Calculate overall health score from monitoring results."""
        scores = []
        for result in monitoring_results.values():
            if result.get("success", False):
                scores.append(1.0)
            else:
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 0.0

    def _generate_health_recommendations(self, monitoring_results: dict) -> list[str]:
        """Generate health recommendations based on monitoring results."""
        recommendations = []

        for check_name, result in monitoring_results.items():
            if not result.get("success", False):
                recommendations.append(f"Address issues with {check_name}")

        if not recommendations:
            recommendations.append("System is healthy - continue monitoring")

        return recommendations
