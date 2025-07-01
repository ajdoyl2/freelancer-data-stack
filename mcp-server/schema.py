"""
GraphQL schema definitions for MCP Server
"""

import strawberry
from typing import List, Optional, Dict, Any
from datetime import datetime


@strawberry.type
class DagsterJob:
    """Dagster job representation"""
    name: str
    status: str
    last_run: Optional[datetime] = None
    description: Optional[str] = None


@strawberry.type
class DbtModel:
    """dbt model representation"""
    name: str
    path: str
    status: str
    last_run: Optional[datetime] = None
    description: Optional[str] = None


@strawberry.type
class SnowflakeWarehouse:
    """Snowflake warehouse representation"""
    name: str
    size: str
    state: str
    auto_suspend: Optional[int] = None


@strawberry.type
class DuckDBTable:
    """DuckDB table representation"""
    name: str
    schema: str
    row_count: Optional[int] = None
    columns: Optional[List[str]] = None


@strawberry.type
class DataHubDataset:
    """DataHub dataset representation"""
    urn: str
    name: str
    platform: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None


@strawberry.type
class LLMResponse:
    """LLM response representation"""
    content: str
    model: str
    tokens_used: int
    generated_at: datetime


@strawberry.type
class HealthStatus:
    """Health status representation"""
    status: str
    message: Optional[str] = None
    timestamp: datetime


@strawberry.input
class CodeGenerationRequest:
    """Code generation request input"""
    prompt: str
    language: str
    context: Optional[str] = None


@strawberry.input
class QuestionRequest:
    """Question request input"""
    question: str
    context: Optional[str] = None
    include_data: bool = False


@strawberry.type
class Query:
    """GraphQL Query root"""
    
    @strawberry.field
    async def dagster_jobs(self) -> List[DagsterJob]:
        """Get all Dagster jobs"""
        # Import here to avoid circular imports
        from main import adapters
        jobs_data = await adapters["dagster"].get_jobs()
        return [
            DagsterJob(
                name=job["name"],
                status=job["status"],
                last_run=job.get("last_run"),
                description=job.get("description")
            )
            for job in jobs_data
        ]
    
    @strawberry.field
    async def dbt_models(self) -> List[DbtModel]:
        """Get all dbt models"""
        from main import adapters
        models_data = await adapters["dbt"].get_models()
        return [
            DbtModel(
                name=model["name"],
                path=model["path"],
                status=model["status"],
                last_run=model.get("last_run"),
                description=model.get("description")
            )
            for model in models_data
        ]
    
    @strawberry.field
    async def snowflake_warehouses(self) -> List[SnowflakeWarehouse]:
        """Get Snowflake warehouses"""
        from main import adapters
        warehouses_data = await adapters["snowflake"].get_warehouses()
        return [
            SnowflakeWarehouse(
                name=wh["name"],
                size=wh["size"],
                state=wh["state"],
                auto_suspend=wh.get("auto_suspend")
            )
            for wh in warehouses_data
        ]
    
    @strawberry.field
    async def duckdb_tables(self) -> List[DuckDBTable]:
        """Get DuckDB tables"""
        from main import adapters
        tables_data = await adapters["duckdb"].get_tables()
        return [
            DuckDBTable(
                name=table["name"],
                schema=table["schema"],
                row_count=table.get("row_count"),
                columns=table.get("columns")
            )
            for table in tables_data
        ]
    
    @strawberry.field
    async def datahub_datasets(self) -> List[DataHubDataset]:
        """Get DataHub datasets"""
        from main import adapters
        datasets_data = await adapters["datahub"].get_datasets()
        return [
            DataHubDataset(
                urn=ds["urn"],
                name=ds["name"],
                platform=ds["platform"],
                description=ds.get("description"),
                tags=ds.get("tags")
            )
            for ds in datasets_data
        ]
    
    @strawberry.field
    async def health_status(self) -> HealthStatus:
        """Get overall health status"""
        return HealthStatus(
            status="healthy",
            message="MCP Server is operational",
            timestamp=datetime.now()
        )


@strawberry.type
class Mutation:
    """GraphQL Mutation root"""
    
    @strawberry.mutation
    async def generate_code(self, request: CodeGenerationRequest) -> LLMResponse:
        """Generate code using LLM"""
        from main import llm_gateway
        response = await llm_gateway.generate_code({
            "prompt": request.prompt,
            "language": request.language,
            "context": request.context
        })
        
        return LLMResponse(
            content=response["content"],
            model=response["model"],
            tokens_used=response["tokens_used"],
            generated_at=datetime.now()
        )
    
    @strawberry.mutation
    async def answer_question(self, request: QuestionRequest) -> LLMResponse:
        """Answer data question using LLM"""
        from main import llm_gateway
        response = await llm_gateway.answer_question({
            "question": request.question,
            "context": request.context,
            "include_data": request.include_data
        })
        
        return LLMResponse(
            content=response["content"],
            model=response["model"],
            tokens_used=response["tokens_used"],
            generated_at=datetime.now()
        )
