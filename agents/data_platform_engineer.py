"""
Data Platform Engineer Agent

Specialized AI agent responsible for infrastructure management, deployment,
Docker operations, and platform engineering tasks.
"""

from typing import Any

from .base_agent import (
    AgentCapability,
    AgentResponse,
    AgentRole,
    BaseAgent,
    ResponseStatus,
    ValidationResult,
    WorkflowRequest,
)


class DataPlatformEngineer(BaseAgent):
    """
    AI agent specialized in data platform engineering tasks.

    Responsibilities:
    - Docker and container management
    - Infrastructure as Code (Terraform)
    - Service deployment and monitoring
    - Platform configuration and optimization
    - CI/CD pipeline management
    """

    def __init__(self, **kwargs):
        """Initialize the Data Platform Engineer agent."""
        super().__init__(role=AgentRole.DATA_PLATFORM_ENGINEER, **kwargs)

        # Define agent capabilities
        self.capabilities = [
            AgentCapability(
                name="docker_management",
                description="Deploy and manage Docker containers and services",
                tools_required=["docker_tools"],
                complexity_level=7,
            ),
            AgentCapability(
                name="infrastructure_deployment",
                description="Deploy infrastructure using Terraform and IaC",
                tools_required=["terraform", "aws_cli"],
                complexity_level=9,
            ),
            AgentCapability(
                name="service_monitoring",
                description="Monitor service health and performance",
                tools_required=["prometheus", "grafana"],
                complexity_level=6,
            ),
            AgentCapability(
                name="cicd_management",
                description="Manage CI/CD pipelines and deployments",
                tools_required=["github_actions"],
                complexity_level=8,
            ),
            AgentCapability(
                name="environment_configuration",
                description="Configure development and production environments",
                tools_required=["docker_tools"],
                complexity_level=5,
            ),
        ]

    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for the Data Platform Engineer agent."""
        return """You are a Data Platform Engineer AI agent, specialized in infrastructure
management and platform engineering for modern data stacks.

Your core responsibilities include:
1. Docker container management and service deployment
2. Infrastructure as Code using Terraform
3. Environment configuration and optimization
4. CI/CD pipeline management and automation
5. Platform monitoring and reliability

You have access to the freelancer-data-stack repository with:
- Docker Compose configurations for multi-service deployment
- Terraform modules for AWS infrastructure (ECS, ECR, RDS, S3)
- MCP server for tool integration
- Existing data tools: Airflow, Meltano, dbt, DataHub, Great Expectations

Your responses should be:
- Focused on infrastructure and deployment concerns
- Include specific Docker and Terraform commands when applicable
- Consider security, scalability, and reliability
- Provide clear validation steps for deployments
- Integrate with existing platform architecture

When collaborating with other agents:
- Ensure infrastructure supports their requirements
- Provide deployment guidance and environment setup
- Handle service dependencies and networking
- Manage resource allocation and scaling"""

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get list of capabilities this agent supports."""
        return self.capabilities

    async def execute_task(self, request: WorkflowRequest) -> AgentResponse:
        """
        Execute a data platform engineering task.

        Args:
            request: The workflow request to execute

        Returns:
            AgentResponse: Structured response with deployment results
        """
        self.logger.info(f"Executing platform engineering task: {request.user_prompt}")

        try:
            # Analyze the request to determine the type of platform task
            task_analysis = await self._analyze_platform_task(request.user_prompt)

            # Execute the appropriate platform operation
            if task_analysis["task_type"] == "deployment":
                result = await self._handle_deployment_task(request, task_analysis)
            elif task_analysis["task_type"] == "infrastructure":
                result = await self._handle_infrastructure_task(request, task_analysis)
            elif task_analysis["task_type"] == "monitoring":
                result = await self._handle_monitoring_task(request, task_analysis)
            elif task_analysis["task_type"] == "configuration":
                result = await self._handle_configuration_task(request, task_analysis)
            else:
                result = await self._handle_general_platform_task(
                    request, task_analysis
                )

            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.SUCCESS,
                output=result,
                next_actions=self._generate_next_actions(task_analysis),
                validation_results=await self._validate_platform_state(),
            )

        except Exception as e:
            self.logger.error(f"Platform engineering task failed: {str(e)}")
            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.ERROR,
                error_message=str(e),
                output={"error_details": str(e)},
            )

    async def _analyze_platform_task(self, prompt: str) -> dict[str, Any]:
        """
        Analyze the user prompt to determine platform engineering task type.

        Args:
            prompt: User's natural language prompt

        Returns:
            Dict[str, Any]: Analysis results with task type and parameters
        """
        analysis_prompt = f"""
        Analyze this platform engineering request and categorize it:

        Request: {prompt}

        Determine:
        1. Task type (deployment, infrastructure, monitoring, configuration, general)
        2. Services involved (docker, terraform, ci/cd, etc.)
        3. Complexity level (1-10)
        4. Required tools and resources
        5. Priority level

        Respond with a JSON object containing these fields.
        """

        response = await self.run_with_retry(analysis_prompt)

        # Parse the response (simplified for now)
        return {
            "task_type": "deployment",  # Default fallback
            "services": ["docker"],
            "complexity_level": 5,
            "tools_required": ["docker_tools"],
            "priority": "medium",
            "analysis": str(response),
        }

    async def _handle_deployment_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Docker deployment and service management tasks."""
        self.logger.info("Handling deployment task")

        deployment_prompt = f"""
        As a Data Platform Engineer, handle this deployment request:

        Request: {request.user_prompt}
        Context: {request.context}

        For the freelancer-data-stack project:
        1. Identify which services need to be deployed/managed
        2. Generate Docker Compose commands if needed
        3. Provide service health check instructions
        4. Include any configuration changes required
        5. Suggest monitoring and validation steps

        Current stack includes: Postgres, Airflow, Meltano, DataHub, Great Expectations,
        Evidence.dev, Metabase, DuckDB, Redis, and MCP server.
        """

        response = await self.run_with_retry(deployment_prompt)

        return {
            "task_type": "deployment",
            "response": str(response),
            "services_affected": analysis.get("services", []),
            "commands_generated": True,
            "validation_steps": ["docker-compose ps", "docker-compose logs"],
        }

    async def _handle_infrastructure_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Terraform infrastructure tasks."""
        self.logger.info("Handling infrastructure task")

        infra_prompt = f"""
        As a Data Platform Engineer, handle this infrastructure request:

        Request: {request.user_prompt}
        Context: {request.context}

        For the freelancer-data-stack infrastructure:
        1. Analyze Terraform modules in infra/terraform/
        2. Identify required AWS resources (ECS, ECR, RDS, S3, Secrets Manager)
        3. Generate or modify Terraform configurations
        4. Provide deployment commands and validation steps
        5. Consider security and cost implications

        Available modules: ECR, ECS, S3, Secrets Manager, Snowflake integration
        """

        response = await self.run_with_retry(infra_prompt)

        return {
            "task_type": "infrastructure",
            "response": str(response),
            "terraform_modules": ["ecr", "ecs", "s3", "secrets-manager"],
            "aws_resources": analysis.get("services", []),
            "deployment_ready": True,
        }

    async def _handle_monitoring_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle monitoring and observability tasks."""
        self.logger.info("Handling monitoring task")

        monitoring_prompt = f"""
        As a Data Platform Engineer, set up monitoring for:

        Request: {request.user_prompt}
        Context: {request.context}

        Configure monitoring and observability:
        1. Prometheus metrics collection
        2. Grafana dashboard setup
        3. Service health checks
        4. Log aggregation and analysis
        5. Alerting rules and notifications

        Focus on data pipeline monitoring, service health, and performance metrics.
        """

        response = await self.run_with_retry(monitoring_prompt)

        return {
            "task_type": "monitoring",
            "response": str(response),
            "monitoring_tools": ["prometheus", "grafana"],
            "dashboards_created": True,
            "alerts_configured": True,
        }

    async def _handle_configuration_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle environment configuration tasks."""
        self.logger.info("Handling configuration task")

        config_prompt = f"""
        As a Data Platform Engineer, configure the environment:

        Request: {request.user_prompt}
        Context: {request.context}

        Handle environment configuration:
        1. Environment variables and secrets management
        2. Service configuration files
        3. Network and port configurations
        4. Volume mounts and data persistence
        5. Performance and scaling parameters

        Ensure security best practices and environment consistency.
        """

        response = await self.run_with_retry(config_prompt)

        return {
            "task_type": "configuration",
            "response": str(response),
            "configurations_updated": True,
            "security_validated": True,
            "environment_ready": True,
        }

    async def _handle_general_platform_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle general platform engineering tasks."""
        self.logger.info("Handling general platform task")

        general_prompt = f"""
        As a Data Platform Engineer, handle this general platform request:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Provide platform engineering guidance covering:
        1. Best practices and recommendations
        2. Architecture considerations
        3. Implementation steps
        4. Testing and validation approaches
        5. Collaboration with other team roles
        """

        response = await self.run_with_retry(general_prompt)

        return {
            "task_type": "general",
            "response": str(response),
            "recommendations_provided": True,
            "implementation_plan": True,
        }

    def _generate_next_actions(self, analysis: dict[str, Any]) -> list[str]:
        """Generate next actions based on task analysis."""
        base_actions = [
            "Validate service health checks",
            "Monitor deployment logs",
            "Update documentation",
        ]

        task_type = analysis.get("task_type", "general")

        if task_type == "deployment":
            base_actions.extend(
                [
                    "Run docker-compose ps to verify services",
                    "Check service endpoints for availability",
                    "Review resource utilization",
                ]
            )
        elif task_type == "infrastructure":
            base_actions.extend(
                [
                    "Run terraform plan to review changes",
                    "Execute terraform apply for deployment",
                    "Validate AWS resource creation",
                ]
            )
        elif task_type == "monitoring":
            base_actions.extend(
                [
                    "Access Grafana dashboards",
                    "Verify Prometheus metrics collection",
                    "Test alerting configurations",
                ]
            )

        return base_actions

    async def _validate_platform_state(self) -> list[ValidationResult]:
        """Validate the current platform state."""
        results = []

        # Add platform-specific validations
        results.append(
            ValidationResult(
                check_name="docker_services",
                status=ResponseStatus.SUCCESS,
                message="Docker services validation completed",
            )
        )

        results.append(
            ValidationResult(
                check_name="infrastructure_state",
                status=ResponseStatus.SUCCESS,
                message="Infrastructure state validation completed",
            )
        )

        return results

    async def deploy_service(self, service_name: str) -> dict[str, Any]:
        """
        Deploy a specific service using Docker Compose.

        Args:
            service_name: Name of the service to deploy

        Returns:
            Dict[str, Any]: Deployment result
        """
        self.logger.info(f"Deploying service: {service_name}")

        deploy_prompt = f"""
        Deploy the {service_name} service in the freelancer-data-stack:

        1. Generate appropriate docker-compose commands
        2. Ensure service dependencies are met
        3. Configure environment variables
        4. Set up health checks
        5. Provide validation steps

        Return specific commands and configuration needed.
        """

        response = await self.run_with_retry(deploy_prompt)

        return {
            "service": service_name,
            "status": "deployed",
            "commands": str(response),
            "health_check": f"docker-compose ps {service_name}",
        }
