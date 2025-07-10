"""Base MCP server implementation with common functionality."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

from mcp.server import FastMCP
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MCPConfig(BaseModel):
    """Base configuration for MCP servers."""

    name: str
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    auth_enabled: bool = True
    monitoring_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes default


class BaseMCPServer(ABC):
    """Base class for all MCP servers with common functionality."""

    def __init__(self, config: MCPConfig):
        self.config = config
        self.mcp = FastMCP(name=config.name, version=config.version)
        self._setup_health_endpoint()
        self._setup_error_handling()
        self.is_healthy = True

    def _setup_health_endpoint(self):
        """Setup health check endpoint."""

        @self.mcp.tool()
        async def health() -> dict[str, Any]:
            """Check server health status."""
            return await self.health_check()

    def _setup_error_handling(self):
        """Setup global error handling."""

        @self.mcp.error_handler()
        async def handle_error(error: Exception) -> dict[str, Any]:
            logger.error(f"MCP server error: {error}", exc_info=True)
            return {
                "error": str(error),
                "type": type(error).__name__,
                "status": "error",
            }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the server."""
        try:
            # Default health check - can be overridden
            checks = await self._perform_health_checks()

            all_healthy = all(check.get("healthy", False) for check in checks.values())

            return {
                "status": "healthy" if all_healthy else "unhealthy",
                "server": self.config.name,
                "version": self.config.version,
                "checks": checks,
                "timestamp": asyncio.get_event_loop().time(),
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "server": self.config.name, "error": str(e)}

    @abstractmethod
    async def _perform_health_checks(self) -> dict[str, dict[str, Any]]:
        """Perform server-specific health checks.

        Returns:
            Dict mapping check names to results with 'healthy' bool
        """
        pass

    @abstractmethod
    async def initialize(self):
        """Initialize server-specific resources."""
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup server-specific resources."""
        pass

    async def start(self):
        """Start the MCP server."""
        try:
            await self.initialize()
            logger.info(
                f"Starting {self.config.name} on {self.config.host}:{self.config.port}"
            )
            await self.mcp.run()
        except Exception as e:
            logger.error(f"Failed to start {self.config.name}: {e}")
            raise
        finally:
            await self.cleanup()

    def register_tool(self, func):
        """Register a tool with the MCP server."""
        return self.mcp.tool()(func)

    def register_resource(self, func):
        """Register a resource with the MCP server."""
        return self.mcp.resource()(func)
