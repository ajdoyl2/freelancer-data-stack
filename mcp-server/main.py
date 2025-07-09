"""
MCP (Model Context Protocol) Server
FastAPI-based service with plugin adapters for data tools
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

import strawberry
from adapters import (
    DagsterAdapter,
    DataHubAdapter,
    DbtAdapter,
    DuckDBAdapter,
    SnowflakeAdapter,
)
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from llm_gateway import LLMGateway
from schema import Mutation, Query
from strawberry.fastapi import GraphQLRouter
from websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
websocket_manager = WebSocketManager()
llm_gateway = LLMGateway()

# Initialize adapters
adapters: dict[str, Any] = {
    "dagster": DagsterAdapter(),
    "dbt": DbtAdapter(),
    "snowflake": SnowflakeAdapter(),
    "duckdb": DuckDBAdapter(),
    "datahub": DataHubAdapter(),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting MCP Server...")

    # Initialize adapters
    for name, adapter in adapters.items():
        try:
            await adapter.initialize()
            logger.info(f"Initialized {name} adapter")
        except Exception as e:
            logger.error(f"Failed to initialize {name} adapter: {e}")

    # Start background monitoring
    asyncio.create_task(websocket_manager.start_monitoring())

    yield

    logger.info("Shutting down MCP Server...")
    # Cleanup adapters
    for name, adapter in adapters.items():
        try:
            await adapter.cleanup()
            logger.info(f"Cleaned up {name} adapter")
        except Exception as e:
            logger.error(f"Failed to cleanup {name} adapter: {e}")


# Create FastAPI app
app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol Server with Data Tool Adapters",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

# Mount GraphQL
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "MCP Server is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Detailed health check"""
    health_status = {"status": "healthy", "adapters": {}}

    for name, adapter in adapters.items():
        try:
            status = await adapter.health_check()
            health_status["adapters"][name] = status
        except Exception as e:
            health_status["adapters"][name] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"

    return health_status


# REST API endpoints for each adapter
@app.get("/api/dagster/jobs")
async def get_dagster_jobs():
    """Get Dagster jobs"""
    try:
        return await adapters["dagster"].get_jobs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dbt/models")
async def get_dbt_models():
    """Get dbt models"""
    try:
        return await adapters["dbt"].get_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/snowflake/warehouses")
async def get_snowflake_warehouses():
    """Get Snowflake warehouses"""
    try:
        return await adapters["snowflake"].get_warehouses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/duckdb/tables")
async def get_duckdb_tables():
    """Get DuckDB tables"""
    try:
        return await adapters["duckdb"].get_tables()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/datahub/datasets")
async def get_datahub_datasets():
    """Get DataHub datasets"""
    try:
        return await adapters["datahub"].get_datasets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# LLM Gateway endpoints
@app.post("/api/llm/generate-code")
async def generate_code(request: dict):
    """Generate code using LLM"""
    try:
        return await llm_gateway.generate_code(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm/answer-question")
async def answer_question(request: dict):
    """Answer data questions using LLM"""
    try:
        return await llm_gateway.answer_question(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time monitoring
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(client_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
