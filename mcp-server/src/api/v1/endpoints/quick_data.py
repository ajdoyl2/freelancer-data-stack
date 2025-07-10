"""
Quick Data endpoints for MCP Server
"""

from typing import Any

from adapters.quick_data_adapter import ChartConfig, DatasetConfig, QuickDataAdapter
from fastapi import APIRouter, Depends, HTTPException

# Placeholder for JWT auth - disable for now
# from ...auth.jwt_handler import get_current_user


def get_current_user():
    """Placeholder for JWT authentication"""
    return "anonymous"


import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/load-dataset")
async def load_dataset(
    config: DatasetConfig, current_user: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Load a dataset into Quick Data MCP"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.load_dataset(config)
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets")
async def list_datasets(
    current_user: str = Depends(get_current_user),
) -> dict[str, Any]:
    """List all loaded datasets"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.list_loaded_datasets()
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/segment/{dataset_name}")
async def segment_by_column(
    dataset_name: str,
    column_name: str,
    method: str = "auto",
    top_n: int = 10,
    current_user: str = Depends(get_current_user),
) -> dict[str, Any]:
    """Segment data by a specific column"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.segment_by_column(
                dataset_name, column_name, method, top_n
            )
    except Exception as e:
        logger.error(f"Failed to segment data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/correlations/{dataset_name}")
async def find_correlations(
    dataset_name: str,
    columns: list[str] | None = None,
    threshold: float = 0.3,
    current_user: str = Depends(get_current_user),
) -> dict[str, Any]:
    """Find correlations in dataset"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.find_correlations(dataset_name, columns, threshold)
    except Exception as e:
        logger.error(f"Failed to find correlations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chart")
async def create_chart(
    config: ChartConfig, current_user: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Create a chart from dataset"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.create_chart(config)
    except Exception as e:
        logger.error(f"Failed to create chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-distribution/{dataset_name}")
async def analyze_distribution(
    dataset_name: str, column_name: str, current_user: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Analyze distribution of a column"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.analyze_distributions(dataset_name, column_name)
    except Exception as e:
        logger.error(f"Failed to analyze distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outliers/{dataset_name}")
async def detect_outliers(
    dataset_name: str,
    columns: list[str] | None = None,
    method: str = "iqr",
    current_user: str = Depends(get_current_user),
) -> dict[str, Any]:
    """Detect outliers in dataset"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.detect_outliers(dataset_name, columns, method)
    except Exception as e:
        logger.error(f"Failed to detect outliers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-quality/{dataset_name}")
async def validate_data_quality(
    dataset_name: str, current_user: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Validate data quality"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.validate_data_quality(dataset_name)
    except Exception as e:
        logger.error(f"Failed to validate data quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-analysis/{dataset_name}")
async def suggest_analysis(
    dataset_name: str, current_user: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Get AI-powered analysis suggestions"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.suggest_analysis(dataset_name)
    except Exception as e:
        logger.error(f"Failed to suggest analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-code/{dataset_name}")
async def execute_custom_code(
    dataset_name: str, python_code: str, current_user: str = Depends(get_current_user)
) -> str:
    """Execute custom Python code against dataset"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.execute_custom_analytics_code(
                dataset_name, python_code
            )
    except Exception as e:
        logger.error(f"Failed to execute code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Resource endpoints
@router.get("/datasets/{dataset_name}/summary")
async def get_dataset_summary(
    dataset_name: str, current_user: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Get dataset summary"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.get_dataset_summary(dataset_name)
    except Exception as e:
        logger.error(f"Failed to get dataset summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_name}/schema")
async def get_dataset_schema(
    dataset_name: str, current_user: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Get dataset schema"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.get_dataset_schema(dataset_name)
    except Exception as e:
        logger.error(f"Failed to get dataset schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_name}/sample")
async def get_dataset_sample(
    dataset_name: str, rows: int = 10, current_user: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Get sample rows from dataset"""
    try:
        async with QuickDataAdapter() as adapter:
            return await adapter.get_dataset_sample(dataset_name, rows)
    except Exception as e:
        logger.error(f"Failed to get dataset sample: {e}")
        raise HTTPException(status_code=500, detail=str(e))
