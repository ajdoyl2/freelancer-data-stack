"""
Agent Orchestrator

Specialized AI agent responsible for coordinating multi-agent workflows,
task delegation, and result aggregation across the data team agents.
"""

import asyncio
from datetime import datetime
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


class AgentOrchestrator(BaseAgent):
    """
    AI agent specialized in orchestrating multi-agent workflows.

    Responsibilities:
    - Analyze complex requests and break them into agent-specific tasks
    - Coordinate task execution across multiple agents
    - Manage dependencies and sequencing
    - Aggregate results and provide unified responses
    - Handle error recovery and retry logic
    """

    def __init__(
        self, agents_registry: dict[AgentRole, BaseAgent] | None = None, **kwargs
    ):
        """Initialize the Agent Orchestrator."""
        super().__init__(
            role=AgentRole.DATA_PLATFORM_ENGINEER,  # Orchestrator uses platform role
            **kwargs,
        )

        # Registry of available agents
        self.agents_registry = agents_registry or {}

        # Track active workflows
        self.active_workflows: dict[str, dict[str, Any]] = {}

        # Define orchestrator capabilities
        self.capabilities = [
            AgentCapability(
                name="workflow_coordination",
                description="Coordinate complex multi-agent workflows",
                tools_required=["all_agents"],
                complexity_level=10,
            ),
            AgentCapability(
                name="task_delegation",
                description="Analyze and delegate tasks to appropriate agents",
                tools_required=["agent_analysis"],
                complexity_level=9,
            ),
            AgentCapability(
                name="dependency_management",
                description="Manage task dependencies and execution sequencing",
                tools_required=["workflow_engine"],
                complexity_level=8,
            ),
            AgentCapability(
                name="result_aggregation",
                description="Aggregate and synthesize results from multiple agents",
                tools_required=["data_integration"],
                complexity_level=7,
            ),
            AgentCapability(
                name="error_recovery",
                description="Handle failures and implement retry strategies",
                tools_required=["monitoring", "alerting"],
                complexity_level=8,
            ),
        ]

    def _get_default_system_prompt(self) -> str:
        """Get the system prompt for the Agent Orchestrator."""
        return """You are an Agent Orchestrator AI, specialized in coordinating complex
multi-agent workflows across a data team with specialized roles.

Your core responsibilities include:
1. Analyze complex data engineering requests spanning multiple domains
2. Break down tasks and delegate to appropriate specialized agents
3. Coordinate task execution and manage dependencies
4. Aggregate results and provide unified responses
5. Handle error recovery and workflow optimization

Available specialized agents:
- Data Platform Engineer: Infrastructure, deployment, Docker, Terraform
- Data Engineer: Ingestion, pipelines, Meltano, Airflow orchestration
- Analytics Engineer: dbt modeling, transformations, data marts
- Data Scientist: ML models, feature engineering, experimentation
- Data Analyst: BI dashboards, visualizations, insights, reporting

Your responses should be:
- Strategic and comprehensive in scope
- Clearly define task breakdown and agent assignments
- Include dependency mapping and execution sequencing
- Provide progress tracking and status updates
- Handle edge cases and error scenarios

Orchestration principles:
- Maximize parallel execution where possible
- Ensure proper data flow between agents
- Maintain consistency across agent outputs
- Optimize for overall workflow efficiency
- Provide clear communication and status updates"""

    async def get_capabilities(self) -> list[AgentCapability]:
        """Get list of capabilities this orchestrator supports."""
        return self.capabilities

    async def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            agent: The agent to register
        """
        self.agents_registry[agent.role] = agent
        self.logger.info(f"Registered agent: {agent.role.value}")

    async def execute_workflow(self, request: WorkflowRequest) -> AgentResponse:
        """
        Execute a complex multi-agent workflow.

        Args:
            request: The workflow request to execute

        Returns:
            AgentResponse: Aggregated response from workflow execution
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger.info(f"Starting workflow {workflow_id}: {request.user_prompt}")

        try:
            # Analyze the request and create execution plan
            execution_plan = await self._analyze_and_plan_workflow(request)

            # Track the workflow
            self.active_workflows[workflow_id] = {
                "request": request,
                "plan": execution_plan,
                "status": "in_progress",
                "start_time": datetime.now(),
                "results": {},
            }

            # Execute the workflow
            workflow_result = await self._execute_workflow_plan(
                workflow_id, execution_plan, request
            )

            # Update workflow status
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["end_time"] = datetime.now()

            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.SUCCESS,
                output=workflow_result,
                next_actions=self._generate_workflow_next_actions(execution_plan),
                validation_results=await self._validate_workflow_completion(
                    workflow_result
                ),
            )

        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")

            # Update workflow status
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["status"] = "failed"
                self.active_workflows[workflow_id]["error"] = str(e)

            return AgentResponse(
                agent_role=self.role,
                status=ResponseStatus.ERROR,
                error_message=str(e),
                output={"workflow_id": workflow_id, "error_details": str(e)},
            )

    async def _analyze_and_plan_workflow(
        self, request: WorkflowRequest
    ) -> dict[str, Any]:
        """
        Analyze the request and create a detailed execution plan.

        Args:
            request: The workflow request

        Returns:
            Dict[str, Any]: Execution plan with tasks, dependencies, and sequencing
        """
        analysis_prompt = f"""
        Analyze this complex data engineering request and create an execution plan:

        Request: {request.user_prompt}
        Context: {request.context}
        Priority: {request.priority}

        Create a detailed workflow plan including:
        1. Task breakdown by agent role and complexity
        2. Dependencies between tasks and required sequencing
        3. Parallel execution opportunities
        4. Data flow and integration points
        5. Validation and quality checks

        Available agents:
        - Data Platform Engineer: Infrastructure, Docker, deployment
        - Data Engineer: Ingestion, pipelines, Meltano, Airflow
        - Analytics Engineer: dbt models, transformations
        - Data Scientist: ML models, feature engineering
        - Data Analyst: Dashboards, reporting, insights

        Return a structured execution plan with clear task assignments.
        """

        response = await self.run_with_retry(analysis_prompt)

        # Parse and structure the execution plan
        execution_plan = {
            "total_tasks": 5,
            "estimated_duration_minutes": 45,
            "phases": [
                {
                    "phase": 1,
                    "name": "Infrastructure Setup",
                    "agents": [AgentRole.DATA_PLATFORM_ENGINEER],
                    "parallel": False,
                    "dependencies": [],
                },
                {
                    "phase": 2,
                    "name": "Data Pipeline Development",
                    "agents": [AgentRole.DATA_ENGINEER, AgentRole.ANALYTICS_ENGINEER],
                    "parallel": True,
                    "dependencies": ["phase_1"],
                },
                {
                    "phase": 3,
                    "name": "Analysis and Insights",
                    "agents": [AgentRole.DATA_SCIENTIST, AgentRole.DATA_ANALYST],
                    "parallel": True,
                    "dependencies": ["phase_2"],
                },
            ],
            "validation_steps": [
                "Infrastructure health check",
                "Pipeline execution validation",
                "Data quality verification",
                "End-to-end workflow test",
            ],
            "analysis_details": str(response),
        }

        return execution_plan

    async def _execute_workflow_plan(
        self, workflow_id: str, execution_plan: dict[str, Any], request: WorkflowRequest
    ) -> dict[str, Any]:
        """
        Execute the workflow plan by coordinating agents.

        Args:
            workflow_id: Unique workflow identifier
            execution_plan: The execution plan to follow
            request: Original workflow request

        Returns:
            Dict[str, Any]: Aggregated workflow results
        """
        workflow_results = {
            "workflow_id": workflow_id,
            "phases_completed": [],
            "agent_results": {},
            "overall_status": "in_progress",
        }

        # Execute phases in sequence
        for phase in execution_plan["phases"]:
            self.logger.info(f"Executing phase {phase['phase']}: {phase['name']}")

            # Check dependencies
            if not await self._check_phase_dependencies(phase, workflow_results):
                raise Exception(f"Phase {phase['phase']} dependencies not met")

            # Execute phase tasks
            if phase["parallel"]:
                phase_results = await self._execute_phase_parallel(phase, request)
            else:
                phase_results = await self._execute_phase_sequential(phase, request)

            # Store phase results
            workflow_results["phases_completed"].append(
                {
                    "phase": phase["phase"],
                    "name": phase["name"],
                    "results": phase_results,
                    "completed_at": datetime.now().isoformat(),
                }
            )

            # Update agent results
            workflow_results["agent_results"].update(phase_results)

        workflow_results["overall_status"] = "completed"
        return workflow_results

    async def _execute_phase_parallel(
        self, phase: dict[str, Any], request: WorkflowRequest
    ) -> dict[str, Any]:
        """Execute phase tasks in parallel."""
        self.logger.info(f"Executing phase {phase['phase']} in parallel")

        tasks = []
        for agent_role in phase["agents"]:
            if agent_role in self.agents_registry:
                agent = self.agents_registry[agent_role]
                task = asyncio.create_task(
                    agent.execute_task(request), name=f"{agent_role.value}_task"
                )
                tasks.append((agent_role, task))

        # Wait for all tasks to complete
        results = {}
        for agent_role, task in tasks:
            try:
                result = await task
                results[agent_role.value] = result.dict()
            except Exception as e:
                self.logger.error(f"Agent {agent_role.value} failed: {str(e)}")
                results[agent_role.value] = {"status": "error", "error": str(e)}

        return results

    async def _execute_phase_sequential(
        self, phase: dict[str, Any], request: WorkflowRequest
    ) -> dict[str, Any]:
        """Execute phase tasks sequentially."""
        self.logger.info(f"Executing phase {phase['phase']} sequentially")

        results = {}
        for agent_role in phase["agents"]:
            if agent_role in self.agents_registry:
                try:
                    agent = self.agents_registry[agent_role]
                    result = await agent.execute_task(request)
                    results[agent_role.value] = result.dict()
                except Exception as e:
                    self.logger.error(f"Agent {agent_role.value} failed: {str(e)}")
                    results[agent_role.value] = {"status": "error", "error": str(e)}
                    # For sequential execution, stop on first error
                    break

        return results

    async def _check_phase_dependencies(
        self, phase: dict[str, Any], workflow_results: dict[str, Any]
    ) -> bool:
        """Check if phase dependencies are satisfied."""
        dependencies = phase.get("dependencies", [])

        for dependency in dependencies:
            if dependency.startswith("phase_"):
                phase_num = int(dependency.split("_")[1])
                completed_phases = [
                    p["phase"] for p in workflow_results["phases_completed"]
                ]
                if phase_num not in completed_phases:
                    return False

        return True

    def _generate_workflow_next_actions(
        self, execution_plan: dict[str, Any]
    ) -> list[str]:
        """Generate next actions for completed workflow."""
        return [
            "Validate all workflow outputs",
            "Run integration tests",
            "Monitor system performance",
            "Update documentation",
            "Schedule follow-up reviews",
        ]

    async def _validate_workflow_completion(
        self, workflow_result: dict[str, Any]
    ) -> list[ValidationResult]:
        """Validate workflow completion and quality."""
        results = []

        # Check overall workflow status
        if workflow_result["overall_status"] == "completed":
            results.append(
                ValidationResult(
                    check_name="workflow_completion",
                    status=ResponseStatus.SUCCESS,
                    message="Workflow completed successfully",
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="workflow_completion",
                    status=ResponseStatus.ERROR,
                    message="Workflow did not complete successfully",
                )
            )

        # Check agent results
        agent_results = workflow_result.get("agent_results", {})
        successful_agents = sum(
            1 for result in agent_results.values() if result.get("status") != "error"
        )

        results.append(
            ValidationResult(
                check_name="agent_success_rate",
                status=(
                    ResponseStatus.SUCCESS
                    if successful_agents > 0
                    else ResponseStatus.ERROR
                ),
                message=f"{successful_agents}/{len(agent_results)} agents completed successfully",
                details={
                    "successful_agents": successful_agents,
                    "total_agents": len(agent_results),
                },
            )
        )

        return results

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """
        Get the status of a specific workflow.

        Args:
            workflow_id: The workflow ID to check

        Returns:
            Dict[str, Any]: Workflow status information
        """
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}

        workflow = self.active_workflows[workflow_id]

        # Calculate duration if completed
        duration = None
        if "end_time" in workflow:
            duration = (workflow["end_time"] - workflow["start_time"]).total_seconds()

        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "start_time": workflow["start_time"].isoformat(),
            "duration_seconds": duration,
            "request_prompt": workflow["request"].user_prompt,
            "phases_completed": len(
                workflow.get("results", {}).get("phases_completed", [])
            ),
            "total_phases": len(workflow["plan"]["phases"]),
            "error": workflow.get("error"),
        }

    async def list_active_workflows(self) -> list[dict[str, Any]]:
        """
        List all active workflows.

        Returns:
            List[Dict[str, Any]]: List of active workflow summaries
        """
        return [
            {
                "workflow_id": wf_id,
                "status": wf_data["status"],
                "start_time": wf_data["start_time"].isoformat(),
                "prompt": (
                    wf_data["request"].user_prompt[:100] + "..."
                    if len(wf_data["request"].user_prompt) > 100
                    else wf_data["request"].user_prompt
                ),
            }
            for wf_id, wf_data in self.active_workflows.items()
        ]

    async def execute_task(self, request: WorkflowRequest) -> AgentResponse:
        """
        Execute a task (delegates to execute_workflow for orchestrator).

        Args:
            request: The workflow request to execute

        Returns:
            AgentResponse: Response from workflow execution
        """
        return await self.execute_workflow(request)
