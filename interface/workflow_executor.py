"""
Workflow Executor

Executes workflows by coordinating with agents and managing the execution flow
based on natural language requests processed by the prompt handler.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agents import get_agent
from agents.base_agent import AgentResponse, AgentRole, ResponseStatus, WorkflowRequest
from agents.orchestrator import AgentOrchestrator

from .prompt_handler import PromptHandler, TaskComplexity
from .response_formatter import ResponseFormatter


class WorkflowExecutor:
    """
    Executes workflows based on natural language requests.

    Coordinates between:
    - Prompt analysis and intent classification
    - Agent selection and orchestration
    - Workflow execution and monitoring
    - Response formatting and user communication
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize the workflow executor."""
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()

        # Initialize components
        self.prompt_handler = PromptHandler()
        self.response_formatter = ResponseFormatter()

        # Initialize agents
        self.agents: dict[AgentRole, Any] = {}
        self.orchestrator: AgentOrchestrator | None = None

        # Workflow tracking
        self.active_workflows: dict[str, dict[str, Any]] = {}

    async def initialize_agents(self, model_config: dict[str, Any] | None = None):
        """
        Initialize all AI agents.

        Args:
            model_config: Configuration for the AI models
        """
        self.logger.info("Initializing AI agents...")

        # Default model configuration
        default_config = {
            "model_name": "openai:gpt-4",
            "max_retries": 3,
            "timeout_seconds": 300,
        }
        config = {**default_config, **(model_config or {})}

        try:
            # Initialize individual agents
            for role in AgentRole:
                self.logger.info(f"Initializing {role.value} agent...")
                agent = get_agent(role, **config)
                self.agents[role] = agent

            # Initialize orchestrator with agent registry
            self.orchestrator = AgentOrchestrator(agents_registry=self.agents, **config)

            # Register agents with orchestrator
            for agent in self.agents.values():
                await self.orchestrator.register_agent(agent)

            self.logger.info("All agents initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise

    async def execute_prompt(
        self,
        user_prompt: str,
        context: dict[str, Any] | None = None,
        stream_response: bool = False,
    ) -> dict[str, Any]:
        """
        Execute a workflow based on a natural language prompt.

        Args:
            user_prompt: The user's natural language request
            context: Additional context information
            stream_response: Whether to stream the response

        Returns:
            Dict[str, Any]: Execution results and formatted response
        """
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.logger.info(f"Executing prompt [{execution_id}]: {user_prompt}")

        try:
            # Step 1: Analyze the prompt
            workflow_request = await self.prompt_handler.create_workflow_request(
                user_prompt, context
            )

            # Step 2: Determine execution strategy
            execution_strategy = self._determine_execution_strategy(workflow_request)

            # Step 3: Execute the workflow
            if execution_strategy["type"] == "orchestrated":
                result = await self._execute_orchestrated_workflow(
                    execution_id, workflow_request, execution_strategy
                )
            else:
                result = await self._execute_single_agent_workflow(
                    execution_id, workflow_request, execution_strategy
                )

            # Step 4: Format the response
            formatted_response = await self.response_formatter.format_response(
                workflow_request, result, execution_strategy
            )

            return {
                "execution_id": execution_id,
                "success": result.status == ResponseStatus.SUCCESS,
                "workflow_request": workflow_request.dict(),
                "execution_strategy": execution_strategy,
                "raw_result": result.dict(),
                "formatted_response": formatted_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Workflow execution failed [{execution_id}]: {str(e)}")

            # Create error response
            error_response = await self.response_formatter.format_error_response(
                user_prompt, str(e), execution_id
            )

            return {
                "execution_id": execution_id,
                "success": False,
                "error": str(e),
                "formatted_response": error_response,
                "timestamp": datetime.now().isoformat(),
            }

    def _determine_execution_strategy(self, request: WorkflowRequest) -> dict[str, Any]:
        """Determine the best execution strategy for the request."""
        analysis = request.context.get("analysis", {})

        # Check if multiple agents are needed
        agents_involved = request.agents_involved
        is_multi_agent = len(agents_involved) > 1

        # Check complexity
        complexity = analysis.get("complexity", TaskComplexity.SIMPLE)

        if is_multi_agent or complexity == TaskComplexity.MULTI_AGENT:
            return {
                "type": "orchestrated",
                "primary_agent": None,
                "agents_involved": agents_involved,
                "coordination_required": True,
                "parallel_execution": True,
            }
        elif agents_involved:
            return {
                "type": "single_agent",
                "primary_agent": agents_involved[0],
                "agents_involved": agents_involved,
                "coordination_required": False,
                "parallel_execution": False,
            }
        else:
            # Default to platform engineer for general queries
            return {
                "type": "single_agent",
                "primary_agent": AgentRole.DATA_PLATFORM_ENGINEER,
                "agents_involved": [AgentRole.DATA_PLATFORM_ENGINEER],
                "coordination_required": False,
                "parallel_execution": False,
            }

    async def _execute_orchestrated_workflow(
        self, execution_id: str, request: WorkflowRequest, strategy: dict[str, Any]
    ) -> AgentResponse:
        """Execute a multi-agent orchestrated workflow."""
        self.logger.info(f"Executing orchestrated workflow [{execution_id}]")

        if not self.orchestrator:
            raise Exception("Orchestrator not initialized")

        # Track the workflow
        self.active_workflows[execution_id] = {
            "type": "orchestrated",
            "status": "in_progress",
            "start_time": datetime.now(),
            "request": request,
            "strategy": strategy,
        }

        # Execute through orchestrator
        result = await self.orchestrator.execute_workflow(request)

        # Update workflow tracking
        self.active_workflows[execution_id].update(
            {"status": "completed", "end_time": datetime.now(), "result": result}
        )

        return result

    async def _execute_single_agent_workflow(
        self, execution_id: str, request: WorkflowRequest, strategy: dict[str, Any]
    ) -> AgentResponse:
        """Execute a single-agent workflow."""
        primary_agent_role = strategy["primary_agent"]
        self.logger.info(
            f"Executing single-agent workflow [{execution_id}] with {primary_agent_role.value}"
        )

        if primary_agent_role not in self.agents:
            raise Exception(f"Agent {primary_agent_role.value} not available")

        # Track the workflow
        self.active_workflows[execution_id] = {
            "type": "single_agent",
            "agent": primary_agent_role.value,
            "status": "in_progress",
            "start_time": datetime.now(),
            "request": request,
            "strategy": strategy,
        }

        # Get the agent and execute
        agent = self.agents[primary_agent_role]
        result = await agent.execute_task(request)

        # Update workflow tracking
        self.active_workflows[execution_id].update(
            {"status": "completed", "end_time": datetime.now(), "result": result}
        )

        return result

    async def get_workflow_status(self, execution_id: str) -> dict[str, Any] | None:
        """Get the status of a specific workflow execution."""
        if execution_id in self.active_workflows:
            workflow = self.active_workflows[execution_id]

            # Calculate duration
            start_time = workflow["start_time"]
            end_time = workflow.get("end_time")

            if end_time:
                duration = (end_time - start_time).total_seconds()
            else:
                duration = (datetime.now() - start_time).total_seconds()

            return {
                "execution_id": execution_id,
                "type": workflow["type"],
                "status": workflow["status"],
                "duration_seconds": duration,
                "agent": workflow.get("agent"),
                "agents_involved": workflow.get("strategy", {}).get(
                    "agents_involved", []
                ),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat() if end_time else None,
            }

        return None

    async def list_active_workflows(self) -> list[dict[str, Any]]:
        """List all active workflow executions."""
        active = []

        for execution_id, workflow in self.active_workflows.items():
            if workflow["status"] == "in_progress":
                status_info = await self.get_workflow_status(execution_id)
                if status_info:
                    active.append(status_info)

        return active

    async def cancel_workflow(self, execution_id: str) -> bool:
        """
        Cancel a running workflow.

        Args:
            execution_id: The execution ID to cancel

        Returns:
            bool: True if successfully cancelled
        """
        if execution_id in self.active_workflows:
            workflow = self.active_workflows[execution_id]

            if workflow["status"] == "in_progress":
                # Mark as cancelled
                workflow["status"] = "cancelled"
                workflow["end_time"] = datetime.now()

                self.logger.info(f"Cancelled workflow [{execution_id}]")
                return True

        return False

    async def get_agent_health(self) -> dict[str, Any]:
        """Get health status of all agents."""
        health_status = {
            "overall_status": "healthy",
            "agents": {},
            "orchestrator_status": "unknown",
        }

        # Check individual agents
        for role, agent in self.agents.items():
            try:
                agent_health = await agent.health_check()
                health_status["agents"][role.value] = agent_health

                if agent_health.get("status") != "success":
                    health_status["overall_status"] = "degraded"

            except Exception as e:
                health_status["agents"][role.value] = {
                    "status": "error",
                    "error": str(e),
                }
                health_status["overall_status"] = "unhealthy"

        # Check orchestrator
        if self.orchestrator:
            try:
                orchestrator_health = await self.orchestrator.health_check()
                health_status["orchestrator_status"] = orchestrator_health.get(
                    "status", "unknown"
                )
            except Exception as e:
                health_status["orchestrator_status"] = "error"
                health_status["orchestrator_error"] = str(e)

        return health_status

    async def execute_streaming_prompt(
        self, user_prompt: str, context: dict[str, Any] | None = None
    ):
        """
        Execute a prompt with streaming response (async generator).

        Args:
            user_prompt: The user's natural language request
            context: Additional context information

        Yields:
            Dict[str, Any]: Streaming response chunks
        """
        execution_id = f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        try:
            # Yield initial status
            yield {
                "type": "status",
                "execution_id": execution_id,
                "message": "Analyzing prompt...",
                "progress": 0.1,
            }

            # Analyze prompt
            workflow_request = await self.prompt_handler.create_workflow_request(
                user_prompt, context
            )

            yield {
                "type": "analysis",
                "execution_id": execution_id,
                "analysis": workflow_request.context.get("analysis", {}),
                "agents_involved": [
                    role.value for role in workflow_request.agents_involved
                ],
                "progress": 0.3,
            }

            # Determine strategy
            execution_strategy = self._determine_execution_strategy(workflow_request)

            yield {
                "type": "strategy",
                "execution_id": execution_id,
                "strategy": execution_strategy,
                "progress": 0.4,
            }

            # Execute workflow
            yield {
                "type": "status",
                "execution_id": execution_id,
                "message": "Executing workflow...",
                "progress": 0.5,
            }

            if execution_strategy["type"] == "orchestrated":
                result = await self._execute_orchestrated_workflow(
                    execution_id, workflow_request, execution_strategy
                )
            else:
                result = await self._execute_single_agent_workflow(
                    execution_id, workflow_request, execution_strategy
                )

            yield {
                "type": "status",
                "execution_id": execution_id,
                "message": "Formatting response...",
                "progress": 0.9,
            }

            # Format response
            formatted_response = await self.response_formatter.format_response(
                workflow_request, result, execution_strategy
            )

            # Yield final result
            yield {
                "type": "complete",
                "execution_id": execution_id,
                "success": result.status == ResponseStatus.SUCCESS,
                "result": formatted_response,
                "progress": 1.0,
            }

        except Exception as e:
            yield {
                "type": "error",
                "execution_id": execution_id,
                "error": str(e),
                "progress": 1.0,
            }
