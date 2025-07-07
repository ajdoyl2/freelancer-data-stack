#!/usr/bin/env python3
"""
Test suite for the natural language interface.

This module tests the prompt handling, workflow execution, and response
formatting components of the natural language interface.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import AgentRole, WorkflowPriority, WorkflowRequest
from interface.prompt_handler import IntentType, PromptHandler, TaskComplexity
from interface.response_formatter import OutputFormat, ResponseFormatter
from interface.workflow_executor import WorkflowExecutor


class TestPromptHandler:
    """Test prompt analysis and processing functionality."""

    @pytest.fixture
    def handler(self):
        return PromptHandler()

    @pytest.mark.asyncio
    async def test_analyze_simple_deployment_prompt(self, handler):
        """Test analysis of simple deployment prompts."""
        prompt = "Deploy the Docker services"

        analysis = await handler.analyze_prompt(prompt)

        assert analysis["intent"] == IntentType.DEPLOYMENT
        assert analysis["complexity"] == TaskComplexity.SIMPLE
        assert AgentRole.DATA_PLATFORM_ENGINEER in analysis["required_agents"]
        assert analysis["confidence"] >= 0.8

    @pytest.mark.asyncio
    async def test_analyze_analytics_prompt(self, handler):
        """Test analysis of analytics-focused prompts."""
        prompt = "Create a dbt model for customer analytics"

        analysis = await handler.analyze_prompt(prompt)

        assert analysis["intent"] == IntentType.ANALYTICS
        assert AgentRole.ANALYTICS_ENGINEER in analysis["required_agents"]
        assert analysis["confidence"] >= 0.8

    @pytest.mark.asyncio
    async def test_analyze_complex_multi_agent_prompt(self, handler):
        """Test analysis of complex prompts requiring multiple agents."""
        prompt = (
            "Set up a complete data pipeline from CSV files to analytics dashboards"
        )

        analysis = await handler.analyze_prompt(prompt)

        assert analysis["complexity"] == TaskComplexity.MULTI_AGENT
        assert len(analysis["required_agents"]) > 1
        assert AgentRole.DATA_ENGINEER in analysis["required_agents"]
        assert AgentRole.DATA_PLATFORM_ENGINEER in analysis["required_agents"]
        assert analysis["confidence"] >= 0.8

    @pytest.mark.asyncio
    async def test_analyze_monitoring_prompt(self, handler):
        """Test analysis of monitoring and operational prompts."""
        prompt = "Monitor the health of all services and alert on failures"

        analysis = await handler.analyze_prompt(prompt)

        assert analysis["intent"] == IntentType.MONITORING
        assert AgentRole.DATA_PLATFORM_ENGINEER in analysis["required_agents"]

    @pytest.mark.asyncio
    async def test_analyze_reporting_prompt(self, handler):
        """Test analysis of reporting and visualization prompts."""
        prompt = "Generate a monthly revenue report with visualizations"

        analysis = await handler.analyze_prompt(prompt)

        assert analysis["intent"] == IntentType.REPORTING
        assert AgentRole.DATA_ANALYST in analysis["required_agents"]

    @pytest.mark.asyncio
    async def test_create_workflow_request(self, handler):
        """Test creating workflow requests from prompts."""
        prompt = "Check the status of our data pipeline"

        workflow_request = await handler.create_workflow_request(prompt)

        assert isinstance(workflow_request, WorkflowRequest)
        assert workflow_request.user_prompt == prompt
        assert len(workflow_request.agents_involved) > 0
        assert workflow_request.priority in WorkflowPriority
        assert workflow_request.request_id.startswith("req_")

    @pytest.mark.asyncio
    async def test_extract_parameters(self, handler):
        """Test parameter extraction from prompts."""
        prompt = "Create a dbt model for customer data from the users table"

        parameters = await handler.extract_parameters(prompt)

        assert isinstance(parameters, dict)
        assert "entity" in parameters
        assert "source" in parameters
        assert parameters["entity"] == "customer"
        assert parameters["source"] == "users table"

    @pytest.mark.asyncio
    async def test_ambiguous_prompt_handling(self, handler):
        """Test handling of ambiguous prompts."""
        prompt = "Fix the data"  # Very ambiguous

        analysis = await handler.analyze_prompt(prompt)

        # Should still provide some analysis but with lower confidence
        assert analysis["confidence"] < 0.7
        assert len(analysis["required_agents"]) > 0

    @pytest.mark.asyncio
    async def test_intent_classification_accuracy(self, handler):
        """Test intent classification accuracy across various prompts."""
        test_cases = [
            ("Deploy containers", IntentType.DEPLOYMENT),
            ("Run dbt models", IntentType.ANALYTICS),
            ("Create dashboard", IntentType.REPORTING),
            ("Monitor services", IntentType.MONITORING),
            ("Ingest CSV data", IntentType.DATA_PIPELINE),
            ("Train ML model", IntentType.MACHINE_LEARNING),
        ]

        for prompt, expected_intent in test_cases:
            analysis = await handler.analyze_prompt(prompt)
            assert analysis["intent"] == expected_intent, f"Failed for prompt: {prompt}"


class TestWorkflowExecutor:
    """Test workflow execution and coordination functionality."""

    @pytest.fixture
    def executor(self):
        return WorkflowExecutor()

    @pytest.mark.asyncio
    async def test_process_simple_request(self, executor):
        """Test processing simple single-agent requests."""
        request = "Check Docker container status"

        with patch.object(executor, "_execute_single_agent_workflow") as mock_execute:
            mock_response = Mock()
            mock_response.status = "completed"
            mock_response.content = "All containers running"
            mock_execute.return_value = mock_response

            result = await executor.process_request(request)

            assert result.status == "completed"
            assert "containers" in result.content.lower()

    @pytest.mark.asyncio
    async def test_process_multi_agent_request(self, executor):
        """Test processing complex multi-agent requests."""
        request = "Set up complete data pipeline with monitoring"

        with patch.object(executor, "_execute_multi_agent_workflow") as mock_execute:
            mock_response = Mock()
            mock_response.status = "completed"
            mock_response.content = "Pipeline setup completed"
            mock_execute.return_value = mock_response

            result = await executor.process_request(request)

            assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_determine_execution_strategy(self, executor):
        """Test execution strategy determination."""
        # Single agent workflow
        single_agent_request = WorkflowRequest(
            request_id="test_001",
            user_prompt="Deploy Docker services",
            agents_involved=[AgentRole.DATA_PLATFORM_ENGINEER],
            priority=WorkflowPriority.MEDIUM,
        )

        strategy = executor._determine_execution_strategy(single_agent_request)
        assert strategy["type"] == "single_agent"
        assert strategy["coordination_required"] is False

        # Multi-agent workflow
        multi_agent_request = WorkflowRequest(
            request_id="test_002",
            user_prompt="Complete pipeline setup",
            agents_involved=[
                AgentRole.DATA_PLATFORM_ENGINEER,
                AgentRole.DATA_ENGINEER,
                AgentRole.ANALYTICS_ENGINEER,
            ],
            priority=WorkflowPriority.HIGH,
        )

        strategy = executor._determine_execution_strategy(multi_agent_request)
        assert strategy["type"] == "multi_agent"
        assert strategy["coordination_required"] is True

    @pytest.mark.asyncio
    async def test_error_handling(self, executor):
        """Test error handling in workflow execution."""
        request = "Invalid request that should fail"

        with patch.object(executor.prompt_handler, "analyze_prompt") as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis failed")

            with pytest.raises(Exception):
                await executor.process_request(request)

    @pytest.mark.asyncio
    async def test_request_validation(self, executor):
        """Test request validation before execution."""
        # Valid request
        valid_request = WorkflowRequest(
            request_id="valid_001",
            user_prompt="Valid request",
            agents_involved=[AgentRole.DATA_ENGINEER],
            priority=WorkflowPriority.MEDIUM,
        )

        # Should not raise exception
        await executor._validate_workflow_request(valid_request)

        # Invalid request (empty prompt)
        invalid_request = WorkflowRequest(
            request_id="invalid_001",
            user_prompt="",
            agents_involved=[AgentRole.DATA_ENGINEER],
            priority=WorkflowPriority.MEDIUM,
        )

        with pytest.raises(ValueError):
            await executor._validate_workflow_request(invalid_request)

    @pytest.mark.asyncio
    async def test_workflow_progress_tracking(self, executor):
        """Test workflow progress tracking."""
        request = "Test workflow progress"

        progress_updates = []

        def mock_progress_callback(progress):
            progress_updates.append(progress)

        with patch.object(executor, "_execute_single_agent_workflow") as mock_execute:
            mock_response = Mock()
            mock_response.status = "completed"
            mock_execute.return_value = mock_response

            # Mock progress updates
            executor._progress_callback = mock_progress_callback

            await executor.process_request(request)

            # Should have received progress updates
            assert len(progress_updates) > 0


class TestResponseFormatter:
    """Test response formatting functionality."""

    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    @pytest.mark.asyncio
    async def test_format_success_response(self, formatter):
        """Test formatting successful responses."""
        response = await formatter.format_success_response(
            user_prompt="Test prompt",
            agent_response="Task completed successfully",
            execution_id="exec_001",
            execution_time=2.5,
            output_format=OutputFormat.MARKDOWN,
        )

        assert response["status"] == "success"
        assert response["format"] == OutputFormat.MARKDOWN.value
        assert "Task completed successfully" in response["content"]
        assert response["execution_time"] == 2.5

    @pytest.mark.asyncio
    async def test_format_error_response(self, formatter):
        """Test formatting error responses."""
        response = await formatter.format_error_response(
            user_prompt="Test prompt",
            error_message="Something went wrong",
            execution_id="exec_002",
            output_format=OutputFormat.JSON,
        )

        assert response["status"] == "error"
        assert response["format"] == OutputFormat.JSON.value
        assert "Something went wrong" in response["error_message"]

    @pytest.mark.asyncio
    async def test_format_multi_agent_response(self, formatter):
        """Test formatting multi-agent workflow responses."""
        agent_responses = {
            AgentRole.DATA_PLATFORM_ENGINEER: "Infrastructure deployed",
            AgentRole.DATA_ENGINEER: "Pipeline configured",
            AgentRole.ANALYTICS_ENGINEER: "Models created",
        }

        response = await formatter.format_multi_agent_response(
            user_prompt="Complete setup",
            agent_responses=agent_responses,
            execution_id="exec_003",
            output_format=OutputFormat.MARKDOWN,
        )

        assert response["status"] == "success"
        assert "Infrastructure deployed" in response["content"]
        assert "Pipeline configured" in response["content"]
        assert "Models created" in response["content"]

    def test_format_progress_update(self, formatter):
        """Test progress update formatting."""
        progress = formatter.format_progress_update(
            execution_id="exec_004", message="Processing request", progress=0.5
        )

        assert progress["execution_id"] == "exec_004"
        assert progress["message"] == "Processing request"
        assert progress["progress"] == 0.5
        assert "timestamp" in progress

    @pytest.mark.asyncio
    async def test_format_with_different_output_formats(self, formatter):
        """Test formatting with different output formats."""
        # Test JSON format
        json_response = await formatter.format_success_response(
            user_prompt="Test",
            agent_response="Success",
            execution_id="exec_005",
            output_format=OutputFormat.JSON,
        )
        assert json_response["format"] == "json"

        # Test Markdown format
        md_response = await formatter.format_success_response(
            user_prompt="Test",
            agent_response="Success",
            execution_id="exec_006",
            output_format=OutputFormat.MARKDOWN,
        )
        assert md_response["format"] == "markdown"

        # Test Plain text format
        text_response = await formatter.format_success_response(
            user_prompt="Test",
            agent_response="Success",
            execution_id="exec_007",
            output_format=OutputFormat.PLAIN,
        )
        assert text_response["format"] == "plain"

    @pytest.mark.asyncio
    async def test_format_streaming_response(self, formatter):
        """Test streaming response formatting."""
        chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]

        responses = []
        async for chunk_response in formatter.format_streaming_response(
            chunks=chunks, execution_id="exec_008"
        ):
            responses.append(chunk_response)

        assert len(responses) == len(chunks)
        assert all(resp["execution_id"] == "exec_008" for resp in responses)
        assert responses[0]["content"] == "Chunk 1"
        assert responses[-1]["is_final"] is True


class TestInterfaceIntegration:
    """Integration tests for the complete interface."""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow processing."""
        executor = WorkflowExecutor()

        # Mock agent execution
        with patch("agents.get_agent") as mock_get_agent:
            mock_agent = Mock()
            mock_agent.execute_task = AsyncMock(
                return_value=Mock(
                    content="Task completed", confidence=0.95, recommendations=[]
                )
            )
            mock_get_agent.return_value = mock_agent

            result = await executor.process_request("Deploy Docker services")

            assert result.status in ["success", "completed"]

    @pytest.mark.asyncio
    async def test_prompt_to_response_pipeline(self):
        """Test the complete pipeline from prompt to formatted response."""
        handler = PromptHandler()
        formatter = ResponseFormatter()

        # Analyze prompt
        prompt = "Create analytics dashboard"
        analysis = await handler.analyze_prompt(prompt)

        # Create workflow request
        workflow_request = await handler.create_workflow_request(prompt)

        # Format mock response
        response = await formatter.format_success_response(
            user_prompt=prompt,
            agent_response="Dashboard created successfully",
            execution_id=workflow_request.request_id,
            output_format=OutputFormat.MARKDOWN,
        )

        assert analysis["intent"] == IntentType.REPORTING
        assert AgentRole.DATA_ANALYST in analysis["required_agents"]
        assert response["status"] == "success"
        assert "Dashboard created successfully" in response["content"]

    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """Test error propagation through the interface components."""
        executor = WorkflowExecutor()

        # Test with invalid prompt that should cause errors
        with patch.object(executor.prompt_handler, "analyze_prompt") as mock_analyze:
            mock_analyze.side_effect = ValueError("Invalid prompt")

            with pytest.raises(ValueError):
                await executor.process_request("Invalid prompt")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
