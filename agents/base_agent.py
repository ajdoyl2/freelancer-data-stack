"""
Base Agent Framework

Provides the foundational abstract base class and data models for all AI agents
in the freelancer data stack. Built using Pydantic AI for type-safe interactions.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName


class AgentRole(str, Enum):
    """Enumeration of available agent roles in the data team."""

    DATA_PLATFORM_ENGINEER = "data_platform_engineer"
    DATA_ENGINEER = "data_engineer"
    ANALYTICS_ENGINEER = "analytics_engineer"
    DATA_SCIENTIST = "data_scientist"
    DATA_ANALYST = "data_analyst"


class ResponseStatus(str, Enum):
    """Status of agent response."""

    SUCCESS = "success"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"


class WorkflowPriority(str, Enum):
    """Priority levels for workflow requests."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ValidationResult(BaseModel):
    """Result of validation check."""

    check_name: str
    status: ResponseStatus
    message: str
    details: dict[str, Any] | None = None


class WorkflowRequest(BaseModel):
    """Request for agent workflow execution."""

    user_prompt: str = Field(description="Natural language prompt from user")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )
    priority: WorkflowPriority = Field(default=WorkflowPriority.MEDIUM)
    agents_involved: list[AgentRole] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentResponse(BaseModel):
    """Structured response from an agent."""

    agent_role: AgentRole
    status: ResponseStatus
    output: dict[str, Any] = Field(default_factory=dict)
    next_actions: list[str] = Field(default_factory=list)
    validation_results: list[ValidationResult] = Field(default_factory=list)
    execution_time_ms: int | None = None
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentCapability(BaseModel):
    """Definition of agent capability."""

    name: str
    description: str
    tools_required: list[str] = Field(default_factory=list)
    complexity_level: int = Field(ge=1, le=10, description="Complexity from 1-10")


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the data stack.

    Provides common functionality and interface that all specialized agents inherit.
    Built on Pydantic AI for type-safe, structured agent interactions.
    """

    def __init__(
        self,
        role: AgentRole,
        model_name: KnownModelName | str = "openai:gpt-4",
        system_prompt: str | None = None,
        **kwargs,
    ):
        """
        Initialize the base agent.

        Args:
            role: The agent's role in the data team
            model_name: The LLM model to use
            system_prompt: Custom system prompt for the agent
            **kwargs: Additional configuration options
        """
        self.role = role
        self.model_name = model_name
        self.logger = logging.getLogger(f"agent.{role.value}")
        self.capabilities: list[AgentCapability] = []

        # Initialize Pydantic AI agent
        self._agent = Agent(
            model=model_name,
            system_prompt=system_prompt or self._get_default_system_prompt(),
            deps_type=type(None),  # Will be overridden by subclasses
        )

        # Agent configuration
        self.config = {
            "max_retries": kwargs.get("max_retries", 3),
            "timeout_seconds": kwargs.get("timeout_seconds", 300),
            "enable_validation": kwargs.get("enable_validation", True),
            **kwargs,
        }

        self.logger.info(f"Initialized {role.value} agent with model {model_name}")

    @abstractmethod
    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for this agent.

        Returns:
            str: System prompt tailored to the agent's role
        """
        pass

    @abstractmethod
    async def get_capabilities(self) -> list[AgentCapability]:
        """
        Get list of capabilities this agent supports.

        Returns:
            List[AgentCapability]: Agent's capabilities
        """
        pass

    @abstractmethod
    async def execute_task(self, request: WorkflowRequest) -> AgentResponse:
        """
        Execute a task based on the workflow request.

        Args:
            request: The workflow request to execute

        Returns:
            AgentResponse: Structured response from the agent
        """
        pass

    async def validate_environment(self) -> list[ValidationResult]:
        """
        Validate that the agent's environment is properly configured.

        Returns:
            List[ValidationResult]: Validation results
        """
        results = []

        # Basic validation - check if model is accessible
        try:
            # Simple test query to validate model connectivity
            await self._agent.run("Hello, can you respond?")
            results.append(
                ValidationResult(
                    check_name="model_connectivity",
                    status=ResponseStatus.SUCCESS,
                    message="Model is accessible and responding",
                )
            )
        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="model_connectivity",
                    status=ResponseStatus.ERROR,
                    message=f"Model connectivity failed: {str(e)}",
                )
            )

        return results

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on the agent.

        Returns:
            Dict[str, Any]: Health status information
        """
        start_time = datetime.now()

        # Run validation
        validation_results = await self.validate_environment()

        # Calculate response time
        response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Determine overall health
        has_errors = any(r.status == ResponseStatus.ERROR for r in validation_results)
        status = ResponseStatus.ERROR if has_errors else ResponseStatus.SUCCESS

        return {
            "agent_role": self.role.value,
            "status": status.value,
            "response_time_ms": response_time_ms,
            "model_name": self.model_name,
            "capabilities_count": len(self.capabilities),
            "validation_results": [r.dict() for r in validation_results],
            "timestamp": datetime.now().isoformat(),
        }

    async def run_with_retry(self, prompt: str, max_retries: int | None = None) -> Any:
        """
        Run agent with retry logic.

        Args:
            prompt: The prompt to send to the agent
            max_retries: Maximum number of retries (uses config default if None)

        Returns:
            Any: Agent response

        Raises:
            Exception: If all retries are exhausted
        """
        max_retries = max_retries or self.config["max_retries"]

        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(f"Agent run attempt {attempt + 1}/{max_retries + 1}")

                # Run with timeout
                response = await asyncio.wait_for(
                    self._agent.run(prompt), timeout=self.config["timeout_seconds"]
                )

                return response

            except TimeoutError:
                self.logger.warning(f"Agent run timed out on attempt {attempt + 1}")
                if attempt == max_retries:
                    raise Exception("Agent run timed out after all retries")

            except Exception as e:
                self.logger.warning(
                    f"Agent run failed on attempt {attempt + 1}: {str(e)}"
                )
                if attempt == max_retries:
                    raise e

                # Wait before retry (exponential backoff)
                await asyncio.sleep(2**attempt)

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(role={self.role.value}, model={self.model_name})"

    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (
            f"{self.__class__.__name__}("
            f"role={self.role.value}, "
            f"model={self.model_name}, "
            f"capabilities={len(self.capabilities)}"
            f")"
        )
