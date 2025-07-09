"""
DuckDB Tools

Provides DuckDB database operations and management functionality for AI agents.
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import duckdb


class DuckDBTools:
    """
    Tools for DuckDB database operations and analytics management.

    Provides functionality for:
    - Database connection management
    - Query execution and result handling
    - Data quality metrics and monitoring
    - Performance optimization and analysis
    - Schema management and validation
    """

    def __init__(self, project_root: Path | None = None):
        """
        Initialize DuckDB tools.

        Args:
            project_root: Path to project root directory
        """
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()
        self.default_db_path = "/data/duckdb/analytics.db"
        self.connection_pool = {}

    @asynccontextmanager
    async def get_connection(
        self, db_path: str | None = None, read_only: bool = False
    ) -> AsyncGenerator[duckdb.DuckDBPyConnection, None]:
        """
        Get a DuckDB connection with proper resource management.

        Args:
            db_path: Path to DuckDB database file
            read_only: Whether to open in read-only mode

        Yields:
            DuckDB connection
        """
        db_path = db_path or self.default_db_path
        connection_key = f"{db_path}_{read_only}"

        try:
            # Create connection
            if db_path == ":memory:":
                conn = duckdb.connect(":memory:")
            else:
                # Ensure directory exists
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                conn = duckdb.connect(db_path, read_only=read_only)

            # Configure connection for optimal performance
            conn.execute("PRAGMA enable_progress_bar = true")
            conn.execute("PRAGMA threads = 4")
            conn.execute("PRAGMA memory_limit = '2GB'")

            self.logger.debug(f"Opened DuckDB connection to {db_path}")
            yield conn

        except Exception as e:
            self.logger.error(f"Failed to connect to DuckDB at {db_path}: {str(e)}")
            raise e
        finally:
            try:
                if "conn" in locals():
                    conn.close()
                    self.logger.debug(f"Closed DuckDB connection to {db_path}")
            except Exception as e:
                self.logger.warning(f"Error closing DuckDB connection: {str(e)}")

    async def execute_query(
        self,
        query: str,
        db_path: str | None = None,
        parameters: dict[str, Any] | None = None,
        fetch_results: bool = True,
    ) -> dict[str, Any]:
        """
        Execute a SQL query against DuckDB.

        Args:
            query: SQL query to execute
            db_path: Path to DuckDB database file
            parameters: Query parameters for parameterized queries
            fetch_results: Whether to fetch and return results

        Returns:
            Dict[str, Any]: Query execution results
        """
        try:
            async with self.get_connection(db_path) as conn:
                self.logger.debug(f"Executing query: {query[:100]}...")

                # Handle parameterized queries
                if parameters:
                    result = conn.execute(query, parameters)
                else:
                    result = conn.execute(query)

                if fetch_results:
                    rows = result.fetchall()
                    columns = (
                        [desc[0] for desc in result.description]
                        if result.description
                        else []
                    )

                    return {
                        "success": True,
                        "rows": rows,
                        "columns": columns,
                        "row_count": len(rows),
                        "query": query,
                        "parameters": parameters,
                    }
                else:
                    return {
                        "success": True,
                        "query": query,
                        "parameters": parameters,
                        "message": "Query executed successfully (no results fetched)",
                    }

        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "parameters": parameters,
            }

    async def execute_query_to_df(
        self,
        query: str,
        db_path: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a query and return results as a pandas DataFrame.

        Args:
            query: SQL query to execute
            db_path: Path to DuckDB database file
            parameters: Query parameters

        Returns:
            Dict[str, Any]: Results with DataFrame
        """
        try:
            async with self.get_connection(db_path, read_only=True) as conn:
                self.logger.debug(f"Executing query to DataFrame: {query[:100]}...")

                if parameters:
                    df = conn.execute(query, parameters).df()
                else:
                    df = conn.execute(query).df()

                return {
                    "success": True,
                    "dataframe": df,
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "dtypes": df.dtypes.to_dict(),
                    "memory_usage": df.memory_usage(deep=True).sum(),
                    "query": query,
                }

        except Exception as e:
            self.logger.error(f"Query to DataFrame failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "parameters": parameters,
            }

    async def get_table_info(
        self, table_name: str, schema: str = "main", db_path: str | None = None
    ) -> dict[str, Any]:
        """
        Get detailed information about a table.

        Args:
            table_name: Name of the table
            schema: Schema name
            db_path: Path to DuckDB database file

        Returns:
            Dict[str, Any]: Table information
        """
        try:
            async with self.get_connection(db_path, read_only=True) as conn:
                # Get table schema
                schema_result = conn.execute(
                    f"DESCRIBE {schema}.{table_name}"
                ).fetchall()

                # Get row count
                count_result = conn.execute(
                    f"SELECT COUNT(*) FROM {schema}.{table_name}"
                ).fetchone()

                # Get table size

                # Basic statistics for numeric columns
                numeric_stats = {}
                for column_info in schema_result:
                    column_name = column_info[0]
                    column_type = column_info[1]

                    if (
                        "INT" in column_type.upper()
                        or "FLOAT" in column_type.upper()
                        or "DECIMAL" in column_type.upper()
                    ):
                        stats_query = f"""
                        SELECT
                            MIN({column_name}) as min_val,
                            MAX({column_name}) as max_val,
                            AVG({column_name}) as avg_val,
                            STDDEV({column_name}) as std_val,
                            COUNT(DISTINCT {column_name}) as distinct_count,
                            COUNT({column_name}) as non_null_count
                        FROM {schema}.{table_name}
                        """
                        stats_result = conn.execute(stats_query).fetchone()
                        numeric_stats[column_name] = {
                            "min": stats_result[0],
                            "max": stats_result[1],
                            "avg": stats_result[2],
                            "std": stats_result[3],
                            "distinct_count": stats_result[4],
                            "non_null_count": stats_result[5],
                        }

                return {
                    "success": True,
                    "table_name": table_name,
                    "schema": schema,
                    "columns": [
                        {
                            "name": col[0],
                            "type": col[1],
                            "null": col[2] == "YES",
                            "key": col[3] if len(col) > 3 else None,
                            "default": col[4] if len(col) > 4 else None,
                            "extra": col[5] if len(col) > 5 else None,
                        }
                        for col in schema_result
                    ],
                    "row_count": count_result[0] if count_result else 0,
                    "numeric_statistics": numeric_stats,
                }

        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name,
                "schema": schema,
            }

    async def get_data_quality_metrics(
        self,
        table_name: str = "stg_transactions",
        schema: str = "main",
        db_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Calculate comprehensive data quality metrics for a table.

        Args:
            table_name: Name of the table to analyze
            schema: Schema name
            db_path: Path to DuckDB database file

        Returns:
            Dict[str, Any]: Data quality metrics
        """
        try:
            async with self.get_connection(db_path, read_only=True) as conn:
                # Get table info first
                table_info = await self.get_table_info(table_name, schema, db_path)
                if not table_info["success"]:
                    return table_info

                total_rows = table_info["row_count"]
                columns = table_info["columns"]

                if total_rows == 0:
                    return {
                        "success": True,
                        "table_name": table_name,
                        "overall_score": 0.0,
                        "total_rows": 0,
                        "message": "Table is empty",
                    }

                # Calculate null percentages
                null_checks = []
                for col in columns:
                    col_name = col["name"]
                    null_checks.append(
                        f"ROUND(100.0 * SUM(CASE WHEN {col_name} IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as {col_name}_null_pct"
                    )

                null_query = f"""
                SELECT {', '.join(null_checks)}
                FROM {schema}.{table_name}
                """

                null_result = conn.execute(null_query).fetchone()
                null_percentages = dict(
                    zip(
                        [col["name"] + "_null_pct" for col in columns],
                        null_result,
                        strict=False,
                    )
                )

                # Calculate completeness score
                avg_null_pct = sum(null_percentages.values()) / len(null_percentages)
                completeness_score = max(0, (100 - avg_null_pct) / 100)

                # Check for duplicates
                duplicate_query = f"""
                SELECT
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT *) as distinct_rows,
                    COUNT(*) - COUNT(DISTINCT *) as duplicate_rows
                FROM {schema}.{table_name}
                """

                duplicate_result = conn.execute(duplicate_query).fetchone()
                duplicate_percentage = (
                    (duplicate_result[2] / duplicate_result[0]) * 100
                    if duplicate_result[0] > 0
                    else 0
                )
                uniqueness_score = max(0, (100 - duplicate_percentage) / 100)

                # Calculate consistency score (example: check data types and formats)
                consistency_score = (
                    1.0  # Placeholder - would need more specific business rules
                )

                # Check data freshness (if there's a date column)
                freshness_score = 1.0
                date_columns = [
                    col["name"] for col in columns if "date" in col["name"].lower()
                ]
                if date_columns:
                    freshness_query = f"""
                    SELECT
                        MAX({date_columns[0]}) as max_date,
                        CURRENT_DATE - MAX({date_columns[0]}) as days_old
                    FROM {schema}.{table_name}
                    """
                    freshness_result = conn.execute(freshness_query).fetchone()
                    days_old = (
                        freshness_result[1] if freshness_result[1] is not None else 0
                    )
                    freshness_score = max(
                        0, 1 - (days_old / 30)
                    )  # Penalty for data older than 30 days

                # Calculate overall quality score
                overall_score = (
                    completeness_score
                    + uniqueness_score
                    + consistency_score
                    + freshness_score
                ) / 4

                return {
                    "success": True,
                    "table_name": table_name,
                    "total_rows": total_rows,
                    "overall_score": round(overall_score, 3),
                    "completeness_score": round(completeness_score, 3),
                    "uniqueness_score": round(uniqueness_score, 3),
                    "consistency_score": round(consistency_score, 3),
                    "freshness_score": round(freshness_score, 3),
                    "null_percentages": {
                        k.replace("_null_pct", ""): v
                        for k, v in null_percentages.items()
                    },
                    "duplicate_count": duplicate_result[2],
                    "duplicate_percentage": round(duplicate_percentage, 2),
                    "column_count": len(columns),
                }

        except Exception as e:
            self.logger.error(f"Failed to calculate data quality metrics: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name,
                "schema": schema,
            }

    async def optimize_database(self, db_path: str | None = None) -> dict[str, Any]:
        """
        Optimize DuckDB database performance.

        Args:
            db_path: Path to DuckDB database file

        Returns:
            Dict[str, Any]: Optimization results
        """
        try:
            async with self.get_connection(db_path) as conn:
                # Analyze tables for query optimization
                conn.execute("ANALYZE")

                # Vacuum to reclaim space
                conn.execute("VACUUM")

                # Get database size information
                size_query = """
                SELECT
                    SUM(estimated_size) as total_size_bytes
                FROM duckdb_tables()
                """
                size_result = conn.execute(size_query).fetchone()

                return {
                    "success": True,
                    "message": "Database optimized successfully",
                    "total_size_bytes": size_result[0] if size_result else 0,
                    "optimizations_applied": ["ANALYZE", "VACUUM"],
                }

        except Exception as e:
            self.logger.error(f"Database optimization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    async def export_table_to_csv(
        self,
        table_name: str,
        output_path: str,
        schema: str = "main",
        db_path: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Export a table to CSV file.

        Args:
            table_name: Name of the table to export
            output_path: Path where CSV file should be saved
            schema: Schema name
            db_path: Path to DuckDB database file
            limit: Maximum number of rows to export

        Returns:
            Dict[str, Any]: Export results
        """
        try:
            async with self.get_connection(db_path, read_only=True) as conn:
                # Prepare query
                query = f"SELECT * FROM {schema}.{table_name}"
                if limit:
                    query += f" LIMIT {limit}"

                # Export to CSV
                export_query = (
                    f"COPY ({query}) TO '{output_path}' (HEADER, DELIMITER ',')"
                )
                conn.execute(export_query)

                # Get row count
                count_query = f"SELECT COUNT(*) FROM ({query})"
                row_count = conn.execute(count_query).fetchone()[0]

                return {
                    "success": True,
                    "table_name": table_name,
                    "output_path": output_path,
                    "rows_exported": row_count,
                    "file_size_bytes": (
                        os.path.getsize(output_path)
                        if os.path.exists(output_path)
                        else 0
                    ),
                }

        except Exception as e:
            self.logger.error(f"Export to CSV failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name,
                "output_path": output_path,
            }

    async def get_query_plan(
        self, query: str, db_path: str | None = None
    ) -> dict[str, Any]:
        """
        Get the execution plan for a query.

        Args:
            query: SQL query to analyze
            db_path: Path to DuckDB database file

        Returns:
            Dict[str, Any]: Query execution plan
        """
        try:
            async with self.get_connection(db_path, read_only=True) as conn:
                # Get execution plan
                plan_query = f"EXPLAIN {query}"
                plan_result = conn.execute(plan_query).fetchall()

                # Get query analysis
                analyze_query = f"EXPLAIN ANALYZE {query}"
                analyze_result = conn.execute(analyze_query).fetchall()

                return {
                    "success": True,
                    "query": query,
                    "execution_plan": [row[0] for row in plan_result],
                    "analysis": [row[0] for row in analyze_result],
                }

        except Exception as e:
            self.logger.error(f"Query plan analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
            }

    async def get_database_stats(self, db_path: str | None = None) -> dict[str, Any]:
        """
        Get comprehensive database statistics.

        Args:
            db_path: Path to DuckDB database file

        Returns:
            Dict[str, Any]: Database statistics
        """
        try:
            async with self.get_connection(db_path, read_only=True) as conn:
                # Get all tables
                tables_query = "SHOW TABLES"
                tables_result = conn.execute(tables_query).fetchall()
                table_names = [row[0] for row in tables_result]

                # Get database version
                version_result = conn.execute("SELECT version()").fetchone()

                # Get memory usage
                memory_query = "PRAGMA memory_limit"
                memory_result = conn.execute(memory_query).fetchone()

                # Calculate total rows across all tables
                total_rows = 0
                table_stats = {}
                for table_name in table_names:
                    try:
                        count_result = conn.execute(
                            f"SELECT COUNT(*) FROM {table_name}"
                        ).fetchone()
                        table_row_count = count_result[0] if count_result else 0
                        total_rows += table_row_count
                        table_stats[table_name] = {"row_count": table_row_count}
                    except:
                        table_stats[table_name] = {
                            "row_count": 0,
                            "error": "Could not count rows",
                        }

                return {
                    "success": True,
                    "database_path": db_path or self.default_db_path,
                    "version": version_result[0] if version_result else "Unknown",
                    "memory_limit": memory_result[0] if memory_result else "Unknown",
                    "table_count": len(table_names),
                    "total_rows": total_rows,
                    "tables": table_stats,
                    "file_size_bytes": (
                        os.path.getsize(db_path or self.default_db_path)
                        if os.path.exists(db_path or self.default_db_path)
                        else 0
                    ),
                }

        except Exception as e:
            self.logger.error(f"Failed to get database stats: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "database_path": db_path or self.default_db_path,
            }
