"""
Tests for data models and schemas.
"""

from datetime import datetime
from src.models import (
    AgentStatus,
    WorkflowStatus,
    AgentDefinition,
    WorkflowRequest,
    AgentResult,
    WorkflowResponse
)


class TestEnums:
    """Test enum types."""
    
    def test_agent_status_values(self):
        """Test AgentStatus enum values."""
        assert AgentStatus.PENDING == "pending"
        assert AgentStatus.RUNNING == "running"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"
        assert AgentStatus.RETRYING == "retrying"
    
    def test_workflow_status_values(self):
        """Test WorkflowStatus enum values."""
        assert WorkflowStatus.CREATED == "created"
        assert WorkflowStatus.RUNNING == "running"
        assert WorkflowStatus.COMPLETED == "completed"
        assert WorkflowStatus.FAILED == "failed"
        assert WorkflowStatus.CANCELLED == "cancelled"


class TestAgentDefinition:
    """Test AgentDefinition model."""
    
    def test_agent_definition_creation(self):
        """Test creating an agent definition."""
        agent_def = AgentDefinition(
            agent_id="test_agent",
            agent_type="data_processor",
            inputs=["agent1", "agent2"],
            config={"param1": "value1"},
            retry_count=5,
            timeout_seconds=60
        )
        
        assert agent_def.agent_id == "test_agent"
        assert agent_def.agent_type == "data_processor"
        assert len(agent_def.inputs) == 2
        assert agent_def.config["param1"] == "value1"
        assert agent_def.retry_count == 5
        assert agent_def.timeout_seconds == 60
    
    def test_agent_definition_defaults(self):
        """Test default values in agent definition."""
        agent_def = AgentDefinition(
            agent_id="test_agent",
            agent_type="data_processor"
        )
        
        assert agent_def.inputs == []
        assert agent_def.config == {}
        assert agent_def.retry_count == 3
        assert agent_def.timeout_seconds == 30
    
    def test_agent_definition_serialization(self):
        """Test JSON serialization."""
        agent_def = AgentDefinition(
            agent_id="test_agent",
            agent_type="test"
        )
        
        data = agent_def.model_dump()
        assert "agent_id" in data
        assert "agent_type" in data
        assert data["agent_id"] == "test_agent"


class TestWorkflowRequest:
    """Test WorkflowRequest model."""
    
    def test_workflow_request_creation(self):
        """Test creating a workflow request."""
        workflow_req = WorkflowRequest(
            agents=[
                AgentDefinition(
                    agent_id="agent1",
                    agent_type="fetcher",
                    inputs=[]
                ),
                AgentDefinition(
                    agent_id="agent2",
                    agent_type="processor",
                    inputs=["agent1"]
                )
            ],
            initial_input={"key": "value"}
        )
        
        assert len(workflow_req.agents) == 2
        assert workflow_req.workflow_id is not None
        assert workflow_req.initial_input["key"] == "value"
    
    def test_workflow_request_auto_id(self):
        """Test automatic workflow ID generation."""
        workflow_req = WorkflowRequest(agents=[])
        
        assert workflow_req.workflow_id is not None
        assert len(workflow_req.workflow_id) > 0
    
    def test_workflow_request_custom_id(self):
        """Test custom workflow ID."""
        custom_id = "my_workflow_123"
        workflow_req = WorkflowRequest(
            workflow_id=custom_id,
            agents=[]
        )
        
        assert workflow_req.workflow_id == custom_id


class TestAgentResult:
    """Test AgentResult model."""
    
    def test_agent_result_success(self):
        """Test successful agent result."""
        result = AgentResult(
            agent_id="test_agent",
            status=AgentStatus.COMPLETED,
            output={"result": "success"},
            execution_time=2.5,
            retry_count=0
        )
        
        assert result.agent_id == "test_agent"
        assert result.status == AgentStatus.COMPLETED
        assert result.output["result"] == "success"
        assert result.execution_time == 2.5
        assert result.retry_count == 0
        assert result.error is None
    
    def test_agent_result_failure(self):
        """Test failed agent result."""
        result = AgentResult(
            agent_id="test_agent",
            status=AgentStatus.FAILED,
            error="Connection timeout",
            execution_time=30.0,
            retry_count=3
        )
        
        assert result.agent_id == "test_agent"
        assert result.status == AgentStatus.FAILED
        assert result.error == "Connection timeout"
        assert result.output is None
        assert result.retry_count == 3


class TestWorkflowResponse:
    """Test WorkflowResponse model."""
    
    def test_workflow_response_creation(self):
        """Test creating a workflow response."""
        response = WorkflowResponse(
            workflow_id="test_workflow",
            status=WorkflowStatus.COMPLETED,
            results={
                "agent1": AgentResult(
                    agent_id="agent1",
                    status=AgentStatus.COMPLETED,
                    output={"data": [1, 2, 3]},
                    execution_time=1.0
                )
            },
            total_duration=3.5
        )
        
        assert response.workflow_id == "test_workflow"
        assert response.status == WorkflowStatus.COMPLETED
        assert "agent1" in response.results
        assert response.total_duration == 3.5
        assert isinstance(response.created_at, datetime)
    
    def test_workflow_response_empty_results(self):
        """Test workflow response with no results."""
        response = WorkflowResponse(
            workflow_id="test_workflow",
            status=WorkflowStatus.CREATED
        )
        
        assert response.results == {}
        assert response.total_duration is None
    
    def test_workflow_response_serialization(self):
        """Test JSON serialization of workflow response."""
        response = WorkflowResponse(
            workflow_id="test_workflow",
            status=WorkflowStatus.COMPLETED,
            results={}
        )
        
        data = response.model_dump()
        assert "workflow_id" in data
        assert "status" in data
        assert "results" in data
        assert data["workflow_id"] == "test_workflow"
