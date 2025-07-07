"""
AI Agents for Freelancer Data Stack

This module provides specialized AI agents for different data team roles:
- DataPlatformEngineer: Infrastructure and deployment management
- DataEngineer: Data ingestion and pipeline management
- AnalyticsEngineer: Data transformation and modeling
- DataScientist: ML model development and experimentation
- DataAnalyst: Reporting and visualization

Each agent is built using Pydantic AI for type-safe, structured interactions.
"""

from .analytics_engineer import AnalyticsEngineer
from .base_agent import AgentResponse, AgentRole, BaseAgent, WorkflowRequest
from .data_analyst import DataAnalyst
from .data_engineer import DataEngineer
from .data_platform_engineer import DataPlatformEngineer
from .data_scientist import DataScientist
from .orchestrator import AgentOrchestrator

# Agent registry for dynamic discovery
AGENT_REGISTRY = {
    AgentRole.DATA_PLATFORM_ENGINEER: DataPlatformEngineer,
    AgentRole.DATA_ENGINEER: DataEngineer,
    AgentRole.ANALYTICS_ENGINEER: AnalyticsEngineer,
    AgentRole.DATA_SCIENTIST: DataScientist,
    AgentRole.DATA_ANALYST: DataAnalyst,
}


def get_agent(role: AgentRole, **kwargs) -> BaseAgent:
    """
    Factory function to create agent instances.

    Args:
        role: The agent role to create
        **kwargs: Additional configuration for the agent

    Returns:
        BaseAgent: Configured agent instance

    Raises:
        ValueError: If role is not supported
    """
    if role not in AGENT_REGISTRY:
        raise ValueError(f"Unsupported agent role: {role}")

    agent_class = AGENT_REGISTRY[role]
    return agent_class(**kwargs)


def list_available_agents() -> list[AgentRole]:
    """
    Get list of all available agent roles.

    Returns:
        list[AgentRole]: List of supported agent roles
    """
    return list(AGENT_REGISTRY.keys())


__all__ = [
    "BaseAgent",
    "AgentRole",
    "AgentResponse",
    "WorkflowRequest",
    "DataPlatformEngineer",
    "DataEngineer",
    "AnalyticsEngineer",
    "DataScientist",
    "DataAnalyst",
    "AgentOrchestrator",
    "AGENT_REGISTRY",
    "get_agent",
    "list_available_agents",
]
