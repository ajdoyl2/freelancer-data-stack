"""
dbt Tools

Provides dbt operations and management functionality for Analytics Engineer agents.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any


class DbtTools:
    """
    Tools for dbt operations and data transformation management.

    Provides functionality for:
    - dbt command execution (run, test, compile, docs)
    - Model management and generation
    - Test creation and validation
    - Documentation generation
    - Project configuration management
    """

    def __init__(self, project_root: Path | None = None):
        """
        Initialize dbt tools.

        Args:
            project_root: Path to project root directory
        """
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()
        self.dbt_project_path = self.project_root / "transformation" / "dbt"
        self.profiles_dir = self.dbt_project_path / "profiles"

    async def run_dbt_command(
        self, command: list[str], working_dir: Path | None = None
    ) -> dict[str, Any]:
        """
        Run a dbt command asynchronously.

        Args:
            command: dbt command to execute as list of strings
            working_dir: Working directory for command execution

        Returns:
            Dict[str, Any]: Command execution results
        """
        try:
            # Ensure we're in the dbt project directory
            cwd = working_dir or self.dbt_project_path

            # Prepend 'dbt' to the command
            full_command = ["dbt"] + command

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
            self.logger.error(f"dbt command execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(["dbt"] + command),
            }

    async def compile_models(self, models: list[str] | None = None) -> dict[str, Any]:
        """
        Compile dbt models.

        Args:
            models: Specific models to compile (None for all)

        Returns:
            Dict[str, Any]: Compilation results
        """
        command = ["compile"]

        if models:
            command.extend(["--models"] + models)

        result = await self.run_dbt_command(command)

        return {
            "success": result["success"],
            "models_compiled": models or "all",
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def run_models(
        self, models: list[str] | None = None, full_refresh: bool = False
    ) -> dict[str, Any]:
        """
        Run dbt models to materialize them.

        Args:
            models: Specific models to run (None for all)
            full_refresh: Whether to perform a full refresh

        Returns:
            Dict[str, Any]: Run results
        """
        command = ["run"]

        if models:
            command.extend(["--models"] + models)

        if full_refresh:
            command.append("--full-refresh")

        result = await self.run_dbt_command(command)

        return {
            "success": result["success"],
            "models_run": models or "all",
            "full_refresh": full_refresh,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def test_models(self, models: list[str] | None = None) -> dict[str, Any]:
        """
        Run dbt tests.

        Args:
            models: Specific models to test (None for all)

        Returns:
            Dict[str, Any]: Test results
        """
        command = ["test"]

        if models:
            command.extend(["--models"] + models)

        result = await self.run_dbt_command(command)

        # Parse test results from output
        test_summary = self._parse_test_results(result.get("stdout", ""))

        return {
            "success": result["success"],
            "models_tested": models or "all",
            "test_summary": test_summary,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    def _parse_test_results(self, output: str) -> dict[str, Any]:
        """Parse dbt test output to extract summary information."""
        lines = output.split("\n")
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": 0,
            "warnings": 0,
        }

        for line in lines:
            if "PASS" in line:
                summary["passed_tests"] += 1
                summary["total_tests"] += 1
            elif "FAIL" in line:
                summary["failed_tests"] += 1
                summary["total_tests"] += 1
            elif "ERROR" in line:
                summary["errors"] += 1
            elif "WARN" in line:
                summary["warnings"] += 1

        return summary

    async def generate_docs(self) -> dict[str, Any]:
        """
        Generate dbt documentation.

        Returns:
            Dict[str, Any]: Documentation generation results
        """
        # Generate docs
        docs_result = await self.run_dbt_command(["docs", "generate"])

        if docs_result["success"]:
            # Serve docs (non-blocking)
            serve_command = ["docs", "serve", "--port", "8080"]
            serve_result = await self.run_dbt_command(serve_command)

            return {
                "success": True,
                "docs_generated": True,
                "docs_served": serve_result["success"],
                "docs_url": (
                    "http://localhost:8080" if serve_result["success"] else None
                ),
                "output": docs_result.get("stdout", ""),
                "errors": docs_result.get("stderr", ""),
            }
        else:
            return docs_result

    async def build_project(self) -> dict[str, Any]:
        """
        Build the entire dbt project (run + test).

        Returns:
            Dict[str, Any]: Build results
        """
        result = await self.run_dbt_command(["build"])

        return {
            "success": result["success"],
            "project_built": True,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def debug_project(self) -> dict[str, Any]:
        """
        Debug dbt project configuration.

        Returns:
            Dict[str, Any]: Debug information
        """
        result = await self.run_dbt_command(["debug"])

        return {
            "success": result["success"],
            "debug_info": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def list_models(self, model_type: str | None = None) -> dict[str, Any]:
        """
        List dbt models in the project.

        Args:
            model_type: Filter by model type (model, test, snapshot, etc.)

        Returns:
            Dict[str, Any]: List of models
        """
        command = ["list"]

        if model_type:
            command.extend(["--resource-type", model_type])

        result = await self.run_dbt_command(command)

        if result["success"]:
            models = [
                line.strip() for line in result["stdout"].split("\n") if line.strip()
            ]

            return {
                "success": True,
                "models": models,
                "total_models": len(models),
                "model_type": model_type or "all",
            }
        else:
            return result

    async def run_operation(
        self, operation_name: str, args: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Run a dbt operation (macro).

        Args:
            operation_name: Name of the operation to run
            args: Arguments to pass to the operation

        Returns:
            Dict[str, Any]: Operation results
        """
        command = ["run-operation", operation_name]

        if args:
            # Convert args to dbt vars format
            vars_str = json.dumps(args)
            command.extend(["--vars", vars_str])

        result = await self.run_dbt_command(command)

        return {
            "success": result["success"],
            "operation": operation_name,
            "args": args,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def snapshot_models(
        self, snapshots: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Run dbt snapshots.

        Args:
            snapshots: Specific snapshots to run (None for all)

        Returns:
            Dict[str, Any]: Snapshot results
        """
        command = ["snapshot"]

        if snapshots:
            command.extend(["--models"] + snapshots)

        result = await self.run_dbt_command(command)

        return {
            "success": result["success"],
            "snapshots_run": snapshots or "all",
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def get_model_dependencies(self, model_name: str) -> dict[str, Any]:
        """
        Get dependencies for a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Dict[str, Any]: Model dependencies
        """
        # Use dbt list with graph selector to get dependencies
        command = ["list", "--models", f"+{model_name}"]

        result = await self.run_dbt_command(command)

        if result["success"]:
            dependencies = [
                line.strip() for line in result["stdout"].split("\n") if line.strip()
            ]
            # Remove the model itself from dependencies
            dependencies = [dep for dep in dependencies if dep != model_name]

            return {
                "success": True,
                "model": model_name,
                "dependencies": dependencies,
                "total_dependencies": len(dependencies),
            }
        else:
            return result

    async def get_model_descendants(self, model_name: str) -> dict[str, Any]:
        """
        Get models that depend on a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Dict[str, Any]: Model descendants
        """
        # Use dbt list with graph selector to get descendants
        command = ["list", "--models", f"{model_name}+"]

        result = await self.run_dbt_command(command)

        if result["success"]:
            descendants = [
                line.strip() for line in result["stdout"].split("\n") if line.strip()
            ]
            # Remove the model itself from descendants
            descendants = [desc for desc in descendants if desc != model_name]

            return {
                "success": True,
                "model": model_name,
                "descendants": descendants,
                "total_descendants": len(descendants),
            }
        else:
            return result

    async def validate_sql(self, model_path: str) -> dict[str, Any]:
        """
        Validate SQL syntax for a model.

        Args:
            model_path: Path to the model file

        Returns:
            Dict[str, Any]: Validation results
        """
        # Use dbt parse to validate SQL
        result = await self.run_dbt_command(["parse"])

        return {
            "success": result["success"],
            "model_path": model_path,
            "sql_valid": result["success"],
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def get_manifest(self) -> dict[str, Any]:
        """
        Get the dbt manifest.json file contents.

        Returns:
            Dict[str, Any]: Manifest data or error
        """
        manifest_path = self.dbt_project_path / "target" / "manifest.json"

        try:
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest_data = json.load(f)

                return {
                    "success": True,
                    "manifest": manifest_data,
                    "manifest_path": str(manifest_path),
                }
            else:
                return {
                    "success": False,
                    "error": "Manifest file not found. Run dbt compile or parse first.",
                }

        except Exception as e:
            return {"success": False, "error": f"Failed to read manifest: {str(e)}"}
