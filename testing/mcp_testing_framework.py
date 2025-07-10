"""
MCP Testing Framework

A comprehensive testing framework for all MCP server integrations.
Supports unit tests, integration tests, and end-to-end tests.
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any

import aiohttp
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestType(Enum):
    """Test types supported by the framework."""

    UNIT = "unit"
    INTEGRATION = "integration"
    END_TO_END = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestResult(BaseModel):
    """Represents the result of a test execution."""

    test_name: str
    test_type: TestType
    status: str = Field(..., regex="^(passed|failed|skipped|error)$")
    duration: float
    error_message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""

    name: str
    host: str = "localhost"
    port: int
    base_url: str = ""
    health_endpoint: str = "/health"
    auth_required: bool = True
    timeout: int = 30
    retries: int = 3

    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://{self.host}:{self.port}"


class MCPTestSuite:
    """Base class for MCP server test suites."""

    def __init__(self, server_config: MCPServerConfig):
        self.server_config = server_config
        self.session: aiohttp.ClientSession | None = None
        self.test_results: list[TestResult] = []

    async def setup(self):
        """Setup test environment."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.server_config.timeout)
        )

    async def teardown(self):
        """Cleanup test environment."""
        if self.session:
            await self.session.close()

    @asynccontextmanager
    async def test_session(self):
        """Context manager for test sessions."""
        await self.setup()
        try:
            yield self
        finally:
            await self.teardown()

    async def execute_test(
        self, test_func, test_name: str, test_type: TestType
    ) -> TestResult:
        """Execute a single test and record results."""
        start_time = time.time()

        try:
            result = await test_func()
            duration = time.time() - start_time

            test_result = TestResult(
                test_name=test_name,
                test_type=test_type,
                status="passed",
                duration=duration,
                details=result if isinstance(result, dict) else {"result": result},
            )

        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                test_type=test_type,
                status="failed",
                duration=duration,
                error_message=str(e),
                details={"exception_type": type(e).__name__},
            )
            logger.error(f"Test {test_name} failed: {e}")

        self.test_results.append(test_result)
        return test_result

    async def health_check(self) -> bool:
        """Check if the MCP server is healthy."""
        try:
            async with self.session.get(
                f"{self.server_config.base_url}{self.server_config.health_endpoint}"
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed for {self.server_config.name}: {e}")
            return False

    async def make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any]:
        """Make an HTTP request to the MCP server."""
        url = f"{self.server_config.base_url}{endpoint}"

        for attempt in range(self.server_config.retries):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(
                            f"HTTP {response.status}: {await response.text()}"
                        )
            except Exception:
                if attempt == self.server_config.retries - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff


class MCPTestRunner:
    """Main test runner for MCP server integrations."""

    def __init__(self, config_file: str | None = None):
        self.server_configs: dict[str, MCPServerConfig] = {}
        self.test_suites: dict[str, MCPTestSuite] = {}
        self.results: list[TestResult] = []

        if config_file:
            self.load_config(config_file)

    def load_config(self, config_file: str):
        """Load server configurations from file."""
        with open(config_file) as f:
            config = json.load(f)

        for server_name, server_config in config.get("servers", {}).items():
            self.server_configs[server_name] = MCPServerConfig(
                name=server_name, **server_config
            )

    def register_server(self, server_name: str, config: MCPServerConfig):
        """Register a new MCP server for testing."""
        self.server_configs[server_name] = config

    def register_test_suite(self, server_name: str, test_suite: MCPTestSuite):
        """Register a test suite for a server."""
        self.test_suites[server_name] = test_suite

    async def run_all_tests(
        self, test_types: list[TestType] = None
    ) -> dict[str, list[TestResult]]:
        """Run all tests for all registered servers."""
        if test_types is None:
            test_types = [TestType.UNIT, TestType.INTEGRATION, TestType.END_TO_END]

        results = {}

        for server_name, test_suite in self.test_suites.items():
            logger.info(f"Running tests for {server_name}")

            async with test_suite.test_session():
                server_results = []

                for test_type in test_types:
                    type_results = await self._run_tests_by_type(test_suite, test_type)
                    server_results.extend(type_results)

                results[server_name] = server_results

        return results

    async def _run_tests_by_type(
        self, test_suite: MCPTestSuite, test_type: TestType
    ) -> list[TestResult]:
        """Run tests of a specific type for a test suite."""
        results = []

        # Get test methods by type
        test_methods = self._get_test_methods(test_suite, test_type)

        for test_name, test_method in test_methods:
            result = await test_suite.execute_test(test_method, test_name, test_type)
            results.append(result)

        return results

    def _get_test_methods(
        self, test_suite: MCPTestSuite, test_type: TestType
    ) -> list[tuple[str, callable]]:
        """Get test methods for a specific test type."""
        methods = []

        for attr_name in dir(test_suite):
            if attr_name.startswith(f"test_{test_type.value}_"):
                method = getattr(test_suite, attr_name)
                if callable(method):
                    methods.append((attr_name, method))

        return methods

    def generate_report(self, results: dict[str, list[TestResult]]) -> dict[str, Any]:
        """Generate a comprehensive test report."""
        total_tests = sum(len(server_results) for server_results in results.values())
        passed_tests = sum(
            1
            for server_results in results.values()
            for result in server_results
            if result.status == "passed"
        )

        report = {
            "summary": {
                "total_servers": len(results),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            },
            "servers": {},
        }

        for server_name, server_results in results.items():
            server_passed = sum(1 for r in server_results if r.status == "passed")
            server_total = len(server_results)

            report["servers"][server_name] = {
                "total_tests": server_total,
                "passed_tests": server_passed,
                "failed_tests": server_total - server_passed,
                "pass_rate": server_passed / server_total if server_total > 0 else 0,
                "results": [result.dict() for result in server_results],
            }

        return report


class MockMCPServer:
    """Mock MCP server for testing."""

    def __init__(self, port: int):
        self.port = port
        self.app = None
        self.server = None
        self.responses = {}

    def add_response(self, endpoint: str, method: str, response: dict[str, Any]):
        """Add a mock response for an endpoint."""
        self.responses[f"{method}:{endpoint}"] = response

    async def start(self):
        """Start the mock server."""
        from aiohttp import web

        self.app = web.Application()

        # Add health endpoint
        self.app.router.add_get("/health", self._health_handler)

        # Add dynamic endpoints
        self.app.router.add_route("*", "/{path:.*}", self._dynamic_handler)

        # Start server
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()

        self.server = runner

    async def stop(self):
        """Stop the mock server."""
        if self.server:
            await self.server.cleanup()

    async def _health_handler(self, request):
        """Health check handler."""
        return web.json_response({"status": "healthy"})

    async def _dynamic_handler(self, request):
        """Dynamic response handler."""
        key = f"{request.method}:{request.path}"

        if key in self.responses:
            return web.json_response(self.responses[key])
        else:
            return web.json_response({"error": "Not found"}, status=404)


# Factory functions for creating test suites
def create_postgres_test_suite(config: MCPServerConfig) -> MCPTestSuite:
    """Create a test suite for PostgreSQL MCP server."""

    class PostgresTestSuite(MCPTestSuite):
        async def test_unit_connection(self):
            """Test PostgreSQL connection."""
            return await self.make_request("GET", "/connection/status")

        async def test_unit_query_validation(self):
            """Test SQL query validation."""
            return await self.make_request(
                "POST",
                "/query/validate",
                json={"query": "SELECT * FROM users LIMIT 10"},
            )

        async def test_integration_schema_introspection(self):
            """Test schema introspection."""
            return await self.make_request("GET", "/schema/tables")

        async def test_integration_query_execution(self):
            """Test query execution."""
            return await self.make_request(
                "POST",
                "/query/execute",
                json={"query": "SELECT COUNT(*) FROM information_schema.tables"},
            )

        async def test_e2e_full_workflow(self):
            """Test complete PostgreSQL workflow."""
            # Check health
            health = await self.health_check()
            assert health, "Server not healthy"

            # Get schema
            schema = await self.make_request("GET", "/schema/tables")
            assert "tables" in schema

            # Execute query
            result = await self.make_request(
                "POST", "/query/execute", json={"query": "SELECT 1 as test_value"}
            )
            assert "rows" in result

            return {"workflow_completed": True}

    return PostgresTestSuite(config)


def create_quick_data_test_suite(config: MCPServerConfig) -> MCPTestSuite:
    """Create a test suite for Quick Data MCP server."""

    class QuickDataTestSuite(MCPTestSuite):
        async def test_unit_dataset_loading(self):
            """Test dataset loading functionality."""
            return await self.make_request(
                "POST",
                "/tools/load_dataset",
                json={"file_path": "/data/test.csv", "dataset_name": "test_dataset"},
            )

        async def test_unit_analytics_tools(self):
            """Test analytics tools."""
            return await self.make_request(
                "POST",
                "/tools/find_correlations",
                json={"dataset_name": "test_dataset", "threshold": 0.5},
            )

        async def test_integration_data_pipeline(self):
            """Test complete data analysis pipeline."""
            # Load dataset
            await self.make_request(
                "POST",
                "/tools/load_dataset",
                json={"file_path": "/data/sales.csv", "dataset_name": "sales_data"},
            )

            # Analyze data
            analysis = await self.make_request(
                "POST",
                "/tools/find_correlations",
                json={"dataset_name": "sales_data", "threshold": 0.3},
            )

            return {"pipeline_completed": True, "analysis": analysis}

        async def test_e2e_business_analysis(self):
            """Test end-to-end business analysis scenario."""
            # Load business data
            await self.make_request(
                "POST",
                "/tools/load_dataset",
                json={
                    "file_path": "/data/business_metrics.csv",
                    "dataset_name": "business_data",
                },
            )

            # Perform analysis
            await self.make_request(
                "POST",
                "/tools/find_correlations",
                json={"dataset_name": "business_data", "threshold": 0.4},
            )

            # Create visualization
            chart = await self.make_request(
                "POST",
                "/tools/create_chart",
                json={
                    "dataset_name": "business_data",
                    "chart_type": "bar",
                    "x_column": "month",
                    "y_column": "revenue",
                },
            )

            return {"business_analysis_completed": True, "chart": chart}

    return QuickDataTestSuite(config)


def create_dbt_test_suite(config: MCPServerConfig) -> MCPTestSuite:
    """Create a test suite for dbt MCP server."""

    class DbtTestSuite(MCPTestSuite):
        async def test_unit_model_compilation(self):
            """Test dbt model compilation."""
            return await self.make_request(
                "POST", "/tools/compile", json={"model": "customers"}
            )

        async def test_unit_test_execution(self):
            """Test dbt test execution."""
            return await self.make_request(
                "POST", "/tools/test", json={"model": "customers"}
            )

        async def test_integration_model_run(self):
            """Test dbt model run."""
            return await self.make_request(
                "POST", "/tools/run", json={"models": ["customers", "orders"]}
            )

        async def test_e2e_transformation_pipeline(self):
            """Test complete dbt transformation pipeline."""
            # Compile models
            compile_result = await self.make_request(
                "POST", "/tools/compile", json={"models": ["staging", "marts"]}
            )

            # Run models
            run_result = await self.make_request(
                "POST", "/tools/run", json={"models": ["staging", "marts"]}
            )

            # Run tests
            test_result = await self.make_request(
                "POST", "/tools/test", json={"models": ["staging", "marts"]}
            )

            return {
                "pipeline_completed": True,
                "compile_result": compile_result,
                "run_result": run_result,
                "test_result": test_result,
            }

    return DbtTestSuite(config)


# Test suite factory
TEST_SUITE_FACTORIES = {
    "postgres-mcp": create_postgres_test_suite,
    "quick-data-mcp": create_quick_data_test_suite,
    "dbt-mcp": create_dbt_test_suite,
}


def create_test_suite(server_name: str, config: MCPServerConfig) -> MCPTestSuite:
    """Create a test suite for a specific server."""
    factory = TEST_SUITE_FACTORIES.get(server_name)
    if factory:
        return factory(config)
    else:
        # Return a generic test suite
        return MCPTestSuite(config)
