"""Monitoring and metrics collection for MCP servers."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from prometheus_client import Counter, Gauge, Histogram, generate_latest

# Prometheus metrics
MCP_REQUESTS_TOTAL = Counter(
    "mcp_requests_total", "Total MCP requests", ["server", "tool", "status"]
)

MCP_REQUEST_DURATION = Histogram(
    "mcp_request_duration_seconds",
    "MCP request duration",
    ["server", "tool"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

MCP_ACTIVE_CONNECTIONS = Gauge(
    "mcp_active_connections", "Active MCP server connections", ["server"]
)

MCP_CACHE_HITS = Counter("mcp_cache_hits_total", "MCP cache hits", ["server", "tool"])

MCP_CACHE_MISSES = Counter(
    "mcp_cache_misses_total", "MCP cache misses", ["server", "tool"]
)

MCP_ERRORS_TOTAL = Counter(
    "mcp_errors_total", "Total MCP errors", ["server", "tool", "error_type"]
)

MCP_TOKEN_USAGE = Counter(
    "mcp_token_usage_total",
    "Total tokens used by MCP operations",
    ["server", "tool", "model"],
)


class MetricsCollector:
    """Collects and exposes metrics for MCP servers."""

    def __init__(self, server_name: str):
        self.server_name = server_name
        self.start_time = time.time()

        # Set initial active connections to 0
        MCP_ACTIVE_CONNECTIONS.labels(server=server_name).set(0)

    def increment_connection(self):
        """Increment active connection count."""
        MCP_ACTIVE_CONNECTIONS.labels(server=self.server_name).inc()

    def decrement_connection(self):
        """Decrement active connection count."""
        MCP_ACTIVE_CONNECTIONS.labels(server=self.server_name).dec()

    def record_request(self, tool: str, status: str, duration: float):
        """Record a request with its status and duration."""
        MCP_REQUESTS_TOTAL.labels(
            server=self.server_name, tool=tool, status=status
        ).inc()

        MCP_REQUEST_DURATION.labels(server=self.server_name, tool=tool).observe(
            duration
        )

    def record_cache_hit(self, tool: str):
        """Record a cache hit."""
        MCP_CACHE_HITS.labels(server=self.server_name, tool=tool).inc()

    def record_cache_miss(self, tool: str):
        """Record a cache miss."""
        MCP_CACHE_MISSES.labels(server=self.server_name, tool=tool).inc()

    def record_error(self, tool: str, error_type: str):
        """Record an error."""
        MCP_ERRORS_TOTAL.labels(
            server=self.server_name, tool=tool, error_type=error_type
        ).inc()

    def record_token_usage(self, tool: str, model: str, tokens: int):
        """Record token usage for LLM operations."""
        MCP_TOKEN_USAGE.labels(server=self.server_name, tool=tool, model=model).inc(
            tokens
        )

    def get_metrics(self) -> bytes:
        """Get Prometheus metrics in text format."""
        return generate_latest()

    def get_server_stats(self) -> dict[str, Any]:
        """Get server statistics."""
        uptime = time.time() - self.start_time

        return {
            "server": self.server_name,
            "uptime_seconds": uptime,
            "active_connections": MCP_ACTIVE_CONNECTIONS.labels(
                server=self.server_name
            )._value.get(),
            "start_time": self.start_time,
        }


def track_metrics(server_name: str):
    """Decorator to track metrics for MCP tool calls."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tool_name = func.__name__
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)

                # Check if result indicates an error
                if isinstance(result, dict) and result.get("status") == "error":
                    status = "error"

                return result

            except Exception as e:
                status = "error"
                error_type = type(e).__name__

                # Record error metric
                MCP_ERRORS_TOTAL.labels(
                    server=server_name, tool=tool_name, error_type=error_type
                ).inc()

                raise

            finally:
                # Record request metrics
                duration = time.time() - start_time
                MCP_REQUESTS_TOTAL.labels(
                    server=server_name, tool=tool_name, status=status
                ).inc()

                MCP_REQUEST_DURATION.labels(server=server_name, tool=tool_name).observe(
                    duration
                )

        return wrapper

    return decorator
