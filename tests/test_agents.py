#!/usr/bin/env python3
"""
Test suite for AI agents functionality.

This module contains comprehensive tests for all agent implementations,
ensuring they work correctly in isolation and in coordination.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents import get_agent, list_available_agents
from agents.analytics_engineer import AnalyticsEngineer
from agents.base_agent import (
    AgentResponse,
    AgentRole,
    WorkflowPriority,
    WorkflowRequest,
)
from agents.data_analyst import DataAnalyst
from agents.data_engineer import DataEngineer
from agents.data_platform_engineer import DataPlatformEngineer
from agents.data_scientist import DataScientist


class TestAgentRegistry:
    """Test the agent registry and factory functions."""

    def test_list_available_agents(self):
        """Test that all expected agent roles are available."""
        available_agents = list_available_agents()

        expected_agents = {
            AgentRole.DATA_PLATFORM_ENGINEER,
            AgentRole.DATA_ENGINEER,
            AgentRole.ANALYTICS_ENGINEER,
            AgentRole.DATA_SCIENTIST,
            AgentRole.DATA_ANALYST,
        }

        assert set(available_agents) == expected_agents
        assert len(available_agents) == 5

    def test_get_agent_creation(self):
        """Test that agents can be created for all roles."""
        for role in AgentRole:
            agent = get_agent(role, model_name="openai:gpt-4")
            assert agent is not None
            assert agent.role == role

    def test_get_agent_invalid_role(self):
        """Test that invalid role raises appropriate error."""
        with pytest.raises((ValueError, TypeError)):
            get_agent("invalid_role")


class TestAgentBase:
    """Test the base agent functionality."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = DataPlatformEngineer(model_name="openai:gpt-4")
        return agent

    @pytest.mark.asyncio
    async def test_get_capabilities(self, mock_agent):
        """Test that agent can return its capabilities."""
        capabilities = await mock_agent.get_capabilities()

        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert all(isinstance(cap, str) for cap in capabilities)

    @pytest.mark.asyncio
    async def test_health_check(self, mock_agent):
        """Test agent health check functionality."""
        health = await mock_agent.health_check()

        assert isinstance(health, dict)
        assert "status" in health
        assert "agent_role" in health
        assert health["agent_role"] == mock_agent.role.value

    @pytest.mark.asyncio
    async def test_validate_request(self, mock_agent):
        """Test request validation."""
        valid_request = WorkflowRequest(
            request_id="test_001",
            user_prompt="Test prompt",
            agents_involved=[AgentRole.DATA_PLATFORM_ENGINEER],
            priority=WorkflowPriority.MEDIUM,
        )

        # Should not raise exception
        await mock_agent.validate_request(valid_request)

        # Test invalid request
        invalid_request = WorkflowRequest(
            request_id="",  # Empty ID should be invalid
            user_prompt="Test prompt",
            agents_involved=[AgentRole.DATA_PLATFORM_ENGINEER],
            priority=WorkflowPriority.MEDIUM,
        )

        with pytest.raises(ValueError):
            await mock_agent.validate_request(invalid_request)


class TestDataPlatformEngineer:
    """Test Data Platform Engineer specific functionality."""

    @pytest.fixture
    def agent(self):
        return DataPlatformEngineer(model_name="openai:gpt-4")

    @pytest.mark.asyncio
    async def test_execute_task_docker_status(self, agent):
        """Test Docker status check task."""
        task = "Check Docker container status"

        with patch.object(agent, "_agent") as mock_pydantic_agent:
            mock_response = Mock()
            mock_response.data = Mock()
            mock_response.data.content = "All containers running normally"
            mock_response.data.confidence = 0.95
            mock_response.data.recommendations = ["Monitor resource usage"]

            mock_pydantic_agent.run = AsyncMock(return_value=mock_response)

            result = await agent.execute_task(task)

            assert isinstance(result, AgentResponse)
            assert "containers" in result.content.lower()
            assert result.confidence > 0.8
            assert isinstance(result.recommendations, list)

    @pytest.mark.asyncio
    async def test_get_capabilities_platform_engineer(self, agent):
        """Test that platform engineer has infrastructure capabilities."""
        capabilities = await agent.get_capabilities()

        expected_capabilities = [
            "docker_container_management",
            "infrastructure_deployment",
            "monitoring_setup",
            "ci_cd_pipeline_management",
            "resource_optimization",
        ]

        for capability in expected_capabilities:
            assert capability in capabilities


class TestDataEngineer:
    """Test Data Engineer specific functionality."""

    @pytest.fixture
    def agent(self):
        return DataEngineer(model_name="openai:gpt-4")

    @pytest.mark.asyncio
    async def test_execute_task_pipeline_status(self, agent):
        """Test pipeline status check task."""
        task = "Check Airflow DAG status"

        with patch.object(agent, "_agent") as mock_pydantic_agent:
            mock_response = Mock()
            mock_response.data = Mock()
            mock_response.data.content = "All DAGs running successfully"
            mock_response.data.confidence = 0.90
            mock_response.data.recommendations = ["Schedule regular maintenance"]

            mock_pydantic_agent.run = AsyncMock(return_value=mock_response)

            result = await agent.execute_task(task)

            assert isinstance(result, AgentResponse)
            assert "dag" in result.content.lower()
            assert result.confidence > 0.8

    @pytest.mark.asyncio
    async def test_get_capabilities_data_engineer(self, agent):
        """Test that data engineer has pipeline capabilities."""
        capabilities = await agent.get_capabilities()

        expected_capabilities = [
            "airflow_dag_management",
            "meltano_pipeline_orchestration",
            "data_quality_validation",
            "database_operations",
            "etl_pipeline_development",
        ]

        for capability in expected_capabilities:
            assert capability in capabilities


class TestAnalyticsEngineer:
    """Test Analytics Engineer specific functionality."""

    @pytest.fixture
    def agent(self):
        return AnalyticsEngineer(model_name="openai:gpt-4")

    @pytest.mark.asyncio
    async def test_execute_task_dbt_run(self, agent):
        """Test dbt run task execution."""
        task = "Run dbt models for customer analytics"

        with patch.object(agent, "_agent") as mock_pydantic_agent:
            mock_response = Mock()
            mock_response.data = Mock()
            mock_response.data.content = "dbt models executed successfully"
            mock_response.data.confidence = 0.95
            mock_response.data.recommendations = ["Update documentation"]

            mock_pydantic_agent.run = AsyncMock(return_value=mock_response)

            result = await agent.execute_task(task)

            assert isinstance(result, AgentResponse)
            assert "dbt" in result.content.lower()
            assert result.confidence > 0.8

    @pytest.mark.asyncio
    async def test_get_capabilities_analytics_engineer(self, agent):
        """Test that analytics engineer has dbt capabilities."""
        capabilities = await agent.get_capabilities()

        expected_capabilities = [
            "dbt_model_development",
            "sql_query_optimization",
            "data_testing_and_validation",
            "analytics_documentation",
            "dimensional_modeling",
        ]

        for capability in expected_capabilities:
            assert capability in capabilities


class TestDataScientist:
    """Test Data Scientist specific functionality."""

    @pytest.fixture
    def agent(self):
        return DataScientist(model_name="openai:gpt-4")

    @pytest.mark.asyncio
    async def test_execute_task_ml_analysis(self, agent):
        """Test ML analysis task execution."""
        task = "Analyze customer churn patterns"

        with patch.object(agent, "_agent") as mock_pydantic_agent:
            mock_response = Mock()
            mock_response.data = Mock()
            mock_response.data.content = "Churn analysis completed with 85% accuracy"
            mock_response.data.confidence = 0.85
            mock_response.data.recommendations = ["Deploy model to production"]

            mock_pydantic_agent.run = AsyncMock(return_value=mock_response)

            result = await agent.execute_task(task)

            assert isinstance(result, AgentResponse)
            assert "churn" in result.content.lower()
            assert result.confidence > 0.8

    @pytest.mark.asyncio
    async def test_get_capabilities_data_scientist(self, agent):
        """Test that data scientist has ML capabilities."""
        capabilities = await agent.get_capabilities()

        expected_capabilities = [
            "machine_learning_modeling",
            "statistical_analysis",
            "data_exploration_and_visualization",
            "model_evaluation_and_validation",
            "predictive_analytics",
        ]

        for capability in expected_capabilities:
            assert capability in capabilities


class TestDataAnalyst:
    """Test Data Analyst specific functionality."""

    @pytest.fixture
    def agent(self):
        return DataAnalyst(model_name="openai:gpt-4")

    @pytest.mark.asyncio
    async def test_execute_task_dashboard_creation(self, agent):
        """Test dashboard creation task."""
        task = "Create revenue dashboard in Metabase"

        with patch.object(agent, "_agent") as mock_pydantic_agent:
            mock_response = Mock()
            mock_response.data = Mock()
            mock_response.data.content = "Revenue dashboard created successfully"
            mock_response.data.confidence = 0.90
            mock_response.data.recommendations = ["Add automated alerts"]

            mock_pydantic_agent.run = AsyncMock(return_value=mock_response)

            result = await agent.execute_task(task)

            assert isinstance(result, AgentResponse)
            assert "dashboard" in result.content.lower()
            assert result.confidence > 0.8

    @pytest.mark.asyncio
    async def test_get_capabilities_data_analyst(self, agent):
        """Test that data analyst has visualization capabilities."""
        capabilities = await agent.get_capabilities()

        expected_capabilities = [
            "business_intelligence_dashboards",
            "data_visualization_and_reporting",
            "kpi_tracking_and_monitoring",
            "ad_hoc_analysis",
            "stakeholder_communication",
        ]

        for capability in expected_capabilities:
            assert capability in capabilities


class TestAgentErrorHandling:
    """Test error handling across all agents."""

    @pytest.mark.asyncio
    async def test_invalid_task_handling(self):
        """Test how agents handle invalid tasks."""
        agent = DataPlatformEngineer(model_name="openai:gpt-4")

        with patch.object(agent, "_agent") as mock_pydantic_agent:
            mock_pydantic_agent.run = AsyncMock(side_effect=Exception("API Error"))

            with pytest.raises(Exception):
                await agent.execute_task("Invalid task that should fail")

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test agent timeout handling."""
        agent = DataPlatformEngineer(model_name="openai:gpt-4")

        with patch.object(agent, "_agent") as mock_pydantic_agent:
            mock_pydantic_agent.run = AsyncMock(side_effect=TimeoutError())

            with pytest.raises(asyncio.TimeoutError):
                await agent.execute_task("Task that times out")


class TestAgentIntegration:
    """Integration tests for agent interactions."""

    @pytest.mark.asyncio
    async def test_multiple_agent_creation(self):
        """Test creating multiple agents simultaneously."""
        agents = []

        for role in AgentRole:
            agent = get_agent(role, model_name="openai:gpt-4")
            agents.append(agent)

        assert len(agents) == 5
        assert len(set(agent.role for agent in agents)) == 5

    @pytest.mark.asyncio
    async def test_agent_health_checks(self):
        """Test health checks for all agents."""
        for role in AgentRole:
            agent = get_agent(role, model_name="openai:gpt-4")
            health = await agent.health_check()

            assert health["status"] in ["healthy", "degraded", "unhealthy"]
            assert health["agent_role"] == role.value


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
