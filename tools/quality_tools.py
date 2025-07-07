"""
Quality Tools

Provides Great Expectations and data quality functionality for all agents.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional


class QualityTools:
    """
    Tools for data quality validation and Great Expectations operations.

    Provides functionality for:
    - Data profiling and expectation generation
    - Checkpoint creation and execution
    - Data validation and testing
    - Quality reporting and monitoring
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Quality tools."""
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()
        self.ge_project_path = self.project_root / "quality" / "great_expectations"

    async def run_ge_command(self, command: List[str]) -> Dict[str, Any]:
        """Run a Great Expectations CLI command."""
        try:
            full_command = ["great_expectations"] + command

            process = await asyncio.create_subprocess_exec(
                *full_command,
                cwd=self.ge_project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "command": " ".join(full_command)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(["great_expectations"] + command)
            }

    async def create_checkpoint(self, checkpoint_name: str, suite_name: str) -> Dict[str, Any]:
        """Create a new checkpoint."""
        command = ["checkpoint", "new", checkpoint_name]

        result = await self.run_ge_command(command)

        return {
            "success": result["success"],
            "checkpoint_name": checkpoint_name,
            "suite_name": suite_name,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", "")
        }

    async def run_checkpoint(self, checkpoint_name: str) -> Dict[str, Any]:
        """Run a checkpoint to validate data."""
        command = ["checkpoint", "run", checkpoint_name]

        result = await self.run_ge_command(command)

        return {
            "success": result["success"],
            "checkpoint_name": checkpoint_name,
            "validation_results": result.get("stdout", ""),
            "errors": result.get("stderr", "")
        }

    async def create_expectation_suite(self, suite_name: str) -> Dict[str, Any]:
        """Create a new expectation suite."""
        command = ["suite", "new", suite_name]

        result = await self.run_ge_command(command)

        return {
            "success": result["success"],
            "suite_name": suite_name,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", "")
        }

    async def profile_dataset(self, datasource_name: str, data_asset_name: str) -> Dict[str, Any]:
        """Profile a dataset to generate basic expectations."""
        command = ["suite", "new", "--profile", datasource_name, data_asset_name]

        result = await self.run_ge_command(command)

        return {
            "success": result["success"],
            "datasource": datasource_name,
            "data_asset": data_asset_name,
            "profile_results": result.get("stdout", ""),
            "errors": result.get("stderr", "")
        }

    async def validate_data(self, suite_name: str, checkpoint_name: Optional[str] = None) -> Dict[str, Any]:
        """Validate data using an expectation suite."""
        if checkpoint_name:
            return await self.run_checkpoint(checkpoint_name)
        else:
            command = ["suite", "validate", suite_name]

            result = await self.run_ge_command(command)

            return {
                "success": result["success"],
                "suite_name": suite_name,
                "validation_results": result.get("stdout", ""),
                "errors": result.get("stderr", "")
            }

    async def list_suites(self) -> Dict[str, Any]:
        """List all expectation suites."""
        command = ["suite", "list"]

        result = await self.run_ge_command(command)

        if result["success"]:
            # Parse suite names from output
            lines = result["stdout"].split("\n")
            suites = [line.strip() for line in lines if line.strip() and not line.startswith("Found")]

            return {
                "success": True,
                "suites": suites,
                "total_suites": len(suites)
            }

        return result

    async def list_checkpoints(self) -> Dict[str, Any]:
        """List all checkpoints."""
        command = ["checkpoint", "list"]

        result = await self.run_ge_command(command)

        if result["success"]:
            # Parse checkpoint names from output
            lines = result["stdout"].split("\n")
            checkpoints = [line.strip() for line in lines if line.strip() and not line.startswith("Found")]

            return {
                "success": True,
                "checkpoints": checkpoints,
                "total_checkpoints": len(checkpoints)
            }

        return result

    async def generate_docs(self) -> Dict[str, Any]:
        """Generate Great Expectations documentation."""
        command = ["docs", "build"]

        result = await self.run_ge_command(command)

        return {
            "success": result["success"],
            "docs_generated": True,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", "")
        }

    def create_basic_expectation(self, column_name: str, expectation_type: str, **kwargs) -> Dict[str, Any]:
        """Create a basic expectation configuration."""
        expectation = {
            "expectation_type": expectation_type,
            "kwargs": {
                "column": column_name,
                **kwargs
            }
        }

        return expectation

    async def add_datasource(self, datasource_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new datasource to Great Expectations."""
        try:
            # Save datasource config to temporary file
            config_path = self.ge_project_path / "temp_datasource_config.json"

            with open(config_path, 'w') as f:
                json.dump(datasource_config, f, indent=2)

            command = ["datasource", "new", "--from-config", str(config_path)]

            result = await self.run_ge_command(command)

            # Clean up temporary file
            config_path.unlink()

            return {
                "success": result["success"],
                "datasource_config": datasource_config,
                "output": result.get("stdout", ""),
                "errors": result.get("stderr", "")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "datasource_config": datasource_config
            }

    async def check_project_config(self) -> Dict[str, Any]:
        """Check Great Expectations project configuration."""
        try:
            config_path = self.ge_project_path / "great_expectations.yml"

            if config_path.exists():
                return {
                    "success": True,
                    "config_exists": True,
                    "config_path": str(config_path),
                    "message": "Great Expectations project configured"
                }
            else:
                return {
                    "success": False,
                    "config_exists": False,
                    "message": "Great Expectations project not initialized"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
