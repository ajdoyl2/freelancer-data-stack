"""
Meltano Tools

Provides Meltano ELT operations and management functionality for Data Engineering agents.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any


class MeltanoTools:
    """
    Tools for Meltano ELT operations and data integration management.

    Provides functionality for:
    - Meltano command execution (install, elt, run, invoke)
    - Extractor and loader management
    - Job execution and scheduling
    - Plugin configuration and testing
    - Environment management
    """

    def __init__(self, project_root: Path | None = None):
        """
        Initialize Meltano tools.

        Args:
            project_root: Path to project root directory
        """
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()
        self.meltano_project_path = self.project_root / "data_stack" / "meltano"
        self.meltano_config_path = self.meltano_project_path / "meltano.yml"

    async def run_meltano_command(
        self, command: list[str], working_dir: Path | None = None
    ) -> dict[str, Any]:
        """
        Run a Meltano command asynchronously.

        Args:
            command: Meltano command to execute as list of strings
            working_dir: Working directory for command execution

        Returns:
            Dict[str, Any]: Command execution results
        """
        try:
            # Ensure we're in the Meltano project directory
            cwd = working_dir or self.meltano_project_path

            # Prepend 'meltano' to the command
            full_command = ["meltano"] + command

            process = await asyncio.create_subprocess_exec(
                *full_command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "command": " ".join(full_command),
            }

        except Exception as e:
            self.logger.error(f"Meltano command execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(["meltano"] + command),
            }

    async def install_plugins(self, plugins: list[str] | None = None) -> dict[str, Any]:
        """
        Install Meltano plugins.

        Args:
            plugins: Specific plugins to install (None for all)

        Returns:
            Dict[str, Any]: Installation results
        """
        command = ["install"]

        if plugins:
            command.extend(plugins)

        result = await self.run_meltano_command(command)

        return {
            "success": result["success"],
            "plugins_installed": plugins or "all",
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def extract_load_data(
        self, extractor: str, loader: str, environment: str = "dev"
    ) -> dict[str, Any]:
        """
        Run Meltano ELT pipeline (extract and load).

        Args:
            extractor: Name of the extractor plugin
            loader: Name of the loader plugin
            environment: Meltano environment to use

        Returns:
            Dict[str, Any]: ELT results
        """
        command = ["--environment", environment, "elt", extractor, loader]

        result = await self.run_meltano_command(command)

        # Parse output for extraction/loading metrics
        metrics = self._parse_elt_metrics(result.get("stdout", ""))

        return {
            "success": result["success"],
            "extractor": extractor,
            "loader": loader,
            "environment": environment,
            "metrics": metrics,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    def _parse_elt_metrics(self, output: str) -> dict[str, Any]:
        """Parse Meltano ELT output to extract metrics."""
        lines = output.split("\n")
        metrics = {
            "records_extracted": 0,
            "records_loaded": 0,
            "errors": 0,
            "warnings": 0,
            "execution_time": None,
        }

        for line in lines:
            if "record" in line.lower() and "extracted" in line.lower():
                # Try to extract record count
                try:
                    words = line.split()
                    for _i, word in enumerate(words):
                        if word.isdigit():
                            metrics["records_extracted"] = int(word)
                            break
                except (ValueError, IndexError) as e:
                    self.logger.debug(
                        f"Could not parse records_extracted from line: {line}. Error: {e}"
                    )
            elif "record" in line.lower() and "loaded" in line.lower():
                try:
                    words = line.split()
                    for _i, word in enumerate(words):
                        if word.isdigit():
                            metrics["records_loaded"] = int(word)
                            break
                except (ValueError, IndexError) as e:
                    self.logger.debug(
                        f"Could not parse records_loaded from line: {line}. Error: {e}"
                    )
            elif "ERROR" in line:
                metrics["errors"] += 1
            elif "WARN" in line:
                metrics["warnings"] += 1

        return metrics

    async def run_job(self, job_name: str, environment: str = "dev") -> dict[str, Any]:
        """
        Run a Meltano job.

        Args:
            job_name: Name of the job to run
            environment: Meltano environment to use

        Returns:
            Dict[str, Any]: Job execution results
        """
        command = ["--environment", environment, "run", job_name]

        result = await self.run_meltano_command(command)

        return {
            "success": result["success"],
            "job_name": job_name,
            "environment": environment,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def invoke_plugin(
        self, plugin_name: str, plugin_args: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Invoke a Meltano plugin directly.

        Args:
            plugin_name: Name of the plugin to invoke
            plugin_args: Arguments to pass to the plugin

        Returns:
            Dict[str, Any]: Plugin invocation results
        """
        command = ["invoke", plugin_name]

        if plugin_args:
            command.extend(plugin_args)

        result = await self.run_meltano_command(command)

        return {
            "success": result["success"],
            "plugin": plugin_name,
            "args": plugin_args,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def test_extractor(self, extractor_name: str) -> dict[str, Any]:
        """
        Test a Meltano extractor.

        Args:
            extractor_name: Name of the extractor to test

        Returns:
            Dict[str, Any]: Test results
        """
        result = await self.invoke_plugin(extractor_name, ["--test"])

        return {
            "success": result["success"],
            "extractor": extractor_name,
            "test_passed": result["success"],
            "output": result.get("output", ""),
            "errors": result.get("errors", ""),
        }

    async def get_plugin_config(self, plugin_name: str) -> dict[str, Any]:
        """
        Get configuration for a Meltano plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Dict[str, Any]: Plugin configuration
        """
        command = ["config", plugin_name]

        result = await self.run_meltano_command(command)

        if result["success"]:
            try:
                # Try to parse configuration as JSON
                config_data = json.loads(result["stdout"])
                return {
                    "success": True,
                    "plugin": plugin_name,
                    "config": config_data,
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "plugin": plugin_name,
                    "config": result["stdout"],
                }
        else:
            return result

    async def set_plugin_config(
        self, plugin_name: str, config_key: str, config_value: str
    ) -> dict[str, Any]:
        """
        Set configuration for a Meltano plugin.

        Args:
            plugin_name: Name of the plugin
            config_key: Configuration key to set
            config_value: Configuration value to set

        Returns:
            Dict[str, Any]: Configuration update results
        """
        command = ["config", plugin_name, "set", config_key, config_value]

        result = await self.run_meltano_command(command)

        return {
            "success": result["success"],
            "plugin": plugin_name,
            "config_key": config_key,
            "config_value": config_value,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def list_plugins(self, plugin_type: str | None = None) -> dict[str, Any]:
        """
        List Meltano plugins.

        Args:
            plugin_type: Filter by plugin type (extractors, loaders, transforms)

        Returns:
            Dict[str, Any]: List of plugins
        """
        command = ["discover"]

        if plugin_type:
            command.append(plugin_type)

        result = await self.run_meltano_command(command)

        if result["success"]:
            plugins = []
            lines = result["stdout"].split("\n")

            for line in lines:
                if line.strip() and not line.startswith("#"):
                    plugins.append(line.strip())

            return {
                "success": True,
                "plugins": plugins,
                "total_plugins": len(plugins),
                "plugin_type": plugin_type or "all",
            }
        else:
            return result

    async def get_environments(self) -> dict[str, Any]:
        """
        List available Meltano environments.

        Returns:
            Dict[str, Any]: Available environments
        """
        command = ["environment", "list"]

        result = await self.run_meltano_command(command)

        if result["success"]:
            environments = [
                line.strip() for line in result["stdout"].split("\n") if line.strip()
            ]

            return {
                "success": True,
                "environments": environments,
                "total_environments": len(environments),
            }
        else:
            return result

    async def validate_project(self) -> dict[str, Any]:
        """
        Validate Meltano project configuration.

        Returns:
            Dict[str, Any]: Validation results
        """
        # Check if meltano.yml exists
        if not self.meltano_config_path.exists():
            return {
                "success": False,
                "error": f"Meltano configuration not found at {self.meltano_config_path}",
                "project_valid": False,
            }

        # Try to run a simple Meltano command to validate setup
        result = await self.run_meltano_command(["--version"])

        return {
            "success": result["success"],
            "project_valid": result["success"],
            "config_path": str(self.meltano_config_path),
            "version_info": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
        }

    async def get_job_status(self, job_name: str) -> dict[str, Any]:
        """
        Get status of a Meltano job.

        Args:
            job_name: Name of the job

        Returns:
            Dict[str, Any]: Job status information
        """
        # Meltano doesn't have built-in job status, so we'll check recent logs
        command = ["state", "list"]

        result = await self.run_meltano_command(command)

        return {
            "success": result["success"],
            "job_name": job_name,
            "status_info": result.get("stdout", ""),
            "command": result.get("command", ""),
        }

    async def reset_state(self, extractor_name: str) -> dict[str, Any]:
        """
        Reset state for a Meltano extractor.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Dict[str, Any]: State reset results
        """
        command = ["state", "clear", extractor_name]

        result = await self.run_meltano_command(command)

        return {
            "success": result["success"],
            "extractor": extractor_name,
            "state_reset": result["success"],
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def schedule_job(
        self, job_name: str, schedule_interval: str
    ) -> dict[str, Any]:
        """
        Schedule a Meltano job.

        Args:
            job_name: Name of the job to schedule
            schedule_interval: Cron-style schedule interval

        Returns:
            Dict[str, Any]: Scheduling results
        """
        # This would typically integrate with Airflow or other scheduler
        # For now, we'll return a placeholder response
        return {
            "success": True,
            "job_name": job_name,
            "schedule_interval": schedule_interval,
            "message": "Job scheduling requires Airflow integration",
            "scheduled": False,
        }

    async def get_logs(self, lines: int = 100) -> dict[str, Any]:
        """
        Get recent Meltano logs.

        Args:
            lines: Number of log lines to retrieve

        Returns:
            Dict[str, Any]: Log information
        """
        # Look for Meltano log files in the project
        log_patterns = [
            self.meltano_project_path / "logs" / "meltano.log",
            self.meltano_project_path / ".meltano" / "logs" / "meltano.log",
        ]

        for log_path in log_patterns:
            if log_path.exists():
                try:
                    with open(log_path) as f:
                        all_lines = f.readlines()
                        recent_lines = (
                            all_lines[-lines:] if len(all_lines) > lines else all_lines
                        )

                    return {
                        "success": True,
                        "log_path": str(log_path),
                        "lines": len(recent_lines),
                        "logs": "".join(recent_lines),
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to read logs: {str(e)}",
                        "log_path": str(log_path),
                    }

        return {
            "success": False,
            "error": "No Meltano log files found",
            "searched_paths": [str(p) for p in log_patterns],
        }
