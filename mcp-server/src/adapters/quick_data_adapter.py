"""
Quick Data MCP adapter for integrating quick-data-mcp server functionality
"""

from typing import Any

import aiohttp
from pydantic import BaseModel, Field

from config import settings

# Placeholder for JWT handler - implement when auth system is available
# from ..auth.jwt_handler import get_current_user


# Placeholder for monitoring - implement tracking decorator
def track_tool_usage(tool_name):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # TODO: Add actual monitoring/tracking logic
            return await func(*args, **kwargs)

        return wrapper

    return decorator


import logging

logger = logging.getLogger(__name__)

QUICK_DATA_URL = f"http://{settings.quick_data_mcp_host}:{settings.quick_data_mcp_port}"


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

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> dict[str, Any]:
        """Make HTTP request to Quick Data MCP server"""
        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.request(method, url, json=data) as response:
                response_data = await response.json()
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

    @track_tool_usage("quick_data.load_dataset")
    async def load_dataset(self, config: DatasetConfig) -> dict[str, Any]:
        """Load a dataset into Quick Data MCP"""
        return await self._make_request("POST", "/tools/load_dataset", config.dict())

    @track_tool_usage("quick_data.list_datasets")
    async def list_loaded_datasets(self) -> dict[str, Any]:
        """List all datasets currently loaded in Quick Data MCP"""
        return await self._make_request("GET", "/tools/list_loaded_datasets")

    @track_tool_usage("quick_data.segment_by_column")
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

    @track_tool_usage("quick_data.find_correlations")
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

    @track_tool_usage("quick_data.create_chart")
    async def create_chart(self, config: ChartConfig) -> dict[str, Any]:
        """Create a chart from dataset"""
        return await self._make_request("POST", "/tools/create_chart", config.dict())

    @track_tool_usage("quick_data.analyze_distributions")
    async def analyze_distributions(
        self, dataset_name: str, column_name: str
    ) -> dict[str, Any]:
        """Analyze distribution of a column"""
        return await self._make_request(
            "POST",
            "/tools/analyze_distributions",
            {"dataset_name": dataset_name, "column_name": column_name},
        )

    @track_tool_usage("quick_data.detect_outliers")
    async def detect_outliers(
        self, dataset_name: str, columns: list[str] | None = None, method: str = "iqr"
    ) -> dict[str, Any]:
        """Detect outliers in dataset"""
        return await self._make_request(
            "POST",
            "/tools/detect_outliers",
            {"dataset_name": dataset_name, "columns": columns, "method": method},
        )

    @track_tool_usage("quick_data.validate_data_quality")
    async def validate_data_quality(self, dataset_name: str) -> dict[str, Any]:
        """Validate data quality of a dataset"""
        return await self._make_request(
            "POST", "/tools/validate_data_quality", {"dataset_name": dataset_name}
        )

    @track_tool_usage("quick_data.suggest_analysis")
    async def suggest_analysis(self, dataset_name: str) -> dict[str, Any]:
        """Get AI-powered analysis suggestions for a dataset"""
        return await self._make_request(
            "POST", "/tools/suggest_analysis", {"dataset_name": dataset_name}
        )

    @track_tool_usage("quick_data.execute_custom_code")
    async def execute_custom_analytics_code(
        self, dataset_name: str, python_code: str
    ) -> str:
        """Execute custom Python code against a dataset"""
        return await self._make_request(
            "POST",
            "/tools/execute_custom_analytics_code",
            {"dataset_name": dataset_name, "python_code": python_code},
        )

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
