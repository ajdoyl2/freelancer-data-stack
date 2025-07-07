"""
Docker Tools

Provides Docker and container management functionality for Data Platform Engineer agents.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any


class DockerTools:
    """
    Tools for Docker and container management operations.

    Provides functionality for:
    - Docker Compose service management
    - Container health checking and monitoring
    - Service deployment and scaling
    - Log aggregation and analysis
    """

    def __init__(self, project_root: Path | None = None):
        """
        Initialize Docker tools.

        Args:
            project_root: Path to project root directory containing docker-compose.yml
        """
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()
        self.compose_file = self.project_root / "docker-compose.yml"

    async def run_command(
        self, command: list[str], cwd: Path | None = None
    ) -> dict[str, Any]:
        """
        Run a command asynchronously and return results.

        Args:
            command: Command to execute as list of strings
            cwd: Working directory for command execution

        Returns:
            Dict[str, Any]: Command execution results
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd or self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "command": " ".join(command),
            }

        except Exception as e:
            self.logger.error(f"Command execution failed: {str(e)}")
            return {"success": False, "error": str(e), "command": " ".join(command)}

    async def get_service_status(
        self, service_name: str | None = None
    ) -> dict[str, Any]:
        """
        Get status of Docker Compose services.

        Args:
            service_name: Specific service to check (None for all services)

        Returns:
            Dict[str, Any]: Service status information
        """
        command = ["docker-compose", "ps"]
        if service_name:
            command.append(service_name)

        result = await self.run_command(command)

        if result["success"]:
            # Parse the output to extract service information
            lines = result["stdout"].split("\n")
            services = []

            for line in lines[2:]:  # Skip header lines
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        services.append(
                            {
                                "name": parts[0],
                                "command": " ".join(parts[1:-3]),
                                "state": parts[-3],
                                "ports": parts[-1] if len(parts) > 4 else "",
                            }
                        )

            return {
                "success": True,
                "services": services,
                "total_services": len(services),
            }
        else:
            return result

    async def start_services(self, services: list[str] | None = None) -> dict[str, Any]:
        """
        Start Docker Compose services.

        Args:
            services: List of services to start (None for all services)

        Returns:
            Dict[str, Any]: Start operation results
        """
        command = ["docker-compose", "up", "-d"]
        if services:
            command.extend(services)

        result = await self.run_command(command)

        if result["success"]:
            # Wait a moment for services to initialize
            await asyncio.sleep(5)

            # Get updated status
            status = await self.get_service_status()

            return {
                "success": True,
                "message": f"Started services: {', '.join(services) if services else 'all'}",
                "services_status": status.get("services", []),
            }
        else:
            return result

    async def stop_services(self, services: list[str] | None = None) -> dict[str, Any]:
        """
        Stop Docker Compose services.

        Args:
            services: List of services to stop (None for all services)

        Returns:
            Dict[str, Any]: Stop operation results
        """
        command = ["docker-compose", "stop"]
        if services:
            command.extend(services)

        result = await self.run_command(command)

        return {
            "success": result["success"],
            "message": f"Stopped services: {', '.join(services) if services else 'all'}",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
        }

    async def restart_service(self, service_name: str) -> dict[str, Any]:
        """
        Restart a specific Docker Compose service.

        Args:
            service_name: Name of the service to restart

        Returns:
            Dict[str, Any]: Restart operation results
        """
        # Stop the service
        stop_result = await self.stop_services([service_name])

        if not stop_result["success"]:
            return stop_result

        # Start the service
        start_result = await self.start_services([service_name])

        return {
            "success": start_result["success"],
            "message": f"Restarted service: {service_name}",
            "stop_output": stop_result.get("output", ""),
            "start_output": start_result.get("services_status", []),
        }

    async def get_service_logs(
        self, service_name: str, lines: int = 100, follow: bool = False
    ) -> dict[str, Any]:
        """
        Get logs from a Docker Compose service.

        Args:
            service_name: Name of the service
            lines: Number of log lines to retrieve
            follow: Whether to follow logs (stream)

        Returns:
            Dict[str, Any]: Service logs
        """
        command = ["docker-compose", "logs", "--tail", str(lines)]
        if follow:
            command.append("-f")
        command.append(service_name)

        result = await self.run_command(command)

        return {
            "success": result["success"],
            "service": service_name,
            "logs": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "lines_requested": lines,
        }

    async def check_service_health(self, service_name: str) -> dict[str, Any]:
        """
        Check health of a specific service.

        Args:
            service_name: Name of the service to check

        Returns:
            Dict[str, Any]: Health check results
        """
        # Get service status
        status_result = await self.get_service_status(service_name)

        if not status_result["success"]:
            return {
                "success": False,
                "service": service_name,
                "healthy": False,
                "error": "Could not get service status",
            }

        services = status_result.get("services", [])
        service_info = next((s for s in services if service_name in s["name"]), None)

        if not service_info:
            return {
                "success": True,
                "service": service_name,
                "healthy": False,
                "status": "not_found",
                "message": "Service not found",
            }

        # Check if service is running
        is_running = "Up" in service_info.get("state", "")

        # Additional health checks could be added here
        # (e.g., HTTP health endpoints, database connectivity)

        return {
            "success": True,
            "service": service_name,
            "healthy": is_running,
            "status": service_info.get("state", "unknown"),
            "ports": service_info.get("ports", ""),
            "message": f"Service is {'healthy' if is_running else 'unhealthy'}",
        }

    async def scale_service(self, service_name: str, replicas: int) -> dict[str, Any]:
        """
        Scale a Docker Compose service.

        Args:
            service_name: Name of the service to scale
            replicas: Number of replicas to run

        Returns:
            Dict[str, Any]: Scaling operation results
        """
        command = [
            "docker-compose",
            "up",
            "-d",
            "--scale",
            f"{service_name}={replicas}",
        ]

        result = await self.run_command(command)

        return {
            "success": result["success"],
            "service": service_name,
            "replicas": replicas,
            "message": f"Scaled {service_name} to {replicas} replicas",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
        }

    async def get_resource_usage(self) -> dict[str, Any]:
        """
        Get resource usage statistics for running containers.

        Returns:
            Dict[str, Any]: Resource usage information
        """
        command = [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "table {{.Container}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.NetIO}}\\t{{.BlockIO}}",
        ]

        result = await self.run_command(command)

        if result["success"]:
            lines = result["stdout"].split("\n")
            containers = []

            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 5:
                        containers.append(
                            {
                                "container": parts[0],
                                "cpu_percent": parts[1],
                                "memory_usage": parts[2],
                                "network_io": parts[3],
                                "block_io": parts[4],
                            }
                        )

            return {
                "success": True,
                "containers": containers,
                "timestamp": "now",  # Could add actual timestamp
            }
        else:
            return result

    async def cleanup_resources(self) -> dict[str, Any]:
        """
        Clean up unused Docker resources.

        Returns:
            Dict[str, Any]: Cleanup operation results
        """
        # Remove stopped containers
        cleanup_containers = await self.run_command(
            ["docker", "container", "prune", "-f"]
        )

        # Remove unused images
        cleanup_images = await self.run_command(["docker", "image", "prune", "-f"])

        # Remove unused volumes
        cleanup_volumes = await self.run_command(["docker", "volume", "prune", "-f"])

        # Remove unused networks
        cleanup_networks = await self.run_command(["docker", "network", "prune", "-f"])

        return {
            "success": True,
            "containers_cleaned": cleanup_containers["success"],
            "images_cleaned": cleanup_images["success"],
            "volumes_cleaned": cleanup_volumes["success"],
            "networks_cleaned": cleanup_networks["success"],
            "cleanup_output": {
                "containers": cleanup_containers.get("stdout", ""),
                "images": cleanup_images.get("stdout", ""),
                "volumes": cleanup_volumes.get("stdout", ""),
                "networks": cleanup_networks.get("stdout", ""),
            },
        }

    async def build_services(self, services: list[str] | None = None) -> dict[str, Any]:
        """
        Build Docker Compose services.

        Args:
            services: List of services to build (None for all services)

        Returns:
            Dict[str, Any]: Build operation results
        """
        command = ["docker-compose", "build"]
        if services:
            command.extend(services)

        result = await self.run_command(command)

        return {
            "success": result["success"],
            "message": f"Built services: {', '.join(services) if services else 'all'}",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
        }

    async def get_compose_config(self) -> dict[str, Any]:
        """
        Get Docker Compose configuration.

        Returns:
            Dict[str, Any]: Compose configuration
        """
        command = ["docker-compose", "config"]

        result = await self.run_command(command)

        return {
            "success": result["success"],
            "config": result.get("stdout", ""),
            "error": result.get("stderr", ""),
        }
