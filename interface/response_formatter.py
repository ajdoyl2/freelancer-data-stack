"""
Response Formatter

Formats agent responses into user-friendly, structured outputs for different
presentation contexts (CLI, web interface, API responses).
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from agents.base_agent import AgentResponse, AgentRole, ResponseStatus, WorkflowRequest


class OutputFormat(str, Enum):
    """Output format types."""

    MARKDOWN = "markdown"
    JSON = "json"
    PLAIN_TEXT = "plain_text"
    HTML = "html"


class ResponseFormatter:
    """
    Formats AI agent responses for user consumption.

    Provides formatting for:
    - Success responses with results and next actions
    - Error responses with troubleshooting guidance
    - Progress updates and status information
    - Multi-agent workflow summaries
    """

    def __init__(self):
        """Initialize the response formatter."""
        self.logger = logging.getLogger(__name__)

        # Agent role display names
        self.agent_display_names = {
            AgentRole.DATA_PLATFORM_ENGINEER: "Data Platform Engineer",
            AgentRole.DATA_ENGINEER: "Data Engineer",
            AgentRole.ANALYTICS_ENGINEER: "Analytics Engineer",
            AgentRole.DATA_SCIENTIST: "Data Scientist",
            AgentRole.DATA_ANALYST: "Data Analyst",
        }

    async def format_response(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
        output_format: OutputFormat = OutputFormat.MARKDOWN,
    ) -> dict[str, Any]:
        """
        Format an agent response for user presentation.

        Args:
            request: The original workflow request
            response: The agent's response
            execution_strategy: The execution strategy used
            output_format: Desired output format

        Returns:
            Dict[str, Any]: Formatted response
        """
        self.logger.info(f"Formatting response in {output_format} format")

        if response.status == ResponseStatus.SUCCESS:
            return await self._format_success_response(
                request, response, execution_strategy, output_format
            )
        else:
            return await self._format_error_response(
                request, response, execution_strategy, output_format
            )

    async def _format_success_response(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
        output_format: OutputFormat,
    ) -> dict[str, Any]:
        """Format a successful response."""

        if output_format == OutputFormat.MARKDOWN:
            return self._format_success_markdown(request, response, execution_strategy)
        elif output_format == OutputFormat.JSON:
            return self._format_success_json(request, response, execution_strategy)
        elif output_format == OutputFormat.PLAIN_TEXT:
            return self._format_success_text(request, response, execution_strategy)
        else:
            return self._format_success_json(request, response, execution_strategy)

    def _format_success_markdown(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Format success response as Markdown."""

        agent_name = self.agent_display_names.get(
            response.agent_role, response.agent_role.value
        )

        # Build the markdown content
        content_parts = []

        # Header
        content_parts.append("# ✅ Task Completed Successfully")
        content_parts.append(f"**Agent:** {agent_name}")

        if execution_strategy.get("type") == "orchestrated":
            agents_involved = execution_strategy.get("agents_involved", [])
            agent_names = [
                self.agent_display_names.get(role, role.value)
                for role in agents_involved
            ]
            content_parts.append(
                f"**Workflow:** Multi-agent coordination ({', '.join(agent_names)})"
            )

        content_parts.append("")

        # Original request
        content_parts.append("## 📝 Request")
        content_parts.append("```")
        content_parts.append(request.user_prompt)
        content_parts.append("```")
        content_parts.append("")

        # Results
        content_parts.append("## 🎯 Results")

        # Format the main response
        if isinstance(response.output.get("response"), str):
            content_parts.append(response.output["response"])
        else:
            # Format structured output
            for key, value in response.output.items():
                if key != "response":
                    content_parts.append(
                        f"- **{key.replace('_', ' ').title()}:** {value}"
                    )

        content_parts.append("")

        # Next actions
        if response.next_actions:
            content_parts.append("## 🚀 Next Actions")
            for i, action in enumerate(response.next_actions, 1):
                content_parts.append(f"{i}. {action}")
            content_parts.append("")

        # Validation results
        if response.validation_results:
            content_parts.append("## ✅ Validation Results")
            for validation in response.validation_results:
                status_icon = (
                    "✅" if validation.status == ResponseStatus.SUCCESS else "❌"
                )
                content_parts.append(
                    f"{status_icon} **{validation.check_name}:** {validation.message}"
                )
            content_parts.append("")

        # Execution details
        content_parts.append("## ℹ️ Execution Details")
        content_parts.append(
            f"- **Execution Time:** {response.execution_time_ms}ms"
            if response.execution_time_ms
            else "- **Execution Time:** Not measured"
        )
        content_parts.append(f"- **Priority:** {request.priority.value.title()}")
        content_parts.append(
            f"- **Timestamp:** {response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        return {
            "format": "markdown",
            "content": "\n".join(content_parts),
            "summary": f"Task completed successfully by {agent_name}",
            "status": "success",
        }

    def _format_success_json(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Format success response as JSON."""

        return {
            "format": "json",
            "status": "success",
            "summary": f"Task completed successfully by {self.agent_display_names.get(response.agent_role, response.agent_role.value)}",
            "data": {
                "request": {
                    "prompt": request.user_prompt,
                    "priority": request.priority.value,
                    "agents_involved": [role.value for role in request.agents_involved],
                },
                "response": {
                    "agent": response.agent_role.value,
                    "output": response.output,
                    "next_actions": response.next_actions,
                    "validation_results": [
                        {
                            "check_name": v.check_name,
                            "status": v.status.value,
                            "message": v.message,
                            "details": v.details,
                        }
                        for v in response.validation_results
                    ],
                    "execution_time_ms": response.execution_time_ms,
                    "timestamp": response.timestamp.isoformat(),
                },
                "execution_strategy": execution_strategy,
            },
        }

    def _format_success_text(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Format success response as plain text."""

        agent_name = self.agent_display_names.get(
            response.agent_role, response.agent_role.value
        )

        content_parts = []
        content_parts.append(f"SUCCESS: Task completed by {agent_name}")
        content_parts.append("")
        content_parts.append(f"Request: {request.user_prompt}")
        content_parts.append("")

        # Main response
        if isinstance(response.output.get("response"), str):
            content_parts.append("Results:")
            content_parts.append(response.output["response"])
        else:
            content_parts.append("Results:")
            for key, value in response.output.items():
                if key != "response":
                    content_parts.append(f"  {key}: {value}")

        content_parts.append("")

        # Next actions
        if response.next_actions:
            content_parts.append("Next Actions:")
            for i, action in enumerate(response.next_actions, 1):
                content_parts.append(f"  {i}. {action}")

        return {
            "format": "plain_text",
            "content": "\n".join(content_parts),
            "summary": f"Task completed successfully by {agent_name}",
            "status": "success",
        }

    async def _format_error_response(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
        output_format: OutputFormat,
    ) -> dict[str, Any]:
        """Format an error response."""

        if output_format == OutputFormat.MARKDOWN:
            return self._format_error_markdown(request, response, execution_strategy)
        elif output_format == OutputFormat.JSON:
            return self._format_error_json(request, response, execution_strategy)
        else:
            return self._format_error_text(request, response, execution_strategy)

    def _format_error_markdown(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Format error response as Markdown."""

        agent_name = self.agent_display_names.get(
            response.agent_role, response.agent_role.value
        )

        content_parts = []
        content_parts.append("# ❌ Task Failed")
        content_parts.append(f"**Agent:** {agent_name}")
        content_parts.append("")

        # Original request
        content_parts.append("## 📝 Request")
        content_parts.append("```")
        content_parts.append(request.user_prompt)
        content_parts.append("```")
        content_parts.append("")

        # Error details
        content_parts.append("## ⚠️ Error Details")
        if response.error_message:
            content_parts.append(f"**Error:** {response.error_message}")

        if response.output.get("error_details"):
            content_parts.append(f"**Details:** {response.output['error_details']}")

        content_parts.append("")

        # Troubleshooting suggestions
        content_parts.append("## 🔧 Troubleshooting Suggestions")
        troubleshooting_tips = self._generate_troubleshooting_tips(
            response.agent_role, response.error_message or "Unknown error"
        )

        for tip in troubleshooting_tips:
            content_parts.append(f"- {tip}")

        content_parts.append("")

        # Validation results (if any)
        if response.validation_results:
            content_parts.append("## 🔍 Validation Results")
            for validation in response.validation_results:
                status_icon = (
                    "✅" if validation.status == ResponseStatus.SUCCESS else "❌"
                )
                content_parts.append(
                    f"{status_icon} **{validation.check_name}:** {validation.message}"
                )

        return {
            "format": "markdown",
            "content": "\n".join(content_parts),
            "summary": f"Task failed in {agent_name}",
            "status": "error",
        }

    def _format_error_json(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Format error response as JSON."""

        return {
            "format": "json",
            "status": "error",
            "summary": f"Task failed in {self.agent_display_names.get(response.agent_role, response.agent_role.value)}",
            "data": {
                "request": {
                    "prompt": request.user_prompt,
                    "priority": request.priority.value,
                },
                "error": {
                    "agent": response.agent_role.value,
                    "message": response.error_message,
                    "details": response.output.get("error_details"),
                    "timestamp": response.timestamp.isoformat(),
                },
                "troubleshooting": self._generate_troubleshooting_tips(
                    response.agent_role, response.error_message or "Unknown error"
                ),
                "validation_results": [
                    {
                        "check_name": v.check_name,
                        "status": v.status.value,
                        "message": v.message,
                    }
                    for v in response.validation_results
                ],
            },
        }

    def _format_error_text(
        self,
        request: WorkflowRequest,
        response: AgentResponse,
        execution_strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Format error response as plain text."""

        agent_name = self.agent_display_names.get(
            response.agent_role, response.agent_role.value
        )

        content_parts = []
        content_parts.append(f"ERROR: Task failed in {agent_name}")
        content_parts.append("")
        content_parts.append(f"Request: {request.user_prompt}")
        content_parts.append("")
        content_parts.append(f"Error: {response.error_message or 'Unknown error'}")

        if response.output.get("error_details"):
            content_parts.append(f"Details: {response.output['error_details']}")

        return {
            "format": "plain_text",
            "content": "\n".join(content_parts),
            "summary": f"Task failed in {agent_name}",
            "status": "error",
        }

    def _generate_troubleshooting_tips(
        self, agent_role: AgentRole, error_message: str
    ) -> list[str]:
        """Generate troubleshooting tips based on agent role and error."""

        tips = []
        error_lower = error_message.lower()

        # General tips
        tips.append("Check system logs for additional details")
        tips.append("Verify all required services are running")

        # Agent-specific tips
        if agent_role == AgentRole.DATA_PLATFORM_ENGINEER:
            tips.extend(
                [
                    "Verify Docker services are running: `docker-compose ps`",
                    "Check container logs: `docker-compose logs <service_name>`",
                    "Ensure sufficient system resources (memory, disk space)",
                ]
            )

            if "connection" in error_lower:
                tips.append("Check network connectivity and service ports")

        elif agent_role == AgentRole.DATA_ENGINEER:
            tips.extend(
                [
                    "Verify Meltano configuration: `meltano config list`",
                    "Check Airflow DAG status and logs",
                    "Validate data source connections",
                ]
            )

            if "pipeline" in error_lower:
                tips.append("Review pipeline configuration and dependencies")

        elif agent_role == AgentRole.ANALYTICS_ENGINEER:
            tips.extend(
                [
                    "Run dbt debug to check configuration",
                    "Verify model dependencies: `dbt list --models <model_name>+`",
                    "Check SQL syntax and compilation errors",
                ]
            )

            if "compilation" in error_lower:
                tips.append("Review SQL syntax and Jinja templating")

        elif agent_role == AgentRole.DATA_SCIENTIST:
            tips.extend(
                [
                    "Check Jupyter notebook server status",
                    "Verify Python package dependencies",
                    "Review data quality and feature availability",
                ]
            )

        elif agent_role == AgentRole.DATA_ANALYST:
            tips.extend(
                [
                    "Verify Metabase/Evidence dashboard connectivity",
                    "Check data source accessibility",
                    "Review visualization configuration",
                ]
            )

        # Error-specific tips
        if "timeout" in error_lower:
            tips.append("Increase timeout settings or optimize query performance")
        elif "permission" in error_lower:
            tips.append("Check file permissions and access rights")
        elif "not found" in error_lower:
            tips.append("Verify file paths and resource availability")

        return tips

    async def format_error_response(
        self,
        user_prompt: str,
        error_message: str,
        execution_id: str,
        output_format: OutputFormat = OutputFormat.MARKDOWN,
    ) -> dict[str, Any]:
        """
        Format a standalone error response.

        Args:
            user_prompt: The original user prompt
            error_message: The error message
            execution_id: The execution ID
            output_format: Desired output format

        Returns:
            Dict[str, Any]: Formatted error response
        """

        if output_format == OutputFormat.MARKDOWN:
            content_parts = []
            content_parts.append("# ❌ Execution Failed")
            content_parts.append(f"**Execution ID:** {execution_id}")
            content_parts.append("")
            content_parts.append("## 📝 Request")
            content_parts.append("```")
            content_parts.append(user_prompt)
            content_parts.append("```")
            content_parts.append("")
            content_parts.append("## ⚠️ Error")
            content_parts.append(error_message)
            content_parts.append("")
            content_parts.append("## 🔧 General Troubleshooting")
            content_parts.append("- Check system status and logs")
            content_parts.append("- Verify all services are running")
            content_parts.append("- Try simplifying the request")

            return {
                "format": "markdown",
                "content": "\n".join(content_parts),
                "summary": "Execution failed",
                "status": "error",
            }
        else:
            return {
                "format": "json",
                "status": "error",
                "summary": "Execution failed",
                "data": {
                    "execution_id": execution_id,
                    "request": user_prompt,
                    "error": error_message,
                    "timestamp": datetime.now().isoformat(),
                },
            }

    def format_progress_update(
        self,
        execution_id: str,
        message: str,
        progress: float,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Format a progress update."""

        return {
            "type": "progress",
            "execution_id": execution_id,
            "message": message,
            "progress": progress,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }
