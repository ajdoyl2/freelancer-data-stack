"""
Tool Configuration Management

Provides configuration for tool access permissions and capabilities
for different AI agents and environments.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agents.base_agent import AgentRole


class PermissionLevel(str, Enum):
    """Permission levels for tool access."""

    NONE = "none"
    READ_ONLY = "read_only"
    WRITE = "write"
    ADMIN = "admin"


class ToolCategory(str, Enum):
    """Categories of tools available to agents."""

    DOCKER = "docker"
    DATABASE = "database"
    PIPELINE = "pipeline"
    ANALYTICS = "analytics"
    MONITORING = "monitoring"
    DEPLOYMENT = "deployment"
    VISUALIZATION = "visualization"
    ML = "machine_learning"


@dataclass
class ToolConfig:
    """Configuration for a specific tool."""

    name: str
    category: ToolCategory
    description: str
    required_permissions: PermissionLevel = PermissionLevel.READ_ONLY
    safety_level: int = 1  # 1 (safe) to 5 (dangerous)
    dependencies: list[str] = field(default_factory=list)
    environment_restrictions: list[str] = field(default_factory=list)
    rate_limit_per_minute: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "required_permissions": self.required_permissions.value,
            "safety_level": self.safety_level,
            "dependencies": self.dependencies,
            "environment_restrictions": self.environment_restrictions,
            "rate_limit_per_minute": self.rate_limit_per_minute,
        }


@dataclass
class AgentToolPermissions:
    """Tool permissions for a specific agent."""

    agent_role: AgentRole
    permissions: dict[str, PermissionLevel] = field(default_factory=dict)
    denied_tools: set[str] = field(default_factory=set)
    rate_limits: dict[str, int] = field(default_factory=dict)

    def has_permission(self, tool_name: str, required_level: PermissionLevel) -> bool:
        """Check if agent has required permission for a tool."""
        if tool_name in self.denied_tools:
            return False

        current_level = self.permissions.get(tool_name, PermissionLevel.NONE)

        # Permission hierarchy: NONE < READ_ONLY < WRITE < ADMIN
        permission_order = [
            PermissionLevel.NONE,
            PermissionLevel.READ_ONLY,
            PermissionLevel.WRITE,
            PermissionLevel.ADMIN,
        ]

        return permission_order.index(current_level) >= permission_order.index(
            required_level
        )


class ToolConfigs:
    """
    Manages tool configurations and permissions for AI agents.

    Provides tool access control, safety restrictions, and permission
    management across different environments and agent roles.
    """

    def __init__(self, environment: str = "development"):
        """Initialize tool configurations."""
        self.logger = logging.getLogger(__name__)
        self.environment = environment
        self.tools: dict[str, ToolConfig] = {}
        self.agent_permissions: dict[AgentRole, AgentToolPermissions] = {}

        # Load configurations
        self._load_tool_configs()
        self._load_agent_permissions()
        self._apply_environment_restrictions()

    def _load_tool_configs(self):
        """Load configurations for all available tools."""

        # Docker and Infrastructure Tools
        self.tools["docker_compose"] = ToolConfig(
            name="docker_compose",
            category=ToolCategory.DOCKER,
            description="Docker Compose service management",
            required_permissions=PermissionLevel.WRITE,
            safety_level=3,
            dependencies=["docker"],
            rate_limit_per_minute=20,
        )

        self.tools["docker_logs"] = ToolConfig(
            name="docker_logs",
            category=ToolCategory.DOCKER,
            description="View Docker container logs",
            required_permissions=PermissionLevel.READ_ONLY,
            safety_level=1,
            dependencies=["docker"],
        )

        self.tools["terraform"] = ToolConfig(
            name="terraform",
            category=ToolCategory.DEPLOYMENT,
            description="Infrastructure as Code management",
            required_permissions=PermissionLevel.ADMIN,
            safety_level=5,
            environment_restrictions=["production"],
            rate_limit_per_minute=5,
        )

        # Database Tools
        self.tools["duckdb_query"] = ToolConfig(
            name="duckdb_query",
            category=ToolCategory.DATABASE,
            description="Execute DuckDB queries",
            required_permissions=PermissionLevel.READ_ONLY,
            safety_level=2,
            rate_limit_per_minute=100,
        )

        self.tools["postgres_query"] = ToolConfig(
            name="postgres_query",
            category=ToolCategory.DATABASE,
            description="Execute PostgreSQL queries",
            required_permissions=PermissionLevel.READ_ONLY,
            safety_level=2,
            rate_limit_per_minute=50,
        )

        self.tools["snowflake_query"] = ToolConfig(
            name="snowflake_query",
            category=ToolCategory.DATABASE,
            description="Execute Snowflake queries",
            required_permissions=PermissionLevel.READ_ONLY,
            safety_level=3,
            environment_restrictions=["staging", "production"],
            rate_limit_per_minute=30,
        )

        # Pipeline Tools
        self.tools["meltano_run"] = ToolConfig(
            name="meltano_run",
            category=ToolCategory.PIPELINE,
            description="Execute Meltano ELT pipelines",
            required_permissions=PermissionLevel.WRITE,
            safety_level=3,
            dependencies=["meltano"],
            rate_limit_per_minute=10,
        )

        self.tools["airflow_trigger"] = ToolConfig(
            name="airflow_trigger",
            category=ToolCategory.PIPELINE,
            description="Trigger Airflow DAGs",
            required_permissions=PermissionLevel.WRITE,
            safety_level=3,
            dependencies=["airflow"],
            rate_limit_per_minute=15,
        )

        self.tools["dbt_run"] = ToolConfig(
            name="dbt_run",
            category=ToolCategory.ANALYTICS,
            description="Execute dbt models",
            required_permissions=PermissionLevel.WRITE,
            safety_level=2,
            dependencies=["dbt"],
            rate_limit_per_minute=20,
        )

        self.tools["dbt_test"] = ToolConfig(
            name="dbt_test",
            category=ToolCategory.ANALYTICS,
            description="Run dbt tests",
            required_permissions=PermissionLevel.READ_ONLY,
            safety_level=1,
            dependencies=["dbt"],
            rate_limit_per_minute=30,
        )

        # Monitoring Tools
        self.tools["prometheus_query"] = ToolConfig(
            name="prometheus_query",
            category=ToolCategory.MONITORING,
            description="Query Prometheus metrics",
            required_permissions=PermissionLevel.READ_ONLY,
            safety_level=1,
            dependencies=["prometheus"],
        )

        self.tools["grafana_dashboard"] = ToolConfig(
            name="grafana_dashboard",
            category=ToolCategory.MONITORING,
            description="Create Grafana dashboards",
            required_permissions=PermissionLevel.WRITE,
            safety_level=2,
            dependencies=["grafana"],
            rate_limit_per_minute=10,
        )

        # Visualization Tools
        self.tools["metabase_query"] = ToolConfig(
            name="metabase_query",
            category=ToolCategory.VISUALIZATION,
            description="Execute Metabase queries",
            required_permissions=PermissionLevel.READ_ONLY,
            safety_level=1,
            dependencies=["metabase"],
        )

        self.tools["evidence_report"] = ToolConfig(
            name="evidence_report",
            category=ToolCategory.VISUALIZATION,
            description="Generate Evidence reports",
            required_permissions=PermissionLevel.WRITE,
            safety_level=2,
            dependencies=["evidence"],
            rate_limit_per_minute=20,
        )

        # Machine Learning Tools
        self.tools["jupyter_notebook"] = ToolConfig(
            name="jupyter_notebook",
            category=ToolCategory.ML,
            description="Execute Jupyter notebooks",
            required_permissions=PermissionLevel.WRITE,
            safety_level=3,
            dependencies=["jupyter"],
            rate_limit_per_minute=5,
        )

        self.tools["model_training"] = ToolConfig(
            name="model_training",
            category=ToolCategory.ML,
            description="Train machine learning models",
            required_permissions=PermissionLevel.WRITE,
            safety_level=4,
            dependencies=["scikit_learn", "pandas"],
            rate_limit_per_minute=3,
        )

    def _load_agent_permissions(self):
        """Load default permissions for each agent role."""

        # Data Platform Engineer - Full infrastructure access
        self.agent_permissions[AgentRole.DATA_PLATFORM_ENGINEER] = AgentToolPermissions(
            agent_role=AgentRole.DATA_PLATFORM_ENGINEER,
            permissions={
                "docker_compose": PermissionLevel.ADMIN,
                "docker_logs": PermissionLevel.READ_ONLY,
                "terraform": PermissionLevel.ADMIN,
                "prometheus_query": PermissionLevel.READ_ONLY,
                "grafana_dashboard": PermissionLevel.WRITE,
                "postgres_query": PermissionLevel.READ_ONLY,
                "duckdb_query": PermissionLevel.READ_ONLY,
            },
        )

        # Data Engineer - Pipeline and data access
        self.agent_permissions[AgentRole.DATA_ENGINEER] = AgentToolPermissions(
            agent_role=AgentRole.DATA_ENGINEER,
            permissions={
                "meltano_run": PermissionLevel.WRITE,
                "airflow_trigger": PermissionLevel.WRITE,
                "postgres_query": PermissionLevel.WRITE,
                "duckdb_query": PermissionLevel.WRITE,
                "snowflake_query": PermissionLevel.READ_ONLY,
                "docker_logs": PermissionLevel.READ_ONLY,
                "prometheus_query": PermissionLevel.READ_ONLY,
            },
            denied_tools={"terraform"},  # No infrastructure changes
        )

        # Analytics Engineer - dbt and analytical tools
        self.agent_permissions[AgentRole.ANALYTICS_ENGINEER] = AgentToolPermissions(
            agent_role=AgentRole.ANALYTICS_ENGINEER,
            permissions={
                "dbt_run": PermissionLevel.WRITE,
                "dbt_test": PermissionLevel.WRITE,
                "postgres_query": PermissionLevel.WRITE,
                "duckdb_query": PermissionLevel.WRITE,
                "snowflake_query": PermissionLevel.WRITE,
                "docker_logs": PermissionLevel.READ_ONLY,
            },
            denied_tools={"terraform", "docker_compose"},
        )

        # Data Scientist - ML and analysis tools
        self.agent_permissions[AgentRole.DATA_SCIENTIST] = AgentToolPermissions(
            agent_role=AgentRole.DATA_SCIENTIST,
            permissions={
                "jupyter_notebook": PermissionLevel.WRITE,
                "model_training": PermissionLevel.WRITE,
                "postgres_query": PermissionLevel.READ_ONLY,
                "duckdb_query": PermissionLevel.READ_ONLY,
                "snowflake_query": PermissionLevel.READ_ONLY,
                "dbt_test": PermissionLevel.READ_ONLY,
            },
            denied_tools={"terraform", "docker_compose", "airflow_trigger"},
        )

        # Data Analyst - Visualization and reporting tools
        self.agent_permissions[AgentRole.DATA_ANALYST] = AgentToolPermissions(
            agent_role=AgentRole.DATA_ANALYST,
            permissions={
                "metabase_query": PermissionLevel.WRITE,
                "evidence_report": PermissionLevel.WRITE,
                "postgres_query": PermissionLevel.READ_ONLY,
                "duckdb_query": PermissionLevel.READ_ONLY,
                "snowflake_query": PermissionLevel.READ_ONLY,
                "dbt_test": PermissionLevel.READ_ONLY,
            },
            denied_tools={
                "terraform",
                "docker_compose",
                "airflow_trigger",
                "meltano_run",
            },
        )

    def _apply_environment_restrictions(self):
        """Apply environment-specific restrictions."""

        if self.environment == "production":
            # Production restrictions - more conservative
            for permissions in self.agent_permissions.values():
                # Reduce rate limits
                for tool_name in permissions.rate_limits:
                    permissions.rate_limits[tool_name] = max(
                        permissions.rate_limits[tool_name] // 2, 1
                    )

                # Add terraform to denied tools for non-platform engineers
                if permissions.agent_role != AgentRole.DATA_PLATFORM_ENGINEER:
                    permissions.denied_tools.add("terraform")

        elif self.environment == "development":
            # Development - more permissive but still safe
            for permissions in self.agent_permissions.values():
                # Remove some production-only restrictions
                if (
                    "terraform" in permissions.denied_tools
                    and permissions.agent_role == AgentRole.DATA_ENGINEER
                ):
                    permissions.denied_tools.remove("terraform")
                    permissions.permissions["terraform"] = PermissionLevel.READ_ONLY

    def check_tool_access(
        self, agent_role: AgentRole, tool_name: str
    ) -> dict[str, Any]:
        """Check if an agent has access to a specific tool."""

        if tool_name not in self.tools:
            return {"allowed": False, "reason": f"Tool '{tool_name}' not found"}

        tool_config = self.tools[tool_name]

        # Check environment restrictions
        if (
            tool_config.environment_restrictions
            and self.environment not in tool_config.environment_restrictions
        ):
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' not available in {self.environment} environment",
            }

        if agent_role not in self.agent_permissions:
            return {
                "allowed": False,
                "reason": f"No permissions configured for agent role: {agent_role}",
            }

        agent_perms = self.agent_permissions[agent_role]

        # Check if tool is denied
        if tool_name in agent_perms.denied_tools:
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' explicitly denied for {agent_role.value}",
            }

        # Check permission level
        if not agent_perms.has_permission(tool_name, tool_config.required_permissions):
            current_level = agent_perms.permissions.get(tool_name, PermissionLevel.NONE)
            return {
                "allowed": False,
                "reason": f"Insufficient permissions: has {current_level.value}, requires {tool_config.required_permissions.value}",
            }

        return {
            "allowed": True,
            "permission_level": agent_perms.permissions.get(
                tool_name, PermissionLevel.NONE
            ).value,
            "rate_limit": tool_config.rate_limit_per_minute,
            "safety_level": tool_config.safety_level,
        }

    def get_agent_tools(self, agent_role: AgentRole) -> list[dict[str, Any]]:
        """Get all tools available to a specific agent."""

        available_tools = []

        for tool_name, tool_config in self.tools.items():
            access_check = self.check_tool_access(agent_role, tool_name)

            if access_check["allowed"]:
                available_tools.append(
                    {
                        "name": tool_name,
                        "category": tool_config.category.value,
                        "description": tool_config.description,
                        "permission_level": access_check["permission_level"],
                        "safety_level": tool_config.safety_level,
                        "rate_limit": tool_config.rate_limit_per_minute,
                    }
                )

        return available_tools

    def get_tools_by_category(self, category: ToolCategory) -> list[ToolConfig]:
        """Get all tools in a specific category."""
        return [tool for tool in self.tools.values() if tool.category == category]

    def get_high_risk_tools(self, min_safety_level: int = 4) -> list[str]:
        """Get tools with high safety risk."""
        return [
            tool_name
            for tool_name, tool_config in self.tools.items()
            if tool_config.safety_level >= min_safety_level
        ]

    def grant_tool_permission(
        self, agent_role: AgentRole, tool_name: str, permission_level: PermissionLevel
    ):
        """Grant a specific permission to an agent for a tool."""

        if agent_role not in self.agent_permissions:
            self.agent_permissions[agent_role] = AgentToolPermissions(
                agent_role=agent_role
            )

        self.agent_permissions[agent_role].permissions[tool_name] = permission_level

        # Remove from denied tools if present
        self.agent_permissions[agent_role].denied_tools.discard(tool_name)

        self.logger.info(
            f"Granted {permission_level.value} permission for '{tool_name}' to {agent_role.value}"
        )

    def deny_tool_access(self, agent_role: AgentRole, tool_name: str):
        """Deny access to a tool for a specific agent."""

        if agent_role not in self.agent_permissions:
            self.agent_permissions[agent_role] = AgentToolPermissions(
                agent_role=agent_role
            )

        self.agent_permissions[agent_role].denied_tools.add(tool_name)

        # Remove from permissions if present
        self.agent_permissions[agent_role].permissions.pop(tool_name, None)

        self.logger.info(f"Denied access to '{tool_name}' for {agent_role.value}")

    def set_rate_limit(
        self, agent_role: AgentRole, tool_name: str, limit_per_minute: int
    ):
        """Set a custom rate limit for an agent's tool usage."""

        if agent_role not in self.agent_permissions:
            self.agent_permissions[agent_role] = AgentToolPermissions(
                agent_role=agent_role
            )

        self.agent_permissions[agent_role].rate_limits[tool_name] = limit_per_minute

        self.logger.info(
            f"Set rate limit for '{tool_name}' to {limit_per_minute}/min for {agent_role.value}"
        )

    def get_permissions_summary(self) -> dict[str, Any]:
        """Get summary of all permissions and configurations."""

        summary = {
            "environment": self.environment,
            "total_tools": len(self.tools),
            "tool_categories": {},
            "agent_permissions": {},
            "high_risk_tools": self.get_high_risk_tools(),
        }

        # Tool categories summary
        for category in ToolCategory:
            tools_in_category = self.get_tools_by_category(category)
            summary["tool_categories"][category.value] = {
                "count": len(tools_in_category),
                "tools": [tool.name for tool in tools_in_category],
            }

        # Agent permissions summary
        for agent_role, permissions in self.agent_permissions.items():
            allowed_tools = [
                tool_name
                for tool_name in self.tools.keys()
                if self.check_tool_access(agent_role, tool_name)["allowed"]
            ]

            summary["agent_permissions"][agent_role.value] = {
                "allowed_tools_count": len(allowed_tools),
                "denied_tools_count": len(permissions.denied_tools),
                "custom_rate_limits": len(permissions.rate_limits),
            }

        return summary

    def validate_configuration(self) -> list[str]:
        """Validate the tool configuration and return any issues."""

        issues = []

        # Check for tools with missing dependencies
        for tool_name, tool_config in self.tools.items():
            for dependency in tool_config.dependencies:
                if dependency not in self.tools:
                    issues.append(
                        f"Tool '{tool_name}' depends on missing tool '{dependency}'"
                    )

        # Check for agents without any tool permissions
        for agent_role in AgentRole:
            if agent_role not in self.agent_permissions:
                issues.append(f"No tool permissions configured for {agent_role.value}")
                continue

            available_tools = self.get_agent_tools(agent_role)
            if not available_tools:
                issues.append(f"No tools available for {agent_role.value}")

        # Check for high-risk tools without proper restrictions
        high_risk_tools = self.get_high_risk_tools()
        for tool_name in high_risk_tools:
            tool_config = self.tools[tool_name]
            if (
                tool_config.required_permissions == PermissionLevel.READ_ONLY
                and tool_config.safety_level >= 4
            ):
                issues.append(
                    f"High-risk tool '{tool_name}' has insufficient permission requirements"
                )

        return issues
