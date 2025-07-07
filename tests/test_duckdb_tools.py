"""
Unit tests for DuckDB Tools

Tests the DuckDBTools class functionality including connection management,
query execution, and data quality metrics calculation.
"""

import asyncio
import os

# Add project root to path
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).parent.parent))

from tools.duckdb_tools import DuckDBTools


class TestDuckDBTools(unittest.TestCase):
    """Test cases for DuckDBTools class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.duckdb_tools = DuckDBTools()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_init(self):
        """Test DuckDBTools initialization."""
        tools = DuckDBTools()
        self.assertIsInstance(tools, DuckDBTools)
        self.assertEqual(tools.default_db_path, "/data/duckdb/analytics.db")

    @pytest.mark.asyncio
    async def test_execute_query_success(self):
        """Test successful query execution."""
        query = "SELECT 1 as test_column"

        result = await self.duckdb_tools.execute_query(query, self.db_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["rows"], [(1,)])
        self.assertEqual(result["columns"], ["test_column"])
        self.assertEqual(result["row_count"], 1)
        self.assertEqual(result["query"], query)

    @pytest.mark.asyncio
    async def test_execute_query_with_parameters(self):
        """Test query execution with parameters."""
        # Create test table
        await self.duckdb_tools.execute_query(
            "CREATE TABLE test_table (id INTEGER, name VARCHAR)", self.db_path
        )

        # Insert test data
        await self.duckdb_tools.execute_query(
            "INSERT INTO test_table VALUES (?, ?)",
            self.db_path,
            parameters=[1, "Test Name"],
        )

        # Query with parameters
        result = await self.duckdb_tools.execute_query(
            "SELECT * FROM test_table WHERE id = ?", self.db_path, parameters=[1]
        )

        self.assertTrue(result["success"])
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0], (1, "Test Name"))

    @pytest.mark.asyncio
    async def test_execute_query_no_fetch(self):
        """Test query execution without fetching results."""
        query = "CREATE TABLE test (id INTEGER)"

        result = await self.duckdb_tools.execute_query(
            query, self.db_path, fetch_results=False
        )

        self.assertTrue(result["success"])
        self.assertNotIn("rows", result)
        self.assertIn("message", result)

    @pytest.mark.asyncio
    async def test_execute_query_to_df(self):
        """Test query execution returning DataFrame."""
        # Create test data
        await self.duckdb_tools.execute_query(
            "CREATE TABLE test_df (id INTEGER, value DECIMAL(10,2))", self.db_path
        )
        await self.duckdb_tools.execute_query(
            "INSERT INTO test_df VALUES (1, 100.50), (2, 200.75)", self.db_path
        )

        result = await self.duckdb_tools.execute_query_to_df(
            "SELECT * FROM test_df ORDER BY id", self.db_path
        )

        self.assertTrue(result["success"])
        self.assertIsInstance(result["dataframe"], pd.DataFrame)
        self.assertEqual(result["shape"], (2, 2))
        self.assertEqual(result["columns"], ["id", "value"])

    @pytest.mark.asyncio
    async def test_get_table_info(self):
        """Test getting table information."""
        # Create test table with various column types
        await self.duckdb_tools.execute_query(
            """CREATE TABLE test_info (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                amount DECIMAL(10,2),
                created_date DATE
            )""",
            self.db_path,
        )

        # Insert test data
        await self.duckdb_tools.execute_query(
            "INSERT INTO test_info VALUES (1, 'Test', 100.50, '2024-01-01')",
            self.db_path,
        )

        result = await self.duckdb_tools.get_table_info(
            "test_info", "main", self.db_path
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["table_name"], "test_info")
        self.assertEqual(result["row_count"], 1)
        self.assertGreater(len(result["columns"]), 0)

    @pytest.mark.asyncio
    async def test_get_data_quality_metrics(self):
        """Test data quality metrics calculation."""
        # Create test table with quality issues
        await self.duckdb_tools.execute_query(
            """CREATE TABLE stg_transactions (
                transaction_id VARCHAR,
                transaction_date DATE,
                amount DECIMAL(10,2),
                category VARCHAR
            )""",
            self.db_path,
        )

        # Insert test data with some quality issues
        test_data = [
            ("1", "2024-01-01", 100.0, "food"),
            ("2", "2024-01-02", 200.0, "transport"),
            ("3", "2024-01-03", None, "shopping"),  # NULL amount
            ("4", None, 150.0, "bills"),  # NULL date
            ("1", "2024-01-01", 100.0, "food"),  # Duplicate
        ]

        for row in test_data:
            if row[1] is None:
                await self.duckdb_tools.execute_query(
                    "INSERT INTO stg_transactions VALUES (?, NULL, ?, ?)",
                    self.db_path,
                    parameters=[row[0], row[2], row[3]],
                )
            elif row[2] is None:
                await self.duckdb_tools.execute_query(
                    "INSERT INTO stg_transactions VALUES (?, ?, NULL, ?)",
                    self.db_path,
                    parameters=[row[0], row[1], row[3]],
                )
            else:
                await self.duckdb_tools.execute_query(
                    "INSERT INTO stg_transactions VALUES (?, ?, ?, ?)",
                    self.db_path,
                    parameters=row,
                )

        result = await self.duckdb_tools.get_data_quality_metrics(
            "stg_transactions", "main", self.db_path
        )

        self.assertTrue(result["success"])
        self.assertIn("overall_score", result)
        self.assertIn("completeness_score", result)
        self.assertIn("uniqueness_score", result)
        self.assertIn("null_percentages", result)
        self.assertIn("duplicate_count", result)
        self.assertEqual(result["total_rows"], 5)
        self.assertGreater(result["duplicate_count"], 0)

    @pytest.mark.asyncio
    async def test_optimize_database(self):
        """Test database optimization."""
        result = await self.duckdb_tools.optimize_database(self.db_path)

        self.assertTrue(result["success"])
        self.assertIn("message", result)
        self.assertIn("optimizations_applied", result)
        self.assertIn("ANALYZE", result["optimizations_applied"])
        self.assertIn("VACUUM", result["optimizations_applied"])

    @pytest.mark.asyncio
    async def test_export_table_to_csv(self):
        """Test table export to CSV."""
        # Create test table
        await self.duckdb_tools.execute_query(
            "CREATE TABLE export_test (id INTEGER, name VARCHAR)", self.db_path
        )
        await self.duckdb_tools.execute_query(
            "INSERT INTO export_test VALUES (1, 'Test1'), (2, 'Test2')", self.db_path
        )

        # Export to temporary CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_csv:
            csv_path = tmp_csv.name

        try:
            result = await self.duckdb_tools.export_table_to_csv(
                "export_test", csv_path, db_path=self.db_path
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["table_name"], "export_test")
            self.assertEqual(result["rows_exported"], 2)
            self.assertTrue(os.path.exists(csv_path))

            # Verify CSV content
            with open(csv_path) as f:
                content = f.read()
                self.assertIn("id,name", content)
                self.assertIn("1,Test1", content)
                self.assertIn("2,Test2", content)

        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)

    @pytest.mark.asyncio
    async def test_get_query_plan(self):
        """Test query execution plan analysis."""
        # Create test table
        await self.duckdb_tools.execute_query(
            "CREATE TABLE plan_test (id INTEGER, value VARCHAR)", self.db_path
        )

        query = "SELECT * FROM plan_test WHERE id = 1"
        result = await self.duckdb_tools.get_query_plan(query, self.db_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["query"], query)
        self.assertIn("execution_plan", result)
        self.assertIn("analysis", result)

    @pytest.mark.asyncio
    async def test_get_database_stats(self):
        """Test database statistics retrieval."""
        # Create test tables
        await self.duckdb_tools.execute_query(
            "CREATE TABLE stats_test1 (id INTEGER)", self.db_path
        )
        await self.duckdb_tools.execute_query(
            "CREATE TABLE stats_test2 (name VARCHAR)", self.db_path
        )
        await self.duckdb_tools.execute_query(
            "INSERT INTO stats_test1 VALUES (1), (2), (3)", self.db_path
        )

        result = await self.duckdb_tools.get_database_stats(self.db_path)

        self.assertTrue(result["success"])
        self.assertIn("database_path", result)
        self.assertIn("version", result)
        self.assertIn("table_count", result)
        self.assertIn("total_rows", result)
        self.assertIn("tables", result)
        self.assertEqual(result["table_count"], 2)
        self.assertEqual(result["total_rows"], 3)

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test connection error handling."""
        # Try to use invalid database path
        invalid_path = "/invalid/path/database.db"

        result = await self.duckdb_tools.execute_query("SELECT 1", invalid_path)

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @pytest.mark.asyncio
    async def test_sql_error_handling(self):
        """Test SQL error handling."""
        # Execute invalid SQL
        result = await self.duckdb_tools.execute_query(
            "SELECT FROM invalid_table", self.db_path
        )

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @pytest.mark.asyncio
    async def test_empty_table_quality_metrics(self):
        """Test data quality metrics for empty table."""
        # Create empty table
        await self.duckdb_tools.execute_query(
            "CREATE TABLE empty_test (id INTEGER, name VARCHAR)", self.db_path
        )

        result = await self.duckdb_tools.get_data_quality_metrics(
            "empty_test", "main", self.db_path
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["total_rows"], 0)
        self.assertEqual(result["overall_score"], 0.0)
        self.assertIn("message", result)


if __name__ == "__main__":
    # Run async tests
    import asyncio

    def run_async_test(coro):
        """Helper to run async test methods."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    # Run the tests
    unittest.main()
