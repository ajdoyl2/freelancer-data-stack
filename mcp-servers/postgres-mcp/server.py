"""PostgreSQL MCP server implementation."""

import asyncio
import os
import sys
from typing import Any

import asyncpg
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import (
    BaseMCPServer,
    MCPConfig,
    MetricsCollector,
    require_auth,
    track_metrics,
)


class PostgresQuery(BaseModel):
    """PostgreSQL query parameters."""

    sql: str = Field(..., description="SQL query to execute")
    params: list[Any] | None = Field(None, description="Query parameters")
    timeout: float | None = Field(30.0, description="Query timeout in seconds")


class PostgresConfig(MCPConfig):
    """PostgreSQL-specific configuration."""

    name: str = "postgres-mcp"
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    database: str = os.getenv("POSTGRES_DB", "data_stack")
    user: str = os.getenv("POSTGRES_USER", "postgres")
    password: str = os.getenv("POSTGRES_PASSWORD", "")
    pool_size: int = 10
    max_pool_size: int = 20


class PostgresMCPServer(BaseMCPServer):
    """PostgreSQL MCP server with query and metadata capabilities."""

    def __init__(self, config: PostgresConfig):
        super().__init__(config)
        self.config = config
        self.pool: asyncpg.Pool | None = None
        self.metrics = MetricsCollector("postgres-mcp")
        self._register_tools()
        self._register_resources()

    async def initialize(self):
        """Initialize PostgreSQL connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=self.config.pool_size,
                max_size=self.config.max_pool_size,
                command_timeout=60,
            )
            self.metrics.increment_connection()
        except Exception as e:
            self.is_healthy = False
            raise RuntimeError(f"Failed to connect to PostgreSQL: {e}")

    async def cleanup(self):
        """Close PostgreSQL connection pool."""
        if self.pool:
            await self.pool.close()
            self.metrics.decrement_connection()

    async def _perform_health_checks(self) -> dict[str, dict[str, Any]]:
        """Perform PostgreSQL-specific health checks."""
        checks = {}

        # Connection pool check
        if self.pool:
            try:
                async with self.pool.acquire() as conn:
                    result = await conn.fetchval("SELECT 1")
                    checks["connection"] = {"healthy": result == 1}
            except Exception as e:
                checks["connection"] = {"healthy": False, "error": str(e)}
        else:
            checks["connection"] = {"healthy": False, "error": "No connection pool"}

        # Database status check
        try:
            async with self.pool.acquire() as conn:
                db_status = await conn.fetchrow(
                    """
                    SELECT
                        current_database() as database,
                        version() as version,
                        pg_database_size(current_database()) as size
                """
                )
                checks["database"] = {
                    "healthy": True,
                    "database": db_status["database"],
                    "version": db_status["version"],
                    "size_bytes": db_status["size"],
                }
        except Exception as e:
            checks["database"] = {"healthy": False, "error": str(e)}

        return checks

    def _register_tools(self):
        """Register PostgreSQL tools."""

        @self.register_tool
        @require_auth
        @track_metrics("postgres-mcp")
        async def postgres_query(query: PostgresQuery) -> dict[str, Any]:
            """Execute a PostgreSQL query with parameters."""
            if not self.pool:
                return {"error": "Database connection not available", "status": "error"}

            try:
                async with self.pool.acquire() as conn:
                    # Set query timeout
                    await conn.execute(
                        f"SET statement_timeout = {int(query.timeout * 1000)}"
                    )

                    # Execute query
                    if query.params:
                        rows = await conn.fetch(query.sql, *query.params)
                    else:
                        rows = await conn.fetch(query.sql)

                    # Convert rows to dictionaries
                    results = [dict(row) for row in rows]

                    return {
                        "status": "success",
                        "rows": results,
                        "row_count": len(results),
                    }
            except asyncpg.PostgresError as e:
                return {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "status": "error",
                }

        @self.register_tool
        @require_auth
        @track_metrics("postgres-mcp")
        async def postgres_schema(schema: str = "public") -> dict[str, Any]:
            """Get PostgreSQL schema information."""
            if not self.pool:
                return {"error": "Database connection not available", "status": "error"}

            try:
                async with self.pool.acquire() as conn:
                    # Get tables
                    tables = await conn.fetch(
                        """
                        SELECT
                            table_name,
                            table_type,
                            pg_relation_size(quote_ident(table_name)::regclass) as size_bytes
                        FROM information_schema.tables
                        WHERE table_schema = $1
                        ORDER BY table_name
                    """,
                        schema,
                    )

                    # Get columns for each table
                    table_info = {}
                    for table in tables:
                        columns = await conn.fetch(
                            """
                            SELECT
                                column_name,
                                data_type,
                                is_nullable,
                                column_default
                            FROM information_schema.columns
                            WHERE table_schema = $1 AND table_name = $2
                            ORDER BY ordinal_position
                        """,
                            schema,
                            table["table_name"],
                        )

                        table_info[table["table_name"]] = {
                            "type": table["table_type"],
                            "size_bytes": table["size_bytes"],
                            "columns": [dict(col) for col in columns],
                        }

                    return {"status": "success", "schema": schema, "tables": table_info}
            except Exception as e:
                return {"error": str(e), "status": "error"}

        @self.register_tool
        @require_auth
        @track_metrics("postgres-mcp")
        async def postgres_explain(query: str) -> dict[str, Any]:
            """Get query execution plan."""
            if not self.pool:
                return {"error": "Database connection not available", "status": "error"}

            try:
                async with self.pool.acquire() as conn:
                    # Get execution plan
                    plan = await conn.fetch(
                        f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                    )

                    return {"status": "success", "plan": plan[0]["QUERY PLAN"][0]}
            except Exception as e:
                return {"error": str(e), "status": "error"}

    def _register_resources(self):
        """Register PostgreSQL resources."""

        @self.register_resource
        async def tables() -> dict[str, Any]:
            """List all tables in the database."""
            if not self.pool:
                return {"error": "Database connection not available"}

            try:
                async with self.pool.acquire() as conn:
                    tables = await conn.fetch(
                        """
                        SELECT
                            schemaname,
                            tablename,
                            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as size
                        FROM pg_tables
                        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY schemaname, tablename
                    """
                    )

                    return {"tables": [dict(table) for table in tables]}
            except Exception as e:
                return {"error": str(e)}

        @self.register_resource
        async def views() -> dict[str, Any]:
            """List all views in the database."""
            if not self.pool:
                return {"error": "Database connection not available"}

            try:
                async with self.pool.acquire() as conn:
                    views = await conn.fetch(
                        """
                        SELECT
                            schemaname,
                            viewname,
                            definition
                        FROM pg_views
                        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY schemaname, viewname
                    """
                    )

                    return {"views": [dict(view) for view in views]}
            except Exception as e:
                return {"error": str(e)}

        @self.register_resource
        async def functions() -> dict[str, Any]:
            """List all functions in the database."""
            if not self.pool:
                return {"error": "Database connection not available"}

            try:
                async with self.pool.acquire() as conn:
                    functions = await conn.fetch(
                        """
                        SELECT
                            n.nspname as schema_name,
                            p.proname as function_name,
                            pg_get_function_arguments(p.oid) as arguments,
                            t.typname as return_type
                        FROM pg_proc p
                        JOIN pg_namespace n ON p.pronamespace = n.oid
                        JOIN pg_type t ON p.prorettype = t.oid
                        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY n.nspname, p.proname
                    """
                    )

                    return {"functions": [dict(func) for func in functions]}
            except Exception as e:
                return {"error": str(e)}


async def main():
    """Run the PostgreSQL MCP server."""
    config = PostgresConfig()
    server = PostgresMCPServer(config)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
