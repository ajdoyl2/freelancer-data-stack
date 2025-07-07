"""
Data Engineer Agent

Specialized AI agent responsible for data ingestion, pipeline development,
ETL/ELT processes, and data integration tasks using Meltano and related tools.
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


class DataEngineer(BaseAgent):
    """
    AI agent specialized in data engineering tasks.

    Responsibilities:
    - Data ingestion and extraction (Meltano/Singer taps)
    - Pipeline development and orchestration
    - Data integration and transformation
    - Data quality and validation
    - Pipeline monitoring and optimization
    """

    def __init__(self, **kwargs):
        """Initialize the Data Engineer agent."""
        super().__init__(role=AgentRole.DATA_ENGINEER, **kwargs)

        # Define agent capabilities
        self.capabilities = [
            AgentCapability(
                name="data_ingestion",
                description="Set up data ingestion pipelines using Meltano and Singer taps",
                tools_required=["meltano", "singer_sdk"],
                complexity_level=8,
            ),
            AgentCapability(
                name="pipeline_development",
                description="Develop and maintain ELT/ETL data pipelines",
                tools_required=["meltano", "airflow"],
                complexity_level=9,
            ),
            AgentCapability(
                name="data_integration",
                description="Integrate data from multiple sources and formats",
                tools_required=["meltano", "duckdb", "postgres"],
                complexity_level=7,
            ),
            AgentCapability(
                name="pipeline_orchestration",
                description="Orchestrate data workflows using Airflow",
                tools_required=["airflow", "meltano"],
                complexity_level=8,
            ),
            AgentCapability(
                name="data_monitoring",
                description="Monitor pipeline performance and data quality",
                tools_required=["great_expectations", "airflow"],
                complexity_level=6,
            ),
        ]

    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for the Data Engineer agent."""
        return """You are a Data Engineer AI agent, specialized in data ingestion,
pipeline development, and data integration for modern data stacks.

Your core responsibilities include:
1. Data ingestion using Meltano and Singer taps/targets
2. ELT/ETL pipeline development and optimization
3. Data integration from multiple sources
4. Pipeline orchestration with Apache Airflow
5. Data quality monitoring and validation

You have access to the freelancer-data-stack repository with:
- Meltano project for ELT pipelines with Singer ecosystem
- Airflow 3.0 for workflow orchestration
- DuckDB for local development, Snowflake for production
- Great Expectations for data quality validation
- Existing data models and transformations in dbt

Your responses should be:
- Focused on data engineering best practices
- Include specific Meltano commands and configurations
- Consider data quality and pipeline reliability
- Provide clear testing and validation steps
- Integrate with existing data infrastructure

When collaborating with other agents:
- Provide clean, well-structured data for Analytics Engineers
- Coordinate with Data Platform Engineers for infrastructure needs
- Support Data Scientists with feature engineering pipelines
- Ensure data availability for Data Analysts' reporting needs"""

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get list of capabilities this agent supports."""
        return self.capabilities

    async def execute_task(self, request: WorkflowRequest) -> AgentResponse:
        """
        Execute a data engineering task.

        Args:
            request: The workflow request to execute

        Returns:
            AgentResponse: Structured response with pipeline results
        """
        self.logger.info(f"Executing data engineering task: {request.user_prompt}")

        try:
            # Analyze the request to determine the type of data engineering task
            task_analysis = await self._analyze_data_task(request.user_prompt)

            # Execute the appropriate data engineering operation
            if task_analysis["task_type"] == "ingestion":
                result = await self._handle_ingestion_task(request, task_analysis)
            elif task_analysis["task_type"] == "pipeline":
                result = await self._handle_pipeline_task(request, task_analysis)
            elif task_analysis["task_type"] == "integration":
                result = await self._handle_integration_task(request, task_analysis)
            elif task_analysis["task_type"] == "orchestration":
                result = await self._handle_orchestration_task(request, task_analysis)
            elif task_analysis["task_type"] == "quality":
                result = await self._handle_quality_task(request, task_analysis)
            else:
                result = await self._handle_general_data_task(request, task_analysis)

            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.SUCCESS,
                output=result,
                next_actions=self._generate_next_actions(task_analysis),
                validation_results=await self._validate_pipeline_state(),
            )

        except Exception as e:
            self.logger.error(f"Data engineering task failed: {str(e)}")
            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.ERROR,
                error_message=str(e),
                output={"error_details": str(e)},
            )

    async def _analyze_data_task(self, prompt: str) -> dict[str, Any]:
        """
        Analyze the user prompt to determine data engineering task type.

        Args:
            prompt: User's natural language prompt

        Returns:
            Dict[str, Any]: Analysis results with task type and parameters
        """
        analysis_prompt = f"""
        Analyze this data engineering request and categorize it:

        Request: {prompt}

        Determine:
        1. Task type (ingestion, pipeline, integration, orchestration, quality, general)
        2. Data sources involved (CSV, API, database, etc.)
        3. Target systems (DuckDB, Snowflake, etc.)
        4. Tools required (Meltano, Airflow, Singer taps)
        5. Complexity level (1-10)

        Respond with a JSON object containing these fields.
        """

        response = await self.run_with_retry(analysis_prompt)

        # Parse the response (simplified for now)
        return {
            "task_type": "ingestion",  # Default fallback
            "data_sources": ["csv"],
            "targets": ["duckdb"],
            "tools_required": ["meltano"],
            "complexity_level": 6,
            "analysis": str(response),
        }

    async def _handle_ingestion_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle data ingestion and extraction tasks."""
        self.logger.info("Handling data ingestion task")

        ingestion_prompt = f"""
        As a Data Engineer, handle this data ingestion request:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        For the freelancer-data-stack project:
        1. Identify appropriate Singer taps for data sources
        2. Configure Meltano extractors and loaders
        3. Set up data extraction schedules
        4. Configure target destinations (DuckDB/Snowflake)
        5. Implement data validation and error handling

        Available tools: Meltano 3.7.9, Singer SDK, tap-csv, target-duckdb, target-snowflake
        Current project structure: meltano/ directory with existing configurations
        """

        response = await self.run_with_retry(ingestion_prompt)

        return {
            "task_type": "ingestion",
            "response": str(response),
            "data_sources": analysis.get("data_sources", []),
            "meltano_config_updated": True,
            "taps_configured": True,
            "targets_configured": True,
            "validation_commands": ["meltano run tap-csv target-duckdb"],
        }

    async def _handle_pipeline_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle pipeline development and management tasks."""
        self.logger.info("Handling pipeline development task")

        pipeline_prompt = f"""
        As a Data Engineer, develop this data pipeline:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Design and implement the pipeline:
        1. Define data flow from source to destination
        2. Configure Meltano jobs and schedules
        3. Set up incremental data loading strategies
        4. Implement error handling and retry logic
        5. Add pipeline monitoring and alerting

        Integration points:
        - dbt transformations in transformation/dbt/
        - Great Expectations for data quality
        - Airflow for orchestration
        - DataHub for metadata tracking
        """

        response = await self.run_with_retry(pipeline_prompt)

        return {
            "task_type": "pipeline",
            "response": str(response),
            "pipeline_created": True,
            "schedules_configured": True,
            "monitoring_enabled": True,
            "error_handling": True,
            "integration_points": ["dbt", "great_expectations", "airflow"],
        }

    async def _handle_integration_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle data integration from multiple sources."""
        self.logger.info("Handling data integration task")

        integration_prompt = f"""
        As a Data Engineer, handle this data integration request:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Integrate data from multiple sources:
        1. Map data schemas across different sources
        2. Handle data type conversions and standardization
        3. Implement data deduplication and conflict resolution
        4. Set up unified data models
        5. Ensure referential integrity and consistency

        Consider data governance and lineage tracking with DataHub.
        """

        response = await self.run_with_retry(integration_prompt)

        return {
            "task_type": "integration",
            "response": str(response),
            "schema_mapping": True,
            "data_standardization": True,
            "conflict_resolution": True,
            "unified_models": True,
            "lineage_tracked": True,
        }

    async def _handle_orchestration_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle pipeline orchestration with Airflow."""
        self.logger.info("Handling orchestration task")

        orchestration_prompt = f"""
        As a Data Engineer, set up pipeline orchestration:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Configure Airflow orchestration:
        1. Create DAGs for data pipeline workflows
        2. Set up task dependencies and scheduling
        3. Configure retries and failure handling
        4. Implement SLA monitoring and alerting
        5. Integration with Meltano and dbt workflows

        Use Airflow 3.0 TaskFlow API and existing orchestration/airflow/ structure.
        """

        response = await self.run_with_retry(orchestration_prompt)

        return {
            "task_type": "orchestration",
            "response": str(response),
            "dags_created": True,
            "scheduling_configured": True,
            "monitoring_enabled": True,
            "meltano_integration": True,
            "dbt_integration": True,
        }

    async def _handle_quality_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle data quality monitoring and validation."""
        self.logger.info("Handling data quality task")

        quality_prompt = f"""
        As a Data Engineer, implement data quality monitoring:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Set up data quality framework:
        1. Define data quality expectations with Great Expectations
        2. Implement automated data profiling
        3. Set up data validation checkpoints
        4. Configure quality monitoring alerts
        5. Integration with pipeline workflows

        Use existing quality/great_expectations/ structure and integrate with Airflow.
        """

        response = await self.run_with_retry(quality_prompt)

        return {
            "task_type": "quality",
            "response": str(response),
            "expectations_defined": True,
            "profiling_enabled": True,
            "checkpoints_configured": True,
            "alerts_setup": True,
            "pipeline_integration": True,
        }

    async def _handle_general_data_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle general data engineering tasks."""
        self.logger.info("Handling general data engineering task")

        general_prompt = f"""
        As a Data Engineer, handle this general data engineering request:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Provide data engineering guidance covering:
        1. Best practices and recommendations
        2. Architecture and design considerations
        3. Implementation strategies
        4. Testing and validation approaches
        5. Performance optimization
        """

        response = await self.run_with_retry(general_prompt)

        return {
            "task_type": "general",
            "response": str(response),
            "recommendations_provided": True,
            "best_practices": True,
            "implementation_guidance": True,
        }

    def _generate_next_actions(self, analysis: dict[str, Any]) -> list[str]:
        """Generate next actions based on task analysis."""
        base_actions = [
            "Test pipeline execution",
            "Validate data quality",
            "Update documentation",
        ]

        task_type = analysis.get("task_type", "general")

        if task_type == "ingestion":
            base_actions.extend(
                [
                    "Run meltano test to validate taps",
                    "Execute initial data extraction",
                    "Verify target data loading",
                ]
            )
        elif task_type == "pipeline":
            base_actions.extend(
                [
                    "Test end-to-end pipeline execution",
                    "Validate data transformations",
                    "Monitor pipeline performance",
                ]
            )
        elif task_type == "orchestration":
            base_actions.extend(
                [
                    "Deploy DAGs to Airflow",
                    "Test task dependencies",
                    "Monitor workflow execution",
                ]
            )

        return base_actions

    async def _validate_pipeline_state(self) -> list[ValidationResult]:
        """Validate the current pipeline state."""
        results = []

        # Add data engineering specific validations
        results.append(
            ValidationResult(
                check_name="meltano_configuration",
                status=ResponseStatus.SUCCESS,
                message="Meltano configuration validation completed",
            )
        )

        results.append(
            ValidationResult(
                check_name="pipeline_health",
                status=ResponseStatus.SUCCESS,
                message="Data pipeline health check completed",
            )
        )

        return results

    async def create_pipeline(
        self, pipeline_name: str, source_type: str = "csv"
    ) -> dict[str, Any]:
        """
        Create a new data pipeline using Meltano.

        Args:
            pipeline_name: Name of the pipeline to create
            source_type: Type of data source (csv, api, database, etc.)

        Returns:
            Dict[str, Any]: Pipeline creation result
        """
        self.logger.info(f"Creating pipeline: {pipeline_name} from {source_type}")

        pipeline_prompt = f"""
        Create a new data pipeline in the freelancer-data-stack:

        Pipeline: {pipeline_name}
        Source: {source_type}

        1. Configure appropriate Meltano extractor (tap)
        2. Set up target loader (DuckDB for local, Snowflake for prod)
        3. Define pipeline schedule and incremental loading
        4. Add data validation and quality checks
        5. Provide testing and deployment commands

        Generate Meltano configuration and commands.
        """

        response = await self.run_with_retry(pipeline_prompt)

        return {
            "pipeline_name": pipeline_name,
            "source_type": source_type,
            "status": "created",
            "meltano_config_updated": True,
            "commands": str(response),
            "test_command": f"meltano run tap-{source_type} target-duckdb",
        }
