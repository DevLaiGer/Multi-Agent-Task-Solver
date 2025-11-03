"""Tests for the workflow execution engine."""

import asyncio
import pytest

from src.agents import BaseAgent, agent_registry
from src.core import ExecutionEngine
from src.models import AgentDefinition, AgentStatus, WorkflowRequest


class IncrementAgent(BaseAgent):
    async def execute(self, input_data):
        value = input_data.get("counter", 0)
        return {"counter": value + 1}


class FailingAgent(BaseAgent):
    async def execute(self, input_data):
        raise RuntimeError("boom")


@pytest.fixture(autouse=True)
def cleanup_registry():
    agent_registry.unregister("increment")
    agent_registry.unregister("fail")
    yield
    agent_registry.unregister("increment")
    agent_registry.unregister("fail")


@pytest.mark.asyncio
async def test_execution_engine_success(monkeypatch):
    agent_registry.register("increment", IncrementAgent)
    engine = ExecutionEngine()

    request = WorkflowRequest(
        workflow_id="wf1",
        agents=[
            AgentDefinition(agent_id="step1", agent_type="increment", inputs=[]),
            AgentDefinition(
                agent_id="step2", agent_type="increment", inputs=["step1"]
            ),
        ],
        initial_input={"counter": 1},
    )

    response = await engine.execute_workflow(request)

    assert response.status.name.lower() == "completed"
    assert response.results["step2"].output == {"counter": 2}


@pytest.mark.asyncio
async def test_execution_engine_failure(monkeypatch):
    agent_registry.register("increment", IncrementAgent)
    agent_registry.register("fail", FailingAgent)
    engine = ExecutionEngine()

    request = WorkflowRequest(
        workflow_id="wf_fail",
        agents=[
            AgentDefinition(agent_id="step1", agent_type="increment", inputs=[]),
            AgentDefinition(agent_id="step2", agent_type="fail", inputs=["step1"]),
        ],
        initial_input={"counter": 5},
    )

    response = await engine.execute_workflow(request)

    assert response.status.name.lower() == "failed"
    assert response.results["step2"].status is AgentStatus.FAILED


@pytest.mark.asyncio
async def test_cancel_workflow(monkeypatch):
    class SlowAgent(BaseAgent):
        async def execute(self, input_data):
            await asyncio.sleep(0.2)
            return {}

    agent_registry.register("slow", SlowAgent)
    engine = ExecutionEngine()

    request = WorkflowRequest(
        workflow_id="wf_cancel",
        agents=[AgentDefinition(agent_id="slow_agent", agent_type="slow", inputs=[])],
    )

    task = asyncio.create_task(engine.execute_workflow(request))
    await asyncio.sleep(0.05)
    engine.cancel_workflow("wf_cancel")

    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_initial_input_propagation():
    agent_registry.register("increment", IncrementAgent)
    engine = ExecutionEngine()

    request = WorkflowRequest(
        workflow_id="wf_initial",
        agents=[AgentDefinition(agent_id="step1", agent_type="increment", inputs=[])],
        initial_input={"counter": 10},
    )

    response = await engine.execute_workflow(request)

    assert response.results["step1"].output == {"counter": 11}
