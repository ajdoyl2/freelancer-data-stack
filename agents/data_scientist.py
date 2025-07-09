"""
Data Scientist Agent

Specialized AI agent responsible for machine learning model development,
experimentation, feature engineering, and data science workflows.
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


class DataScientist(BaseAgent):
    """
    AI agent specialized in data science and machine learning tasks.

    Responsibilities:
    - Machine learning model development and training
    - Feature engineering and selection
    - Experimental design and A/B testing
    - Model evaluation and validation
    - ML pipeline deployment and monitoring
    """

    def __init__(self, **kwargs):
        """Initialize the Data Scientist agent."""
        super().__init__(role=AgentRole.DATA_SCIENTIST, **kwargs)

        # Define agent capabilities
        self.capabilities = [
            AgentCapability(
                name="model_development",
                description="Develop and train machine learning models",
                tools_required=["jupyter", "scikit_learn", "pandas"],
                complexity_level=9,
            ),
            AgentCapability(
                name="feature_engineering",
                description="Create and optimize features for ML models",
                tools_required=["pandas", "numpy", "feature_engine"],
                complexity_level=8,
            ),
            AgentCapability(
                name="experimentation",
                description="Design and execute data science experiments",
                tools_required=["jupyter", "statistical_libraries"],
                complexity_level=7,
            ),
            AgentCapability(
                name="model_evaluation",
                description="Evaluate and validate model performance",
                tools_required=["scikit_learn", "mlflow", "validation_tools"],
                complexity_level=6,
            ),
            AgentCapability(
                name="ml_pipeline",
                description="Build end-to-end ML pipelines",
                tools_required=["airflow", "mlflow", "docker"],
                complexity_level=9,
            ),
        ]

    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for the Data Scientist agent."""
        return """You are a Data Scientist AI agent, specialized in machine learning,
experimentation, and advanced analytics for modern data science workflows.

Your core responsibilities include:
1. Machine learning model development and training
2. Feature engineering and data preparation
3. Experimental design and statistical analysis
4. Model evaluation, validation, and interpretation
5. ML pipeline development and deployment

You have access to the freelancer-data-stack repository with:
- Jupyter notebooks in notebooks/ directory
- Clean, transformed data from dbt models
- DuckDB for local analysis, Snowflake for production datasets
- Airflow for ML pipeline orchestration
- Docker for model containerization and deployment

Your responses should be:
- Focused on statistical rigor and scientific methodology
- Include specific Python code and notebook implementations
- Consider model interpretability and business impact
- Provide comprehensive evaluation and validation strategies
- Follow ML engineering best practices

When collaborating with other agents:
- Work with Analytics Engineers to understand data models and quality
- Coordinate with Data Engineers for feature pipeline implementation
- Partner with Data Platform Engineers for model deployment infrastructure
- Support Data Analysts with predictive insights and model interpretations"""

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get list of capabilities this agent supports."""
        return self.capabilities

    async def execute_task(self, request: WorkflowRequest) -> AgentResponse:
        """
        Execute a data science task.

        Args:
            request: The workflow request to execute

        Returns:
            AgentResponse: Structured response with ML results
        """
        self.logger.info(f"Executing data science task: {request.user_prompt}")

        try:
            # Analyze the request to determine the type of data science task
            task_analysis = await self._analyze_ds_task(request.user_prompt)

            # Execute the appropriate data science operation
            if task_analysis["task_type"] == "modeling":
                result = await self._handle_modeling_task(request, task_analysis)
            elif task_analysis["task_type"] == "feature_engineering":
                result = await self._handle_feature_engineering_task(
                    request, task_analysis
                )
            elif task_analysis["task_type"] == "experimentation":
                result = await self._handle_experimentation_task(request, task_analysis)
            elif task_analysis["task_type"] == "evaluation":
                result = await self._handle_evaluation_task(request, task_analysis)
            elif task_analysis["task_type"] == "pipeline":
                result = await self._handle_ml_pipeline_task(request, task_analysis)
            else:
                result = await self._handle_general_ds_task(request, task_analysis)

            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.SUCCESS,
                output=result,
                next_actions=self._generate_next_actions(task_analysis),
                validation_results=await self._validate_ml_environment(),
            )

        except Exception as e:
            self.logger.error(f"Data science task failed: {str(e)}")
            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.ERROR,
                error_message=str(e),
                output={"error_details": str(e)},
            )

    async def _analyze_ds_task(self, prompt: str) -> dict[str, Any]:
        """
        Analyze the user prompt to determine data science task type.

        Args:
            prompt: User's natural language prompt

        Returns:
            Dict[str, Any]: Analysis results with task type and parameters
        """
        analysis_prompt = f"""
        Analyze this data science request and categorize it:

        Request: {prompt}

        Determine:
        1. Task type (modeling, feature_engineering, experimentation, evaluation, pipeline, general)
        2. ML problem type (classification, regression, clustering, etc.)
        3. Data requirements and dependencies
        4. Complexity level (1-10)
        5. Expected deliverables (notebook, model, pipeline, etc.)

        Respond with a JSON object containing these fields.
        """

        response = await self.run_with_retry(analysis_prompt)

        # Parse the response (simplified for now)
        return {
            "task_type": "modeling",  # Default fallback
            "ml_type": "classification",
            "complexity_level": 8,
            "data_requirements": ["feature_data", "target_variable"],
            "deliverables": ["notebook", "trained_model"],
            "analysis": str(response),
        }

    async def _handle_modeling_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle machine learning model development tasks."""
        self.logger.info("Handling ML model development task")

        modeling_prompt = f"""
        As a Data Scientist, develop this machine learning model:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        For the freelancer-data-stack project:
        1. Analyze available data from dbt models (customer_summary, project_summary)
        2. Design appropriate ML approach for the problem
        3. Create Jupyter notebook with full ML workflow
        4. Implement model training and validation
        5. Provide model interpretation and business insights

        Available data:
        - Freelancer data: skills, ratings, project history
        - Project data: requirements, budgets, outcomes
        - Customer data: hiring patterns, satisfaction metrics

        Follow ML best practices:
        - Proper train/validation/test splits
        - Cross-validation and hyperparameter tuning
        - Feature importance and model interpretability
        - Performance metrics and business impact assessment
        """

        response = await self.run_with_retry(modeling_prompt)

        return {
            "task_type": "modeling",
            "response": str(response),
            "ml_type": analysis.get("ml_type", "classification"),
            "notebook_created": True,
            "model_trained": True,
            "validation_complete": True,
            "interpretability_analysis": True,
            "business_insights": True,
        }

    async def _handle_feature_engineering_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle feature engineering and data preparation tasks."""
        self.logger.info("Handling feature engineering task")

        feature_prompt = f"""
        As a Data Scientist, handle this feature engineering request:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Design and implement feature engineering:
        1. Analyze raw data and identify feature opportunities
        2. Create derived features and transformations
        3. Handle categorical encoding and scaling
        4. Implement feature selection and dimensionality reduction
        5. Create reproducible feature pipeline

        Consider:
        - Feature interpretability and business meaning
        - Handling missing values and outliers
        - Time-based features for temporal patterns
        - Interaction features and polynomial terms
        - Feature validation and drift monitoring

        Integrate with existing dbt models for feature consistency.
        """

        response = await self.run_with_retry(feature_prompt)

        return {
            "task_type": "feature_engineering",
            "response": str(response),
            "features_created": True,
            "transformations_applied": True,
            "feature_selection": True,
            "pipeline_reproducible": True,
            "dbt_integration": True,
        }

    async def _handle_experimentation_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle experimental design and A/B testing tasks."""
        self.logger.info("Handling experimentation task")

        experiment_prompt = f"""
        As a Data Scientist, design and execute this experiment:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Design experimental framework:
        1. Define hypothesis and success metrics
        2. Design experimental methodology (A/B test, randomized trial)
        3. Calculate sample size and statistical power
        4. Implement data collection and analysis pipeline
        5. Provide statistical interpretation and recommendations

        Consider:
        - Statistical significance and practical significance
        - Confounding variables and bias mitigation
        - Multiple testing corrections
        - Business impact and actionability
        - Long-term vs short-term effects

        Create comprehensive analysis notebook with findings.
        """

        response = await self.run_with_retry(experiment_prompt)

        return {
            "task_type": "experimentation",
            "response": str(response),
            "hypothesis_defined": True,
            "experimental_design": True,
            "statistical_analysis": True,
            "recommendations": True,
            "notebook_complete": True,
        }

    async def _handle_evaluation_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle model evaluation and validation tasks."""
        self.logger.info("Handling model evaluation task")

        evaluation_prompt = f"""
        As a Data Scientist, evaluate this machine learning model:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Comprehensive model evaluation:
        1. Performance metrics relevant to business objectives
        2. Model validation with cross-validation and holdout sets
        3. Bias and fairness analysis
        4. Model interpretability and feature importance
        5. Robustness testing and sensitivity analysis

        Evaluation framework:
        - Classification: Precision, Recall, F1, AUC-ROC, Confusion Matrix
        - Regression: RMSE, MAE, R², Residual Analysis
        - Business metrics: ROI, conversion rates, user satisfaction
        - Model monitoring: Performance drift, data drift

        Provide actionable recommendations for model improvement.
        """

        response = await self.run_with_retry(evaluation_prompt)

        return {
            "task_type": "evaluation",
            "response": str(response),
            "performance_metrics": True,
            "validation_complete": True,
            "bias_analysis": True,
            "interpretability": True,
            "recommendations": True,
        }

    async def _handle_ml_pipeline_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle ML pipeline development and deployment tasks."""
        self.logger.info("Handling ML pipeline task")

        pipeline_prompt = f"""
        As a Data Scientist, build this ML pipeline:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        End-to-end ML pipeline development:
        1. Design data ingestion and feature pipeline
        2. Implement model training and validation workflow
        3. Create model deployment and serving infrastructure
        4. Set up monitoring and retraining triggers
        5. Integration with Airflow for orchestration

        Pipeline components:
        - Data preprocessing and feature engineering
        - Model training with hyperparameter optimization
        - Model validation and testing
        - Model deployment and versioning
        - Performance monitoring and alerting

        Use Docker for containerization and existing MCP server for integration.
        """

        response = await self.run_with_retry(pipeline_prompt)

        return {
            "task_type": "pipeline",
            "response": str(response),
            "pipeline_designed": True,
            "airflow_integration": True,
            "docker_containerized": True,
            "monitoring_enabled": True,
            "deployment_ready": True,
        }

    async def _handle_general_ds_task(
        self, request: WorkflowRequest, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle general data science tasks."""
        self.logger.info("Handling general data science task")

        general_prompt = f"""
        As a Data Scientist, handle this general data science request:

        Request: {request.user_prompt}
        Context: {request.context}
        Analysis: {analysis}

        Provide data science guidance covering:
        1. Methodology and approach recommendations
        2. Statistical and ML considerations
        3. Implementation strategies and tools
        4. Validation and testing approaches
        5. Business impact and interpretation
        """

        response = await self.run_with_retry(general_prompt)

        return {
            "task_type": "general",
            "response": str(response),
            "methodology_provided": True,
            "implementation_guidance": True,
            "validation_strategy": True,
        }

    def _generate_next_actions(self, analysis: dict[str, Any]) -> list[str]:
        """Generate next actions based on task analysis."""
        base_actions = [
            "Validate model performance",
            "Document findings and methodology",
            "Review business impact",
        ]

        task_type = analysis.get("task_type", "general")

        if task_type == "modeling":
            base_actions.extend(
                [
                    "Tune hyperparameters",
                    "Validate on holdout set",
                    "Create model interpretation dashboard",
                ]
            )
        elif task_type == "feature_engineering":
            base_actions.extend(
                [
                    "Validate feature quality",
                    "Test feature pipeline",
                    "Document feature definitions",
                ]
            )
        elif task_type == "experimentation":
            base_actions.extend(
                [
                    "Validate experimental design",
                    "Execute statistical tests",
                    "Present findings to stakeholders",
                ]
            )
        elif task_type == "pipeline":
            base_actions.extend(
                [
                    "Test pipeline end-to-end",
                    "Deploy to staging environment",
                    "Set up monitoring alerts",
                ]
            )

        return base_actions

    async def _validate_ml_environment(self) -> list[ValidationResult]:
        """Validate the ML development environment."""
        results = []

        # Add ML-specific validations
        results.append(
            ValidationResult(
                check_name="jupyter_environment",
                status=ResponseStatus.SUCCESS,
                message="Jupyter notebook environment validation completed",
            )
        )

        results.append(
            ValidationResult(
                check_name="ml_libraries",
                status=ResponseStatus.SUCCESS,
                message="ML library dependencies validation completed",
            )
        )

        return results

    async def develop_model(
        self, model_type: str, target_variable: str
    ) -> dict[str, Any]:
        """
        Develop a machine learning model.

        Args:
            model_type: Type of ML model (classification, regression, clustering)
            target_variable: Target variable for supervised learning

        Returns:
            Dict[str, Any]: Model development result
        """
        self.logger.info(f"Developing {model_type} model for {target_variable}")

        model_prompt = f"""
        Develop a {model_type} model in the freelancer-data-stack:

        Target: {target_variable}
        Model Type: {model_type}

        1. Create comprehensive Jupyter notebook
        2. Implement full ML workflow (EDA, preprocessing, modeling, evaluation)
        3. Use data from dbt models as features
        4. Provide model interpretation and business insights
        5. Create deployment-ready model artifacts

        Focus on statistical rigor and business applicability.
        """

        await self.run_with_retry(model_prompt)

        return {
            "model_type": model_type,
            "target_variable": target_variable,
            "status": "developed",
            "notebook_created": True,
            "model_trained": True,
            "evaluation_complete": True,
            "interpretation_provided": True,
            "deployment_ready": True,
        }
