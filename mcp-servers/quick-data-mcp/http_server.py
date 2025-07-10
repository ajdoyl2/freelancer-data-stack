#!/usr/bin/env python3
"""
HTTP server wrapper for quick-data-mcp server.
This exposes the MCP server tools as HTTP endpoints for integration.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from input_validation import validator as input_validator
from security_middleware import RequestValidationMiddleware, SecurityMiddleware

# Add the quick-data-mcp source to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "quick-data-mcp/src"))

from mcp_server.server import get_server
from mcp_server.tools import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for request/response
class DatasetLoadRequest(BaseModel):
    file_path: str
    dataset_name: str
    sample_size: int | None = None

    @validator("file_path")
    def validate_file_path(cls, v):
        return input_validator.validate_file_path(v)

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        return input_validator.validate_dataset_name(v)


class SegmentRequest(BaseModel):
    dataset_name: str
    column_name: str
    method: str = "auto"
    top_n: int = 10

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        return input_validator.validate_dataset_name(v)

    @validator("column_name")
    def validate_column_name(cls, v):
        return input_validator.validate_column_name(v)


class CorrelationRequest(BaseModel):
    dataset_name: str
    columns: list[str] | None = None
    threshold: float = 0.3

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        return input_validator.validate_dataset_name(v)

    @validator("columns")
    def validate_columns(cls, v):
        if v is not None:
            return [input_validator.validate_column_name(col) for col in v]
        return v


class ChartRequest(BaseModel):
    dataset_name: str
    chart_type: str
    x_column: str
    y_column: str | None = None
    groupby_column: str | None = None
    title: str | None = None
    save_path: str | None = None


class DistributionRequest(BaseModel):
    dataset_name: str
    column_name: str

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        return input_validator.validate_dataset_name(v)

    @validator("column_name")
    def validate_column_name(cls, v):
        return input_validator.validate_column_name(v)


class OutlierRequest(BaseModel):
    dataset_name: str
    columns: list[str] | None = None
    method: str = "iqr"

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        return input_validator.validate_dataset_name(v)

    @validator("columns")
    def validate_columns(cls, v):
        if v is not None:
            return [input_validator.validate_column_name(col) for col in v]
        return v


class DataQualityRequest(BaseModel):
    dataset_name: str

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        return input_validator.validate_dataset_name(v)


class AnalysisRequest(BaseModel):
    dataset_name: str

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        return input_validator.validate_dataset_name(v)


class CustomCodeRequest(BaseModel):
    dataset_name: str
    python_code: str

    @validator("dataset_name")
    def validate_dataset_name(cls, v):
        return input_validator.validate_dataset_name(v)

    @validator("python_code")
    def validate_python_code(cls, v):
        return input_validator.validate_python_code(v)


# Global MCP server instance
mcp_server = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global mcp_server

    logger.info("Starting Quick Data MCP HTTP server...")

    # Initialize MCP server
    mcp_server = get_server()

    yield

    logger.info("Shutting down Quick Data MCP HTTP server...")


# Create FastAPI app
app = FastAPI(
    title="Quick Data MCP HTTP Server",
    description="HTTP wrapper for quick-data-mcp server",
    version="1.0.0",
    lifespan=lifespan,
)

# Add security middleware
app.add_middleware(SecurityMiddleware, rate_limit_requests=100, rate_limit_window=60)
app.add_middleware(RequestValidationMiddleware, max_request_size=10 * 1024 * 1024)

# Add CORS middleware with secure configuration
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-Total-Count"],
    max_age=600,  # 10 minutes
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Quick Data MCP HTTP Server is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "quick-data-mcp"}


# Tool endpoints
@app.post("/tools/load_dataset")
async def load_dataset_endpoint(request: DatasetLoadRequest):
    """Load a dataset"""
    try:
        result = await load_dataset(
            request.file_path, request.dataset_name, request.sample_size
        )
        return result
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/list_loaded_datasets")
async def list_loaded_datasets_endpoint():
    """List all loaded datasets"""
    try:
        result = await list_loaded_datasets()
        return result
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/segment_by_column")
async def segment_by_column_endpoint(request: SegmentRequest):
    """Segment data by column"""
    try:
        result = await segment_by_column(
            request.dataset_name, request.column_name, request.method, request.top_n
        )
        return result
    except Exception as e:
        logger.error(f"Error segmenting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/find_correlations")
async def find_correlations_endpoint(request: CorrelationRequest):
    """Find correlations"""
    try:
        result = await find_correlations(
            request.dataset_name, request.columns, request.threshold
        )
        return result
    except Exception as e:
        logger.error(f"Error finding correlations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/create_chart")
async def create_chart_endpoint(request: ChartRequest):
    """Create a chart"""
    try:
        result = await create_chart(
            request.dataset_name,
            request.chart_type,
            request.x_column,
            request.y_column,
            request.groupby_column,
            request.title,
            request.save_path,
        )
        return result
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/analyze_distributions")
async def analyze_distributions_endpoint(request: DistributionRequest):
    """Analyze distributions"""
    try:
        result = await analyze_distributions(request.dataset_name, request.column_name)
        return result
    except Exception as e:
        logger.error(f"Error analyzing distributions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/detect_outliers")
async def detect_outliers_endpoint(request: OutlierRequest):
    """Detect outliers"""
    try:
        result = await detect_outliers(
            request.dataset_name, request.columns, request.method
        )
        return result
    except Exception as e:
        logger.error(f"Error detecting outliers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/validate_data_quality")
async def validate_data_quality_endpoint(request: DataQualityRequest):
    """Validate data quality"""
    try:
        result = await validate_data_quality(request.dataset_name)
        return result
    except Exception as e:
        logger.error(f"Error validating data quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/suggest_analysis")
async def suggest_analysis_endpoint(request: AnalysisRequest):
    """Suggest analysis"""
    try:
        result = await suggest_analysis(request.dataset_name)
        return result
    except Exception as e:
        logger.error(f"Error suggesting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/execute_custom_analytics_code")
async def execute_custom_analytics_code_endpoint(request: CustomCodeRequest):
    """Execute custom analytics code"""
    try:
        result = await execute_custom_analytics_code(
            request.dataset_name, request.python_code
        )
        return {"output": result}
    except Exception as e:
        logger.error(f"Error executing custom code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Resource endpoints
@app.get("/resources/datasets/{dataset_name}/summary")
async def get_dataset_summary(dataset_name: str):
    """Get dataset summary"""
    try:
        from mcp_server.resources.data_resources import get_dataset_summary

        result = await get_dataset_summary(dataset_name)
        return result
    except Exception as e:
        logger.error(f"Error getting dataset summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resources/datasets/{dataset_name}/schema")
async def get_dataset_schema(dataset_name: str):
    """Get dataset schema"""
    try:
        from mcp_server.resources.data_resources import get_dataset_schema

        result = await get_dataset_schema(dataset_name)
        return result
    except Exception as e:
        logger.error(f"Error getting dataset schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resources/datasets/{dataset_name}/sample")
async def get_dataset_sample(dataset_name: str, rows: int = 10):
    """Get dataset sample"""
    try:
        from mcp_server.resources.data_resources import get_dataset_sample

        result = await get_dataset_sample(dataset_name, rows)
        return result
    except Exception as e:
        logger.error(f"Error getting dataset sample: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
