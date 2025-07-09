"""
Agent Configuration Management

Provides configuration settings for each AI agent including capabilities,
tool access, and behavior parameters.
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agents.base_agent import AgentRole


class EnvironmentType(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class AgentConfig:
    """Configuration for a single agent."""

    role: AgentRole
    enabled: bool = True
    model_name: str = "openai:gpt-4"
    max_retries: int = 3
    timeout_seconds: int = 300
    enable_validation: bool = True
    log_level: str = "INFO"
    tools_enabled: list[str] = field(default_factory=list)
    custom_system_prompt: str | None = None
    rate_limit_requests_per_minute: int = 60

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "role": self.role.value,
            "enabled": self.enabled,
            "model_name": self.model_name,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "enable_validation": self.enable_validation,
            "log_level": self.log_level,
            "tools_enabled": self.tools_enabled,
            "custom_system_prompt": self.custom_system_prompt,
            "rate_limit_requests_per_minute": self.rate_limit_requests_per_minute,
        }


class AgentConfigs:
    """
    Manages configuration for all AI agents in the system.

    Provides environment-specific configurations and agent-specific settings
    for deployment across different environments.
    """

    def __init__(self, environment: EnvironmentType | None = None):
        """Initialize agent configurations."""
        self.logger = logging.getLogger(__name__)
        self.environment = environment or self._detect_environment()
        self.configs: dict[AgentRole, AgentConfig] = {}

        # Load configurations
        self._load_default_configs()
        self._load_environment_configs()

    def _detect_environment(self) -> EnvironmentType:
        """Detect the current environment."""
        env = os.getenv("ENVIRONMENT", "development").lower()

        if env in ["prod", "production"]:
            return EnvironmentType.PRODUCTION
        elif env in ["staging", "stage"]:
            return EnvironmentType.STAGING
        else:
            return EnvironmentType.DEVELOPMENT

    def _load_default_configs(self):
        """Load default configurations for all agents."""

        # Data Platform Engineer - Infrastructure and deployment
        self.configs[AgentRole.DATA_PLATFORM_ENGINEER] = AgentConfig(
            role=AgentRole.DATA_PLATFORM_ENGINEER,
            model_name="openai:gpt-4",
            timeout_seconds=600,  # Longer timeout for deployment tasks
            tools_enabled=["docker_tools", "terraform", "aws_cli", "monitoring_tools"],
            rate_limit_requests_per_minute=30,  # Conservative for infrastructure tasks
        )

        # Data Engineer - Pipeline development and data processing
        self.configs[AgentRole.DATA_ENGINEER] = AgentConfig(
            role=AgentRole.DATA_ENGINEER,
            model_name="openai:gpt-4",
            timeout_seconds=450,
            tools_enabled=[
                "meltano",
                "airflow_tools",
                "database_tools",
                "quality_tools",
            ],
            rate_limit_requests_per_minute=45,
        )

        # Analytics Engineer - dbt and data modeling
        self.configs[AgentRole.ANALYTICS_ENGINEER] = AgentConfig(
            role=AgentRole.ANALYTICS_ENGINEER,
            model_name="openai:gpt-4",
            timeout_seconds=300,
            tools_enabled=[
                "dbt_tools",
                "sql_tools",
                "quality_tools",
                "documentation_tools",
            ],
            rate_limit_requests_per_minute=60,
        )

        # Data Scientist - ML and experimentation
        self.configs[AgentRole.DATA_SCIENTIST] = AgentConfig(
            role=AgentRole.DATA_SCIENTIST,
            model_name="openai:gpt-4",
            timeout_seconds=900,  # Longer timeout for ML tasks
            tools_enabled=[
                "jupyter_tools",
                "ml_libraries",
                "statistical_tools",
                "experimentation_tools",
            ],
            rate_limit_requests_per_minute=30,  # Conservative for compute-intensive tasks
        )

        # Data Analyst - Reporting and visualization
        self.configs[AgentRole.DATA_ANALYST] = AgentConfig(
            role=AgentRole.DATA_ANALYST,
            model_name="openai:gpt-4",
            timeout_seconds=240,
            tools_enabled=[
                "visualization_tools",
                "metabase_tools",
                "evidence_tools",
                "reporting_tools",
            ],
            rate_limit_requests_per_minute=60,
        )

    def _load_environment_configs(self):
        """Load environment-specific configuration overrides."""

        if self.environment == EnvironmentType.PRODUCTION:
            # Production configurations - more conservative settings
            for config in self.configs.values():
                config.max_retries = 5
                config.enable_validation = True
                config.log_level = "WARNING"
                config.rate_limit_requests_per_minute = max(
                    config.rate_limit_requests_per_minute // 2, 10
                )

                # Use Claude for production for potentially better reliability
                if config.model_name.startswith("openai:"):
                    config.model_name = "anthropic:claude-3-5-sonnet-20241022"

        elif self.environment == EnvironmentType.STAGING:
            # Staging configurations - balanced settings
            for config in self.configs.values():
                config.max_retries = 3
                config.enable_validation = True
                config.log_level = "INFO"
                config.rate_limit_requests_per_minute = int(
                    config.rate_limit_requests_per_minute * 0.75
                )

        else:  # Development
            # Development configurations - more permissive settings
            for config in self.configs.values():
                config.max_retries = 2
                config.enable_validation = True
                config.log_level = "DEBUG"
                config.timeout_seconds = min(
                    config.timeout_seconds, 180
                )  # Shorter timeouts for dev

    def get_config(self, agent_role: AgentRole) -> AgentConfig:
        """Get configuration for a specific agent."""
        if agent_role not in self.configs:
            raise ValueError(f"No configuration found for agent role: {agent_role}")

        return self.configs[agent_role]

    def update_config(self, agent_role: AgentRole, **kwargs):
        """Update configuration for a specific agent."""
        if agent_role not in self.configs:
            raise ValueError(f"No configuration found for agent role: {agent_role}")

        config = self.configs[agent_role]

        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {key}")

    def get_all_configs(self) -> dict[AgentRole, AgentConfig]:
        """Get all agent configurations."""
        return self.configs.copy()

    def get_enabled_agents(self) -> list[AgentRole]:
        """Get list of enabled agent roles."""
        return [role for role, config in self.configs.items() if config.enabled]

    def disable_agent(self, agent_role: AgentRole):
        """Disable a specific agent."""
        if agent_role in self.configs:
            self.configs[agent_role].enabled = False

    def enable_agent(self, agent_role: AgentRole):
        """Enable a specific agent."""
        if agent_role in self.configs:
            self.configs[agent_role].enabled = True

    def set_model_for_all(self, model_name: str):
        """Set the same model for all agents."""
        for config in self.configs.values():
            config.model_name = model_name

    def set_log_level_for_all(self, log_level: str):
        """Set the same log level for all agents."""
        for config in self.configs.values():
            config.log_level = log_level

    def get_environment_summary(self) -> dict[str, Any]:
        """Get summary of current environment configuration."""
        enabled_agents = self.get_enabled_agents()

        models_used = {config.model_name for config in self.configs.values()}

        return {
            "environment": self.environment.value,
            "total_agents": len(self.configs),
            "enabled_agents": len(enabled_agents),
            "enabled_agent_roles": [role.value for role in enabled_agents],
            "models_used": list(models_used),
            "validation_enabled": all(
                config.enable_validation for config in self.configs.values()
            ),
            "average_timeout": sum(
                config.timeout_seconds for config in self.configs.values()
            )
            // len(self.configs),
        }

    def validate_configurations(self) -> list[str]:
        """Validate all agent configurations and return any issues."""
        issues = []

        for role, config in self.configs.items():
            # Check timeouts
            if config.timeout_seconds < 30:
                issues.append(
                    f"{role.value}: Timeout too short ({config.timeout_seconds}s)"
                )
            elif config.timeout_seconds > 1800:
                issues.append(
                    f"{role.value}: Timeout very long ({config.timeout_seconds}s)"
                )

            # Check retries
            if config.max_retries < 1:
                issues.append(
                    f"{role.value}: Max retries too low ({config.max_retries})"
                )
            elif config.max_retries > 10:
                issues.append(
                    f"{role.value}: Max retries too high ({config.max_retries})"
                )

            # Check rate limits
            if config.rate_limit_requests_per_minute < 5:
                issues.append(
                    f"{role.value}: Rate limit too restrictive ({config.rate_limit_requests_per_minute}/min)"
                )
            elif config.rate_limit_requests_per_minute > 200:
                issues.append(
                    f"{role.value}: Rate limit very high ({config.rate_limit_requests_per_minute}/min)"
                )

            # Check model name format
            if not config.model_name or ":" not in config.model_name:
                issues.append(
                    f"{role.value}: Invalid model name format ({config.model_name})"
                )

        return issues

    def export_configs(self) -> dict[str, Any]:
        """Export all configurations to a dictionary."""
        return {
            "environment": self.environment.value,
            "agents": {
                role.value: config.to_dict() for role, config in self.configs.items()
            },
        }

    def load_from_env_vars(self):
        """Load configuration overrides from environment variables."""

        for role in AgentRole:
            role_prefix = f"AGENT_{role.value.upper()}_"

            # Check for environment variables with agent-specific prefixes
            if os.getenv(f"{role_prefix}ENABLED"):
                enabled = os.getenv(f"{role_prefix}ENABLED", "true").lower() == "true"
                self.configs[role].enabled = enabled

            if os.getenv(f"{role_prefix}MODEL"):
                self.configs[role].model_name = os.getenv(f"{role_prefix}MODEL")

            if os.getenv(f"{role_prefix}TIMEOUT"):
                try:
                    timeout = int(os.getenv(f"{role_prefix}TIMEOUT"))
                    self.configs[role].timeout_seconds = timeout
                except ValueError:
                    self.logger.warning(f"Invalid timeout value for {role.value}")

            if os.getenv(f"{role_prefix}MAX_RETRIES"):
                try:
                    retries = int(os.getenv(f"{role_prefix}MAX_RETRIES"))
                    self.configs[role].max_retries = retries
                except ValueError:
                    self.logger.warning(f"Invalid max_retries value for {role.value}")

            if os.getenv(f"{role_prefix}RATE_LIMIT"):
                try:
                    rate_limit = int(os.getenv(f"{role_prefix}RATE_LIMIT"))
                    self.configs[role].rate_limit_requests_per_minute = rate_limit
                except ValueError:
                    self.logger.warning(f"Invalid rate_limit value for {role.value}")

        # Global overrides
        if os.getenv("AGENTS_MODEL"):
            self.set_model_for_all(os.getenv("AGENTS_MODEL"))

        if os.getenv("AGENTS_LOG_LEVEL"):
            self.set_log_level_for_all(os.getenv("AGENTS_LOG_LEVEL"))
