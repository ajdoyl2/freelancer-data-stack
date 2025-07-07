#!/usr/bin/env python3
"""
AI Agent API Server

FastAPI server that provides REST endpoints for the AI agent system.
"""

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from agents import get_agent, list_available_agents
from agents.base_agent import AgentRole
from config.agent_configs import AgentConfigs
from config.model_configs import ModelConfigs
from config.tool_configs import ToolConfigs
from interface.response_formatter import OutputFormat
from interface.workflow_executor import WorkflowExecutor


# Request/Response Models
class AgentRequest(BaseModel):
    prompt: str
    agent_role: AgentRole | None = None
    output_format: OutputFormat | None = OutputFormat.JSON
    metadata: dict | None = None


class AgentResponse(BaseModel):
    status: str
    content: str
    execution_id: str
    execution_time: float | None = None
    agent_roles: list[str]
    confidence: float | None = None
    metadata: dict | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    agents_available: int
    models_configured: int
    environment: str


class AgentListResponse(BaseModel):
    agents: list[dict[str, str]]
    total: int


class ConfigResponse(BaseModel):
    environment: str
    agents: dict
    models: list[str]
    tools_summary: dict


# Global variables
workflow_executor: WorkflowExecutor | None = None
agent_configs: AgentConfigs | None = None
model_configs: ModelConfigs | None = None
tool_configs: ToolConfigs | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global workflow_executor, agent_configs, model_configs, tool_configs

    # Startup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Initializing AI Agent API server...")

    try:
        # Initialize configurations
        agent_configs = AgentConfigs()
        model_configs = ModelConfigs()
        tool_configs = ToolConfigs()

        # Initialize workflow executor
        workflow_executor = WorkflowExecutor()

        logger.info("Server initialized successfully")
        logger.info(f"Environment: {agent_configs.environment.value}")
        logger.info(f"Available agents: {len(list_available_agents())}")
        logger.info(f"Available models: {len(model_configs.models)}")

    except Exception as e:
        logger.error(f"Failed to initialize server: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Agent API server...")


# Create FastAPI app
app = FastAPI(
    title="AI Agent Data Stack API",
    description="REST API for the AI Agent Data Stack system",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    try:
        available_agents = list_available_agents()

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            agents_available=len(available_agents),
            models_configured=len(model_configs.models) if model_configs else 0,
            environment=agent_configs.environment.value if agent_configs else "unknown",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# Process agent request
@app.post("/agents/process", response_model=AgentResponse)
async def process_agent_request(
    request: AgentRequest, background_tasks: BackgroundTasks
):
    """Process a request using the AI agent system."""
    try:
        if not workflow_executor:
            raise HTTPException(
                status_code=500, detail="Workflow executor not initialized"
            )

        # Process the request
        result = await workflow_executor.process_request(
            request.prompt,
            output_format=request.output_format,
            metadata=request.metadata,
        )

        # Extract agent roles from result
        agent_roles = []
        if hasattr(result, "agents_involved"):
            agent_roles = [role.value for role in result.agents_involved]

        return AgentResponse(
            status=result.status,
            content=result.content,
            execution_id=result.execution_id,
            execution_time=getattr(result, "execution_time", None),
            agent_roles=agent_roles,
            confidence=getattr(result, "confidence", None),
            metadata=getattr(result, "metadata", {}),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# Get available agents
@app.get("/agents", response_model=AgentListResponse)
async def get_agents():
    """Get list of available agents."""
    try:
        available_agents = list_available_agents()

        agents_list = []
        for role in available_agents:
            agent = get_agent(role)
            capabilities = await agent.get_capabilities()

            agents_list.append(
                {
                    "role": role.value,
                    "name": role.value.replace("_", " ").title(),
                    "description": f"Specialized agent for {role.value.replace('_', ' ')}",
                    "capabilities_count": len(capabilities),
                    "status": "available",
                }
            )

        return AgentListResponse(agents=agents_list, total=len(agents_list))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")


# Get agent details
@app.get("/agents/{agent_role}")
async def get_agent_details(agent_role: str):
    """Get detailed information about a specific agent."""
    try:
        # Convert string to AgentRole
        try:
            role = AgentRole(agent_role.lower())
        except ValueError:
            raise HTTPException(
                status_code=404, detail=f"Agent role '{agent_role}' not found"
            )

        agent = get_agent(role)
        capabilities = await agent.get_capabilities()
        health = await agent.health_check()

        # Get agent configuration
        config = agent_configs.get_config(role) if agent_configs else None

        # Get available tools
        tools = tool_configs.get_agent_tools(role) if tool_configs else []

        return {
            "role": role.value,
            "name": role.value.replace("_", " ").title(),
            "capabilities": capabilities,
            "health": health,
            "configuration": config.to_dict() if config else None,
            "available_tools": tools,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get agent details: {str(e)}"
        )


# Get system configuration
@app.get("/config", response_model=ConfigResponse)
async def get_configuration():
    """Get system configuration summary."""
    try:
        if not all([agent_configs, model_configs, tool_configs]):
            raise HTTPException(status_code=500, detail="Configuration not initialized")

        return ConfigResponse(
            environment=agent_configs.environment.value,
            agents=agent_configs.export_configs(),
            models=list(model_configs.models.keys()),
            tools_summary=tool_configs.get_permissions_summary(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get configuration: {str(e)}"
        )


# Execute specific agent task
@app.post("/agents/{agent_role}/execute")
async def execute_agent_task(agent_role: str, task: str):
    """Execute a specific task with a designated agent."""
    try:
        # Convert string to AgentRole
        try:
            role = AgentRole(agent_role.lower())
        except ValueError:
            raise HTTPException(
                status_code=404, detail=f"Agent role '{agent_role}' not found"
            )

        agent = get_agent(role)
        result = await agent.execute_task(task)

        return {
            "status": "completed",
            "agent_role": role.value,
            "task": task,
            "result": {
                "content": result.content,
                "confidence": result.confidence,
                "recommendations": result.recommendations,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logging.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error", "error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
