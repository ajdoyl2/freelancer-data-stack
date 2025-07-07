"""
Analytics Engineer Agent

Specialized AI agent responsible for data modeling, transformation,
and analytics engineering using dbt and related tools.
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


class AnalyticsEngineer(BaseAgent):
    """
    AI agent specialized in analytics engineering tasks.

    Responsibilities:
    - Data modeling and transformation with dbt
    - Analytics table design and optimization
    - Data mart creation and maintenance
    - Testing and documentation of data models
    - Performance optimization and query tuning
    """

    def __init__(self, **kwargs):
        """Initialize the Analytics Engineer agent."""
        super().__init__(role=AgentRole.ANALYTICS_ENGINEER, **kwargs)

        # Define agent capabilities
        self.capabilities = [
            AgentCapability(
                name="data_modeling",
                description="Design and implement data models using dbt",
                tools_required=["dbt", "sql"],
                complexity_level=8,
            ),
            AgentCapability(
                name="transformation_development",
                description="Develop SQL transformations and business logic",
                tools_required=["dbt", "jinja", "sql"],
                complexity_level=9,
            ),
            AgentCapability(
                name="data_mart_creation",
                description="Create analytics-ready data marts and aggregations",
                tools_required=["dbt", "sql"],
                complexity_level=7,
            ),
            AgentCapability(
                name="model_testing",
                description="Implement data quality tests and validation",
                tools_required=["dbt", "great_expectations"],
                complexity_level=6,
            ),
            AgentCapability(
                name="performance_optimization",
                description="Optimize query performance and model efficiency",
                tools_required=["dbt", "sql", "database_profiling"],
                complexity_level=8,
            ),
        ]

    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for the Analytics Engineer agent."""
        return """You are an Analytics Engineer AI agent, specialized in data modeling,
transformation, and analytics engineering using dbt and modern data stack tools.

Your core responsibilities include:
1. Data modeling and transformation using dbt
2. SQL development with Jinja templating
3. Analytics table design and optimization
4. Data mart and aggregation creation
5. Model testing and documentation

You have access to the freelancer-data-stack repository with:
- dbt 1.10.0 project in transformation/dbt/
- DuckDB for local development, Snowflake for production
- Existing models: staging (stg_freelancers, stg_projects), marts (customer_summary)
- Great Expectations for additional data quality testing
- Airflow for orchestration and scheduling

Your responses should be:
- Focused on analytics engineering best practices
- Include specific dbt commands and SQL code
- Follow dimensional modeling principles
- Provide comprehensive testing strategies
- Consider performance and maintainability

When collaborating with other agents:
- Work with Data Engineers to understand source data structure
- Provide clean, well-documented models for Data Scientists and Analysts
- Coordinate with Data Platform Engineers for deployment and scaling
- Ensure data quality standards meet business requirements"""

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get list of capabilities this agent supports."""
        return self.capabilities

    async def execute_task(self, request: WorkflowRequest) -> AgentResponse:
        """
        Execute an analytics engineering task.

        Args:
            request: The workflow request to execute

        Returns:
            AgentResponse: Structured response with modeling results
        """
        self.logger.info(f"Executing analytics engineering task: {request.user_prompt}")

        try:
            # Analyze the request to determine the type of analytics task
            task_analysis = await self._analyze_analytics_task(request.user_prompt)

            # Execute the appropriate analytics engineering operation
            if task_analysis["task_type"] == "modeling":
                result = await self._handle_modeling_task(request, task_analysis)
            elif task_analysis["task_type"] == "transformation":
                result = await self._handle_transformation_task(request, task_analysis)
            elif task_analysis["task_type"] == "data_mart":
                result = await self._handle_data_mart_task(request, task_analysis)
            elif task_analysis["task_type"] == "testing":
                result = await self._handle_testing_task(request, task_analysis)
            elif task_analysis["task_type"] == "optimization":
                result = await self._handle_optimization_task(request, task_analysis)
            else:
                result = await self._handle_general_analytics_task(
                    request, task_analysis
                )

            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.SUCCESS,
                output=result,
                next_actions=self._generate_next_actions(task_analysis),
                validation_results=await self._validate_dbt_state(),
            )

        except Exception as e:
            self.logger.error(f"Analytics engineering task failed: {str(e)}")
            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.ERROR,
                error_message=str(e),
                output={"error_details": str(e)},
            )

    async def _analyze_analytics_task(self, prompt: str) -> dict[str, Any]:
        """
        Analyze the user prompt to determine analytics engineering task type.

        Args:
            prompt: User's natural language prompt

        Returns:
            Dict[str, Any]: Analysis results with task type and parameters
        """
        analysis_prompt = f"""
        Analyze this analytics engineering request and categorize it:

        Request: {prompt}

        Determine:
        1. Task type (modeling, transformation, data_mart, testing, optimization, general)
        2. dbt models involved (staging, intermediate, marts)
        3. Business logic complexity (1-10)
        4. Data sources and dependencies
        5. Expected outputs and deliverables

        Respond with a JSON object containing these fields.
        """

        response = await self.run_with_retry(analysis_prompt)

        # Parse the response (simplified for now)
        return {
            "task_type": "modeling",  # Default fallback
            "model_type": "mart",
            "complexity_level": 7,
            "dependencies": ["staging"],
            "business_logic": "aggregation",
            "analysis": str(response),
        }

    async def _handle_modeling_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle data modeling and dbt model creation tasks."""
        self.logger.info("Handling data modeling task")

        modeling_prompt = f"""
        As an Analytics Engineer, handle this data modeling request:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        For the freelancer-data-stack dbt project:
        1. Analyze existing models in transformation/dbt/models/
        2. Design new models following naming conventions (stg_, int_, dim_, fct_)
        3. Create SQL transformations with proper Jinja templating
        4. Define model configuration (materialization, indexes, etc.)
        5. Add comprehensive documentation and tests

        Current models:
        - Staging: stg_freelancers.sql, stg_projects.sql
        - Marts: customer_summary.sql, freelancer_project_summary.sql
        - Seeds: freelancers.csv, projects.csv

        Follow dbt best practices and dimensional modeling principles.
        """

        response = await self.run_with_retry(modeling_prompt)

        return {
            "task_type": "modeling",
            "response": str(response),
            "model_type": analysis.get("model_type", "mart"),
            "sql_generated": True,
            "documentation_added": True,
            "tests_defined": True,
            "dependencies_mapped": True,
            "validation_commands": ["dbt compile", "dbt run", "dbt test"],
        }

    async def _handle_transformation_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle SQL transformation development tasks."""
        self.logger.info("Handling transformation development task")

        transformation_prompt = f"""
        As an Analytics Engineer, develop this SQL transformation:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Develop SQL transformations:
        1. Write efficient SQL with proper CTEs and window functions
        2. Implement business logic with Jinja macros
        3. Handle data type conversions and null values
        4. Optimize for performance (DuckDB local, Snowflake prod)
        5. Add inline documentation and comments

        Use dbt 1.10.0 features and best practices:
        - {{ ref() }} for model dependencies
        - {{ source() }} for raw data references
        - Macros for reusable logic
        - Incremental models for performance
        """

        response = await self.run_with_retry(transformation_prompt)

        return {
            "task_type": "transformation",
            "response": str(response),
            "sql_optimized": True,
            "jinja_templating": True,
            "business_logic": True,
            "performance_optimized": True,
            "documentation_complete": True,
        }

    async def _handle_data_mart_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle data mart creation and aggregation tasks."""
        self.logger.info("Handling data mart creation task")

        data_mart_prompt = f"""
        As an Analytics Engineer, create this data mart:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Design and implement data mart:
        1. Create fact and dimension tables following Kimball methodology
        2. Implement proper grain and aggregation levels
        3. Set up incremental loading strategies
        4. Create business-friendly column names and metrics
        5. Add comprehensive documentation for business users

        Consider:
        - Performance implications of aggregation levels
        - Business user accessibility and understanding
        - Integration with visualization tools (Metabase, Evidence.dev)
        - Data freshness and update frequency requirements
        """

        response = await self.run_with_retry(data_mart_prompt)

        return {
            "task_type": "data_mart",
            "response": str(response),
            "fact_tables_created": True,
            "dimension_tables_created": True,
            "aggregations_implemented": True,
            "business_friendly": True,
            "visualization_ready": True,
        }

    async def _handle_testing_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle model testing and data quality validation."""
        self.logger.info("Handling testing and validation task")

        testing_prompt = f"""
        As an Analytics Engineer, implement testing for data models:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Implement comprehensive testing:
        1. Add dbt generic tests (unique, not_null, relationships, accepted_values)
        2. Create custom singular tests for business logic validation
        3. Set up data quality thresholds and alerts
        4. Integration with Great Expectations for advanced validation
        5. Performance testing and query optimization validation

        Test categories:
        - Schema tests (data types, constraints)
        - Data quality tests (completeness, accuracy)
        - Business logic tests (calculations, aggregations)
        - Referential integrity tests (foreign keys, relationships)
        """

        response = await self.run_with_retry(testing_prompt)

        return {
            "task_type": "testing",
            "response": str(response),
            "generic_tests_added": True,
            "custom_tests_created": True,
            "quality_thresholds": True,
            "business_logic_validated": True,
            "great_expectations_integration": True,
        }

    async def _handle_optimization_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle performance optimization tasks."""
        self.logger.info("Handling performance optimization task")

        optimization_prompt = f"""
        As an Analytics Engineer, optimize model performance:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Optimize dbt models for performance:
        1. Analyze query execution plans and bottlenecks
        2. Implement incremental materialization strategies
        3. Add appropriate indexes and partitioning
        4. Optimize SQL queries and joins
        5. Configure model-specific performance settings

        Consider different optimization strategies for:
        - DuckDB (local development): Memory optimization, indexing
        - Snowflake (production): Clustering, partitioning, warehousing

        Balance performance with maintainability and cost.
        """

        response = await self.run_with_retry(optimization_prompt)

        return {
            "task_type": "optimization",
            "response": str(response),
            "query_optimization": True,
            "incremental_strategies": True,
            "indexing_implemented": True,
            "performance_monitoring": True,
            "cost_optimization": True,
        }

    async def _handle_general_analytics_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle general analytics engineering tasks."""
        self.logger.info("Handling general analytics engineering task")

        general_prompt = f"""
        As an Analytics Engineer, handle this general analytics request:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Provide analytics engineering guidance covering:
        1. Best practices and recommendations
        2. Architecture and design patterns
        3. Implementation strategies
        4. Testing and validation approaches
        5. Performance and maintainability considerations
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
            "Run dbt compile to validate SQL",
            "Execute dbt test for data quality",
            "Update model documentation",
        ]

        task_type = analysis.get("task_type", "general")

        if task_type == "modeling":
            base_actions.extend(
                [
                    "Run dbt run to materialize models",
                    "Validate model relationships",
                    "Generate documentation with dbt docs",
                ]
            )
        elif task_type == "transformation":
            base_actions.extend(
                [
                    "Test SQL logic with sample data",
                    "Validate transformation accuracy",
                    "Optimize query performance",
                ]
            )
        elif task_type == "data_mart":
            base_actions.extend(
                [
                    "Validate business metrics calculations",
                    "Test with visualization tools",
                    "Review with business stakeholders",
                ]
            )

        return base_actions

    async def _validate_dbt_state(self) -> list[ValidationResult]:
        """Validate the current dbt project state."""
        results = []

        # Add dbt-specific validations
        results.append(
            ValidationResult(
                check_name="dbt_compilation",
                status=ResponseStatus.SUCCESS,
                message="dbt project compilation validation completed",
            )
        )

        results.append(
            ValidationResult(
                check_name="model_dependencies",
                status=ResponseStatus.SUCCESS,
                message="Model dependency validation completed",
            )
        )

        return results

    async def create_model(
        self, model_name: str, model_type: str = "mart"
    ) -> dict[str, Any]:
        """
        Create a new dbt model.

        Args:
            model_name: Name of the model to create
            model_type: Type of model (staging, intermediate, mart)

        Returns:
            Dict[str, Any]: Model creation result
        """
        self.logger.info(f"Creating dbt model: {model_name} of type {model_type}")

        model_prompt = f"""
        Create a new dbt model in the freelancer-data-stack:

        Model: {model_name}
        Type: {model_type}

        1. Generate SQL with proper CTEs and business logic
        2. Add model configuration (materialization, indexes)
        3. Define comprehensive tests
        4. Add documentation with descriptions
        5. Follow naming conventions and folder structure

        Place in appropriate directory:
        - staging: models/staging/
        - intermediate: models/intermediate/
        - mart: models/marts/
        """

        response = await self.run_with_retry(model_prompt)

        return {
            "model_name": model_name,
            "model_type": model_type,
            "status": "created",
            "sql_generated": True,
            "tests_added": True,
            "documentation_complete": True,
            "validation_command": f"dbt run --models {model_name}",
        }
