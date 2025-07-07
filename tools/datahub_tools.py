"""
DataHub Tools

Provides DataHub operations for metadata management and data catalog functionality.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any


class DataHubTools:
    """
    Tools for DataHub metadata management and data catalog operations.

    Provides functionality for:
    - Metadata ingestion and publishing
    - Data lineage tracking
    - Dataset documentation and tagging
    - Data discovery and search
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize DataHub tools."""
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()
        self.datahub_config_path = self.project_root / "catalog" / "datahub"

    async def run_datahub_command(self, command: list[str]) -> dict[str, Any]:
        """Run a DataHub CLI command."""
        try:
            full_command = ["datahub"] + command

            process = await asyncio.create_subprocess_exec(
                *full_command,
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
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(["datahub"] + command),
            }

    async def ingest_metadata(self, config_file: str) -> dict[str, Any]:
        """Ingest metadata using a configuration file."""
        command = ["ingest", "-c", config_file]

        result = await self.run_datahub_command(command)

        return {
            "success": result["success"],
            "config_file": config_file,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
            "command": result.get("command", ""),
        }

    async def search_entities(
        self, query: str, entity_type: str | None = None
    ) -> dict[str, Any]:
        """Search for entities in DataHub."""
        command = ["search", "--query", query]

        if entity_type:
            command.extend(["--entity-type", entity_type])

        result = await self.run_datahub_command(command)

        return {
            "success": result["success"],
            "query": query,
            "entity_type": entity_type,
            "results": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
        }

    async def get_dataset_info(self, dataset_urn: str) -> dict[str, Any]:
        """Get information about a specific dataset."""
        command = ["get", "--urn", dataset_urn]

        result = await self.run_datahub_command(command)

        return {
            "success": result["success"],
            "dataset_urn": dataset_urn,
            "info": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
        }

    async def add_tag(self, entity_urn: str, tag: str) -> dict[str, Any]:
        """Add a tag to an entity."""
        command = ["tag", "add", "--urn", entity_urn, "--tag", tag]

        result = await self.run_datahub_command(command)

        return {
            "success": result["success"],
            "entity_urn": entity_urn,
            "tag": tag,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
        }

    async def remove_tag(self, entity_urn: str, tag: str) -> dict[str, Any]:
        """Remove a tag from an entity."""
        command = ["tag", "remove", "--urn", entity_urn, "--tag", tag]

        result = await self.run_datahub_command(command)

        return {
            "success": result["success"],
            "entity_urn": entity_urn,
            "tag": tag,
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
        }

    async def check_connection(self) -> dict[str, Any]:
        """Check DataHub connection status."""
        command = ["check"]

        result = await self.run_datahub_command(command)

        return {
            "success": result["success"],
            "connection_status": "connected" if result["success"] else "disconnected",
            "output": result.get("stdout", ""),
            "errors": result.get("stderr", ""),
        }

    def generate_ingestion_config(
        self, source_type: str, connection_params: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate a DataHub ingestion configuration."""
        config = {
            "source": {"type": source_type, "config": connection_params},
            "sink": {
                "type": "datahub-rest",
                "config": {"server": "http://localhost:8080"},
            },
        }

        return config

    async def save_ingestion_config(
        self, config: dict[str, Any], filename: str
    ) -> dict[str, Any]:
        """Save ingestion configuration to file."""
        try:
            config_path = self.datahub_config_path / filename

            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            return {
                "success": True,
                "config_path": str(config_path),
                "message": f"Configuration saved to {config_path}",
            }

        except Exception as e:
            return {"success": False, "error": str(e), "filename": filename}
