"""
Core data models and schemas for the Multi-Agent Task Solver system.

This module defines the fundamental data structures used throughout the system:
- Status enumerations for agents and workflows
- Agent definition with configuration and dependencies
- Workflow request with agent composition
- Execution results and responses
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class AgentStatus(str, Enum):
    """Enumeration of possible agent execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class WorkflowStatus(str, Enum):
    """Enumeration of possible workflow execution states."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentDefinition(BaseModel):
    """
    Definition of an agent in the workflow.
    
    This model specifies how an agent should be instantiated and executed,
    including its dependencies on other agents and configuration parameters.
    """
    agent_id: str = Field(..., description="Unique identifier for the agent")
    agent_type: str = Field(..., description="Type of agent to execute")
    inputs: List[str] = Field(default_factory=list, description="Input dependencies from other agents")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific configuration")
    retry_count: int = Field(default=3, description="Number of retry attempts")
    timeout_seconds: int = Field(default=30, description="Timeout in seconds")
    
    class Config:
        """Pydantic configuration for AgentDefinition."""
        json_schema_extra = {
            "example": {
                "agent_id": "data_processor_1",
                "agent_type": "data_processor",
                "inputs": ["data_fetcher_1"],
                "config": {"operation": "filter", "threshold": 100},
                "retry_count": 3,
                "timeout_seconds": 30
            }
        }


class WorkflowRequest(BaseModel):
    """
    Request to create and execute a workflow.
    
    A workflow consists of multiple agents that are executed in a coordinated
    manner based on their dependencies, forming a Directed Acyclic Graph (DAG).
    """
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique workflow identifier")
    agents: List[AgentDefinition] = Field(..., description="List of agents in the workflow")
    initial_input: Dict[str, Any] = Field(default_factory=dict, description="Initial input data")
    
    class Config:
        """Pydantic configuration for WorkflowRequest."""
        json_schema_extra = {
            "example": {
                "workflow_id": "workflow_123",
                "agents": [
                    {
                        "agent_id": "fetcher",
                        "agent_type": "data_fetcher",
                        "inputs": [],
                        "config": {"source": "database"}
                    },
                    {
                        "agent_id": "processor",
                        "agent_type": "data_processor",
                        "inputs": ["fetcher"],
                        "config": {"operation": "filter"}
                    }
                ],
                "initial_input": {"query": "SELECT * FROM data"}
            }
        }


class AgentResult(BaseModel):
    """
    Result from agent execution.
    
    Captures the outcome of an agent's execution including status,
    output data, errors, and execution metrics.
    """
    agent_id: str = Field(..., description="Identifier of the executed agent")
    status: AgentStatus = Field(..., description="Execution status")
    output: Optional[Dict[str, Any]] = Field(None, description="Agent output data")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: Optional[float] = Field(None, description="Execution duration in seconds")
    retry_count: int = Field(default=0, description="Number of retries performed")
    
    class Config:
        """Pydantic configuration for AgentResult."""
        json_schema_extra = {
            "example": {
                "agent_id": "data_processor_1",
                "status": "completed",
                "output": {"processed_items": 100, "filtered_count": 45},
                "error": None,
                "execution_time": 2.5,
                "retry_count": 0
            }
        }


class WorkflowResponse(BaseModel):
    """
    Workflow execution response.
    
    Contains the complete state of a workflow execution including
    all agent results, overall status, and timing information.
    """
    workflow_id: str = Field(..., description="Unique workflow identifier")
    status: WorkflowStatus = Field(..., description="Overall workflow status")
    results: Dict[str, AgentResult] = Field(default_factory=dict, description="Results from each agent")
    total_duration: Optional[float] = Field(None, description="Total workflow duration in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Workflow creation timestamp")
    
    class Config:
        """Pydantic configuration for WorkflowResponse."""
        json_schema_extra = {
            "example": {
                "workflow_id": "workflow_123",
                "status": "completed",
                "results": {
                    "fetcher": {
                        "agent_id": "fetcher",
                        "status": "completed",
                        "output": {"data": [1, 2, 3]},
                        "execution_time": 1.5
                    },
                    "processor": {
                        "agent_id": "processor",
                        "status": "completed",
                        "output": {"filtered_data": [3]},
                        "execution_time": 0.5
                    }
                },
                "total_duration": 2.1,
                "created_at": "2024-01-01T00:00:00"
            }
        }
