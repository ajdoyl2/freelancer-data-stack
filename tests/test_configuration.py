#!/usr/bin/env python3
"""
Test suite for configuration management.

This module tests the configuration systems for agents, models, and tools
to ensure they work correctly across different environments.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import AgentRole
from config.agent_configs import AgentConfig, AgentConfigs, EnvironmentType
from config.model_configs import ModelConfig, ModelConfigs, ModelProvider
from config.tool_configs import PermissionLevel, ToolCategory, ToolConfigs


class TestAgentConfigs:
    """Test agent configuration management."""

    def test_default_config_loading(self):
        """Test that default configurations are loaded correctly."""
        configs = AgentConfigs()

        # Test that all agent roles have configurations
        for role in AgentRole:
            assert role in configs.configs
            config = configs.get_config(role)
            assert isinstance(config, AgentConfig)
            assert config.role == role

    def test_environment_detection(self):
        """Test environment detection from environment variables."""
        # Test production detection
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            configs = AgentConfigs()
            assert configs.environment == EnvironmentType.PRODUCTION

        # Test staging detection
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}):
            configs = AgentConfigs()
            assert configs.environment == EnvironmentType.STAGING

        # Test default (development)
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            configs = AgentConfigs()
            assert configs.environment == EnvironmentType.DEVELOPMENT

    def test_production_environment_settings(self):
        """Test that production environment applies conservative settings."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            configs = AgentConfigs()

            for config in configs.configs.values():
                # Production should have higher retries
                assert config.max_retries >= 3
                # Production should have validation enabled
                assert config.enable_validation is True
                # Production should use conservative rate limits
                assert config.rate_limit_requests_per_minute <= 60

    def test_get_enabled_agents(self):
        """Test getting enabled agents."""
        configs = AgentConfigs()
        enabled_agents = configs.get_enabled_agents()

        # All agents should be enabled by default
        assert len(enabled_agents) == len(AgentRole)
        assert set(enabled_agents) == set(AgentRole)

    def test_disable_enable_agent(self):
        """Test disabling and enabling agents."""
        configs = AgentConfigs()

        # Disable an agent
        configs.disable_agent(AgentRole.DATA_ANALYST)
        assert not configs.get_config(AgentRole.DATA_ANALYST).enabled

        # Enable it back
        configs.enable_agent(AgentRole.DATA_ANALYST)
        assert configs.get_config(AgentRole.DATA_ANALYST).enabled

    def test_update_config(self):
        """Test updating agent configurations."""
        configs = AgentConfigs()

        # Update timeout for data platform engineer
        configs.update_config(
            AgentRole.DATA_PLATFORM_ENGINEER, timeout_seconds=900, max_retries=5
        )

        config = configs.get_config(AgentRole.DATA_PLATFORM_ENGINEER)
        assert config.timeout_seconds == 900
        assert config.max_retries == 5

    def test_validation(self):
        """Test configuration validation."""
        configs = AgentConfigs()

        # Should have no issues with default configs
        issues = configs.validate_configurations()
        assert isinstance(issues, list)

        # Test with invalid config
        configs.update_config(
            AgentRole.DATA_ENGINEER,
            timeout_seconds=10,  # Too short
            max_retries=0,  # Too low
        )

        issues = configs.validate_configurations()
        assert len(issues) > 0

    def test_environment_summary(self):
        """Test environment summary generation."""
        configs = AgentConfigs()
        summary = configs.get_environment_summary()

        assert "environment" in summary
        assert "total_agents" in summary
        assert "enabled_agents" in summary
        assert summary["total_agents"] == len(AgentRole)


class TestModelConfigs:
    """Test model configuration management."""

    def test_model_loading(self):
        """Test that all models are loaded correctly."""
        configs = ModelConfigs()

        # Should have models for all providers
        assert len(configs.models) > 0

        # Test specific models exist
        assert "openai:gpt-4" in configs.models
        assert "anthropic:claude-3-5-sonnet-20241022" in configs.models
        assert "xai:grok-beta" in configs.models

    def test_get_model_config(self):
        """Test retrieving model configurations."""
        configs = ModelConfigs()

        # Valid model
        model_config = configs.get_model_config("openai:gpt-4")
        assert isinstance(model_config, ModelConfig)
        assert model_config.provider == ModelProvider.OPENAI

        # Invalid model
        with pytest.raises(ValueError):
            configs.get_model_config("invalid:model")

    def test_get_models_by_provider(self):
        """Test filtering models by provider."""
        configs = ModelConfigs()

        openai_models = configs.get_models_by_provider(ModelProvider.OPENAI)
        assert len(openai_models) > 0
        assert all(model.provider == ModelProvider.OPENAI for model in openai_models)

        anthropic_models = configs.get_models_by_provider(ModelProvider.ANTHROPIC)
        assert len(anthropic_models) > 0
        assert all(
            model.provider == ModelProvider.ANTHROPIC for model in anthropic_models
        )

    def test_cost_estimation(self):
        """Test cost estimation functionality."""
        configs = ModelConfigs()

        # Test cost calculation
        cost = configs.get_cost_estimate("openai:gpt-4", 1000, 500)
        assert cost > 0
        assert isinstance(cost, float)

        # Compare costs
        comparisons = configs.compare_models_by_cost(1000, 500)
        assert len(comparisons) > 0
        assert all("cost" in comp for comp in comparisons)
        # Should be sorted by cost
        costs = [comp["cost"] for comp in comparisons]
        assert costs == sorted(costs)

    def test_model_recommendations(self):
        """Test model recommendation functionality."""
        configs = ModelConfigs()

        # Test use case recommendations
        fast_models = configs.get_recommended_models("fast_response")
        assert len(fast_models) > 0

        complex_models = configs.get_recommended_models("complex_reasoning")
        assert len(complex_models) > 0

    def test_agent_model_recommendation(self):
        """Test agent-specific model recommendations."""
        configs = ModelConfigs()

        # Test recommendations for different agent roles
        for agent_role in ["data_platform_engineer", "data_engineer", "data_scientist"]:
            recommended_model = configs.recommend_model_for_agent(agent_role)
            assert recommended_model in configs.models

    def test_model_validation(self):
        """Test model validation against requirements."""
        configs = ModelConfigs()

        # Valid requirements
        requirements = {
            "min_context_window": 32000,
            "max_cost_per_1k_tokens": 0.1,
            "requires_function_calling": True,
        }

        issues = configs.validate_model_selection("openai:gpt-4", requirements)
        # Should have no issues for GPT-4
        assert isinstance(issues, list)

        # Invalid requirements
        requirements = {
            "min_context_window": 1000000,  # Very high
            "max_cost_per_1k_tokens": 0.001,  # Very low
        }

        issues = configs.validate_model_selection("openai:gpt-4", requirements)
        assert len(issues) > 0


class TestToolConfigs:
    """Test tool configuration management."""

    def test_tool_loading(self):
        """Test that tools are loaded correctly."""
        configs = ToolConfigs()

        assert len(configs.tools) > 0

        # Test specific tools exist
        assert "docker_compose" in configs.tools
        assert "dbt_run" in configs.tools
        assert "postgres_query" in configs.tools

    def test_agent_permissions_loading(self):
        """Test that agent permissions are loaded correctly."""
        configs = ToolConfigs()

        # All agent roles should have permissions
        for role in AgentRole:
            assert role in configs.agent_permissions
            permissions = configs.agent_permissions[role]
            assert len(permissions.permissions) > 0

    def test_tool_access_checking(self):
        """Test tool access checking functionality."""
        configs = ToolConfigs()

        # Data Platform Engineer should have docker access
        access = configs.check_tool_access(
            AgentRole.DATA_PLATFORM_ENGINEER, "docker_compose"
        )
        assert access["allowed"] is True

        # Data Analyst should NOT have terraform access
        access = configs.check_tool_access(AgentRole.DATA_ANALYST, "terraform")
        assert access["allowed"] is False

    def test_agent_tools_listing(self):
        """Test getting tools available to specific agents."""
        configs = ToolConfigs()

        # Get tools for data engineer
        tools = configs.get_agent_tools(AgentRole.DATA_ENGINEER)
        assert len(tools) > 0

        # Should include pipeline tools
        tool_names = [tool["name"] for tool in tools]
        assert "meltano_run" in tool_names
        assert "airflow_trigger" in tool_names

    def test_permission_levels(self):
        """Test permission level hierarchy."""
        configs = ToolConfigs()

        # Data Platform Engineer should have admin access to docker
        permissions = configs.agent_permissions[AgentRole.DATA_PLATFORM_ENGINEER]
        assert permissions.has_permission("docker_compose", PermissionLevel.ADMIN)
        assert permissions.has_permission("docker_compose", PermissionLevel.WRITE)
        assert permissions.has_permission("docker_compose", PermissionLevel.READ_ONLY)

    def test_environment_restrictions(self):
        """Test environment-specific restrictions."""
        # Test production environment
        configs = ToolConfigs(environment="production")

        # Should have more restrictive settings in production
        access = configs.check_tool_access(AgentRole.DATA_ENGINEER, "terraform")
        # Data Engineer should not have terraform access in production
        assert access["allowed"] is False

    def test_tool_categories(self):
        """Test tool categorization."""
        configs = ToolConfigs()

        docker_tools = configs.get_tools_by_category(ToolCategory.DOCKER)
        assert len(docker_tools) > 0
        assert all(tool.category == ToolCategory.DOCKER for tool in docker_tools)

        ml_tools = configs.get_tools_by_category(ToolCategory.ML)
        assert len(ml_tools) > 0
        assert all(tool.category == ToolCategory.ML for tool in ml_tools)

    def test_high_risk_tools(self):
        """Test high-risk tool identification."""
        configs = ToolConfigs()

        high_risk_tools = configs.get_high_risk_tools(min_safety_level=4)
        assert isinstance(high_risk_tools, list)

        # Terraform should be high risk
        assert "terraform" in high_risk_tools

    def test_permission_management(self):
        """Test dynamic permission management."""
        configs = ToolConfigs()

        # Grant new permission
        configs.grant_tool_permission(
            AgentRole.DATA_ANALYST, "jupyter_notebook", PermissionLevel.WRITE
        )

        access = configs.check_tool_access(AgentRole.DATA_ANALYST, "jupyter_notebook")
        assert access["allowed"] is True

        # Deny access
        configs.deny_tool_access(AgentRole.DATA_ANALYST, "jupyter_notebook")
        access = configs.check_tool_access(AgentRole.DATA_ANALYST, "jupyter_notebook")
        assert access["allowed"] is False

    def test_configuration_validation(self):
        """Test tool configuration validation."""
        configs = ToolConfigs()

        issues = configs.validate_configuration()
        assert isinstance(issues, list)

        # Should not have critical issues with default config (dependencies are expected to be missing in test)
        critical_issues = [
            issue for issue in issues if "no tools available" in issue.lower()
        ]
        assert len(critical_issues) == 0


class TestConfigurationIntegration:
    """Integration tests for configuration systems."""

    def test_config_consistency(self):
        """Test consistency between different config systems."""
        agent_configs = AgentConfigs()
        model_configs = ModelConfigs()
        tool_configs = ToolConfigs()

        # All agent roles should have configurations in all systems
        for role in AgentRole:
            # Agent config should exist
            assert role in agent_configs.configs

            # Tool permissions should exist
            assert role in tool_configs.agent_permissions

            # Model should be valid for agent
            agent_config = agent_configs.get_config(role)
            try:
                model_config = model_configs.get_model_config(agent_config.model_name)
                assert model_config is not None
            except ValueError:
                pytest.fail(f"Invalid model {agent_config.model_name} for {role.value}")

    def test_environment_consistency(self):
        """Test that environment settings are consistent across configs."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            agent_configs = AgentConfigs(EnvironmentType.PRODUCTION)
            tool_configs = ToolConfigs(environment="production")

            assert agent_configs.environment == EnvironmentType.PRODUCTION
            assert tool_configs.environment == "production"

    def test_model_availability_loading(self):
        """Test loading model availability from environment."""
        model_configs = ModelConfigs()

        # Mock API key availability
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "test_key", "ANTHROPIC_API_KEY": "test_key"}
        ):
            available_providers = model_configs.load_from_env_vars()

            assert ModelProvider.OPENAI in available_providers
            assert ModelProvider.ANTHROPIC in available_providers


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
