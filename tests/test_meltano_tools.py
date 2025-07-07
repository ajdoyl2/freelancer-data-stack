"""
Unit tests for Meltano Tools

Tests the MeltanoTools class functionality including project validation,
ELT execution, and plugin management.
"""

# Add project root to path
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from tools.meltano_tools import MeltanoTools


class TestMeltanoTools(unittest.TestCase):
    """Test cases for MeltanoTools class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.meltano_tools = MeltanoTools(Path(self.temp_dir))

    def test_init(self):
        """Test MeltanoTools initialization."""
        tools = MeltanoTools()
        self.assertIsInstance(tools, MeltanoTools)
        self.assertEqual(tools.project_root, Path.cwd())

    def test_init_with_path(self):
        """Test MeltanoTools initialization with custom path."""
        custom_path = Path("/custom/path")
        tools = MeltanoTools(custom_path)
        self.assertEqual(tools.project_root, custom_path)

    @patch("tools.meltano_tools.asyncio.create_subprocess_exec")
    @pytest.mark.asyncio
    async def test_run_meltano_command_success(self, mock_subprocess):
        """Test successful Meltano command execution."""
        # Mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"Success output", b"")
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        result = await self.meltano_tools.run_meltano_command(["--version"])

        self.assertTrue(result["success"])
        self.assertEqual(result["returncode"], 0)
        self.assertIn("stdout", result)
        self.assertIn("stderr", result)

        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0]
        self.assertEqual(args[0], "meltano")
        self.assertIn("--version", args)

    @patch("tools.meltano_tools.asyncio.create_subprocess_exec")
    @pytest.mark.asyncio
    async def test_run_meltano_command_failure(self, mock_subprocess):
        """Test failed Meltano command execution."""
        # Mock subprocess failure
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"Error output")
        mock_process.returncode = 1
        mock_subprocess.return_value = mock_process

        result = await self.meltano_tools.run_meltano_command(["invalid-command"])

        self.assertFalse(result["success"])
        self.assertEqual(result["returncode"], 1)
        self.assertIn("Error output", result["stderr"])

    @patch("tools.meltano_tools.asyncio.create_subprocess_exec")
    @pytest.mark.asyncio
    async def test_run_meltano_command_timeout(self, mock_subprocess):
        """Test Meltano command timeout."""
        # Mock subprocess timeout
        mock_subprocess.side_effect = TimeoutError()

        result = await self.meltano_tools.run_meltano_command(
            ["long-running-command"], timeout=1
        )

        self.assertFalse(result["success"])
        self.assertIn("timeout", result["error"].lower())

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_validate_project_success(self, mock_run_command):
        """Test successful project validation."""
        # Mock successful meltano commands
        mock_run_command.side_effect = [
            {"success": True, "stdout": "meltano 3.7.9", "stderr": ""},
            {"success": True, "stdout": "Project valid", "stderr": ""},
            {"success": True, "stdout": "tap-csv\ntarget-duckdb", "stderr": ""},
        ]

        result = await self.meltano_tools.validate_project()

        self.assertTrue(result["success"])
        self.assertIn("meltano_version", result)
        self.assertIn("project_validation", result)
        self.assertIn("installed_plugins", result)

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_validate_project_failure(self, mock_run_command):
        """Test project validation failure."""
        # Mock meltano command failure
        mock_run_command.return_value = {"success": False, "error": "Meltano not found"}

        result = await self.meltano_tools.validate_project()

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_extract_load_data_success(self, mock_run_command):
        """Test successful ELT execution."""
        # Mock successful ELT output
        elt_output = """
        2024-01-01 12:00:00 [INFO] Starting ELT
        2024-01-01 12:00:01 [INFO] Extracted 100 records
        2024-01-01 12:00:02 [INFO] Loaded 100 records
        2024-01-01 12:00:03 [INFO] ELT completed successfully
        """

        mock_run_command.return_value = {
            "success": True,
            "stdout": elt_output,
            "stderr": "",
            "returncode": 0,
        }

        result = await self.meltano_tools.extract_load_data(
            "tap-csv", "target-duckdb", "dev"
        )

        self.assertTrue(result["success"])
        self.assertIn("metrics", result)
        self.assertIn("execution_time_seconds", result)

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(
            ["--environment", "dev", "elt", "tap-csv", "target-duckdb"], timeout=1800
        )

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_extract_load_data_failure(self, mock_run_command):
        """Test ELT execution failure."""
        mock_run_command.return_value = {
            "success": False,
            "error": "ELT failed",
            "returncode": 1,
        }

        result = await self.meltano_tools.extract_load_data(
            "tap-csv", "target-duckdb", "dev"
        )

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_parse_elt_metrics(self):
        """Test ELT metrics parsing."""
        elt_output = """
        2024-01-01 12:00:00 [INFO] Starting extraction
        2024-01-01 12:00:01 [INFO] Extracted 150 records from source
        2024-01-01 12:00:02 [INFO] Loading data to target
        2024-01-01 12:00:03 [INFO] Loaded 150 records successfully
        2024-01-01 12:00:04 [INFO] ELT completed in 4.5 seconds
        """

        metrics = self.meltano_tools._parse_elt_metrics(elt_output)

        self.assertIn("extracted_records", metrics)
        self.assertIn("loaded_records", metrics)
        self.assertIn("execution_time_seconds", metrics)
        self.assertEqual(metrics["extracted_records"], 150)
        self.assertEqual(metrics["loaded_records"], 150)
        self.assertEqual(metrics["execution_time_seconds"], 4.5)

    def test_parse_elt_metrics_no_matches(self):
        """Test ELT metrics parsing with no matches."""
        elt_output = "No useful metrics in this output"

        metrics = self.meltano_tools._parse_elt_metrics(elt_output)

        self.assertEqual(metrics["extracted_records"], 0)
        self.assertEqual(metrics["loaded_records"], 0)
        self.assertEqual(metrics["execution_time_seconds"], 0.0)

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_install_plugin_success(self, mock_run_command):
        """Test successful plugin installation."""
        mock_run_command.return_value = {
            "success": True,
            "stdout": "Successfully installed tap-csv",
            "stderr": "",
        }

        result = await self.meltano_tools.install_plugin("extractor", "tap-csv")

        self.assertTrue(result["success"])
        self.assertIn("output", result)

        # Verify command
        mock_run_command.assert_called_once_with(
            ["add", "extractor", "tap-csv"], timeout=600
        )

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_install_plugin_failure(self, mock_run_command):
        """Test plugin installation failure."""
        mock_run_command.return_value = {"success": False, "error": "Plugin not found"}

        result = await self.meltano_tools.install_plugin("extractor", "invalid-tap")

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_list_plugins(self, mock_run_command):
        """Test plugin listing."""
        plugin_output = """
        extractors:
          - tap-csv
          - tap-postgres
        loaders:
          - target-duckdb
          - target-jsonl
        """

        mock_run_command.return_value = {
            "success": True,
            "stdout": plugin_output,
            "stderr": "",
        }

        result = await self.meltano_tools.list_plugins()

        self.assertTrue(result["success"])
        self.assertIn("plugins", result)

        # Verify command
        mock_run_command.assert_called_once_with(["list", "plugins"])

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_get_plugin_config_success(self, mock_run_command):
        """Test successful plugin configuration retrieval."""
        config_output = """
        {
          "files": ["data.csv"],
          "csv_files_definition": "files_def.json"
        }
        """

        mock_run_command.return_value = {
            "success": True,
            "stdout": config_output,
            "stderr": "",
        }

        result = await self.meltano_tools.get_plugin_config("tap-csv")

        self.assertTrue(result["success"])
        self.assertIn("config", result)

        # Verify command
        mock_run_command.assert_called_once_with(["config", "tap-csv", "list"])

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_test_plugin_connection_success(self, mock_run_command):
        """Test successful plugin connection test."""
        mock_run_command.return_value = {
            "success": True,
            "stdout": "Connection successful",
            "stderr": "",
        }

        result = await self.meltano_tools.test_plugin_connection("tap-csv")

        self.assertTrue(result["success"])
        self.assertIn("test_output", result)

        # Verify command
        mock_run_command.assert_called_once_with(
            ["invoke", "tap-csv", "--test"], timeout=300
        )

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_test_plugin_connection_failure(self, mock_run_command):
        """Test plugin connection test failure."""
        mock_run_command.return_value = {"success": False, "error": "Connection failed"}

        result = await self.meltano_tools.test_plugin_connection("tap-csv")

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_get_run_logs(self, mock_run_command):
        """Test run logs retrieval."""
        log_output = """
        2024-01-01 12:00:00 [INFO] Starting run
        2024-01-01 12:00:01 [INFO] Processing data
        2024-01-01 12:00:02 [INFO] Run completed
        """

        mock_run_command.return_value = {
            "success": True,
            "stdout": log_output,
            "stderr": "",
        }

        result = await self.meltano_tools.get_run_logs("run_123")

        self.assertTrue(result["success"])
        self.assertIn("logs", result)
        self.assertIn("log_lines", result)

        # Verify command
        mock_run_command.assert_called_once_with(["logs", "run_123"])

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_schedule_run_success(self, mock_run_command):
        """Test successful schedule run."""
        mock_run_command.return_value = {
            "success": True,
            "stdout": "Schedule started successfully",
            "stderr": "",
        }

        result = await self.meltano_tools.schedule_run("daily_elt")

        self.assertTrue(result["success"])
        self.assertIn("schedule_output", result)

        # Verify command
        mock_run_command.assert_called_once_with(
            ["schedule", "run", "daily_elt"], timeout=3600
        )

    @patch.object(MeltanoTools, "run_meltano_command")
    @pytest.mark.asyncio
    async def test_get_environments(self, mock_run_command):
        """Test environment listing."""
        env_output = """
        dev:
          description: Development environment
        prod:
          description: Production environment
        """

        mock_run_command.return_value = {
            "success": True,
            "stdout": env_output,
            "stderr": "",
        }

        result = await self.meltano_tools.get_environments()

        self.assertTrue(result["success"])
        self.assertIn("environments", result)

        # Verify command
        mock_run_command.assert_called_once_with(["environment", "list"])


if __name__ == "__main__":
    # Run the tests
    unittest.main()
