"""
Unit tests for Data Stack Engineer Agent

Tests the DataStackEngineer agent functionality including task execution,
health checks, and pipeline management.
"""

import asyncio

# Add project root to path
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import AgentResponse, AgentRole, ResponseStatus, WorkflowRequest
from agents.data_stack_engineer import DataStackEngineer


class TestDataStackEngineer(unittest.TestCase):
    """Test cases for DataStackEngineer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = DataStackEngineer()

    def test_init(self):
        """Test DataStackEngineer initialization."""
        self.assertIsInstance(self.agent, DataStackEngineer)
        self.assertEqual(self.agent.role, AgentRole.DATA_PLATFORM_ENGINEER)
        self.assertIsNotNone(self.agent.docker_tools)
        self.assertIsNotNone(self.agent.meltano_tools)
        self.assertIsNotNone(self.agent.dbt_tools)
        self.assertIsNotNone(self.agent.duckdb_tools)
        self.assertIsNotNone(self.agent.airflow_tools)

    @pytest.mark.asyncio
    async def test_get_capabilities(self):
        """Test getting agent capabilities."""
        capabilities = await self.agent.get_capabilities()

        self.assertIsInstance(capabilities, list)
        self.assertGreater(len(capabilities), 0)

        # Check for expected capabilities
        capability_names = [cap.name for cap in capabilities]
        expected_capabilities = [
            "data_stack_deployment",
            "pipeline_monitoring",
            "infrastructure_troubleshooting",
            "performance_optimization",
            "automated_operations",
        ]

        for expected in expected_capabilities:
            self.assertIn(expected, capability_names)

    def test_analyze_task_type(self):
        """Test task type analysis."""
        test_cases = [
            ("deploy the data stack", "deployment"),
            ("setup the infrastructure", "deployment"),
            ("check pipeline health", "monitoring"),
            ("monitor system status", "monitoring"),
            ("troubleshoot the error", "troubleshooting"),
            ("fix the issue", "troubleshooting"),
            ("optimize performance", "optimization"),
            ("improve speed", "optimization"),
            ("run the pipeline", "pipeline_execution"),
            ("execute ETL", "pipeline_execution"),
            ("health check", "health_check"),
            ("random request", "general"),
        ]

        for prompt, expected_type in test_cases:
            result = asyncio.run(self.agent._analyze_task_type(prompt))
            self.assertEqual(result, expected_type, f"Failed for prompt: '{prompt}'")

    @patch.object(DataStackEngineer, "_handle_deployment")
    @pytest.mark.asyncio
    async def test_execute_task_deployment(self, mock_handler):
        """Test task execution for deployment."""
        # Mock deployment handler
        mock_handler.return_value = {
            "success": True,
            "message": "Deployment completed",
            "step_results": [],
        }

        request = WorkflowRequest(
            user_prompt="deploy the data stack",
            agent_role=AgentRole.DATA_PLATFORM_ENGINEER,
        )

        response = await self.agent.execute_task(request)

        self.assertIsInstance(response, AgentResponse)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertTrue(response.output["success"])
        mock_handler.assert_called_once_with(request)

    @patch.object(DataStackEngineer, "_handle_monitoring")
    @pytest.mark.asyncio
    async def test_execute_task_monitoring(self, mock_handler):
        """Test task execution for monitoring."""
        # Mock monitoring handler
        mock_handler.return_value = {
            "success": True,
            "overall_health": True,
            "monitoring_results": {},
        }

        request = WorkflowRequest(
            user_prompt="check system health",
            agent_role=AgentRole.DATA_PLATFORM_ENGINEER,
        )

        response = await self.agent.execute_task(request)

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertTrue(response.output["success"])
        mock_handler.assert_called_once_with(request)

    @patch.object(DataStackEngineer, "_handle_general_request")
    @pytest.mark.asyncio
    async def test_execute_task_general(self, mock_handler):
        """Test task execution for general requests."""
        mock_handler.return_value = {
            "success": True,
            "message": "General request processed",
        }

        request = WorkflowRequest(
            user_prompt="tell me about the system",
            agent_role=AgentRole.DATA_PLATFORM_ENGINEER,
        )

        response = await self.agent.execute_task(request)

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        mock_handler.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_execute_task_error_handling(self):
        """Test task execution error handling."""
        # Mock a method to raise an exception
        with patch.object(
            self.agent, "_analyze_task_type", side_effect=Exception("Test error")
        ):
            request = WorkflowRequest(
                user_prompt="cause an error",
                agent_role=AgentRole.DATA_PLATFORM_ENGINEER,
            )

            response = await self.agent.execute_task(request)

            self.assertEqual(response.status, ResponseStatus.ERROR)
            self.assertFalse(response.output["success"])
            self.assertIn("Test error", response.error_message)

    @patch("agents.data_stack_engineer.DockerTools")
    @patch("agents.data_stack_engineer.MeltanoTools")
    @patch("agents.data_stack_engineer.DbtTools")
    @patch("agents.data_stack_engineer.DuckDBTools")
    @pytest.mark.asyncio
    async def test_handle_deployment(
        self, mock_duckdb, mock_dbt, mock_meltano, mock_docker
    ):
        """Test deployment handling."""
        # Mock tool responses
        mock_docker.return_value.get_service_status.return_value = {"success": True}
        mock_docker.return_value.start_services.return_value = {"success": True}
        mock_meltano.return_value.validate_project.return_value = {"success": True}
        mock_dbt.return_value.run_dbt_command.return_value = {"success": True}
        mock_dbt.return_value.compile_models.return_value = {"success": True}
        mock_duckdb.return_value.execute_query.return_value = {"success": True}

        request = WorkflowRequest(
            user_prompt="deploy infrastructure",
            agent_role=AgentRole.DATA_PLATFORM_ENGINEER,
        )

        result = await self.agent._handle_deployment(request)

        self.assertTrue(result["success"])
        self.assertIn("step_results", result)
        self.assertIn("next_actions", result)

    @patch("agents.data_stack_engineer.DockerTools")
    @patch("agents.data_stack_engineer.DuckDBTools")
    @pytest.mark.asyncio
    async def test_handle_deployment_failure(self, mock_duckdb, mock_docker):
        """Test deployment handling with failure."""
        # Mock tool failure
        mock_docker.return_value.get_service_status.return_value = {"success": False}

        request = WorkflowRequest(
            user_prompt="deploy infrastructure",
            agent_role=AgentRole.DATA_PLATFORM_ENGINEER,
        )

        result = await self.agent._handle_deployment(request)

        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("next_actions", result)

    @patch("agents.data_stack_engineer.DockerTools")
    @patch("agents.data_stack_engineer.DuckDBTools")
    @pytest.mark.asyncio
    async def test_handle_monitoring(self, mock_duckdb, mock_docker):
        """Test monitoring handling."""
        # Mock tool responses
        mock_docker.return_value.get_service_status.return_value = {"success": True}
        mock_docker.return_value.get_resource_usage.return_value = {"success": True}
        mock_duckdb.return_value.get_database_stats.return_value = {"success": True}
        mock_duckdb.return_value.get_data_quality_metrics.return_value = {
            "success": True
        }

        request = WorkflowRequest(
            user_prompt="monitor system", agent_role=AgentRole.DATA_PLATFORM_ENGINEER
        )

        result = await self.agent._handle_monitoring(request)

        self.assertTrue(result["success"])
        self.assertIn("overall_health", result)
        self.assertIn("monitoring_results", result)
        self.assertIn("health_score", result)

    @patch("agents.data_stack_engineer.MeltanoTools")
    @patch("agents.data_stack_engineer.DbtTools")
    @patch("agents.data_stack_engineer.DuckDBTools")
    @pytest.mark.asyncio
    async def test_handle_pipeline_execution(self, mock_duckdb, mock_dbt, mock_meltano):
        """Test pipeline execution handling."""
        # Mock successful pipeline execution
        mock_meltano.return_value.extract_load_data.return_value = {
            "success": True,
            "metrics": {"extracted_records": 100},
        }
        mock_dbt.return_value.run_models.return_value = {"success": True}
        mock_dbt.return_value.test_models.return_value = {"success": True}
        mock_duckdb.return_value.get_data_quality_metrics.return_value = {
            "success": True
        }

        request = WorkflowRequest(
            user_prompt="run the pipeline", agent_role=AgentRole.DATA_PLATFORM_ENGINEER
        )

        result = await self.agent._handle_pipeline_execution(request)

        self.assertTrue(result["success"])
        self.assertIn("meltano_metrics", result)
        self.assertIn("dbt_result", result)
        self.assertIn("test_results", result)
        self.assertIn("data_quality", result)

    @patch("agents.data_stack_engineer.MeltanoTools")
    @pytest.mark.asyncio
    async def test_handle_pipeline_execution_failure(self, mock_meltano):
        """Test pipeline execution handling with failure."""
        # Mock Meltano failure
        mock_meltano.return_value.extract_load_data.return_value = {
            "success": False,
            "error": "ELT failed",
        }

        request = WorkflowRequest(
            user_prompt="run the pipeline", agent_role=AgentRole.DATA_PLATFORM_ENGINEER
        )

        result = await self.agent._handle_pipeline_execution(request)

        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("next_actions", result)

    @patch("agents.data_stack_engineer.DockerTools")
    @patch("agents.data_stack_engineer.DuckDBTools")
    @patch("agents.data_stack_engineer.MeltanoTools")
    @patch("agents.data_stack_engineer.DbtTools")
    @pytest.mark.asyncio
    async def test_handle_health_check(
        self, mock_dbt, mock_meltano, mock_duckdb, mock_docker
    ):
        """Test health check handling."""
        # Mock all health checks as successful
        mock_docker.return_value.get_service_status.return_value = {"success": True}
        mock_duckdb.return_value.get_database_stats.return_value = {"success": True}
        mock_meltano.return_value.validate_project.return_value = {"success": True}
        mock_dbt.return_value.compile_models.return_value = {"success": True}

        request = WorkflowRequest(
            user_prompt="health check", agent_role=AgentRole.DATA_PLATFORM_ENGINEER
        )

        result = await self.agent._handle_health_check(request)

        self.assertTrue(result["success"])
        self.assertTrue(result["overall_healthy"])
        self.assertIn("health_checks", result)
        self.assertIn("timestamp", result)

    @patch("agents.data_stack_engineer.DockerTools")
    @pytest.mark.asyncio
    async def test_handle_health_check_failure(self, mock_docker):
        """Test health check handling with failures."""
        # Mock Docker service failure
        mock_docker.return_value.get_service_status.return_value = {"success": False}

        request = WorkflowRequest(
            user_prompt="health check", agent_role=AgentRole.DATA_PLATFORM_ENGINEER
        )

        result = await self.agent._handle_health_check(request)

        self.assertTrue(result["success"])  # Health check itself succeeds
        self.assertFalse(result["overall_healthy"])  # But overall health is poor
        self.assertIn("health_checks", result)

    def test_calculate_health_score(self):
        """Test health score calculation."""
        # Test with all successful results
        monitoring_results = {
            "service1": {"success": True},
            "service2": {"success": True},
            "service3": {"success": True},
        }

        score = self.agent._calculate_health_score(monitoring_results)
        self.assertEqual(score, 1.0)

        # Test with mixed results
        monitoring_results = {
            "service1": {"success": True},
            "service2": {"success": False},
            "service3": {"success": True},
        }

        score = self.agent._calculate_health_score(monitoring_results)
        self.assertAlmostEqual(score, 0.667, places=2)

        # Test with all failed results
        monitoring_results = {
            "service1": {"success": False},
            "service2": {"success": False},
        }

        score = self.agent._calculate_health_score(monitoring_results)
        self.assertEqual(score, 0.0)

    def test_generate_health_recommendations(self):
        """Test health recommendations generation."""
        # Test with failed services
        monitoring_results = {
            "docker_services": {"success": False},
            "database_connection": {"success": True},
            "pipeline_status": {"success": False},
        }

        recommendations = self.agent._generate_health_recommendations(
            monitoring_results
        )

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("docker_services" in rec for rec in recommendations))
        self.assertTrue(any("pipeline_status" in rec for rec in recommendations))

        # Test with all services healthy
        monitoring_results = {
            "service1": {"success": True},
            "service2": {"success": True},
        }

        recommendations = self.agent._generate_health_recommendations(
            monitoring_results
        )
        self.assertIn("System is healthy - continue monitoring", recommendations)


if __name__ == "__main__":
    # Run the tests
    unittest.main()
