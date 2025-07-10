"""
Quick Data MCP adapter for integrating quick-data-mcp server functionality
"""

import logging
from typing import Any

import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Configuration - these should match docker-compose.mcp.yml
QUICK_DATA_HOST = "quick-data-mcp"
QUICK_DATA_PORT = 8000
QUICK_DATA_URL = f"http://{QUICK_DATA_HOST}:{QUICK_DATA_PORT}"


class DatasetConfig(BaseModel):
    """Configuration for dataset operations"""

    file_path: str = Field(..., description="Path to the dataset file")
    dataset_name: str = Field(..., description="Name to assign to the dataset")
    sample_size: int | None = Field(
        None, description="Optional sample size for large datasets"
    )


class ChartConfig(BaseModel):
    """Configuration for chart generation"""

    dataset_name: str = Field(..., description="Name of the dataset to use")
    chart_type: str = Field(..., description="Type of chart (bar, line, scatter, etc.)")
    x_column: str = Field(..., description="Column for x-axis")
    y_column: str | None = Field(None, description="Column for y-axis")
    groupby_column: str | None = Field(None, description="Column to group by")
    title: str | None = Field(None, description="Chart title")
    save_path: str | None = Field(None, description="Path to save the chart")


class QuickDataAdapter:
    """Adapter for Quick Data MCP server integration"""

    def __init__(self):
        self.base_url = QUICK_DATA_URL
        self.session = None
        self.initialized = False

    async def initialize(self):
        """Initialize the adapter"""
        try:
            self.session = aiohttp.ClientSession()
            # Test connection to quick-data-mcp server
            await self._test_connection()
            self.initialized = True
            logger.info("Quick Data MCP adapter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Quick Data MCP adapter: {e}")
            if self.session:
                await self.session.close()
            raise

    async def cleanup(self):
        """Cleanup adapter resources"""
        if self.session:
            await self.session.close()
        self.initialized = False
        logger.info("Quick Data MCP adapter cleaned up")

    async def health_check(self) -> dict[str, Any]:
        """Check health of Quick Data MCP server"""
        try:
            if not self.session:
                return {"status": "unhealthy", "error": "Session not initialized"}

            async with self.session.get(
                f"{self.base_url}/health", timeout=5
            ) as response:
                if response.status == 200:
                    return {"status": "healthy", "url": self.base_url}
                else:
                    return {"status": "unhealthy", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def _test_connection(self):
        """Test connection to Quick Data MCP server"""
        try:
            async with self.session.get(
                f"{self.base_url}/health", timeout=10
            ) as response:
                if response.status != 200:
                    raise Exception(f"Quick Data MCP server returned {response.status}")
        except aiohttp.ClientError as e:
            raise Exception(f"Failed to connect to Quick Data MCP server: {str(e)}")

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't close session here as it's managed by initialize/cleanup
        pass

    async def _make_request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> dict[str, Any]:
        """Make HTTP request to Quick Data MCP server"""
        if not self.session:
            raise Exception("QuickDataAdapter not initialized")

        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.request(
                method, url, json=data, timeout=30
            ) as response:
                if response.content_type == "application/json":
                    response_data = await response.json()
                else:
                    # Handle text responses (like from execute_custom_analytics_code)
                    response_data = {"output": await response.text()}

                if response.status == 200:
                    return response_data
                else:
                    logger.error(
                        f"Quick Data MCP error: {response.status} - {response_data}"
                    )
                    raise Exception(
                        f"Quick Data MCP error: {response_data.get('detail', 'Unknown error')}"
                    )
        except aiohttp.ClientError as e:
            logger.error(f"Connection error to Quick Data MCP: {e}")
            raise Exception(f"Failed to connect to Quick Data MCP server: {str(e)}")

    # Tool methods
    async def load_dataset(self, config: DatasetConfig) -> dict[str, Any]:
        """Load a dataset into Quick Data MCP"""
        return await self._make_request("POST", "/tools/load_dataset", config.dict())

    async def list_loaded_datasets(self) -> dict[str, Any]:
        """List all datasets currently loaded in Quick Data MCP"""
        return await self._make_request("POST", "/tools/list_loaded_datasets")

    async def segment_by_column(
        self, dataset_name: str, column_name: str, method: str = "auto", top_n: int = 10
    ) -> dict[str, Any]:
        """Segment data by a specific column"""
        return await self._make_request(
            "POST",
            "/tools/segment_by_column",
            {
                "dataset_name": dataset_name,
                "column_name": column_name,
                "method": method,
                "top_n": top_n,
            },
        )

    async def find_correlations(
        self,
        dataset_name: str,
        columns: list[str] | None = None,
        threshold: float = 0.3,
    ) -> dict[str, Any]:
        """Find correlations between numerical columns"""
        return await self._make_request(
            "POST",
            "/tools/find_correlations",
            {"dataset_name": dataset_name, "columns": columns, "threshold": threshold},
        )

    async def create_chart(self, config: ChartConfig) -> dict[str, Any]:
        """Create a chart from dataset"""
        return await self._make_request("POST", "/tools/create_chart", config.dict())

    async def analyze_distributions(
        self, dataset_name: str, column_name: str
    ) -> dict[str, Any]:
        """Analyze distribution of a column"""
        return await self._make_request(
            "POST",
            "/tools/analyze_distributions",
            {"dataset_name": dataset_name, "column_name": column_name},
        )

    async def detect_outliers(
        self, dataset_name: str, columns: list[str] | None = None, method: str = "iqr"
    ) -> dict[str, Any]:
        """Detect outliers in dataset"""
        return await self._make_request(
            "POST",
            "/tools/detect_outliers",
            {"dataset_name": dataset_name, "columns": columns, "method": method},
        )

    async def validate_data_quality(self, dataset_name: str) -> dict[str, Any]:
        """Validate data quality of a dataset"""
        return await self._make_request(
            "POST", "/tools/validate_data_quality", {"dataset_name": dataset_name}
        )

    async def suggest_analysis(self, dataset_name: str) -> dict[str, Any]:
        """Get AI-powered analysis suggestions for a dataset"""
        return await self._make_request(
            "POST", "/tools/suggest_analysis", {"dataset_name": dataset_name}
        )

    async def execute_custom_analytics_code(
        self, dataset_name: str, python_code: str
    ) -> str:
        """Execute custom Python code against a dataset"""
        result = await self._make_request(
            "POST",
            "/tools/execute_custom_analytics_code",
            {"dataset_name": dataset_name, "python_code": python_code},
        )
        # Return just the output string for compatibility
        return result.get("output", str(result))

    # Resource endpoints
    async def get_dataset_summary(self, dataset_name: str) -> dict[str, Any]:
        """Get summary of a loaded dataset"""
        return await self._make_request(
            "GET", f"/resources/datasets/{dataset_name}/summary"
        )

    async def get_dataset_schema(self, dataset_name: str) -> dict[str, Any]:
        """Get schema of a loaded dataset"""
        return await self._make_request(
            "GET", f"/resources/datasets/{dataset_name}/schema"
        )

    async def get_dataset_sample(
        self, dataset_name: str, rows: int = 10
    ) -> dict[str, Any]:
        """Get sample rows from a dataset"""
        return await self._make_request(
            "GET", f"/resources/datasets/{dataset_name}/sample?rows={rows}"
        )
