"""API routes for the Multi-Agent Task Solver."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, FastAPI, HTTPException, status

from .. import __version__
from ..agents import agent_registry
from ..core import ExecutionEngine
from ..models import WorkflowRequest, WorkflowResponse
from ..tools import register_builtin_tools, tool_registry

_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "linear_two_step": {
        "workflow_id": "linear_example",
        "initial_input": {"value": 1},
        "agents": [
            {
                "agent_id": "step_a",
                "agent_type": "increment",
                "inputs": [],
            },
            {
                "agent_id": "step_b",
                "agent_type": "increment",
                "inputs": ["step_a"],
            },
        ],
    }
}


def _create_router(engine: ExecutionEngine) -> APIRouter:
    router = APIRouter()

    @router.get("/", summary="Root", tags=["meta"])
    async def root() -> Dict[str, str]:
        return {
            "application": "Multi-Agent Task Solver",
            "version": __version__,
        }

    @router.get("/health", summary="Health check", tags=["meta"])
    async def health() -> Dict[str, str]:
        return {"status": "ok"}

    @router.get("/agents", summary="List registered agents", tags=["registry"])
    async def list_agents() -> Dict[str, Any]:
        return {"agents": list(agent_registry.list_agents())}

    @router.get("/tools", summary="List registered tools", tags=["registry"])
    async def list_tools() -> Dict[str, Any]:
        return {"tools": list(tool_registry.list_tools())}

    @router.post(
        "/workflows",
        response_model=WorkflowResponse,
        summary="Execute a workflow",
        tags=["workflows"],
    )
    async def execute_workflow(request: WorkflowRequest) -> WorkflowResponse:
        return await engine.execute_workflow(request)

    @router.get(
        "/workflows/{workflow_id}",
        response_model=WorkflowResponse,
        summary="Get workflow status",
        tags=["workflows"],
    )
    async def get_workflow(workflow_id: str) -> WorkflowResponse:
        response = engine.get_workflow_status(workflow_id)
        if response is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found",
            )
        return response

    @router.post(
        "/workflows/{workflow_id}/cancel",
        summary="Cancel a running workflow",
        tags=["workflows"],
    )
    async def cancel_workflow(workflow_id: str) -> Dict[str, Any]:
        cancelled = engine.cancel_workflow(workflow_id)
        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not active or already completed",
            )
        return {"workflow_id": workflow_id, "status": "cancelled"}

    @router.get(
        "/workflows/templates/{template_name}",
        summary="Retrieve a workflow template",
        tags=["workflows"],
    )
    async def get_template(template_name: str) -> Dict[str, Any]:
        template = _TEMPLATES.get(template_name)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        return template

    return router


def create_app() -> FastAPI:
    """Instantiate the FastAPI application."""

    app = FastAPI(
        title="Multi-Agent Task Solver",
        version=__version__,
        description="API layer for coordinating multi-agent workflows.",
    )

    engine = ExecutionEngine()
    register_builtin_tools()
    app.state.engine = engine

    app.include_router(_create_router(engine))

    return app
